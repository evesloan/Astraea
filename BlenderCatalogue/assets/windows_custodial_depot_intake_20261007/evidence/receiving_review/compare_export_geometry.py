"""Plain-Python exact accessor payload and semantic-transform comparison of old/new GLBs."""
from pathlib import Path
import json,struct,hashlib,math,io
from PIL import Image
B=Path(__file__).resolve().parents[1];OLD=B/'full_review001/WP09_D01_directory_10/exports/WP09_custodial_depot.glb';NEW=B/'export_successor001/exports/WP09_custodial_depot.glb'
I=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]
def mul(a,b):return [sum(a[k*4+r]*b[c*4+k] for k in range(4)) for c in range(4) for r in range(4)]
def local(n):
 if 'matrix' in n:return n['matrix']
 x,y,z,w=n.get('rotation',[0,0,0,1]);sx,sy,sz=n.get('scale',[1,1,1]);tx,ty,tz=n.get('translation',[0,0,0])
 return [(1-2*y*y-2*z*z)*sx,(2*x*y+2*z*w)*sx,(2*x*z-2*y*w)*sx,0,(2*x*y-2*z*w)*sy,(1-2*x*x-2*z*z)*sy,(2*y*z+2*x*w)*sy,0,(2*x*z+2*y*w)*sz,(2*y*z-2*x*w)*sz,(1-2*x*x-2*y*y)*sz,0,tx,ty,tz,1]
def parse(path):
 raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);o=20+n;size,_=struct.unpack_from('<II',raw,o);binary=raw[o+8:o+8+size]
 def accessor(idx):
  a=g['accessors'][idx];assert not a.get('sparse');v=g['bufferViews'][a['bufferView']];comp={5120:1,5121:1,5122:2,5123:2,5125:4,5126:4}[a['componentType']];width={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']]*comp;off=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',width);data=b''.join(binary[off+i*stride:off+i*stride+width] for i in range(a['count']))
  return {'type':a['type'],'componentType':a['componentType'],'count':a['count'],'normalized':a.get('normalized',False),'sha256':hashlib.sha256(data).hexdigest()}
 cache={}
 def mesh(idx):
  if idx in cache:return cache[idx]
  rows=[]
  for p in g['meshes'][idx]['primitives']:
   rows.append({'mode':p.get('mode',4),'attributes':{k:accessor(v) for k,v in p['attributes'].items()},'indices':accessor(p['indices']) if 'indices' in p else None})
  cache[idx]=sorted(rows,key=lambda r:json.dumps(r,sort_keys=True));return cache[idx]
 nodes={};lights={}
 def walk(idx,M):
  n=g['nodes'][idx];W=mul(M,local(n));name=n.get('name',str(idx))
  if 'mesh' in n:nodes[name]={'world_transform':W,'geometry':mesh(n['mesh'])}
  li=n.get('extensions',{}).get('KHR_lights_punctual',{}).get('light')
  if li is not None:lights[name]={'world_transform':W,'light':g['extensions']['KHR_lights_punctual']['lights'][li]}
  for c in n.get('children',[]):walk(c,W)
 for idx in g['scenes'][g.get('scene',0)]['nodes']:walk(idx,I)
 images=[]
 for r in g.get('images',[]):
  assert 'bufferView' in r and 'uri' not in r;v=g['bufferViews'][r['bufferView']];data=binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];im=Image.open(io.BytesIO(data));im.load();images.append({'name':r.get('name'),'sha256':hashlib.sha256(data).hexdigest(),'size':list(im.size),'decoded':True})
 return {'sha256':hashlib.sha256(raw).hexdigest(),'nodes':nodes,'images':images,'lights':lights}
a=parse(OLD);b=parse(NEW);expected=set(json.loads((B/'export_successor001/qa/INPUT_PINS.json').read_text())['expected_authored_sign_names']);old=set(a['nodes']);new=set(b['nodes']);geom=[];trans=[]
for n in sorted(old&new):
 if a['nodes'][n]['geometry']!=b['nodes'][n]['geometry']:geom.append(n)
 delta=max(abs(x-y) for x,y in zip(a['nodes'][n]['world_transform'],b['nodes'][n]['world_transform']))
 if delta>1e-6:trans.append({'name':n,'max_delta':delta})
image_equal=sorted((r['sha256'],r['size']) for r in a['images'])==sorted((r['sha256'],r['size']) for r in b['images'])
checks={'exact24_added_sign_mesh_names':new-old==expected,'no_original_mesh_removed':old<=new,'all_original_mesh_accessor_payloads_identical':not geom,'all_original_mesh_transforms_match_1e_6':not trans,'embedded_image_bytes_identical':image_equal,'light_definitions_and_transforms_identical':a['lights']==b['lights']}
r={'scope':'Non-sign geometry parity using exact original accessor bytes and resolved world transforms, embedded pixel payloads and punctual lights','checks':checks,'pass':all(checks.values()),'old_sha256':a['sha256'],'new_sha256':b['sha256'],'old_mesh_count':len(old),'new_mesh_count':len(new),'added_mesh_names':sorted(new-old),'removed_mesh_names':sorted(old-new),'changed_original_geometry':geom,'changed_original_transforms':trans,'successor_images':b['images'],'punctual_lights':len(b['lights'])}
(B/'export_successor001/qa/GEOMETRY_RESOURCE_PARITY.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k not in ['successor_images','added_mesh_names']},indent=2));assert r['pass']
