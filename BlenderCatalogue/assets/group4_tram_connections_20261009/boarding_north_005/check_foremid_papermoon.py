from pathlib import Path
import json,hashlib,numpy as np
W=Path(__file__).resolve().parent;R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');F=R/'BlenderCatalogue/assets/group4_tram_connections_20261009';S=F/'port_successor_002';U={'W':W};exec((F/'receiving_module_003/glb_source_reader.py').read_text(),U);base=U['read'];U['read']=lambda p:(S/Path(p).name).read_bytes() if 'AST-TRM-G4-010' in p else base(p)
old=list(U['triangles']('SOL_D09_directory_03_source001.glb',(-8,52.5,-250),0));new=list(U['triangles']('AST-TRM-G4-010_fore_midship_source.glb'))
def intersects(a,b):
 ea=np.roll(a,-1,axis=0)-a;eb=np.roll(b,-1,axis=0)-b;na=np.cross(ea[0],ea[1]);nb=np.cross(eb[0],eb[1]);axes=[na,nb]+[np.cross(x,y) for x in ea for y in eb]+[np.cross(na,x) for x in ea]+[np.cross(nb,x) for x in eb]
 for v in axes:
  d=np.linalg.norm(v)
  if d<1e-12:continue
  v=v/d;pa=a@v;pb=b@v
  if pa.max()<pb.min()-1e-6 or pb.max()<pa.min()-1e-6:return False
 return True
hits=[]
for n,t in new:
 lo=t.min(axis=(0,1));hi=t.max(axis=(0,1))
 for m,q in old:
  a=q.min(axis=1);b=q.max(axis=1);mask=np.all((a<hi-1e-5)&(b>lo+1e-5),axis=1)
  if not mask.any():continue
  target=q[mask];aa=a[mask];bb=b[mask];witness=None
  for nt in t:
   nl=nt.min(axis=0);nh=nt.max(axis=0);ids=np.flatnonzero(np.all((aa<=nh+1e-6)&(bb>=nl-1e-6),axis=1))
   for i in ids:
    if intersects(nt,target[i]):witness={'station_triangle':nt.tolist(),'retained_triangle':target[i].tolist()};break
   if witness:break
  if witness:hits.append({'station_mesh':n,'retained_papermoon_mesh':m,'station_bounds_xyz':[lo.tolist(),hi.tolist()],'retained_bounds_xyz':[q.min(axis=(0,1)).tolist(),q.max(axis=(0,1)).tolist()],'witness':witness})
C={};exec((F/'receiving_module_003/source_contact_math.py').read_text(),C);D=json.loads((R/'Game/data/generated/received_structural_meshes.json').read_text());floors=[]
for q in D['regions']:
 if q.get('floor_y')!=52.5:continue
 ar=0
 for t in q['triangles']:
  poly=[list(p) for p in t]
  for ax,v,gt in [(0,-13.4,True),(0,-4,False),(1,-240.5,True),(1,-196.2,False)]:poly=C['clip'](poly,ax,v,gt) if poly else []
  ar+=C['area'](poly)
 if ar>1e-6:floors.append({'owner':q['id'],'annex_overlap_m2':ar})
pins={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in ['Game/data/architecture/received_sections.json','Game/data/architecture/received_section_floors.json','Game/data/generated/received_structural_meshes.json','Game/assets/models/SOL_D09_directory_03_source001.glb','BlenderCatalogue/assets/group4_tram_connections_20261009/port_successor_002/AST-TRM-G4-010_fore_midship_source.glb','BlenderCatalogue/assets/group4_tram_connections_20261009/port_successor_002/SUCCESSOR_INTERFACE.json']}
rep={'status':'FOREMID_STATION_LOCAL_PAPERMOON_HOLD' if hits else 'NO_TRIANGLE_INTERSECTION','source_only':True,'no_geometry_changed':True,'intersection_pairs':hits,'proposed_annex_floor_overlap_with_actual_received_owners':floors,'retained_source_pins':pins,'scope':'One existing frozen fore-midship station against actual installed Paper Moon source; no whole-route audit.','limits':['Triangle-surface witnesses establish intersection, not the complete penetration volume.','Frozen source and Paper Moon retained unchanged; no allocation, door or floor altered.']};(W/'FOREMID_PAPERMOON_LOCAL_HOLD.json').write_text(json.dumps(rep,indent=2)+'\n');print(rep['status'],'pairs',len(hits));print([(x['station_mesh'],x['retained_papermoon_mesh']) for x in hits]);print('floor overlaps',floors)
