"""Create ordinary compact delivery ZIPs from an already verified full archive.

Refines the successful batch01 split workflow. It never mutates the source ZIP.
Source/assets remain independently usable. Only optional history is byte-split.
"""
from pathlib import Path
import argparse, hashlib, json, zipfile
from source_family_packages import partition_sources, is_review_file

PAYLOAD=7_500_000
LIMIT=8_000_000

def sha(raw):return hashlib.sha256(raw).hexdigest()

def read_manifest(z):
 names=[n for n in z.namelist() if n.endswith('/BACKUP_MANIFEST.json')]
 if len(names)!=1:raise ValueError('Expected exactly one backup manifest')
 path=names[0];return path.rsplit('/',1)[0]+'/',json.loads(z.read(path))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('full_zip',type=Path);ap.add_argument('output_dir',type=Path);ap.add_argument('--label',required=True);ap.add_argument('--base-zip',type=Path);ap.add_argument('--base-library-file-id');ap.add_argument('--family-sources',action='store_true');a=ap.parse_args()
 if any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for c in a.label):raise SystemExit('Use a simple label')
 if a.output_dir.exists():raise SystemExit('Output directory exists; preserve it and choose a new delivery version')
 a.output_dir.mkdir(parents=True)
 base={};base_manifest=None
 if a.base_zip:
  with zipfile.ZipFile(a.base_zip) as bz:
   if bz.testzip():raise ValueError('Base archive CRC failed')
   _,base_manifest=read_manifest(bz);base={r['path']:r['sha256'] for r in base_manifest['files']}
 outputs=[];coverage={};prior=[]
 def write_zip(name,items,note):
  p=a.output_dir/(a.label+'_'+name+'.zip')
  with zipfile.ZipFile(p,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as out:
   for n,b in items:out.writestr(n,b)
   out.writestr('START_HERE.txt',note+'\n')
   out.writestr('PACKAGE_CHECKSUMS.json',json.dumps([{'path':n,'bytes':len(b),'sha256':sha(b)} for n,b in items],indent=2)+'\n')
  with zipfile.ZipFile(p) as out:
   if out.testzip():raise ValueError('New archive CRC failed: '+str(p))
   for n,b in items:
    if sha(out.read(n))!=sha(b):raise ValueError('New archive byte mismatch: '+n)
  if p.stat().st_size>=LIMIT:raise ValueError('Package exceeds8MB; do not deliver: '+str(p))
  outputs.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())})
 with zipfile.ZipFile(a.full_zip) as z:
  if z.testzip():raise ValueError('Full archive CRC failed')
  prefix,manifest=read_manifest(z);sources=[];reviews=[]
  for row in manifest['files']:
   rel=row['path'];raw=z.read(prefix+rel)
   if sha(raw)!=row['sha256']:raise ValueError('Source manifest mismatch: '+rel)
   review=is_review_file(rel)
   if review and base.get(rel)==row['sha256']:
    prior.append(row);coverage[rel]='prior_verified_archive';continue
   target=reviews if review else sources
   target.append(('Astraea_Catalogue/'+rel,raw));coverage[rel]='review' if review else 'source'
  restoration={'scope':'New independent Blender catalogue only, no original game recovery','git_commit':manifest['git_commit'],'source_assets':'Complete current editable sources, generators, runtime texture dependencies and exported models. No optional Git step is needed to use them.','review':'New or changed review evidence is supplied separately. Unchanged prior review/reference files remain in the named verified archive.','prior_archive_library_file_id':a.base_library_file_id,'prior_commit':base_manifest['git_commit'] if base_manifest else None,'prior_review_files':prior,'source_history':manifest['source_history'],'all_tracked_files_classified':len(coverage)==len(manifest['files'])}
  sources.append(('Astraea_Catalogue/RESTORATION_MANIFEST.json',json.dumps(restoration,indent=2).encode()))
  if a.family_sources:
   config=json.loads(z.read(prefix+'standards/source_package_groups.json'));catalogue=json.loads(z.read(prefix+'catalogue_manifest.json'))
   for family,items,_ in partition_sources(sources,config,catalogue):
    write_zip('Source_'+family,items,'COMPLETE EDITABLE FAMILY SOURCE/ASSETS. Extract normally. All common material/generator dependencies are included. Read FAMILY_CONTENTS_'+family+'.json for the exact supplied assets. Multiple family ZIPs may be extracted together; shared files are byte-identical. Review media/history are separate. This is not the missing original game.')
  else:
   write_zip('Source_Assets',sources,'CURRENT EDITABLE CATALOGUE SOURCE/ASSETS. Extract normally. Materials and generator dependencies are included. Review media and optional history are separate. This is not the missing original game.')
  buckets=[[]];size=0
  for item in reviews:
   # Large structured evidence may compress to a small ordinary ZIP. Keep it
   # whole in a dedicated bucket; write_zip still enforces the actual 8MB cap.
   # No file is truncated, rewritten, split internally, or silently omitted.
   if len(item[1])>PAYLOAD:
    if buckets[-1]:buckets.append([])
    buckets[-1].append(item);buckets.append([]);size=0;continue
   if buckets[-1] and size+len(item[1])>PAYLOAD:buckets.append([]);size=0
   buckets[-1].append(item);size+=len(item[1])
  for i,items in enumerate(buckets,1):
   if items:write_zip('Review_%02d'%i,items,'NEW/CHANGED COMPONENT REVIEW MEDIA. Extract with the current Source_Assets ZIP. These are Blender component checks; no game or physics acceptance is implied. See RESTORATION_MANIFEST.json for prior unchanged references/evidence.')
  hist=z.read(prefix+'source-history.bundle');expected=sha(hist);chunks=[hist[i:i+PAYLOAD] for i in range(0,len(hist),PAYLOAD)]
  stem=a.label+'_history.bundle';names=[stem+'.part%02d'%(i+1) for i in range(len(chunks))]
  ps="$ErrorActionPreference = 'Stop'\n$base = $PSScriptRoot\n$out = Join-Path $base '"+stem+"'\nif (Test-Path $out) { throw 'Output exists; preserve it before restoring.' }\n$names = @("+', '.join("'"+n+"'" for n in names)+")\nforeach ($n in $names) { if (-not (Test-Path (Join-Path $base $n))) { throw ('Missing ' + $n) } }\n$stream = [System.IO.File]::Create($out)\ntry { foreach ($n in $names) { $bytes = [System.IO.File]::ReadAllBytes((Join-Path $base $n)); $stream.Write($bytes,0,$bytes.Length) } } finally { $stream.Dispose() }\nif ((Get-FileHash -Algorithm SHA256 $out).Hash.ToLowerInvariant() -ne '"+expected+"') { throw 'Checksum mismatch; do not use bundle.' }\nWrite-Output 'History bytes restored and checksum verified. No project code executed.'\n"
  for i,raw in enumerate(chunks):
   items=[('history/'+names[i],raw)]
   if i==0:items += [('history/Restore-Version-History.ps1',ps.encode()),('history/HISTORY_MANIFEST.json',json.dumps(manifest['source_history'],indent=2).encode())]
   write_zip('Optional_History_%02d'%(i+1),items,'OPTIONAL GIT HISTORY ONLY. Extract every history ZIP into one folder. The PowerShell join helper reconstructs and verifies the unchanged bundle; it does not run project code. Incremental history requires the prior backed-up commit identified in HISTORY_MANIFEST.json. Source_Assets ZIP needs no history restore.')
  if b''.join(chunks)!=hist:raise ValueError('History segment reassembly mismatch')
 report={'full_archive':str(a.full_zip),'full_archive_sha256':sha(a.full_zip.read_bytes()),'git_commit':manifest['git_commit'],'source_delivery':'complete_family_zips' if a.family_sources else 'complete_catalogue_zip','outputs':outputs,'tracked_files':len(coverage),'current_source_files':sum(x=='source' for x in coverage.values()),'current_review_files':sum(x=='review' for x in coverage.values()),'prior_unchanged_review_files':len(prior),'all_files_accounted_for':len(coverage)==len(manifest['files']),'history_reassembly_sha256':expected,'all_outputs_below_8MB':all(x['bytes']<LIMIT for x in outputs)}
 (a.output_dir/'DELIVERY_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))

if __name__=='__main__':main()
