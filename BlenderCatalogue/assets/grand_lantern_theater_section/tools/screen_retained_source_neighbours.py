"""Pure source/compiled-slab neighbour screen. Not a live scene census.
No import of another build script (those may write on import). Read-only inputs.
"""
import json,hashlib,struct
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];G=Path('/workspace/shared/astraea-godot-production-20261003')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def glb(path):
 raw=path.read_bytes();assert raw[:4]==b'glTF';offset=12;chunks={}
 while offset<len(raw):
  n,kind=struct.unpack_from('<II',raw,offset);chunks[kind]=raw[offset+8:offset+8+n];offset+=8+n
 d=json.loads(chunks[0x4e4f534a]);blob=chunks[0x004e4942];out=[]
 def acc(k):
  a=d['accessors'][k];assert 'sparse'not in a;v=d['bufferViews'][a['bufferView']];w={'SCALAR':1,'VEC3':3}[a['type']];dt=np.dtype({5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']]);off=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',w*dt.itemsize)
  return np.ndarray((a['count'],w),dt,blob,off,(stride,dt.itemsize)).copy()
 def visit(i,parent):
  nd=d['nodes'][i]
  if 'matrix'in nd:m=np.array(nd['matrix']).reshape(4,4).T
  else:
   x,y,z,w=nd.get('rotation',[0,0,0,1]);q=np.array([[1-2*y*y-2*z*z,2*x*y-2*z*w,2*x*z+2*y*w],[2*x*y+2*z*w,1-2*x*x-2*z*z,2*y*z-2*x*w],[2*x*z-2*y*w,2*y*z+2*x*w,1-2*x*x-2*y*y]]);m=np.eye(4);m[:3,:3]=q@np.diag(nd.get('scale',[1,1,1]));m[:3,3]=nd.get('translation',[0,0,0])
  m=parent@m
  if'mesh'in nd:
   for p in d['meshes'][nd['mesh']]['primitives']:
    assert p.get('mode',4)==4
    a=acc(p['attributes']['POSITION']);a=(np.column_stack([a,np.ones(len(a))])@m.T)[:,:3];idx=acc(p['indices']).flatten()if'indices'in p else np.arange(len(a));out.append((nd.get('name',str(i)),a,idx.reshape(-1,3)))
  for c in nd.get('children',[]):visit(c,m)
 for i in d['scenes'][d.get('scene',0)]['nodes']:visit(i,np.eye(4))
 return out
geo=json.loads((R/'source/geometry.json').read_text());allv=np.array([v for o in geo['objects']if o['role']!='preview_only'for v in o['vertices_world']]);lo=allv.min(0);hi=allv.max(0)
# Installed world-coordinate architecture is verified from named current builders.
models=[('AST-HUL-001.glb',[0,0,0],'scripts/ship.gd'),('AST-ATR-001.glb',[0,0,0],'scripts/ship.gd'),('AST-CMD-001.glb',[0,0,0],'scripts/central_command_crown.gd'),('AST-CMD-002.glb',[0,0,0],'scripts/aft_command_crown.gd'),('AST-CMD-003.glb',[0,0,0],'scripts/bridge_platform.gd'),('AST-CMD-004.glb',[0,0,0],'scripts/bridge_enclosure.gd'),('AST-CMD-005.glb',[0,0,0],'scripts/aft_crown_platform.gd'),('AST-CMD-006.glb',[0,0,0],'scripts/upper_horizon_enclosure.gd'),('AST-RES-006.glb',[0,0,0],'scripts/d17_connected_house.gd'),('AST-AQU-016.glb',[0,0,0],'scripts/grand_pool_section.gd'),('AST-STF-009_pool_market.glb',[0,0,0],'scripts/lower_staff_network.gd'),('AST-LIB-011.glb',[-80,78,0],'scripts/star_atlas.gd'),('AST-DIN-008.glb',[8,61,-250],'scripts/orchard_foodhall.gd'),('AST-RTL-009.glb',[4,52.5,-250],'scripts/orchard_exchange.gd')]
for cfg in ['PRIMARY_ATRIUM_CORE','FORWARD_PUBLIC_CORE','FORE_MIDSHIP_PUBLIC_CORE','AFT_MIDSHIP_PUBLIC_CORE','AFT_PUBLIC_CORE','AFT_CROWN_LINK']:
 p=G/'data/architecture'/f'{cfg}.json';d=json.loads(p.read_text());models.append((d.get('enclosure_file','AST-CIR-005.glb'),d['origin'],str(p.relative_to(G))))
reports=[];contacts=[]
for file,origin,builder in models:
 p=G/'assets/models'/file;meshes=glb(p);candidates=[];vsall=[]
 for n,v,idx in meshes:
  v=v+np.array(origin);vsall.append(v);t=v[idx];hit=np.all(t.max(1)>=lo-1e-8,axis=1)&np.all(t.min(1)<=hi+1e-8,axis=1)
  if hit.any():candidates.append({'node':n,'triangle_aabb_candidates':int(hit.sum())})
 v=np.concatenate(vsall);row={'model':file,'origin':origin,'builder':builder,'builder_sha256':sha(G/builder),'model_sha256':sha(p),'world_bounds':{'min':v.min(0).tolist(),'max':v.max(0).tolist()},'triangle_count':sum(len(i)for _,_,i in meshes),'triangle_aabb_candidates':candidates};reports.append(row)
 if candidates:contacts.append(row)
compiled=G/'data/generated/structural_meshes.json';slabs=[];target=box(lo[0],lo[2],hi[0],hi[2])
for r in json.loads(compiled.read_text())['regions']:
 if r['floor_y']<lo[1]-1e-8 or r['floor_y']-r['thickness']>hi[1]+1e-8:continue
 shape=unary_union([Polygon(t)for t in r['triangles']]);area=shape.intersection(target).area
 if area>1e-8:slabs.append({'id':r['id'],'floor_y':r['floor_y'],'thickness':r['thickness'],'positive_plan_overlap_m2':area})
report={'status':'Listed retained source models and every current compiled slab checked; live complete scene census remains required','source_geometry_sha256':sha(R/'source/geometry.json'),'target_bounds':{'min':lo.tolist(),'max':hi.tolist()},'models':reports,'listed_model_contacts':contacts,'compiled_source_sha256':sha(compiled),'compiled_slab_contacts':slabs,'scope_limits':['Only listed world-transformed GLBs; dynamic cabins, gates and procedural fixture/prop instances need the live scene probe','Empty triangle AABB candidate lists prove exclusion; nonempty lists would need exact triangles','No engine/import/runtime acceptance']}
(R/'qa/retained_source_neighbour_screen.json').write_text(json.dumps(report,indent=2)+'\n');assert not contacts and not slabs,(contacts,slabs)
print(json.dumps({'listed_models_checked':len(reports),'listed_model_contacts':len(contacts),'compiled_slab_contacts':len(slabs),'live_scene_census_still_required':True}))
