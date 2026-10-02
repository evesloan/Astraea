"""Binary GLB audit including resolved actual node hierarchy and negative controls."""
import json,struct,math,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]
p=ROOT/'AST-ENG-003.glb';data=p.read_bytes();assert struct.unpack_from('<III',data)==(0x46546c67,2,len(data))
off=12
while off<len(data):
 n,kind=struct.unpack_from('<II',data,off);off+=8;blob=data[off:off+n];off+=n
 if kind==0x4e4f534a:j=json.loads(blob)
 elif kind==0x004e4942:binary=blob
def accessor(i):
 a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];fmt={5121:'B',5123:'H',5125:'I',5126:'f'}[a['componentType']];n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];size=struct.calcsize(fmt)*n;stride=v.get('byteStride',size);start=v.get('byteOffset',0)+a.get('byteOffset',0)
 return np.array([struct.unpack_from('<'+fmt*n,binary,start+k*stride) for k in range(a['count'])])
def local(node):
 if 'matrix' in node:return np.array(node['matrix']).reshape(4,4).T
 x,y,z,w=node.get('rotation',[0,0,0,1]);r=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
 out=np.eye(4);out[:3,:3]=r@np.diag(node.get('scale',[1,1,1]));out[:3,3]=node.get('translation',[0,0,0]);return out
world={};parents={c:i for i,n in enumerate(j['nodes']) for c in n.get('children',[])}
def transform(i):
 if i not in world:world[i]=(transform(parents[i]) if i in parents else np.eye(4))@local(j['nodes'][i])
 return world[i]
positions=[];tris=[];node_rows=[];issues=[];uv_zero_surface=0;opposed=0;degenerate=0;triangle_count=0
for i,n in enumerate(j['nodes']):
 T=transform(i);node_rows.append({'name':n.get('name'),'translation_gltf_yup_m':T[:3,3].tolist(),'parent':j['nodes'][parents[i]].get('name') if i in parents else None})
 if 'mesh' not in n:continue
 for pr in j['meshes'][n['mesh']]['primitives']:
  ps=accessor(pr['attributes']['POSITION']);ps=(T@np.column_stack([ps,np.ones(len(ps))]).T).T[:,:3];ns=accessor(pr['attributes']['NORMAL'])@np.linalg.inv(T[:3,:3]);ix=accessor(pr['indices']).reshape(-1).astype(int);uu=accessor(pr['attributes']['TEXCOORD_0']);triangle_count+=len(ix)//3
  if not np.isfinite(ps).all() or not np.isfinite(ns).all() or not np.isfinite(uu).all():issues.append('Nonfinite geometry')
  if set(k for k in pr['attributes'] if k.startswith('TEXCOORD_'))!={'TEXCOORD_0'}:issues.append('Incorrect UV sets')
  tt=ps[ix].reshape(-1,3,3);ff=np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]);areas=np.linalg.norm(ff,axis=1)/2;degenerate+=int(np.sum(areas<1e-12));nn=ns[ix].reshape(-1,3,3).mean(axis=1);opposed+=int(np.sum(np.einsum('ij,ij->i',ff,nn)<-1e-10))
  uv=uu[ix].reshape(-1,3,2);a=uv[:,1]-uv[:,0];b=uv[:,2]-uv[:,0];uarea=np.abs(a[:,0]*b[:,1]-a[:,1]*b[:,0])/2;uv_zero_surface+=float(areas[uarea<1e-12].sum());positions.extend(ps);tris.extend(tt)
P=np.array(positions);TR=np.array(tris);manifest=json.loads((ROOT/'AST-ENG-003.manifest.json').read_text());lo=P.min(0);hi=P.max(0)
if np.max(abs(lo-manifest['min_gltf_yup_m']))>1e-6 or np.max(abs(hi-manifest['max_gltf_yup_m']))>1e-6:issues.append('Actual world bounds disagree with source mapping')
if degenerate:issues.append('Degenerate triangles')
if opposed:issues.append('Opposed face/vertex normals')
if uv_zero_surface>1e-9:issues.append('Collapsed UV area')
if triangle_count!=manifest['triangles']:issues.append('Triangle count mismatch')
# Point-to-triangle distance using all edge segments plus in-triangle projections.
def distance(point):
 p=np.array(point);a,b,c=TR[:,0],TR[:,1],TR[:,2];ab=b-a;ac=c-a;n=np.cross(ab,ac);nlen=np.linalg.norm(n,axis=1);good=nlen>1e-12;n=n[good]/nlen[good,None];a=a[good];b=b[good];c=c[good];signed=np.einsum('ij,ij->i',p-a,n);q=p-signed[:,None]*n
 inside=np.ones(len(a),dtype=bool)
 for u,v in [(a,b),(b,c),(c,a)]:inside&=np.einsum('ij,ij->i',np.cross(v-u,q-u),n)>=-1e-9
 ds=[np.min(np.abs(signed[inside])) if inside.any() else 1e9]
 for u,v in [(a,b),(b,c),(c,a)]:
  e=v-u;t=np.clip(np.einsum('ij,ij->i',p-u,e)/np.einsum('ij,ij->i',e,e),0,1);ds.append(np.min(np.linalg.norm(p-u-t[:,None]*e,axis=1)))
 return float(min(ds))
byname={n.get('name'):(i,n) for i,n in enumerate(j['nodes'])};checks=[]
for c in manifest['mounts']:
 i,n=byname[c['name']];actual=transform(i)[:3,3];correct=np.array(c['point_gltf_yup_m']);wrong=np.array(c['point_blender_source_m']);d=distance(correct)
 row={'name':c['name'],'kind':'physical_wall_pad_contact','actual_node_gltf_yup_m':actual.tolist(),'expected_gltf_yup_m':correct.tolist(),'node_error_m':float(np.linalg.norm(actual-correct)),'mesh_distance_m':d,'wrong_unconverted_point_node_error_m':float(np.linalg.norm(actual-wrong)),'passes':np.linalg.norm(actual-correct)<1e-7 and d<1e-6 and np.linalg.norm(actual-wrong)>.1};checks.append(row)
for c in manifest['controls']:
 i,n=byname[c['node']];actual=transform(i)[:3,3];correct=np.array(c['pivot_gltf_yup_m']);touch=c['interaction_gltf_yup_m'];d=distance(touch);extras=n['extras'];ap='press_axis' if c['kind']=='button' else 'rotation_axis';axis=extras[ap+'_gltf_yup'];expected=c['axis_gltf_yup'];wrong=c['axis_blender_source']
 row={'name':c['node'],'kind':c['kind'],'actual_pivot_gltf_yup_m':actual.tolist(),'expected_pivot_gltf_yup_m':correct.tolist(),'node_error_m':float(np.linalg.norm(actual-correct)),'interaction_mesh_distance_m':d,'actual_axis_extras_gltf_yup':axis,'correct_axis_error':float(np.linalg.norm(np.array(axis)-expected)),'wrong_unconverted_axis_error':float(np.linalg.norm(np.array(axis)-wrong)),'passes':np.linalg.norm(actual-correct)<1e-7 and d<1e-6 and np.linalg.norm(np.array(axis)-expected)<1e-7 and np.linalg.norm(np.array(axis)-wrong)>1};checks.append(row)
if not all(c['passes'] for c in checks):issues.append('Frame/contact/control checks failed')
textures=[]
for im in j['images']:
 bv=j['bufferViews'][im['bufferView']];src=CAT/'materials/staff'/(im['name']+'.png')
 if im['name']=='console_graphics':src=ROOT/'textures/console_graphics.png'
 h=hashlib.sha256(binary[bv.get('byteOffset',0):bv.get('byteOffset',0)+bv['byteLength']]).hexdigest();matches=src.exists() and hashlib.sha256(src.read_bytes()).hexdigest()==h;textures.append({'name':im['name'],'embedded_sha256':h,'matches_original':matches})
 if not matches:issues.append('Texture mismatch '+im['name'])
for m in j['materials']:
 if 'baseColorTexture' not in m.get('pbrMetallicRoughness',{}):issues.append('Missing texture '+m['name'])
 if m.get('emissiveFactor',[0,0,0])!=[0,0,0]:issues.append('Unexpected emission')
report={'status':'PASS' if not issues else 'FAIL','file':p.name,'sha256':hashlib.sha256(data).hexdigest(),'scope':'Actual binary GLB world geometry and node hierarchy; independent of Blender renderer','triangles':triangle_count,'mesh_count':len(j['meshes']),'primitive_count':sum(len(m['primitives']) for m in j['meshes']),'node_count':len(j['nodes']),'min_gltf_yup_m':lo.tolist(),'max_gltf_yup_m':hi.tolist(),'degenerate_triangles':degenerate,'opposed_normal_triangles':opposed,'collapsed_uv_surface_m2':uv_zero_surface,'textures':textures,'actual_node_hierarchy':node_rows,'mount_control_frame_checks':checks,'issues':issues}
(ROOT/'qa/glb_validation.json').write_text(json.dumps(report,indent=2,default=lambda v:v.item()));print(json.dumps({'status':report['status'],'triangles':triangle_count,'issues':issues,'frame_checks':checks},indent=2,default=lambda v:v.item()));assert not issues
