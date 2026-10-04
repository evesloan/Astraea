"""Isolated actual source rebuild, preserving every current catalogue master."""
from pathlib import Path
import hashlib,json,shutil,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[2];F=ROOT/'assets/library_contents';OUT=ROOT/'qa/batch08/library_texture_path_revision'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
masters={str(p.relative_to(ROOT)):sha(p) for p in F.rglob('*') if p.is_file() and p.suffix in ('.blend','.glb','.png') and 'qa' not in p.parts}
inputs=[F/'build_library_contents.py',F/'build_stock_variants.py',F/'make_book_textures.py',F/'texture_manifest.json',ROOT/'standards/materials.py'];commands=[];matches=[]
with tempfile.TemporaryDirectory(prefix='astraea-library-path-rebuild-') as tmp:
 t=Path(tmp);local=t/'assets/library_contents';local.mkdir(parents=True);(t/'standards').mkdir();shutil.copytree(ROOT/'materials',t/'materials')
 shutil.copy2(ROOT/'standards/materials.py',t/'standards/materials.py');shutil.copytree(F/'textures',local/'textures')
 for p in inputs:
  if p.parent==F:shutil.copy2(p,local/p.name)
 for script in ('build_library_contents.py','build_stock_variants.py'):
  cmd=['blender','--background','--threads','1','--python-exit-code','1','--python',str(local/script)]
  done=subprocess.run(cmd,cwd=t,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);(OUT/(script+'.rebuild.log')).write_text(done.stdout);assert done.returncode==0,(script,done.returncode)
  commands.append({'script':script,'exit_code':done.returncode,'render':False})
 for p in sorted(F.glob('*.glb')):
  new=local/p.name;assert new.is_file();assert new.read_bytes()==p.read_bytes(),p.name
  matches.append({'export':str(p.relative_to(ROOT)),'sha256':sha(p),'isolated_generated_bytes_identical':True})
 assert len(matches)==4
 for p in sorted(local.glob('AST-LIB-*.manifest.json')):
  m=json.loads(p.read_text());assert m['texture_manifest_interface_revision']=='library-texture-paths-02';assert m['texture_manifest_sha256']==sha(F/'texture_manifest.json')
for rel,digest in masters.items():assert sha(ROOT/rel)==digest,rel
report={'passed':True,'scope':'Actual isolated generator rebuild and four exported byte comparisons; no render, no current master overwrite, no network','commands':commands,'inputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in inputs],'byte_identical_glb_rebuilds':matches,'unchanged_current_master_files':masters,'temporary_staging_removed':True}
(OUT/'isolated_rebuild_report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'identical_glbs':len(matches),'masters_unchanged':len(masters)},indent=2))
