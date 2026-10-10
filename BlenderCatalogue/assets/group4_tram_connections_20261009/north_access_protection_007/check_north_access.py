from pathlib import Path
import json,hashlib,numpy as np
W=Path(__file__).resolve().parent;G={'__file__':str(W/'north_access_geometry.py'),'__name__':'geometry'};exec((W/'north_access_geometry.py').read_text(),G);R=G['R'];F=G['F'];P=G['P'];Q=G['Q'];U=G['U'];recipes=G['recipes'];plan=G['plan'];code=(P/'check_north_candidate.py').read_text();a=code.index('def intersects(');b=code.index('\nsources=',a);exec(code[a:b],globals())
sources=[('SOL_D09_directory_03_source001.glb',(-8,52.5,-250),0,'PaperMoon'),('AST-CIR-005_fore_midship_cinema2_d11.glb',(0,0,-272),0,'ForemidCore'),('AST-CIR-001.glb',(3,52.5,-268),np.pi,'ExistingD09_D10_core_stairs'),('AST-RTL-009.glb',(4,52.5,-250),0,'OrchardExchange'),('AST-RTL-007.glb',(8,52.5,-216),0,'ThreadShell'),('AST-TRM-G4-020_foremid_north_candidate.glb',(0,0,0),0,'Frozen_North_Station_005'),('AST-TRM-G4-021_north_missing_only_receiving.glb',(0,0,0),0,'Frozen_North_Receiving_006'),('AST-CIR-003.glb',(-11.2,52.5,-225),-np.pi,'One_actual_lower_cabin_pose')]
near=[];pins={}
for f,at,yaw,owner in sources:
 pp=str(((P if 'AST-TRM-G4-020' in f else Q)/f).relative_to(R)) if 'AST-TRM-G4' in f else 'Game/assets/models/'+f;pins[pp]=hashlib.sha256((R/pp).read_bytes()).hexdigest()
 for n,t in U['triangles'](f,at,yaw):
  aa=t.min(axis=1);bb=t.max(axis=1);mask=(aa[:,0]<-3)&(bb[:,0]>-14)&(aa[:,2]<-221)&(bb[:,2]>-266)&(aa[:,1]<56.2)&(bb[:,1]>52.1)
  if mask.any():near.append((owner,n,t[mask]))
hits=[];allowed=[]
for q in recipes:
 t=q['triangles'];lo=np.array(q['min']);hi=np.array(q['max'])
 for owner,n,v in near:
  aa=v.min(axis=1);bb=v.max(axis=1);mask=np.all((aa<hi-1e-5)&(bb>lo+1e-5),axis=1)
  if not mask.any():continue
  vv=v[mask];aa=aa[mask];bb=bb[mask];hit=False
  for nt in t:
   nl=nt.min(axis=0);nh=nt.max(axis=0);ids=np.flatnonzero(np.all((aa<=nh+1e-6)&(bb>=nl-1e-6),axis=1))
   if any(intersects(nt,vv[i]) for i in ids):hit=True;break
  if not hit:continue
  rec={'new_mesh':q['name'],'retained_owner':owner,'retained_mesh':n}
  if n in q['allowed_retained_receiver_meshes'] or (owner=='Frozen_North_Receiving_006' and n.startswith('N006_MissingOnlyFloor_')):rec['purpose']='explicit fixed skirt/guard receiving';allowed.append(rec)
  else:hits.append(rec)
# Six ordinary-adult stationary probes on retained treads, landings and open floor approaches; no traversal.
probes=[('Flight0_first_tread',[-12,52.65,-260.15]),('Half_landing',[-10.65,54.3,-264.5]),('Flight1_first_tread',[-9.3,54.45,-263.45]),('Upper_return',[-10.65,56.1,-252]),('Lower_lift_approach',[-11.2,52.5,-225.55]),('Current_axial_route_seam',[-4,52.5,-240])];probe_rows=[]
for name,at in probes:
 lo=np.array(at)+[-.18,.001,-.18];hi=np.array(at)+[.18,1.801,.18];contacts=[]
 for q in recipes:
  if np.all(np.minimum(hi,q['max'])-np.maximum(lo,q['min'])>1e-5):contacts.append(q['name'])
 assert not contacts,(name,contacts);probe_rows.append({'name':name,'foot_xyz':at,'envelope_width_depth_m':.36,'height_m':1.8,'new_protection_contacts':contacts})
# Every independent new panel is a closed finite positive-height prism.
mesh_rows=[]
for q in recipes:
 t=q['triangles'];bad=int((np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)<1e-9).sum());assert not bad and np.isfinite(t).all();edges={}
 for tri in t:
  for x,y in zip(tri,np.roll(tri,-1,axis=0)):
   key=tuple(sorted((tuple(x),tuple(y))));edges[key]=edges.get(key,0)+1
 assert all(v==2 for v in edges.values()),q['name'];mesh_rows.append({'name':q['name'],'triangles':len(t),'closed_manifold_prism':True})
for pp in ['BlenderCatalogue/catalogue_manifest.json','Game/data/generated/structural_meshes.json','Game/data/generated/received_structural_meshes.json',str((P/'FROZEN_BOARDING_AND_NORTH_BATCH.json').relative_to(R)),str((Q/'FROZEN_NORTH_RECEIVING_BATCH.json').relative_to(R))]:pins[pp]=hashlib.sha256((R/pp).read_bytes()).hexdigest()
rep={'status':'NORTH_LOW_POCKET_AND_EDGE_SOURCE_PASS' if not hits else 'NORTH_ACCESS_LOCAL_HOLD','source_only':True,'whole_group_complete':False,'runtime_changed':False,'members':len(recipes),'triangles':sum(q['triangles'] for q in mesh_rows),'retained_instances_screened':len(sources),'unexpected_exact_triangle_contacts':hits,'declared_fixed_receiver_contacts':allowed,'ordinary_adult_stationary_probes':probe_rows,'closed_prism_checks':mesh_rows,'source_pins':pins,'limits':['Eight local retained instances including one actual lower cabin pose; six stationary ordinary-adult probes only. No route audit, dynamic movement, Godot or whole-species acceptance.','Fixed enclosures do not allocate a service room or change stairs, floors, lifts, controllers or retained sources.','Root stop/floor/controller adoption, normal-world collision/receiving, species, capacity and final access acceptance remain open.']};(W/'NORTH_ACCESS_LOCAL_CHECK.json').write_text(json.dumps(rep,indent=2)+'\n');(W/'NORTH_ACCESS_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print(rep['status'],len(hits),'unexpected contacts');print(json.dumps(hits,indent=2));print('declared fixed receivers',len(allowed),'ordinary probes',len(probe_rows))
