from pathlib import Path
import json,hashlib,numpy as np
W=Path(__file__).resolve().parent;R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');G={'__file__':str(W/'north_candidate_geometry.py'),'__name__':'source_geometry'};exec((W/'north_candidate_geometry.py').read_text(),G);recipes=G['recipes'];U=G['U'];plan=G['plan'];base=U['read'];U['read']=lambda p:(G['S']/Path(p).name).read_bytes() if 'AST-TRM-G4-011' in p else base(p)
def intersects(a,b):
 ea=np.roll(a,-1,axis=0)-a;eb=np.roll(b,-1,axis=0)-b;na=np.cross(ea[0],ea[1]);nb=np.cross(eb[0],eb[1]);axes=[na,nb]+[np.cross(x,y) for x in ea for y in eb]+[np.cross(na,x) for x in ea]+[np.cross(nb,x) for x in eb]
 for v in axes:
  d=np.linalg.norm(v)
  if d<1e-12:continue
  v=v/d;pa=a@v;pb=b@v
  if pa.max()<pb.min()-1e-6 or pb.max()<pa.min()-1e-6:return False
 return True
sources=[('SOL_D09_directory_03_source001.glb',(-8,52.5,-250),0,'PaperMoon'),('AST-CIR-005_fore_midship_cinema2_d11.glb',(0,0,-272),0,'ForemidCore'),('AST-CIR-001.glb',(3,52.5,-268),np.pi,'ExistingD09_D10_core_stairs'),('AST-RTL-009.glb',(4,52.5,-250),0,'OrchardExchange'),('AST-RTL-007.glb',(8,52.5,-216),0,'ThreadShell'),('AST-TRM-G4-011_cart_tram_component.glb',(-5.6,56.1,-241),0,'One_actual_long_car_pose')]
near=[];pins={}
for f,at,yaw,owner in sources:
 p=('BlenderCatalogue/assets/group4_tram_connections_20261009/port_successor_002/'+f) if 'AST-TRM-G4' in f else 'Game/assets/models/'+f;pins[p]=hashlib.sha256((R/p).read_bytes()).hexdigest()
 for n,t in U['triangles'](f,at,yaw):
  a=t.min(axis=1);b=t.max(axis=1);mask=(a[:,0]<-2)&(b[:,0]>-13.7)&(a[:,2]<-221)&(b[:,2]>-266)&(a[:,1]<59.7)&(b[:,1]>52.1)
  if mask.any():near.append((owner,n,t[mask]))
hits=[]
for q in recipes:
 t=q['triangles'];lo=t.min(axis=(0,1));hi=t.max(axis=(0,1))
 for owner,n,v in near:
  a=v.min(axis=1);b=v.max(axis=1);mask=np.all((a<hi-1e-5)&(b>lo+1e-5),axis=1)
  if not mask.any():continue
  target=v[mask];aa=a[mask];bb=b[mask];hit=False
  for nt in t:
   nl=nt.min(axis=0);nh=nt.max(axis=0);ids=np.flatnonzero(np.all((aa<=nh+1e-6)&(bb>=nl-1e-6),axis=1))
   if any(intersects(nt,target[i]) for i in ids):hit=True;break
  if hit:hits.append({'candidate_mesh':q['name'],'owner':owner,'retained_mesh':n})
C={};exec((G['F']/'receiving_module_003/source_contact_math.py').read_text(),C);generic=json.loads((R/'Game/data/generated/structural_meshes.json').read_text())['regions'];received=json.loads((R/'Game/data/generated/received_structural_meshes.json').read_text())['regions']
def owners(rect):
 a,c,b,d=rect;rows=[]
 for q in generic+received:
  if q.get('floor_y')!=52.5:continue
  ar=0
  for t in q['triangles']:
   poly=[list(p) for p in t]
   for ax,v,gt in [(0,a,True),(0,b,False),(1,c,True),(1,d,False)]:poly=C['clip'](poly,ax,v,gt) if poly else []
   ar+=C['area'](poly)
  if ar>1e-6:rows.append({'owner':q['id'],'area_m2':ar})
 return rows
feet=[]
for z in [-249,-241,-233]:
 rect=[-2.61,z-.375,-2.19,z+.375];o=owners(rect);assert len(o)==1 and o[0]['owner']=='D09_fore_route' and abs(o[0]['area_m2']-.315)<1e-6;feet.append({'rect_xz':rect,'contacts':o})
annex=owners(plan['proposed_new_lower_annex_xz']);pit=owners(plan['proposed_lift_recess_xz']);assert not pit
for p in ['Game/data/generated/structural_meshes.json','Game/data/generated/received_structural_meshes.json','Game/data/architecture/received_sections.json','Game/data/architecture/received_section_floors.json','BlenderCatalogue/assets/group4_tram_connections_20261009/port_successor_002/AST-TRM-G4-010_fore_midship_source.glb']:pins[p]=hashlib.sha256((R/p).read_bytes()).hexdigest()
rep={'status':'NORTH_FOREMID_BOUNDED_SOURCE_CLEAR_WITH_RECEIVING_BINDING_HOLDS' if not hits else 'NORTH_FOREMID_LOCAL_HOLD','source_only':True,'whole_group_complete':False,'candidate_meshes':len(recipes),'retained_source_instances_screened':len(sources),'unexpected_exact_triangle_contacts':hits,'three_axial_pad_contacts':feet,'old_proposed_annex_received_floor_overlap_m2':59.2,'new_annex_actual_generic_and_received_floor_overlaps':annex,'new_lift_recess_current_floor_overlap_m2':sum(q['area_m2'] for q in pit),'floor_proposal_policy':'Missing-only new floor; exclude all named current owners. No existing slab cut or actual floor export in this candidate.','proposed_missing_only_floor_rectangles_xz':[[-13.6,-265.5,-7.8,-252],[-13.6,-252,-4,-225.2],[-13.6,-225.2,-13.4,-221.2],[-9,-225.2,-4,-221.2]],'root_stop_change_required':{'station_identity':'FORE_MIDSHIP','master_catchment_z':-216,'old_physical_stop_z':-216,'new_proposed_stop_z':-241,'runtime_changed':False},'source_geometry_pins':pins,'limits':['One north candidate and one actual-car resting pose only; no route sweep or actual-main traversal.','No floor, control, destination or frozen export changed. Source clear is not route/boarding acceptance.','Secondary-stair/lift/lower-annex receiving, structural capacity and root stop/lift/interface adoption remain open.']};(W/'NORTH_STATION_LOCAL_SCREEN.json').write_text(json.dumps(rep,indent=2)+'\n');print(rep['status'],len(hits),'contacts');print(hits);print('annex',annex,'pit',pit)
