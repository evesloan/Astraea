"""Independent actual-binary GLB validation; resolves node TRS/hierarchy in exchange frame."""
from pathlib import Path
import json,struct,math,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 d=p.read_bytes();a,b,c=struct.unpack_from('<III',d);assert a==0x46546c67 and b==2 and c==len(d);off=12;doc=None;raw=None
 while off<len(d):
  size,tag=struct.unpack_from('<II',d,off);off+=8;x=d[off:off+size];off+=size
  if tag==0x4e4f534a:doc=json.loads(x)
  elif tag==0x004e4942:raw=x
 return doc,raw

def acc(j,b,k):
 a=j['accessors'][k];v=j['bufferViews'][a['bufferView']];typ={5120:'b',5121:'B',5122:'h',5123:'H',5125:'I',5126:'f'}[a['componentType']];n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];size=struct.calcsize(typ)*n;start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',size)
 return np.array([struct.unpack_from('<'+typ*n,b,start+i*stride) for i in range(a['count'])])
def local(n):
 if 'matrix' in n:return np.array(n['matrix']).reshape((4,4),order='F')
 x,y,z,w=n.get('rotation',[0,0,0,1]);r=np.eye(4);r[:3,:3]=[[1-2*y*y-2*z*z,2*x*y-2*z*w,2*x*z+2*y*w],[2*x*y+2*z*w,1-2*x*x-2*z*z,2*y*z-2*x*w],[2*x*z-2*y*w,2*y*z+2*x*w,1-2*x*x-2*y*y]];r[:3,:3]=r[:3,:3]@np.diag(n.get('scale',[1,1,1]));r[:3,3]=n.get('translation',[0,0,0]);return r
def globals(j):
 out={}
 def visit(k,m):
  out[k]=m@local(j['nodes'][k])
  for c in j['nodes'][k].get('children',[]):visit(c,out[k])
 for k in j['scenes'][j.get('scene',0)]['nodes']:visit(k,np.eye(4))
 return out

def triangle_distance(p,a,b,c):
 # Orthogonal projection to triangle, otherwise shortest edge distance.
 ab=b-a;ac=c-a;n=np.cross(ab,ac);nn=float(n@n)
 if nn>1e-20:
  q=p-n*float((p-a)@n)/nn;d00=ab@ab;d01=ab@ac;d11=ac@ac;d20=(q-a)@ab;d21=(q-a)@ac;den=d00*d11-d01*d01
  if abs(den)>1e-20:
   v=(d11*d20-d01*d21)/den;w=(d00*d21-d01*d20)/den
   if v>=-1e-8 and w>=-1e-8 and v+w<=1+1e-8:return float(np.linalg.norm(p-q))
 def edge(u,v):
  d=v-u;t=max(0,min(1,float((p-u)@d)/float(d@d))) if d@d>1e-20 else 0;return np.linalg.norm(p-(u+t*d))
 return float(min(edge(a,b),edge(b,c),edge(c,a)))

shared=json.loads((ROOT/'dependency_manifest.json').read_text())['unchanged_shared_dependencies'];source_textures={p.stem:p for p in (ROOT/'textures').glob('*.png')}
for d in shared:
 p=BASE/d['path'];assert sha(p)==d['sha256'],p
 if p.suffix=='.png':source_textures[p.stem]=p
reports=[]
for glb in sorted((ROOT/'exports').glob('*.glb')):
 mf=json.loads((ROOT/(glb.stem+'.manifest.json')).read_text());j,b=read(glb);gm=globals(j);triangles=[];points=[];issues=[];uvcollapsed=0.;opposed=0;degenerate=0;uvsets=set();count=0
 for node_idx,mat in gm.items():
  nd=j['nodes'][node_idx]
  if 'mesh' not in nd:continue
  if np.linalg.det(mat[:3,:3])<=0:issues.append('Nonpositive world determinant')
  for prim in j['meshes'][nd['mesh']]['primitives']:
   ps=acc(j,b,prim['attributes']['POSITION']);ns=acc(j,b,prim['attributes']['NORMAL']);inds=acc(j,b,prim['indices']).astype(int).reshape(-1,3);ps=(np.c_[ps,np.ones(len(ps))]@mat.T)[:,:3];ns=ns@np.linalg.inv(mat[:3,:3]);points.extend(ps);uvsets.update(k for k in prim['attributes'] if k.startswith('TEXCOORD'))
   uv=acc(j,b,prim['attributes']['TEXCOORD_0']);assert np.isfinite(ps).all() and np.isfinite(ns).all() and np.isfinite(uv).all()
   for ids in inds:
    pp=ps[ids];triangles.append(pp);normal=np.cross(pp[1]-pp[0],pp[2]-pp[0]);area=np.linalg.norm(normal)/2;count+=1
    if area<1e-12:degenerate+=1
    elif normal@np.mean(ns[ids],axis=0)<-1e-10:opposed+=1
    u=uv[ids];ar=abs(np.cross(u[1]-u[0],u[2]-u[0]))*.5
    if ar<1e-12:uvcollapsed+=area
 pts=np.array(points);lo=pts.min(axis=0);hi=pts.max(axis=0);expected=np.array(mf['dimensions_blender_xyz_m'])[[0,2,1]];error=float(np.max(abs(hi-lo-expected)))
 if error>1e-5:issues.append('Source dimension mismatch')
 if count!=mf['evaluated_triangles']:issues.append('Source triangle mismatch')
 if degenerate:issues.append('Degenerate triangles')
 if opposed:issues.append('Opposed normals')
 if uvcollapsed>1e-9:issues.append('Collapsed UV area')
 if uvsets!={'TEXCOORD_0'}:issues.append('Unexpected UV set inventory')
 textures=[]
 for im in j['images']:
  v=j['bufferViews'][im['bufferView']];raw=b[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];h=hashlib.sha256(raw).hexdigest();p=source_textures.get(im['name']);okay=p is not None and sha(p)==h
  textures.append({'name':im['name'],'embedded_sha256':h,'matches_declared_dependency':okay})
  if not okay:issues.append('Texture mismatch '+im['name'])
 roles=[]
 for m in j['materials']:
  role=m.get('extras',{}).get('astraea_material_role',m['name'].replace('ASTRAEA_',''));roles.append(role)
  if 'baseColorTexture' not in m.get('pbrMetallicRoughness',{}):issues.append('Missing ordinary base-color texture '+role)
  if any(v!=0 for v in m.get('emissiveFactor',[0,0,0])):issues.append('Unrequested emission '+role)
 if sorted(set(roles))!=mf['material_roles']:issues.append('Material roles mismatch')
 markers=[]
 for rec in mf['positions_and_normals']:
  k=next(i for i,n in enumerate(j['nodes']) if n['name']==rec['node_name']);actual=gm[k][:3,3];err=float(max(abs(actual-np.array(rec['exchange_gltf_yup_m']))));extra=j['nodes'][k].get('extras',{});normerr=float(max(abs(np.array(extra['exchange_normal'])-np.array(rec['normal_exchange_gltf']))));r={'name':rec['name'],'kind':rec['kind'],'actual_exchange_world_m':actual.tolist(),'declared_exchange_m':rec['exchange_gltf_yup_m'],'position_error_m':err,'normal_record_error':normerr,'hierarchy_resolved':True}
  if err>1e-6 or normerr>1e-6:issues.append('Marker mismatch '+rec['name'])
  if rec['kind'] in ['physical_contact','physical_surface']:
   dist=min(triangle_distance(actual,*t) for t in triangles);r['distance_to_actual_export_surface_m']=dist
   if dist>2e-5:issues.append('Physical marker misses surface '+rec['name'])
  markers.append(r)
 report={'catalogue_id':mf['catalogue_id'],'status':'PASS' if not issues else 'FAIL','source_sha256':sha(ROOT/mf['source']),'export_sha256':sha(glb),'generator_sha256':sha(ROOT/mf['generator']),'node_count':len(j['nodes']),'mesh_count':len(j['meshes']),'material_primitives':sum(len(m['primitives']) for m in j['meshes']),'triangles':count,'bounds_min_exchange_m':lo.tolist(),'bounds_max_exchange_m':hi.tolist(),'dimensions_exchange_xyz_m':(hi-lo).tolist(),'source_dimension_error_m':error,'degenerate_triangles':degenerate,'opposed_normal_triangles':opposed,'collapsed_uv_area_m2':uvcollapsed,'texture_records':textures,'material_roles':sorted(set(roles)),'markers':markers,'issues':issues,'no_animations':'animations' not in j,'no_lights':'KHR_lights_punctual' not in j.get('extensions',{})};reports.append(report)
(ROOT/'qa/glb_independent_validation.json').write_text(json.dumps(reports,indent=2));print(json.dumps([{'id':r['catalogue_id'],'status':r['status'],'issues':r['issues'],'tris':r['triangles']} for r in reports],indent=2));assert all(r['status']=='PASS' for r in reports)
