"""Freeze a complete catalogue checkpoint for verified durable upload.

Does not upload, run model generators, or touch the missing game location.
Run only after review and commit. Existing outputs are never overwritten.
"""
from pathlib import Path
import argparse, hashlib, json, subprocess, tempfile, zipfile

ROOT=Path(__file__).resolve().parents[1]

def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('output_zip',type=Path);args=ap.parse_args()
 output=args.output_zip.resolve()
 if output.exists(): raise SystemExit('Output exists; use a new versioned archive path')
 if output.is_relative_to(ROOT): raise SystemExit('Archive must be outside source tree')
 status=subprocess.check_output(['git','-C',str(ROOT),'status','--porcelain'],text=True)
 if status: raise SystemExit('Commit the reviewed source snapshot before packaging:\n'+status)
 commit=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
 names=subprocess.check_output(['git','-C',str(ROOT),'ls-files','-z']).decode().split('\0')
 files=[ROOT/n for n in names if n]
 rows=[]
 for p in files:
  if not p.is_file() or p.is_symlink(): raise SystemExit('Unexpected non-regular source: '+str(p))
  rows.append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p)})
 manifest={'kind':'complete-independent-catalogue-batch','original_game_recovered':False,
   'scope':'New Blender catalogue only; no live-game integration or recovery claim.',
   'git_commit':commit,'files':rows}
 output.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='astraea-catalogue-freeze-') as tmp:
  bundle=Path(tmp)/'source-history.bundle'
  subprocess.run(['git','-C',str(ROOT),'bundle','create',str(bundle),'--all'],check=True)
  subprocess.run(['git','-C',str(ROOT),'bundle','verify',str(bundle)],check=True,capture_output=True)
  manifest['source_history']={'path':'source-history.bundle','bytes':bundle.stat().st_size,'sha256':digest(bundle)}
  with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
   for row,p in zip(rows,files):z.write(p,'Astraea_Catalogue_Batch01/'+row['path'])
   z.write(bundle,'Astraea_Catalogue_Batch01/source-history.bundle')
   z.writestr('Astraea_Catalogue_Batch01/BACKUP_MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
 for row,p in zip(rows,files):
  if digest(p)!=row['sha256']: raise SystemExit('Source changed during archive: '+row['path'])
 with zipfile.ZipFile(output) as z:
  bad=z.testzip()
  if bad: raise SystemExit('CRC failure: '+bad)
  for row in rows:
   if hashlib.sha256(z.read('Astraea_Catalogue_Batch01/'+row['path'])).hexdigest()!=row['sha256']:raise SystemExit('Archive hash mismatch: '+row['path'])
 report={'archive':str(output),'bytes':output.stat().st_size,'sha256':digest(output),'git_commit':commit,'files':len(rows),'crc_pass':True,'source_snapshot_unchanged':True,'durable_upload':'pending durable Library verification'}
 output.with_suffix('.verification.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))

if __name__=='__main__':main()
