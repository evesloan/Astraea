"""Read-only actual native placement/interface checks for the lead's proposed arrangement."""
from pathlib import Path
import json,hashlib,sys,numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch10'
sys.path.insert(0,str(ROOT/'qa/batch07'));from independent_geometry import Native,C
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
planpath=OUT/'assembly/plan.json';plan=json.loads(planpath.read_text());items={};inputs=[bind(planpath)]
for row in plan['items']:
 n=Native(ROOT/row['path']);theta=np.deg2rad(row['source_z_rotation_deg']);rot=np.array([[np.cos(theta),-np.sin(theta),0],[np.sin(theta),np.cos(theta),0],[0,0,1.]]);pos=np.asarray(row['inspection_source_origin_m']);source=n.tris@C;placed=source@rot.T+pos;ship=placed@C.T+np.asarray(plan['inspection_origin_ship_m']);items[row['key']]={'native':n,'row':row,'rot':rot,'pos':pos,'bounds_ship_m':{'min':ship.reshape(-1,3).min(axis=0).tolist(),'max':ship.reshape(-1,3).max(axis=0).tolist()}};inputs.extend(bind(ROOT/row[k])for k in ['path','source_path','manifest_path'])
joins=[]
for j in plan['joins']:
 a,b=items[j['a']],items[j['b']];pa=np.asarray(j['a_local_m']);pb=np.asarray(j['b_local_m']);ap=pa@a['rot'].T+a['pos'];bp=pb@b['rot'].T+b['pos'];an=np.asarray(j['a_normal'])@a['rot'].T;bn=np.asarray(j['b_normal'])@b['rot'].T
 da=a['native'].nearest(C@pa);db=b['native'].nearest(C@pb);gap=float(np.linalg.norm(ap-bp));normalerr=float(np.linalg.norm(an+bn));r={'name':j['name'],'parts':[j['a'],j['b']],'placed_source_points_m':[ap.tolist(),bp.tolist()],'placed_native_points_m':[(C@ap).tolist(),(C@bp).tolist()],'gap_m':gap,'opposed_normal_error':normalerr,'actual_native_surface_witnesses':[da,db],'passed':gap<1e-6 and normalerr<1e-6 and max(da['distance_m'],db['distance_m'])<.0002};joins.append(r)
res={'passed':all(x['passed']for x in joins),'inputs':inputs,'status':plan['status'],'scope':'Finite physical interfaces in new proposed component arrangement, distinct from recovered host geometry.','joins':joins,'placed_native_bounds':[{'key':k,**x['bounds_ship_m']}for k,x in items.items()],'limits':['Contact coincidence does not establish substrate attachment, load rating or complete overlap/collision acceptance.','SAL005 terminal has a genuine physical portal mate in this arrangement; its infill, actual terrace and guard safety remain unresolved.','Public/service moving-door dimensions, stroke/cassette/head reservation and guest polygon remain unknown.','Spatial route/archived-constraint audit and final normal-height pixels are separate gates.']}
(OUT/'independent_arrangement_interfaces.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps({'passed':res['passed'],'joins':[{k:r[k]for k in ['name','gap_m','passed']}for r in joins]},indent=2))
