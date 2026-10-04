"""Read actual native clinical components in the lead's proposed inspection arrangement."""
from pathlib import Path
import json,hashlib,sys,numpy as np,itertools
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch12';A=OUT/'assembly';sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'qa/batch07'));from independent_geometry import Native,C
sys.path.insert(0,str(ROOT/'qa/batch08'));from independent_collision_geometry import inside_mesh,segment_triangles
sys.path.insert(0,str(OUT));from independent_void_geometry import triangle_box_mask
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
plan=json.loads((A/'plan.json').read_text());items={x['key']:x for x in plan['items']};res=[]
for state in ['closed','open']:
 shapes={};records=[]
 for key,item in items.items():
  path=ROOT/(plan['privacy_state_exports'][state]if key=='privacy'else item['path']);native=Native(path);angle=np.deg2rad(item['source_z_rotation_deg']);rot=np.array([[np.cos(angle),-np.sin(angle),0],[np.sin(angle),np.cos(angle),0],[0,0,1]]);t=(native.tris@C)@rot.T+item['source_origin_m'];shapes[key]=t;v=t.reshape(-1,3);records.append({'key':key,'catalogue_id':item['catalogue_id'],'export':bind(path),'source_origin_m':item['source_origin_m'],'source_z_rotation_deg':item['source_z_rotation_deg'],'actual_bounds_source_m':[v.min(0).tolist(),v.max(0).tolist()],'floor_datum_error_m':float(abs(v[:,2].min()))})
 lo=np.asarray(plan['empty_component_approach']['min_source_m'])+.0002;hi=np.asarray(plan['empty_component_approach']['max_source_m'])-.0002;void=[]
 for key,t in shapes.items():
  mask=triangle_box_mask(t,lo,hi);inside=bool(inside_mesh([(lo+hi)/2],t)[0]);void.append({'key':key,'intruding_triangles':int(mask.sum()),'midpoint_inside_asset':inside,'pass':not mask.any()and not inside})
 pairs=[]
 for a,b in itertools.combinations(shapes,2):
  av=shapes[a].reshape(-1,3);bv=shapes[b].reshape(-1,3);separation=float(max((bv.min(0)-av.max(0)).max(),(av.min(0)-bv.max(0)).max()));pairs.append({'parts':[a,b],'separating_axis_gap_m':separation,'pass':separation>0})
 support=items['support'];m=json.loads((ROOT/support['manifest_path']).read_text());p=np.asarray(next(x for x in m['physical_and_proposal_markers']if x['name']=='PAD_2_PHYSICAL_CONTACT')['source_m'])+support['source_origin_m'];eye=plan['views']['privacy_'+state+'_arrival']['source_eye_m'];blocked=bool(segment_triangles(eye,p,shapes['privacy']));pad={'source_eye_m':eye,'actual_middle_pad_contact_source_m':p.tolist(),'blocked_by_screen':blocked,'expected_blocked':state=='closed','pass':blocked==(state=='closed')}
 res.append({'state':state,'items':records,'whole_empty_approach_box':void,'disjoint_component_aabb_pairs':pairs,'actual_middle_pad_privacy_witness':pad,'pass':all(x['pass']for x in void+pairs+[pad])and all(x['floor_datum_error_m']<1e-6 for x in records)})
report={'passed':all(x['pass']for x in res),'executed_script_sha256':sha(Path(__file__)),'plan':bind(A/'plan.json'),'states':res,'scope':'Proposed source-frame component inspection arrangement only. Native meshes transformed by explicit source positions and Z-rotations; approach tested as whole box and all separate component pairs proven disjoint by their actual transformed bounds.','limits':['No host room, usable ceiling, moving door, floor support, clinical capacity or species/body/cart route approval.','One real pad-surface ray in each state is a bounded arrangement witness, not privacy for every platform point or patient/body silhouette.','Static source floor datum and proposed clear volume do not establish installed support or navigability.']}
(OUT/'independent_assembly_geometry_review.json').write_text(json.dumps(report,indent=2)+'\n');print('Independent native arrangement pass',report['passed'])
