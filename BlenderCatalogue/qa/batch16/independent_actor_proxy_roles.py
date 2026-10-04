"""Bind every proxy-retained/omitted role to actual frozen semantic source materials."""
from pathlib import Path
import json,hashlib,numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch16';SIDE=ROOT/'assets/auditorium_use/actor_proxies';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rp=SIDE/'selection_rationale.json';r=json.loads(rp.read_text());cp=SIDE/'body_subset_checks.json';c=json.loads(cp.read_text());rows=[]
for ident,a in r['assets'].items():
 s=json.loads((OUT/f'independent_source_{ident}.json').read_text());assert sha(ROOT/s['path'])==s['sha256'];objects={x['name']:x for x in s['objects']};checked=[]
 for status in ['retained','omitted']:
  for x in a[status]:
   roles=sorted({m.removeprefix('ASTRAEA_')for p in x['covered_parts']for m in objects[p]['materials']});assert roles==sorted(x['material_roles']);checked.append({'shape_id':x['base_shape_id'],'status':status,'parts':x['covered_parts'],'source_verified_material_roles':roles,'reason':x['reason'],'pass':True})
 actual=next(x for x in c['assets']if x['catalogue_id']==ident);dimensions=[]
 for x in actual['omissions']:
  part=x['covered_parts'][0];o=objects[part];d=np.array(o['max_xyz'])-np.array(o['min_xyz']);err=float(max(abs(d-np.array(x['source_aabb_dimensions_m']))));assert err<1e-6;dimensions.append({'part':part,'actual_source_aabb_dimensions_m':d.tolist(),'declaration_max_error_m':err,'pass':True})
 rows.append({'catalogue_id':ident,'roles':checked,'omitted_part_dimensions':dimensions,'pass':True})
report={'passed':True,'assets':rows,'rationale_binding':{'path':str(rp.relative_to(ROOT)),'sha256':sha(rp)},'author_measurement_binding':{'path':str(cp.relative_to(ROOT)),'sha256':sha(cp)},'limit':'AABB dimensions describe extent and are not equated with material thickness, omission distance or actor size.','executed_script_sha256':sha(Path(__file__))};(OUT/'independent_actor_proxy_roles.json').write_text(json.dumps(report,indent=2)+'\n');print('Every retained/omitted role and omitted extent matches frozen source')
