"""Check complete disjoint side-field coverage, actual contacts and GLB integrity."""
import json,sys,hashlib,itertools
from pathlib import Path
sys.path.insert(0,'C:/Users/cered/Dolphin/AstraeaTools/pythondeps')
import numpy as np
from shapely.geometry import Polygon,MultiPoint,box
from shapely.ops import unary_union
from check_retained_exports import read,acc,nodes
P=Path(__file__).resolve().parents[1];D=P/'dependencies/canonical_77a745';L=P/'dependencies/canonical_9d6f85';plan=json.loads((P/'docs/MIDDLE_SKIN_PLACEMENT_AND_INTERFACES.json').read_text());geo=json.loads((P/'qa/middle_skin_geometry.json').read_text())
support=unary_union([Polygon(t) for t in json.loads((P/'qa/lower_hull_top_contact.json').read_text())['triangles']]);contacts=[];coverage=[]
for edge in range(16):
 fields=[box(*[g['uv_edge_interval'][0],g['y_interval'][0],g['uv_edge_interval'][1],g['y_interval'][1]]) for g in geo if g['edge']==edge];union=unary_union(fields);missing=box(0,16.5,1,61).difference(union).area;overlap=sum(q.area for q in fields)-union.area;assert missing<1e-9 and abs(overlap)<1e-9,(edge,missing,overlap)
 coverage.append({'edge':edge,'missing_parametric_face_area':missing,'overlap_parametric_face_area':overlap,'coverage_interval_y':[16.5,61]})
for g in geo:
 if g['y_interval'][0]!=16.5:continue
 p=Polygon([(v[0],v[2]) for v in g['vertices_world_xyz'][:4]]);missing=p.difference(support).area;assert missing<1e-5,(g['object'],missing);contacts.append({'object':g['object'],'missing_contact_area_m2':missing,'contact_y':16.5})
outline=np.array(json.loads((D/'Game/data/hull_envelope.json').read_text())['plan_xz_m']);normal=[]
for a,b in zip(outline,np.roll(outline,-1,axis=0)):
 t=b-a;n=np.array([t[1],-t[0]],dtype=float);n/=np.linalg.norm(n);normal.append(n if np.dot(n,-a)>0 else -n)
normal=np.array(normal);v=np.array([q for g in geo for q in g['vertices_world_xyz']]);dist=np.min(np.sum((v[:,[0,2]][:,None,:]-outline[None,:,:])*normal[None,:,:],axis=2),axis=1);assert dist.min()>=.02-1e-4 and dist.max()<=.18+1e-4
floors=json.loads((D/'Game/data/generated/structural_meshes.json').read_text())['regions']+json.loads((D/'Game/data/architecture/REMAINING_BATCH_FLOORS.json').read_text())['regions']+json.loads((L/'Game/data/generated/received_structural_meshes.json').read_text())['regions'];regions=[]
for f in floors:
 if f['floor_y']<=16.5 or f['floor_y']-f['thickness']>=61:continue
 regions.append((f,unary_union([Polygon(t) for t in f['triangles']])))
overlaps=[]
# One edge's whole skin prism is a conservative bound for its individual fields.
for edge in range(16):
 a=np.array([q for g in geo if g['edge']==edge for q in g['vertices_world_xyz']]);p=MultiPoint(a[:,[0,2]]).convex_hull
 for f,q in regions:
  area=p.intersection(q).area
  if area>1e-7:overlaps.append({'edge':edge,'floor':f['id'],'projected_area_m2':area})
assert not overlaps,overlaps
void=box(-48,-64,48,64);assert all(MultiPoint(np.array(g['vertices_world_xyz'])[:,[0,2]]).convex_hull.intersection(void).area<1e-7 for g in geo)
def match(a,b):
 bins={}
 for q in b:bins.setdefault(tuple(np.floor(q/.001).astype(int)),[]).append(q)
 maximum=0
 for q in a:
  k=tuple(np.floor(q/.001).astype(int));near=[]
  for delta in itertools.product([-1,0,1],repeat=3):near.extend(bins.get(tuple(k[i]+delta[i] for i in range(3)),[]))
  assert near;e=float(np.sqrt(np.min(np.sum((np.array(near)-q)**2,axis=1))));assert e<1e-4;maximum=max(maximum,e)
 return maximum
exports=[]
for r in plan['exports']:
 path=P/r['path'];assert hashlib.sha256(path.read_bytes()).hexdigest()==r['sha256'];d,b=read(path);pts=[];tris=0
 for image in d.get('images',[]):assert 'bufferView' in image and 'uri' not in image
 assert any(m.get('alphaMode')=='BLEND' for m in d['materials']),r['edge']
 for n,m in nodes(d):
  for q in d['meshes'][n['mesh']]['primitives']:
   a=acc(d,b,q['attributes']['POSITION']);assert np.isfinite(a).all();pts.extend((np.c_[a,np.ones(len(a))]@m.T)[:,:3]);idx=acc(d,b,q['indices']).ravel();assert len(idx)%3==0 and idx.max()<len(a);tris+=len(idx)//3
   for key in ['NORMAL','TEXCOORD_0']:assert np.isfinite(acc(d,b,q['attributes'][key])).all()
 src=np.array([q for g in geo if g['edge']==r['edge'] for q in g['vertices_world_xyz']]);a=np.array(pts);error=max(match(a,src),match(src,a));assert tris==sum(g['triangles'] for g in geo if g['edge']==r['edge']);exports.append({'edge':r['edge'],'triangles':tris,'bytes':path.stat().st_size,'source_export_max_error_m':error})
assert hashlib.sha256((P/plan['source']).read_bytes()).hexdigest()==plan['native_sha256']
out={'passed':True,'side_fields':coverage,'rim_contacts':contacts,'missing_contact_area_m2':sum(r['missing_contact_area_m2'] for r in contacts),'actual_normal_material_distance_m':[float(dist.min()),float(dist.max())],'floor_overlap_candidates':overlaps,'floor_regions_screened':len(regions),'exports':exports,'limits':'Continuous coverage proof is the middle vertical side field only. Lower/upper seals, room windows/privacy, pressure/load engineering, maintenance routes, renderer transparency and engine imports remain root interfaces. No whole enclosure or operating window acceptance.'}
(P/'qa/middle_skin_checks.json').write_text(json.dumps(out,indent=2)+'\n');print('MIDDLE_SKIN_CHECKS',len(geo),'parts',len(exports),'exports',len(contacts),'rim contacts')
