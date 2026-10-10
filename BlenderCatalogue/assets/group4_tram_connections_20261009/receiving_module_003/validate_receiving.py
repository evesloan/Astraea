from pathlib import Path
import json,hashlib,struct,math,numpy as np
W=Path(__file__).resolve().parent;R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');S=R/'BlenderCatalogue/assets/group4_tram_connections_20261009/port_successor_002';meta=json.loads((W/'MODULE_INTERFACE.json').read_text());rows=json.loads((W/'MESH_PARTS.json').read_text());rc={r['mesh']:r for r in rows};U={};exec((W/'glb_source_reader.py').read_text(),U);ori=U['read'];U['read']=lambda p:(W/Path(p).name).read_bytes() if 'AST-TRM-G4-017' in p else ori(p)
new=[];bad=0;ntri=0
for n,t in U['triangles'](meta['asset']):
 lo=t.min(axis=(0,1));hi=t.max(axis=(0,1));assert n in rc and np.allclose(lo,rc[n]['min'],atol=1e-4) and np.allclose(hi,rc[n]['max'],atol=1e-4);assert np.isfinite(t).all();bad+=int((np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)<1e-9).sum());ntri+=len(t);new.append((n,t))
assert bad==0,bad
# Standalone exact planar clipping definitions from the bounded receiver planner.
C={};exec((W/'source_contact_math.py').read_text(),C);D=json.loads((R/'Game/data/generated/structural_meshes.json').read_text());clip=C['clip'];area=C['area']
def overlap(rect,floor):
 a,c,b,d=rect;out=[]
 for r in D['regions']:
  if r['floor_y']!=floor:continue
  ar=0
  for t in r['triangles']:
   if max(p[0] for p in t)<a or min(p[0] for p in t)>b or max(p[1] for p in t)<c or min(p[1] for p in t)>d:continue
   poly=[list(p) for p in t]
   for ax,val,gt in [(0,a,True),(0,b,False),(1,c,True),(1,d,False)]:poly=clip(poly,ax,val,gt) if poly else []
   ar+=area(poly)
  if ar>1e-9:out.append({'owner':r['id'],'area_m2':ar})
 return out
contacts=[]
for r in meta['receiver_bindings']:
 q=r.get('footprint_xz',r.get('positive_footprint_xz'));floor=61 if r['xyz'][1]>60 else 52.5;o=overlap(q,floor);assert len(o)==1 and o[0]['owner']==r['owner'] and abs(o[0]['area_m2']-r['area_m2'])<1e-6,(r,o)
 contacts.append({'member':r['member'],'floor_y':floor,'contacts':o,'positive_footprint_xz':q})
# Existing named support shoe connections: positive volume, no merely hovering rods.
srows=json.loads((S/'MESH_PARTS.json').read_text());sr={r['mesh']:r for r in srows};joint_checks=[]
for j in meta['joints']:
 if j['right'] not in sr:continue
 a=rc[j['left']];b=sr[j['right']];ext=np.minimum(a['max'],b['max'])-np.maximum(a['min'],b['min']);assert (ext>1e-5).all(),(j,ext)
 joint_checks.append({'new':j['left'],'receiving':j['right'],'positive_aabb_overlap_dimensions_m':ext.tolist()})
# Exact triangle convex-separation refinement after conservative broadphase.
def exact_intersects(a,b):
 ea=np.roll(a,-1,axis=0)-a;eb=np.roll(b,-1,axis=0)-b;na=np.cross(ea[0],ea[1]);nb=np.cross(eb[0],eb[1]);axes=[na,nb]
 axes += [np.cross(x,y) for x in ea for y in eb];axes += [np.cross(na,x) for x in ea]+[np.cross(nb,x) for x in eb]
 for v in axes:
  nn=np.linalg.norm(v)
  if nn<1e-12:continue
  v=v/nn;pa=a@v;pb=b@v
  if pa.max()<pb.min()-1e-7 or pb.max()<pa.min()-1e-7:return False
 return True
# Actual installed-source instances include full upper branches up to the receiving plates60.83.
sources=json.loads((W/'SOURCE_INSTANCES.json').read_text())['source_instances'];ret=[];pins={}
for f,at,yaw,own in sources:
 for n,t in U['triangles'](f,at,yaw):
  lo=t.min(axis=1);hi=t.max(axis=1);m=(lo[:,1]<60.84)&(hi[:,1]>52.51)&(lo[:,0]<44)&(hi[:,0]>-14)&(lo[:,2]<460)&(hi[:,2]>-465)
  if m.any():ret.append((f,n,own,t[m],lo[m],hi[m]))
# Frozen station parts are also receiving interfaces, not silently editable architecture.
for f in sorted(S.glob('AST-TRM-G4-*.glb')):
 if f.name.startswith(('AST-TRM-G4-011','AST-TRM-G4-016')):continue
 oldread=U['read'];U['read']=lambda p,f=f:f.read_bytes() if Path(p).name==f.name else oldread(p)
 for n,t in U['triangles'](f.name):
  lo=t.min(axis=1);hi=t.max(axis=1);m=(lo[:,1]<60.84)&(hi[:,1]>52.51)&(lo[:,0]<44)&(hi[:,0]>-14)&(lo[:,2]<460)&(hi[:,2]>-465)
  if m.any():ret.append((f.name,n,'frozen_station_interface',t[m],lo[m],hi[m]))
 U['read']=oldread
expected={(j['left'],j['right']) for j in meta['joints'] if j['right'] in sr};hits=[];broad=0
for name,tt in new:
 lo=tt.min(axis=(0,1));hi=tt.max(axis=(0,1))
 for f,n,own,t,a,b in ret:
  if (name,n) in expected:continue
  mask=np.all((a<hi-1e-6)&(b>lo+1e-6),axis=1)
  if not mask.any():continue
  tr=t[mask];aa=a[mask];bb=b[mask];has=False
  for nt in tt:
   nl=nt.min(axis=0);nh=nt.max(axis=0);ix=np.flatnonzero(np.all((aa<=nh+1e-7)&(bb>=nl-1e-7),axis=1));broad+=len(ix)
   if any(exact_intersects(nt,tr[k]) for k in ix):has=True;break
  if has:hits.append({'new_mesh':name,'retained_file':f,'retained_mesh':n,'owner':own})
# Main lower route and unchanged Group7 reservation.
axis=[r['mesh'] for r in rows if r['min'][0]<2-1e-6 and r['max'][0]>-2+1e-6 and r['min'][1]<55.55-1e-6 and r['max'][1]>52.5+1e-6];assert not axis,axis
g7=[r['mesh'] for r in rows if r['min'][0]<46.5 and r['max'][0]>43 and r['min'][2]<-19 and r['max'][2]>-25 and r['min'][1]<54.6 and r['max'][1]>52.5];assert not g7,g7
frozen=json.loads((S/'FROZEN_SUCCESSOR_BATCH.json').read_text());assert all(hashlib.sha256((S/n).read_bytes()).hexdigest()==a['sha256'] for n,a in frozen['files'].items())
retained_pins={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in sorted(set(U['PIN']+['Game/data/generated/structural_meshes.json','Game/data/architecture/ATRIUM_GALLERY_RECEIVING.json','BlenderCatalogue/catalogue_manifest.json']))}
report={'status':'PASS' if not hits else 'ADJACENT_SOURCE_CONFLICT_HOLD','source_only':True,'whole_group_complete':False,'export_sha256':hashlib.sha256((W/meta['asset']).read_bytes()).hexdigest(),'native_part_count':len(rows),'export_triangles':ntri,'degenerate_triangles':bad,'native_export_bounds_match':True,'positive_area_receiver_checks':contacts,'positive_existing_shoe_joint_checks':joint_checks,'adjacent_exact_triangle_contacts':hits,'triangle_pair_broadphase_candidates':broad,'source_instances_screened':len(sources),'retained_input_pins':retained_pins,'lower4m_axis_intrusions':axis,'group7_lower_gallery_intrusions':g7,'frozen_successor_all_hashes_unchanged':True,'limits':['Bounded static source contacts, no whole-world or actual-main/runtime acceptance.','New intended receiver overlaps are identified and checked, not ignored globally.','No new route poses or exhaustive movement campaign. Structural capacity and all operating controllers remain root gates.']}
(W/'SOURCE_RECEIVING_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n');print('MODULE',len(rows),'members',len(contacts),'positive-area receivers',len(joint_checks),'positive shoes','sourcehits',len(hits));print(json.dumps(hits,indent=2))
