"""Binary/source equivalence, real rim contacts and bounded structural exclusions."""
import json,sys,hashlib,itertools
from pathlib import Path
sys.path.insert(0,'C:/Users/cered/Dolphin/AstraeaTools/pythondeps')
import numpy as np
from shapely.geometry import Polygon,MultiPoint
from shapely.ops import unary_union
from check_retained_exports import read,acc,nodes
P=Path(__file__).resolve().parents[1];D=P/'dependencies/canonical_77a745';plan=json.loads((P/'docs/MIDDLE_EXTERIOR_PLACEMENT_AND_SEAMS.json').read_text());geo=json.loads((P/'qa/middle_exterior_geometry.json').read_text());rim=json.loads((P/'qa/lower_hull_top_contact.json').read_text());support=unary_union([Polygon(t) for t in rim['triangles']]);contacts=[]
for r in plan['rim_foot_contacts']:
 poly=Polygon(r['boundary_xz']);missing=poly.difference(support).area;assert missing<1e-7,(r['object'],missing);contacts.append({'object':r['object'],'supported_area_m2':poly.area,'missing_area_m2':missing,'contact_y':r['contact_y']})
outline=np.array(json.loads((D/'Game/data/hull_envelope.json').read_text())['plan_xz_m']);normal=[]
for a,b in zip(outline,np.roll(outline,-1,axis=0)):
 t=b-a;n=np.array([t[1],-t[0]],dtype=float);n/=np.linalg.norm(n)
 if np.dot(n,-a)<0:n=-n
 normal.append(n)
normal=np.array(normal);v=np.array([q for g in geo for q in g['vertices_world_xyz']]);distances=np.min(np.sum((v[:,[0,2]][:,None,:]-outline[None,:,:])*normal[None,:,:],axis=2),axis=1)
assert distances.min()>=.18-1e-4 and distances.max()<=.4+1e-4,(distances.min(),distances.max())
floors=json.loads((D/'Game/data/generated/structural_meshes.json').read_text())['regions']+json.loads((D/'Game/data/architecture/REMAINING_BATCH_FLOORS.json').read_text())['regions'];floors+=json.loads((P/'dependencies/canonical_9d6f85/Game/data/generated/received_structural_meshes.json').read_text())['regions'];floor_polys=[]
for f in floors:
 if f['floor_y']<=16.5 or f['floor_y']-f['thickness']>=61:continue
 floor_polys.append((f,unary_union([Polygon(t) for t in f['triangles']])))
overlaps=[]
for g in geo:
 a=np.array(g['vertices_world_xyz']);lo=a.min(axis=0);hi=a.max(axis=0);poly=MultiPoint(a[:,[0,2]]).convex_hull
 for f,p in floor_polys:
  if min(hi[1],f['floor_y'])-max(lo[1],f['floor_y']-f['thickness'])<=1e-6:continue
  area=poly.intersection(p).area
  if area>1e-7:overlaps.append({'object':g['object'],'floor':f['id'],'projected_area_m2':area})
assert not overlaps,overlaps[:10]
void=Polygon([[-48,-64],[48,-64],[48,64],[-48,64]]);assert all(MultiPoint(np.array(g['vertices_world_xyz'])[:,[0,2]]).convex_hull.intersection(void).area<1e-7 for g in geo)
rows=[];maxerror=0
def match(a,b):
 bins={}
 for q in b:bins.setdefault(tuple(np.floor(q/.001).astype(int)),[]).append(q)
 maximum=0
 for q in a:
  k=tuple(np.floor(q/.001).astype(int));near=[]
  for delta in itertools.product([-1,0,1],repeat=3):near.extend(bins.get(tuple(k[i]+delta[i] for i in range(3)),[]))
  assert near
  e=float(np.sqrt(np.min(np.sum((np.array(near)-q)**2,axis=1))));assert e<1e-4,e;maximum=max(maximum,e)
 return maximum
for r in plan['exports']:
 d,b=read(P/r['path']);pts=[];triangles=0;mesh_nodes=0
 for image in d.get('images',[]):assert 'bufferView' in image and 'uri' not in image
 for n,m in nodes(d):
  mesh_nodes+=1
  for p in d['meshes'][n['mesh']]['primitives']:
   a=acc(d,b,p['attributes']['POSITION']);assert np.isfinite(a).all();pts.extend((np.c_[a,np.ones(len(a))]@m.T)[:,:3]);idx=acc(d,b,p['indices']).ravel();assert len(idx)%3==0 and idx.max()<len(a);triangles+=len(idx)//3
   for key in ['NORMAL','TEXCOORD_0']:assert np.isfinite(acc(d,b,p['attributes'][key])).all()
 src=np.array([q for g in geo if g['edge']==r['edge'] for q in g['vertices_world_xyz']]);a=np.array(pts);error=max(match(a,src),match(src,a));maxerror=max(maxerror,error);assert triangles==sum(g['triangles'] for g in geo if g['edge']==r['edge'])
 assert hashlib.sha256((P/r['path']).read_bytes()).hexdigest()==r['sha256'];rows.append({'edge':r['edge'],'mesh_nodes':mesh_nodes,'triangles':triangles,'bidirectional_vertex_max_error_m':error,'export_bytes':(P/r['path']).stat().st_size,'world_actual_bounds':[a.min(axis=0).tolist(),a.max(axis=0).tolist()]})
assert hashlib.sha256((P/plan['source']).read_bytes()).hexdigest()==plan['native_sha256']
out={'passed':True,'real_lower_hull_rim_contacts':len(contacts),'missing_contact_area_m2':sum(r['missing_area_m2'] for r in contacts),'actual_normal_material_distance_m':[float(distances.min()),float(distances.max())],'compiled_floor_overlap_candidates':overlaps,'compiled_floor_regions_screened':len(floor_polys),'protected_atrium_intrusions':0,'retained_HUL002':'New frame ends atY61, existing shoulder beginsY61; boundary contact only, no positive-volume height overlap','source_export_bidirectional_max_error_m':maxerror,'exports':rows,'contacts':contacts,'remaining':'Actual all-room/window/fixture mesh census and pressure/enclosure/source-owner seams still open; no engineering load acceptance, engine import or full traversal. Structural floor exclusion does not certify all occupied room contents.'}
(P/'qa/middle_exterior_checks.json').write_text(json.dumps(out,indent=2)+'\n');print('MIDDLE_FRAME_CHECKS',len(contacts),'real contacts',len(rows),'exports',maxerror,'vertex error')
