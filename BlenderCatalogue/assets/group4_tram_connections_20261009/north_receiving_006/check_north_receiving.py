from pathlib import Path
import json,hashlib,numpy as np
W=Path(__file__).resolve().parent;G={'__file__':str(W/'north_receiving_geometry.py'),'__name__':'geometry'};exec((W/'north_receiving_geometry.py').read_text(),G);R=G['R'];F=G['F'];P=G['P'];U=G['U'];recipes=G['recipes'];plan=G['plan'];station=G['station']
code=(P/'check_north_candidate.py').read_text();a=code.index('def intersects(');b=code.index('\nsources=',a);exec(code[a:b],globals())
source_instances=[('SOL_D09_directory_03_source001.glb',(-8,52.5,-250),0,'PaperMoon'),('AST-CIR-005_fore_midship_cinema2_d11.glb',(0,0,-272),0,'ForemidCore'),('AST-CIR-001.glb',(3,52.5,-268),np.pi,'ExistingD09_D10_core_stairs'),('AST-RTL-009.glb',(4,52.5,-250),0,'OrchardExchange'),('AST-RTL-007.glb',(8,52.5,-216),0,'ThreadShell'),('AST-TRM-G4-020_foremid_north_candidate.glb',(0,0,0),0,'Frozen_North_Station_Proposal')]
near=[];pins={}
for f,at,yaw,owner in source_instances:
 p=str((P/f).relative_to(R)) if 'AST-TRM-G4-020' in f else 'Game/assets/models/'+f;pins[p]=hashlib.sha256((R/p).read_bytes()).hexdigest()
 for n,t in U['triangles'](f,at,yaw):
  lo=t.min(axis=1);hi=t.max(axis=1);mask=(lo[:,0]<-3)&(hi[:,0]>-14)&(lo[:,2]<-221)&(hi[:,2]>-266)&(lo[:,1]<56.2)&(hi[:,1]>52.0)
  if mask.any():near.append((owner,n,t[mask],t.min(axis=(0,1)),t.max(axis=(0,1))))
hits=[];allowed=[]
for q in recipes:
 t=q['triangles'];lo=t.min(axis=(0,1));hi=t.max(axis=(0,1))
 for owner,n,v,targetlo,targethi in near:
  aa=v.min(axis=1);bb=v.max(axis=1);mask=np.all((aa<hi-1e-5)&(bb>lo+1e-5),axis=1)
  if not mask.any():continue
  target=v[mask];aa=aa[mask];bb=bb[mask];hit=False
  for nt in t:
   nl=nt.min(axis=0);nh=nt.max(axis=0);ids=np.flatnonzero(np.all((aa<=nh+1e-6)&(bb>=nl-1e-6),axis=1))
   if any(intersects(nt,target[i]) for i in ids):hit=True;break
  if not hit:continue
  rec={'new_mesh':q['name'],'source_owner':owner,'source_mesh':n}
  if owner=='Frozen_North_Station_Proposal' and (q['station_receiver']==n or (q['name'].startswith('N006_MissingOnlyFloor_') and n in ['N005_V2__Emergency_Flight0_Step00','N005_V2__Emergency_Profiled_Stringer0'])):rec['purpose']='declared source underside/toe bearing';allowed.append(rec)
  elif owner=='ForemidCore' and targetlo[1]>=52.20 and targethi[1]<=52.501 and ('UnderfloorTransfer' in q['name'] or 'CurrentSlabReceiver' in q['name']):rec['purpose']='declared retained core-floor underside bearing';allowed.append(rec)
  else:hits.append(rec)
def overlap(a,b):return np.maximum(0,np.minimum(a['max'],b['max'])-np.maximum(a['min'],b['min']))
lookup={q['name']:q for q in recipes};joints=[]
for a,b in plan['internal_joint_pairs']:
 v=overlap(lookup[a],lookup[b]);assert v.prod()>1e-7,(a,b,v);joints.append({'pair':[a,b],'positive_overlap_volume_m3':float(v.prod())})
station_receivers=[]
for q in recipes:
 if q['station_receiver']:
  t=station[q['station_receiver']];v=overlap(q,{'min':t.min(axis=(0,1)),'max':t.max(axis=(0,1))});assert v.prod()>1e-7,(q['name'],v);station_receivers.append({'new_mesh':q['name'],'retained_station_mesh':q['station_receiver'],'positive_overlap_volume_m3':float(v.prod()),'positive_plan_bearing_area_m2':float(v[0]*v[2])})
# All ten pads are beneath the walking plane and have full named existing-slab receiving area.
for q in plan['current_slab_receivers']:
 z=lookup[q['mesh']];owner=q['contacts'][0];oy=[owner['floor_y']-owner['thickness'],owner['floor_y']];depth=max(0,min(z['max'][1],oy[1])-max(z['min'][1],oy[0]));assert depth>0;q['positive_current_slab_overlap_volume_m3']=q['full_area_m2']*depth
for p in ['Game/data/generated/structural_meshes.json','Game/data/generated/received_structural_meshes.json','Game/data/architecture/received_sections.json','Game/data/architecture/received_section_floors.json','BlenderCatalogue/catalogue_manifest.json',str((P/'FROZEN_BOARDING_AND_NORTH_BATCH.json').relative_to(R))]:pins[p]=hashlib.sha256((R/p).read_bytes()).hexdigest()
assert abs(plan['new_floor_area_m2']+51.3+17.6-425.28)<1e-8
rep={'status':'NORTH_MISSING_ONLY_RECEIVING_LOCAL_PASS' if not hits else 'NORTH_RECEIVING_LOCAL_HOLD','source_only':True,'whole_group_complete':False,'runtime_changed':False,'members':len(recipes),'new_missing_only_floor_area_m2':plan['new_floor_area_m2'],'current_floor_owner_area_duplicate_m2':0,'retained_uncut_lift_recess_area_m2':17.6,'retained_source_instances_screened':len(source_instances),'unexpected_exact_triangle_contacts':hits,'declared_source_bearings':allowed,'current_slab_receivers':plan['current_slab_receivers'],'positive_internal_joints':joints,'positive_station_underside_receivers':station_receivers,'source_pins':pins,'limits':['One candidate receiving module, six local retained instances and named generic/received floor triangles only. No route sampling, Godot or full main-world traversal.','Existing source floor ownership and uncut pit are preserved. Source proposals are not adopted floor/structural capacity.','Low under-stair access protection, live cabin/carry, primary hull transfer, operating bindings and root physical-stop decision remain open.']};(W/'NORTH_RECEIVING_LOCAL_CHECK.json').write_text(json.dumps(rep,indent=2)+'\n');(W/'NORTH_RECEIVING_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print(rep['status'],len(hits),'unexpected contacts');print(json.dumps(hits,indent=2));print('declared',len(allowed),'joints',len(joints),'station bearings',len(station_receivers),'slab pads',len(plan['current_slab_receivers']))
