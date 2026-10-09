"""Source/export/contact/retained-neighbor checks for the approved gallery batch."""
import json,sys,math,hashlib,itertools
from pathlib import Path
sys.path.insert(0,'C:/Users/cered/Dolphin/AstraeaTools/pythondeps')
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
from check_retained_exports import read,acc,nodes
P=Path(__file__).resolve().parents[1];D=P/'dependencies/canonical_77a745';LATEST=P/'dependencies/canonical_9d6f85'
quiet='--quiet' in sys.argv;plan=json.loads((P/'docs'/('QUIETER_GALLERY_PLACEMENT_AND_INTERFACES.json' if quiet else 'GALLERY_PLACEMENT_AND_INTERFACES.json')).read_text());floors=json.loads((D/'Game/data/generated/structural_meshes.json').read_text())['regions'];retained=[]
def decode(path):
 d,b=read(path);pts=[];tris=0;names=[]
 for im in d.get('images',[]):assert 'bufferView' in im and 'uri' not in im
 for n,m in nodes(d):
  names.append(n.get('name',''))
  for p in d['meshes'][n['mesh']]['primitives']:
   a=acc(d,b,p['attributes']['POSITION']);assert np.isfinite(a).all();pts.extend((np.c_[a,np.ones(len(a))]@m.T)[:,:3]);i=acc(d,b,p['indices']).ravel();assert len(i)%3==0 and i.max()<len(a);tris+=len(i)//3
   for name in ['NORMAL','TEXCOORD_0']:assert name in p['attributes'] and np.isfinite(acc(d,b,p['attributes'][name])).all()
 return np.array(pts),tris,names
for family,asset,origin in [('atrium_guard_network','AST-ATR-001',[0,0,0]),('atrium_garden','AST-GAR-001',[0,6,0]),('canopy_terrace','AST-GAR-004',[-52,27,0]),('upper_hull_theater_shoulders002','AST-HUL-002',[0,0,0])]:
 a,_,_=decode(D/f'BlenderCatalogue/assets/{family}/exports/{asset}.glb');a+=np.array(origin);retained.append({'id':asset,'bounds':[a.min(axis=0),a.max(axis=0)],'path':str(D/f'BlenderCatalogue/assets/{family}/exports/{asset}.glb'),'origin':origin})
catalogue=json.loads((D/'BlenderCatalogue/catalogue_manifest.json').read_text())['assets']
for asset,origin in [('AST-SAL-007',[64,52.5,-15]),('AST-GAR-003',[-39,27,-27]),('AST-GAR-005',[-52,27,0]),('AST-COM-001',[63,84,0]),('AST-COM-002',[79,84,4]),('AST-CMD-001',[0,0,0])]:
 entry=next(r for r in catalogue if r['catalogue_id']==asset);a,_,_=decode(LATEST/'BlenderCatalogue'/entry['export']);a+=np.array(origin);retained.append({'id':asset,'bounds':[a.min(axis=0),a.max(axis=0)],'path':str(LATEST/'BlenderCatalogue'/entry['export']),'origin':origin})
retained+=json.loads((P/'qa/gallery_proposal_floor_contacts.json').read_text())['retained_bearing_bounds']
def match(a,b):
 buckets={}
 for q in b:buckets.setdefault(tuple(np.floor(q/.001).astype(int)),[]).append(q)
 max_error=0
 for q in a:
  k=tuple(np.floor(q/.001).astype(int));near=[]
  for delta in itertools.product([-1,0,1],repeat=3):near.extend(buckets.get(tuple(k[i]+delta[i] for i in range(3)),[]))
  assert near,'Export vertex absent from source'
  distance=float(np.sqrt(np.min(np.sum((np.array(near)-q)**2,axis=1))));assert distance<1e-4,distance;max_error=max(max_error,distance)
 return max_error
rows=[]
for r in plan['rooms']:
 a,tris,names=decode(P/r['export']);source=json.loads((P/f"qa/gallery_geometry_{r['deck']}.json").read_text());v=np.array([q for s in source for q in s['vertices_local_xyz']]);error=max(match(a,v),match(v,a));assert tris==r['triangles']
 origin=np.array(r['origin_world_xyz']);world=a+origin;lo=world.min(axis=0);hi=world.max(axis=0);bounds=np.array(r['bounds_world_xyz']);assert np.all(lo>=bounds[0]-1e-5) and np.all(hi<=bounds[1]+1e-5)
 floor=next(f for f in floors if f['id']==r['retained_floor_owner']);support=unary_union([Polygon(t) for t in floor['triangles']]);foot_area=0
 for foot in r['foot_contacts']:
  poly=Polygon([[q[0]+origin[0],q[1]+origin[2]] for q in foot['boundary']]);missing=poly.difference(support).area;assert missing<1e-8,(foot['object'],missing);foot_area+=poly.area
 candidates=[]
 for q in retained:
  x,z=map(np.array,q.get('bounds',q.get('bounds_xyz')))
  if np.all(np.minimum(hi,z)-np.maximum(lo,x)>1e-5):
   if 'path' not in q:candidates.append(q['id']);continue
   d,b=read(Path(q['path']));hits=0
   for n,m in nodes(d):
    for primitive in d['meshes'][n['mesh']]['primitives']:
     vertices=acc(d,b,primitive['attributes']['POSITION']);vertices=(np.c_[vertices,np.ones(len(vertices))]@m.T)[:,:3]+np.array(q['origin']);indices=acc(d,b,primitive['indices']).ravel().astype(int);tri=vertices[indices].reshape(-1,3,3)
     overlaps=np.minimum(hi,tri.max(axis=1))-np.maximum(lo,tri.min(axis=1));hits+=int(np.sum(np.all(overlaps>1e-5,axis=1)))
   if hits:candidates.append(q['id']+':'+str(hits)+' triangle AABBs')
 assert not candidates,(r['id'],candidates)
 for light in r['lights']:
  x,y,z=light['position_local_xyz'];radius=light['cone_horizontal_bound_m'];assert x-radius>=0 and x+radius<=3.5 and z-radius>=0 and z+radius<=6
 assert hashlib.sha256((P/r['source']).read_bytes()).hexdigest()==r['native_sha256'];assert hashlib.sha256((P/r['export']).read_bytes()).hexdigest()==r['export_sha256']
 rows.append({'id':r['id'],'mesh_nodes':len(names),'triangles':tris,'source_export_bidirectional_vertex_max_error_m':error,'world_actual_bounds':[lo.tolist(),hi.tolist()],'floor_contacts':len(r['foot_contacts']),'footprint_sum_area_m2':foot_area,'missing_floor_area_m2':0,'retained_neighbor_triangle_AABB_candidates':candidates,'protected_strip_furniture_margin_min_m':float(lo[0]-42),'light_cones_inside_approved_footprint':True,'export_bytes':(P/r['export']).stat().st_size})
out={'passed':True,'source_baseline':'9d6f8518f9ddbe5892711ca4eb4849a46fbd32be','checked_neighbor_bounds':len(retained),'rooms':rows,'limitations':'No engine/import, species pose, full movement/cart, display/audio interactions or final art acceptance. No triangle-AABB candidates (refined from whole-model bounds) proves exclusion only for listed neighboring sources, not all dynamic props. Existing slab thickness/headroom remains source-owned.'}
(P/'qa'/('quieter_gallery_batch_checks.json' if quiet else 'gallery_batch_checks.json')).write_text(json.dumps(out,indent=2)+'\n');print('GALLERY_BATCH_CHECKS',len(rows),sum(x['triangles'] for x in rows),'triangles',sum(x['export_bytes'] for x in rows),'bytes')
