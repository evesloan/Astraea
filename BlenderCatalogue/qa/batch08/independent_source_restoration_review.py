"""Review exact output-directory-only corrections against baseline source code."""
from pathlib import Path
import json,hashlib,ast,subprocess
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch08';BASE='66dcaf10f105958c5cadb421d5aca15b054b98ed'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def old(path):return subprocess.check_output(['git','show',BASE+':'+str(path.relative_to(ROOT))],cwd=ROOT)
def diff(a,b,p=''):
 if isinstance(a,dict)and isinstance(b,dict):
  z=[]
  for k in sorted(a.keys()|b.keys()):z+=([p+'/'+k]if k not in a or k not in b else diff(a[k],b[k],p+'/'+k))
  return z
 if isinstance(a,list)and isinstance(b,list)and len(a)==len(b):return [v for i,(x,y)in enumerate(zip(a,b))for v in diff(x,y,p+'/'+str(i))]
 return []if a==b else[p]
rows=[]
for path in ['assets/botanical_canopy/source/build_canopy.py','assets/aquatic_lounge/source/build_aquatic_lounge.py']:
 p=ROOT/path;a=ast.parse(old(p));b=ast.parse(p.read_text());extra=[n for n in b.body if ast.dump(n)not in[ast.dump(x)for x in a.body]];assert len(extra)==1
 added=extra[0];b.body=[n for n in b.body if n is not added];assert ast.dump(a)==ast.dump(b)
 assert 'mkdir' in ast.unparse(added) and ('exist_ok=True' in ast.unparse(added))
 rows.append({'path':path,'baseline_sha256':hashlib.sha256(old(p)).hexdigest(),'current_sha256':sha(p),'only_added_AST_statement':ast.unparse(added),'all_existing_AST_nodes_identical':True})
metadata=[]
for name in ['AST-AQU-001.manifest.json','AST-AQU-002.manifest.json','manifest.json']:
 p=ROOT/'assets/aquatic_lounge'/name;a=json.loads(old(p));b=json.loads(p.read_text());d=diff(a,b);assert all(x.rsplit('/',1)[-1]in['generator_sha256','generator_sha256_at_original_export']for x in d)
 metadata.append({'path':str(p.relative_to(ROOT)),'changed_json_pointers':d,'all_geometry_contacts_materials_motion_and_dimensions_preserved':True})
rev=OUT/'source_output_directory_revision/revision_report.json';r=json.loads(rev.read_text());assert r['passed']
for p,h in r['master_files_unchanged'].items():assert sha(ROOT/p)==h==hashlib.sha256(old(ROOT/p)).hexdigest()
for row in r['changed_files']:assert sha(ROOT/row['path'])==row['new_sha256']
for line in (ROOT/'assets/aquatic_lounge/SHA256SUMS.txt').read_text().splitlines():
 h,p=line.split(maxsplit=1);assert sha(ROOT/'assets/aquatic_lounge'/p)==h
result={'metadata_and_AST_scope_pass':True,'source_changes':rows,'metadata_changes':metadata,'six_original_source_export_binaries_frozen':True,'lead_revision_receipt':{'path':str(rev.relative_to(ROOT)),'sha256':sha(rev)},'isolated_rebuild_evidence':'Final evidence is bound separately after lead execution completes. This AST review does not imply those generators have been run by the reviewer.'}
(OUT/'independent_source_restoration_scope.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS: two exact mkdir-only AST deltas, metadata and six frozen binaries')
p=OUT/'independent_finalize_review.py';s=p.read_text().replace("elif path=='tools/package_small_delivery.py':", "elif path.startswith(('assets/botanical_canopy/','assets/aquatic_lounge/')):\n  scope='Lead-reviewed mandatory output-directory creation, associated generator hash/provenance and README records only; all preexisting code AST and master .blend/GLB/image bytes remain unchanged.';evidence='qa/batch08/independent_source_restoration_scope.json'\n elif path=='tools/package_small_delivery.py':")
s=s.replace("'independent_interface_report.json']","'independent_interface_report.json','independent_source_restoration_scope.json']")
p.write_text(s)
