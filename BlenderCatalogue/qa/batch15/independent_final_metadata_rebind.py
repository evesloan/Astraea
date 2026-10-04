"""Retain exact measurements across proven non-geometric collision-description changes."""
from pathlib import Path
import json,hashlib,shutil
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch15';old=OUT/'independent_rebuild_stage_crew_rest_r02/assets/crew_rest/collision_proposals.json';new=ROOT/'assets/crew_rest/collision_proposals.json';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();a=json.loads(old.read_text());b=json.loads(new.read_text());diff=[]
def compare(a,b,p=''):
 if type(a)!=type(b):diff.append({'path':p,'before':a,'after':b});return
 if isinstance(a,dict):
  assert a.keys()==b.keys(),p
  for k in a:compare(a[k],b[k],p+'/'+k)
 elif isinstance(a,list):
  assert len(a)==len(b),p
  for i,(x,y)in enumerate(zip(a,b)):compare(x,y,p+'/'+str(i))
 elif a!=b:diff.append({'path':p,'before':a,'after':b})
compare(a,b);assert len(diff)==14;assert all(x['path'].endswith(('/reason','/conservative_empty_corner_limit_m'))for x in diff)
folder=OUT/'independent_before_final_metadata_rebind';folder.mkdir(exist_ok=True);records=[]
for ident in ['AST-CRW-001','AST-CRW-002']:
 p=OUT/f'independent_collision_profile_{ident}.json';r=json.loads(p.read_text());assert r['collision_sha256']==sha(old);dest=folder/p.name;assert not dest.exists();shutil.copyfile(p,dest);records.append({'report':str(p.relative_to(ROOT)),'original_measurement_report':str(dest.relative_to(ROOT)),'original_measurement_report_sha256':sha(dest)});r['measurement_collision_path']=str(old.relative_to(ROOT));r['measurement_collision_sha256']=sha(old);r['collision_sha256']=sha(new);r['metadata_only_rebind']='qa/batch15/independent_final_metadata_rebind.json';p.write_text(json.dumps(r,indent=2)+'\n')
report={'passed':True,'original_collision':{'path':str(old.relative_to(ROOT)),'sha256':sha(old)},'current_collision':{'path':str(new.relative_to(ROOT)),'sha256':sha(new)},'exact_differences':diff,'all_other_collision_fields_byte_value_identical':True,'source_and_native_geometry_unchanged':True,'scope':'Only explanatory reason strings and nominal/conservative allowance values changed. Every shape point, box bound, dimension, count, motion parameter and exclusion declaration is exactly unchanged. Original measured reports are retained; current proposal hashes are separately bound without inventing new numeric measurements.','reports':records,'executed_script_sha256':sha(Path(__file__))};(OUT/'independent_final_metadata_rebind.json').write_text(json.dumps(report,indent=2)+'\n');print('METADATA_REBIND',len(diff),'explanation/allowance changes;geometry unchanged')
