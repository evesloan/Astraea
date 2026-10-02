"""Rebuild all products from a closed input-only package in an initially output-free tree."""
from pathlib import Path
import json,hashlib,shutil,subprocess,zipfile
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1];SANDBOX=BASE/'qa/source_only_rebuild_tree'
dep=json.loads((BASE/'dependency_manifest.json').read_text());paths=[d['path'] for d in dep['unchanged_shared_dependencies']]+[d['path'] for d in dep['production_generators']]
if SANDBOX.exists():shutil.rmtree(SANDBOX)
SANDBOX.mkdir(parents=True)
for p in paths:
 dst=SANDBOX/p;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(CAT/p,dst)
archive=BASE/'qa/salon_threshold_source_only.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in paths:z.write(CAT/p,p)
assert not list(SANDBOX.rglob('*.glb')) and not list(SANDBOX.rglob('*.blend'))
cmd=['blender','--background','--threads','2','--python-exit-code','1','--python',str(SANDBOX/'assets/salon_threshold/source/build_salon_threshold.py')]
p=subprocess.run(cmd,cwd='/tmp',text=True,capture_output=True);(BASE/'qa/source_only_rebuild.log').write_text(p.stdout+p.stderr);assert p.returncode==0
report={'status':'PASS','source_package_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'package_file_count':len(paths),'package_contains_outputs':False,'command':cmd,'invoked_from':'/tmp','output_directories_created_by_generator':True,'assets':[]}
for ident in('AST-SAL-001','AST-SAL-002','AST-SAL-003'):
 original=BASE/'exports'/f'{ident}.glb';rebuilt=SANDBOX/'assets/salon_threshold/exports'/f'{ident}.glb';match=original.read_bytes()==rebuilt.read_bytes();report['assets'].append({'catalogue_id':ident,'original_glb_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),'rebuilt_glb_sha256':hashlib.sha256(rebuilt.read_bytes()).hexdigest(),'byte_identical_glb':match});assert match,ident
(BASE/'qa/source_only_rebuild.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
# Keep the input-only zip and exhaustive result; remove duplicated rebuild products from catalogue delivery.
shutil.rmtree(SANDBOX)
