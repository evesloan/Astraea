from pathlib import Path
import json,hashlib,numpy as np
W=Path(__file__).resolve().parent;R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');F=R/'BlenderCatalogue/assets/group4_tram_connections_20261009';S=F/'port_successor_002';M=F/'receiving_module_003'
for folder,file in [(F,'FROZEN_FIRST_BATCH.json'),(S,'FROZEN_SUCCESSOR_BATCH.json'),(M,'FROZEN_RECEIVING_MODULE.json')]:
 d=json.loads((folder/file).read_text());assert all(hashlib.sha256((folder/n).read_bytes()).hexdigest()==v['sha256'] for n,v in d['files'].items())
U={};exec((S/'glb_source_reader.py').read_text().split('protected=[')[0],U);U['read']=lambda p:(S/Path(p).name).read_bytes();T={n:t for n,t in U['triangles']('AST-TRM-G4-014_central_source.glb')};rows=json.loads((S/'MESH_PARTS.json').read_text());old={q['mesh']:q for q in rows if q['collection']=='CENTRAL_STATIC_SOURCE'}
D=json.loads((R/'Game/data/generated/structural_meshes.json').read_text());C={};exec((M/'source_contact_math.py').read_text(),C)
def owner(rect):
 a,c,b,d=rect;out=[]
 for q in D['regions']:
  if q['floor_y']!=52.5:continue
  ar=0
  for t in q['triangles']:
   if max(p[0] for p in t)<a or min(p[0] for p in t)>b or max(p[1] for p in t)<c or min(p[1] for p in t)>d:continue
   poly=[list(p) for p in t]
   for ax,v,gt in [(0,a,True),(0,b,False),(1,c,True),(1,d,False)]:poly=C['clip'](poly,ax,v,gt) if poly else []
   ar+=C['area'](poly)
  if ar>1e-9:out.append({'owner':q['id'],'area_m2':ar,'floor_y':52.5,'underside_y':52.5-q['thickness']})
 return out
def bottom(name,x,z):
 ys=[]
 for t in T[name]:
  p=t[:,[0,2]];det=np.linalg.det(np.array([p[1]-p[0],p[2]-p[0]]).T)
  if abs(det)<1e-9:continue
  u,v=np.linalg.solve(np.array([p[1]-p[0],p[2]-p[0]]).T,np.array([x,z])-p[0])
  if u>=-1e-6 and v>=-1e-6 and u+v<=1+1e-6:ys.append(t[0,1]+u*(t[1,1]-t[0,1])+v*(t[2,1]-t[0,1]))
 assert ys,(name,x,z);return min(ys)
feet=[];boxes=[];shoes=[];joints=[]
def box(name,c,s,role,target=None):boxes.append({'name':name,'center':c,'size':s,'role':role,'target_source_mesh':target})
def pier(name,x,z,top,target):
 rect=[x-.16,z-.20,x+.16,z+.20];o=owner(rect);assert len(o)==1 and abs(o[0]['area_m2']-.128)<1e-6,(name,o);feet.append({'member':name+'_Pad','center_xyz':[x,52.5,z],'footprint_xz':rect,'contacts':o})
 box(name+'_Pad',[x,52.54,z],[.32,.08,.40],'full positive-area retained D09 contact')
 assert top>52.58;box(name+'_Pier',[x,(52.58+top)/2,z],[.18,top-52.58,.22],'under-footprint receiver pier',target)
 return name+'_Pier'
# Beam-supported landing plates, using their actual frozen lower faces.
for label,target,zs,xs in [('Mid','V2_Central__Emergency_MidLanding',[-79.65,-78.55],[-12.78,-9.98]),('Upper','V2_Central__Emergency_UpperLanding',[-74.35,-72.45],[-11.07,-10.07]),('Approach','V2_Central__Emergency_TopApproach',[-71.8,-68.0],[-12.78,-9.98]),('Return','V2_Central_StairReturn',[-72.25,-68.75],[-9.55,-8.02])]:
 q=old[target];y=q['min'][1];a=q['min'][0]+.04;b=q['max'][0]-.04
 for k,z in enumerate(zs):
  name='M004_'+label+'_Beam_'+str(k);box(name,[(a+b)/2,y-.0975,z],[b-a,.22,.24],'positive source landing/return lower-face contact',target)
  for j,x in enumerate(xs):
   p=pier('M004_'+label+'_'+str((k,j)),x,z,y-.16,target);joints.append({'new_member':p,'receiver_new_member':name,'contact':'positive-volume overlap'})
  joints.append({'new_member':name,'receiver_source_mesh':target,'contact':'positive lower-face overlap','overlap_depth_m':.0125})
# Four closed inclined shoes conform to frozen stringer lower faces; no guessed slope or stair remake.
for flight,cx,zs in [(0,-12.19,[-76.25,-77.35]),(1,-10.57,[-77.35,-75.65])]:
 target='V2_Central__Emergency_Profiled_Stringer'+str(flight)
 for k,z in enumerate(zs):
  name='M004_Flight'+str(flight)+'_Shoe_'+str(k);foot=[]
  for x,zz in [(cx-.69,z-.18),(cx+.69,z-.18),(cx+.69,z+.18),(cx-.69,z+.18)]:foot.append([x,bottom(target,x,zz)+.0125,zz])
  shoes.append({'name':name,'upper_corners_xyz':foot,'thickness_m':.14,'target_source_mesh':target,'source_overlap_depth_m':.0125})
  posttop=bottom(target,cx,z)+.0125-.14+.045;p=pier('M004_Flight'+str(flight)+'_'+str(k),cx,z,posttop,target)
  joints.append({'new_member':p,'receiver_new_member':name,'contact':'positive inclined-foot contact'})
  joints.append({'new_member':name,'receiver_source_mesh':target,'contact':'conforming lower-face contact','overlap_depth_m':.0125})
pins={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in ['Game/data/generated/structural_meshes.json','BlenderCatalogue/catalogue_manifest.json','BlenderCatalogue/assets/group4_tram_connections_20261009/port_successor_002/AST-TRM-G4-014_central_source.glb','BlenderCatalogue/assets/group4_tram_connections_20261009/port_successor_002/FROZEN_SUCCESSOR_BATCH.json','BlenderCatalogue/assets/group4_tram_connections_20261009/receiving_module_003/FROZEN_RECEIVING_MODULE.json']}
rep={'schema':'astraea.group4.central_stair_receiving.v1','source_only':True,'whole_group_complete':False,'catalogue_id':'AST-TRM-G4-018','family':'group4_central_stair_receiving_004','scope':'Additive under-footprint central secondary stair/stringer/landing/return receivers, no stair/floor/rail replacement.','boxes':boxes,'inclined_shoes':shoes,'positive_floor_contacts':feet,'joints':joints,'retained_source_pins':pins,'protected_central_lift_recess_xz':[-7.8,-68.4,-3.4,-64.4],'root_floor_owner':'D09_atrium_circulation','root_recess_area_m2':17.6,'floor_changes':'NONE; parent owns all pit/fill/receiving integration.','operating_changes':'NONE; retain commons_lift/AST-CIR-003 and existing E/RMB bindings.','limits':['Geometric receiving construction only; slab/primary-hull capacity, deflection/vibration not accepted.','Secondary stairs remain1.44m-wide source candidates, not universal-species/loaded-cart routes.','No whole-route sampling or Godot/import/full build.']}
(W/'RECEIVING_PLAN.json').write_text(json.dumps(rep,indent=2)+'\n');print('PLAN',len(boxes),'boxes',len(shoes),'inclinedshoes',len(feet),'positive D09 contacts',sorted(set(f['contacts'][0]['owner'] for f in feet)))
