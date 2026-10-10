from pathlib import Path
import json,hashlib,numpy as np,math
W=Path(__file__).resolve().parent;R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');F=R/'BlenderCatalogue/assets/group4_tram_connections_20261009';S=F/'port_successor_002';M=F/'receiving_module_003';P=json.loads((W/'RECEIVING_PLAN.json').read_text());meta=json.loads((W/'MODULE_INTERFACE.json').read_text());rows=json.loads((W/'MESH_PARTS.json').read_text());rc={r['mesh']:r for r in rows};U={'W':W};exec((W/'glb_source_reader.py').read_text(),U);base=U['read']
U['read']=lambda p:(W/Path(p).name).read_bytes() if 'AST-TRM-G4-018' in p else ((S/Path(p).name).read_bytes() if 'AST-TRM-G4-014' in p else base(p))
new={};bad=0;triangles=0
for n,t in U['triangles'](meta['asset']):
 assert n in rc and np.isfinite(t).all();lo=t.min(axis=(0,1));hi=t.max(axis=(0,1));assert np.allclose(lo,rc[n]['min'],atol=1e-4) and np.allclose(hi,rc[n]['max'],atol=1e-4);bad+=int((np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)<1e-9).sum());triangles+=len(t);new[n]=t
assert bad==0 and len(new)==52
old={n:t for n,t in U['triangles']('AST-TRM-G4-014_central_source.glb')}
def interval(t,x,z):
 out=[]
 for q in t:
  p=q[:,[0,2]];v=np.array([p[1]-p[0],p[2]-p[0]]).T
  if abs(np.linalg.det(v))<1e-10:continue
  a,b=np.linalg.solve(v,np.array([x,z])-p[0])
  if a>=-1e-7 and b>=-1e-7 and a+b<=1+1e-7:out.append(float(q[0,1]+a*(q[1,1]-q[0,1])+b*(q[2,1]-q[0,1])))
 assert out,(x,z);return min(out),max(out)
# Exact central vertical witnesses distinguish conforming joints from merely overlapping broad boxes.
joints=[]
for j in P['joints']:
 n=j['new_member'];t=new[n];v=t.reshape(-1,3);x=float((v[:,0].min()+v[:,0].max())/2);z=float((v[:,2].min()+v[:,2].max())/2);aa=interval(t,x,z)
 receiver=j.get('receiver_new_member',j.get('receiver_source_mesh'));bb=interval(new[receiver] if receiver in new else old[receiver],x,z);depth=min(aa[1],bb[1])-max(aa[0],bb[0]);assert depth>1e-5,(j,aa,bb)
 joints.append({'new_member':n,'receiver':receiver,'witness_xz':[x,z],'positive_vertical_overlap_m':depth})
# Exact floor footprint proof from current source triangles.
C={};exec((W/'source_contact_math.py').read_text(),C);D=json.loads((R/'Game/data/generated/structural_meshes.json').read_text());feet=[]
for f in P['positive_floor_contacts']:
 a,c,b,d=f['footprint_xz'];owners=[]
 for q in D['regions']:
  if q['floor_y']!=52.5:continue
  ar=0
  for t in q['triangles']:
   if max(p[0] for p in t)<a or min(p[0] for p in t)>b or max(p[1] for p in t)<c or min(p[1] for p in t)>d:continue
   poly=[list(p) for p in t]
   for ax,val,gt in [(0,a,True),(0,b,False),(1,c,True),(1,d,False)]:poly=C['clip'](poly,ax,val,gt) if poly else []
   ar+=C['area'](poly)
  if ar>1e-9:owners.append({'owner':q['id'],'positive_contact_area_m2':ar})
 assert len(owners)==1 and owners[0]['owner']==f['contacts'][0]['owner'] and abs(owners[0]['positive_contact_area_m2']-.128)<1e-6,(f,owners);feet.append({'member':f['member'],'bounds_xz':f['footprint_xz'],'contacts':owners})
# Source-plane and walking-surface gap witnesses for all four inclined shoes.
shoe_checks=[]
for q in P['inclined_shoes']:
 samples=[]
 for x,y,z in q['upper_corners_xyz']:
  bot,top=interval(old[q['target_source_mesh']],x,z);assert abs((y-bot)-.0125)<2e-5;samples.append({'xyz':[x,y,z],'receiver_lower_y':bot,'inside_receiver_depth_m':y-bot,'receiver_top_y':top})
 shoe_checks.append({'shoe':q['name'],'target':q['target_source_mesh'],'source_lower_plane_corners':samples})
# Bounded nearby source screen, not a whole-route audit. Intended stair/landing contacts are named.
expected=set((j['new_member'],j['receiver_source_mesh']) for j in P['joints'] if 'receiver_source_mesh' in j)
def intersects(a,b):
 ea=np.roll(a,-1,axis=0)-a;eb=np.roll(b,-1,axis=0)-b;na=np.cross(ea[0],ea[1]);nb=np.cross(eb[0],eb[1]);axes=[na,nb]+[np.cross(x,y) for x in ea for y in eb]+[np.cross(na,x) for x in ea]+[np.cross(nb,x) for x in eb]
 for v in axes:
  d=np.linalg.norm(v)
  if d<1e-12:continue
  v/=d;pa=a@v;pb=b@v
  if pa.max()<pb.min()-1e-7 or pb.max()<pa.min()-1e-7:return False
 return True
near=[]
for n,t in old.items():near.append(('frozen_central_station',n,t))
sources=[('AST-CIR-005.glb',(0,0,-100),0,'current_primary_core'),('AST-ATR-001.glb',(0,0,0),0,'current_atrium_garden')]
for f,at,yaw,owner in sources:
 for n,t in U['triangles'](f,at,yaw):
  a=t.min(axis=1);b=t.max(axis=1);mask=(a[:,0]<-7.7)&(b[:,0]>-13.2)&(a[:,2]<-67.4)&(b[:,2]>-80.1)&(a[:,1]<56.0)&(b[:,1]>52.5)
  if mask.any():near.append((owner,n,t[mask]))
hits=[];incidental=[]
for name,t in new.items():
 lo=t.min(axis=(0,1));hi=t.max(axis=(0,1))
 for own,n,q in near:
  if (name,n) in expected:continue
  a=q.min(axis=1);b=q.max(axis=1);mask=np.all((a<hi-1e-6)&(b>lo+1e-6),axis=1)
  if not mask.any():continue
  target=q[mask];ta=a[mask];tb=b[mask];hit=False
  for nt in t:
   aa=nt.min(axis=0);bb=nt.max(axis=0);ids=np.flatnonzero(np.all((ta<=bb+1e-7)&(tb>=aa-1e-7),axis=1))
   if any(intersects(nt,target[i]) for i in ids):hit=True;break
  if hit:
   rec={'new_member':name,'owner':own,'retained_mesh':n}
   # Shoes are beneath the existing flight assembly, with no change to walking surfaces.
   if own=='frozen_central_station' and '_Shoe_' in name and '__Emergency_Flight' in n:incidental.append(rec)
   else:hits.append(rec)
axis=[r['mesh'] for r in rows if r['min'][0]<2 and r['max'][0]>-2 and r['min'][1]<55.55 and r['max'][1]>52.5];assert not axis
pit=P['protected_central_lift_recess_xz'];pit_hits=[r['mesh'] for r in rows if r['min'][0]<pit[2] and r['max'][0]>pit[0] and r['min'][2]<pit[3] and r['max'][2]>pit[1]];assert not pit_hits
for p,h in P['retained_source_pins'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
for folder,file in [(F,'FROZEN_FIRST_BATCH.json'),(S,'FROZEN_SUCCESSOR_BATCH.json'),(M,'FROZEN_RECEIVING_MODULE.json')]:
 d=json.loads((folder/file).read_text());assert all(hashlib.sha256((folder/n).read_bytes()).hexdigest()==v['sha256'] for n,v in d['files'].items())
report={'status':'BOUNDED_CENTRAL_STAIR_SOURCE_PASS' if not hits else 'ADJACENT_SOURCE_HOLD','source_only':True,'whole_group_complete':False,'export_sha256':hashlib.sha256((W/meta['asset']).read_bytes()).hexdigest(),'editable_members':len(new),'triangles':triangles,'degenerate_triangles':bad,'native_export_bounds_match':True,'positive_floor_contact_checks':feet,'positive_joint_witnesses':joints,'matched_stringer_plane_checks':shoe_checks,'unintended_adjacent_triangle_contacts':hits,'associated_flight_underside_contacts':incidental,'lower4m_axis_intrusions':axis,'protected_lift_recess_intrusions':pit_hits,'all_three_frozen_slices_unchanged':True,'retained_geometry_pins':{**P['retained_source_pins'],**{p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in sorted(set(U['PIN']))}},'limits':['Only the local frozen station, current primary-core and nearby atrium source shapes screened.','Static source receiving proof, no Godot/import/full build or whole-route sampling.','Source support layout does not establish structural capacity, normal stair traversal, all-species fit or whole Group4 completion.']}
(W/'SOURCE_BATCH_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(new),'members',len(feet),'exact floor areas',len(joints),'joint witnesses','unexpected',len(hits),'associated flight',len(incidental));print(json.dumps(hits,indent=2))
