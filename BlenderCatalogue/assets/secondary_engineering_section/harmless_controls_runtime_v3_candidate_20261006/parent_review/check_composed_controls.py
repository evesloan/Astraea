from pathlib import Path
import sys,json,math,hashlib,numpy as np
R=Path(__file__).resolve().parent;D=Path('/workspace/scratch/375c2e438292/engineering-controls-runtime-v3-20261006');G=Path('/workspace/shared/astraea-godot-production-20261003');sys.path.insert(0,str(D/'tools'));from audit_source_poses import capsule_query;from glb_geometry import glb,Query
C=json.loads((D/'data/ENGINEERING_CALIBRATION_DRAFT.json').read_text());route=json.loads((D/'data/ENGINEERING_CONTROLS_WALK_ROUTE_V3.json').read_text());meshes=[];inputs={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['AST-ENG-008_workbay_section_gate_v2.glb','AST-ENG-008_receiving_shoulders.glb','AST-ENG-008_essentials.glb']:
 p=G/'assets/models'/name;g=glb(p);inputs[str(p)]=g['sha256']
 for m in g['meshes']:
  role=m['extras'].get('collision_contract','static_surface')
  if name.startswith('AST-ENG-008_workbay') and role not in ['static_surface','contact_only_glass_26mm','stair_flight_contact','moving_door_leaf']:continue
  if not name.startswith('AST-ENG-008_workbay') and role=='none':continue
  m['node']=name+'/'+m['node'];meshes.append(m)
q=Query(meshes);owners=np.array([q.meshes[int(i)]['node']for i in q.owner]);compiled=G/'data/generated/structural_meshes.json';floor=json.loads(compiled.read_text());inputs[str(compiled)]=sha(compiled);fmesh=[]
for row in floor['regions']:
 if row['id']in ['D02_secondary_engineering_floor','D02_secondary_engineering_workbay_cell_lower']:fmesh.append({'node':row['id'],'primitive':0,'triangles':np.array([[[p[0],row['floor_y'],p[1]]for p in t]for t in row['triangles']])})
fq=Query(fmesh);poses=[];fails=[];centres=np.array([r['target_center_xyz']for r in C['controls']]);radius=.018
for idx,r in enumerate(C['controls']):
 foot=np.array(r['proposed_approach_xyz']);eye=np.array(r['proposed_eye_xyz']);target=centres[idx];length=float(np.linalg.norm(target-eye));direction=(target-eye)/length;first=length-radius;hits=[x for x in q.rays(eye,target)if x['distance_m']<first-1e-5];body,_=capsule_query(q.tri,owners,foot);f=fq.rays(foot+[0,.15,0],foot-[0,.15,0]);support=bool(f and f[0]['node']==r['floor_owner'])
 # The complete new target sphere roster must select this exact control first.
 delta=centres-eye;t=delta@direction;perp2=np.einsum('ij,ij->i',delta,delta)-t*t;ok=(perp2<=radius*radius)&(t>0);dist=np.where(ok,t-np.sqrt(np.maximum(0,radius*radius-perp2)),math.inf);nearest=int(np.argmin(dist));row={'id':r['id'],'physical_occluders':hits[:4],'capsule_contacts':body[:4],'floor_support_exact_owner':support,'nearest_precise_sphere_id':C['controls'][nearest]['id'],'first_sphere_distance_m':float(dist[nearest])};poses.append(row)
 if hits or body or not support or nearest!=idx or dist[idx]>2.5:fails.append(row)
prior=np.array(route['initial_supported_arrival_xyz']);edges=[];walkfails=[];samples=0
for segment in route['segments']:
 stops=list(segment['waypoints_xyz'])+[r['proposed_approach_xyz']for r in C['controls']if r['panel']==segment['panel']]
 for target in stops:
  target=np.array(target);steps=max(1,math.ceil(float(np.linalg.norm(target-prior))/.15));bad=[]
  for j in range(steps+1):
   p=prior+(target-prior)*j/steps;samples+=1;h,_=capsule_query(q.tri,owners,p);f=fq.rays(p+[0,.15,0],p-[0,.15,0]);support=bool(f and f[0]['node']==route['floor_owner'])
   if h or not support:bad.append({'position_xyz':p.tolist(),'contacts':h[:4],'floor_support_exact_owner':support});break
  row={'panel':segment['panel'],'from_xyz':prior.tolist(),'to_xyz':target.tolist(),'samples':steps+1,'failures':bad};edges.append(row)
  if bad:walkfails.append(row)
  prior=target
out={'status':'COMPOSED_SOURCE_SCREEN_PASS'if not fails and not walkfails else'COMPOSED_SOURCE_SCREEN_FAILED','source_inputs':inputs,'controls':len(poses),'failed_controls':fails,'poses':poses,'walk_edges':len(edges),'walk_samples':samples,'failed_walk_edges':walkfails,'edge_records':edges,'scope':'Three frozen engineering source GLBs, compiler host/lower floor support and all120 target spheres. Excludes runtime-import differences, unrelated ship nodes, live actors and moving contact response; actual Game traversal still required.','actual_engine_run':False};p=R/'COMPOSED_SCREEN_001.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n');print(out['status'],'controls',len(poses),'failed',len(fails),'walkedges',len(edges),'failed',len(walkfails),'samples',samples)
for row in fails[:5]:print(row)
for row in walkfails[:3]:print(row)
