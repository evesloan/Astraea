"""Independent GLB binary/placement/floor checks, short construction gate only."""
from pathlib import Path
import json,struct,math,hashlib,sys,itertools
sys.path.insert(0,'C:/Users/cered/Dolphin/AstraeaTools/pythondeps')
import numpy as np
from shapely.geometry import Polygon,Point
P=Path(__file__).resolve().parents[1];PLAN=json.loads((P/'docs/PLACEMENT_AND_CONNECTORS.json').read_text());SOURCE=json.loads((P/'qa/source_geometry.json').read_text());stats=[];errors=[]
def glb(path):
 raw=path.read_bytes();magic,version,size=struct.unpack_from('<III',raw);assert magic==0x46546c67 and version==2 and size==len(raw),path
 n,k=struct.unpack_from('<II',raw,12);assert k==0x4e4f534a;d=json.loads(raw[20:20+n]);nb,kb=struct.unpack_from('<II',raw,20+n);assert kb==0x004e4942;binary=raw[28+n:28+n+nb];return d,binary
def accessor(d,b,idx):
 a=d['accessors'][idx];v=d['bufferViews'][a['bufferView']];types={5120:'i1',5121:'u1',5122:'<i2',5123:'<u2',5125:'<u4',5126:'<f4'};counts={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16};dtype=np.dtype(types[a['componentType']]);n=counts[a['type']];stride=v.get('byteStride',n*dtype.itemsize);offset=v.get('byteOffset',0)+a.get('byteOffset',0);assert offset+(a['count']-1)*stride+n*dtype.itemsize<=len(b)
 return np.ndarray((a['count'],n),dtype=dtype,buffer=b,offset=offset,strides=(stride,dtype.itemsize)).copy()
def matrix(n):
 if 'matrix' in n:return np.array(n['matrix']).reshape(4,4).T
 t=n.get('translation',[0,0,0]);s=n.get('scale',[1,1,1]);x,y,z,w=n.get('rotation',[0,0,0,1]);r=np.eye(4);r[:3,:3]=np.array([[1-2*y*y-2*z*z,2*x*y-2*z*w,2*x*z+2*y*w],[2*x*y+2*z*w,1-2*x*x-2*z*z,2*y*z-2*x*w],[2*x*z-2*y*w,2*y*z+2*x*w,1-2*x*x-2*y*y]])@np.diag(s);r[:3,3]=t;return r
def traverse(d):
 def visit(i,parent):
  n=d['nodes'][i];m=parent@matrix(n)
  if 'mesh' in n:yield n,m
  for j in n.get('children',[]):yield from visit(j,m)
 for i in d['scenes'][d.get('scene',0)]['nodes']:yield from visit(i,np.eye(4))
def match(a,b,tol=1e-4):
 cells={}
 for p in b:
  k=tuple(np.floor(p/.001).astype(int));cells.setdefault(k,[]).append(p)
 maximum=0
 for p in a:
  k=tuple(np.floor(p/.001).astype(int));candidates=[]
  for delta in itertools.product([-1,0,1],repeat=3):candidates.extend(cells.get(tuple(k[j]+delta[j] for j in range(3)),[]))
  assert candidates,'Missing vertex bucket'
  dist=float(np.sqrt(np.min(np.sum((np.array(candidates)-p)**2,axis=1))));maximum=max(maximum,dist);assert dist<tol,('Vertex error',dist,p)
 return maximum
policies={};all_bounds={};maxerror=0
for r in PLAN['rooms']+PLAN['chunks']:
 if r.get('retained'):continue
 for layer,path in r['exports'].items():
  try:
   d,b=glb(P/path);pts=[];area=0;triangles=0;mesh_nodes=0
   for node,m in traverse(d):
    mesh_nodes+=1;policies[node['name'].replace('.','_')]={'chunk_id':r['chunk_id'],'layer':layer,'collide':'shop_glass' not in node['name'],'opaque':'shop_glass' not in node['name'] and layer=='shell'}
    for p in d['meshes'][node['mesh']]['primitives']:
     pos=accessor(d,b,p['attributes']['POSITION']);pos=(np.c_[pos,np.ones(len(pos))]@m.T)[:,:3];assert np.isfinite(pos).all();pts.extend(pos.tolist());norm=accessor(d,b,p['attributes']['NORMAL']);assert np.isfinite(norm).all()
     mat=d['materials'][p['material']];tex=mat.get('pbrMetallicRoughness',{}).get('baseColorTexture')
     if tex:
      assert 'TEXCOORD_0' in p['attributes'];uv=accessor(d,b,p['attributes']['TEXCOORD_0']);assert np.isfinite(uv).all();image=d['images'][d['textures'][tex['index']]['source']];assert 'bufferView' in image and 'uri' not in image
     ind=accessor(d,b,p['indices']).ravel().astype(int);assert np.max(ind)<len(pos);assert len(ind)%3==0;tri=pos[ind].reshape(-1,3,3);triangles+=len(tri)
     if layer=='floor':
      top=tri[np.max(np.abs(tri[:,:,1]),axis=1)<1e-5]
      if len(top):
       aa=top[:,1][:,[0,2]]-top[:,0][:,[0,2]];bb=top[:,2][:,[0,2]]-top[:,0][:,[0,2]];area+=float(np.sum(np.abs(aa[:,0]*bb[:,1]-aa[:,1]*bb[:,0]))*.5)
   source=np.array([p for row in SOURCE[r['chunk_id']+'__'+layer] for p in row['vertices_xyz']]);actual=np.array(pts)
   err=max(match(actual,source),match(source,actual));maxerror=max(maxerror,err);all_bounds[r['chunk_id']+'__'+layer]={'min':actual.min(axis=0).tolist(),'max':actual.max(axis=0).tolist()}
   if layer=='floor':
    expected=sum(Polygon(f['boundary'],f.get('holes',[])).area for f in PLAN['floor_proposals'] if f['chunk_id']==r['chunk_id']);assert abs(area-expected)<.003,(r['chunk_id'],area,expected)
   assert mesh_nodes<=12,(r['chunk_id'],layer,mesh_nodes)
   stats.append({'path':path,'layer':layer,'runtime_meshes':mesh_nodes,'triangles':triangles,'max_position_error_m':err,'floor_area_m2':area if layer=='floor' else None,'sha256':hashlib.sha256((P/path).read_bytes()).hexdigest()})
  except Exception as e:errors.append({'path':path,'error':str(e)})
retained=json.loads((P/'qa/retained_input_hashes.json').read_text());host=P.parents[1];changed=[n for n,h in retained.items() if hashlib.sha256((host/n).read_bytes()).hexdigest()!=h]
aq=json.loads((P/'qa/aquatic_retention.json').read_text());aqhost=host/'external_packages/aquatic_district_20261009';aqchanged=[n for n,h in aq['files'].items() if hashlib.sha256((aqhost/n).read_bytes()).hexdigest()!=h]
floors=PLAN['floor_proposals'];floorid_unique=len({r['id'] for r in floors})==len(floors);contacts=json.loads((P/'qa/floor_contact_proposals.json').read_text());failedcontacts=[r for r in contacts if abs(r['bottom_height_m'])>1e-6]
output={'passed':not errors and not changed and not aqchanged and not failedcontacts and floorid_unique,'checked_glbs':len(stats),'maximum_checked_vertex_position_error_m':maxerror,'source_match':'Bidirectional literal transformed vertex positions;1e-4m tolerance; all chunks/layers checked','unique_floor_ids':floorid_unique,'grounded_source_foundations':len(contacts),'failed_foundations':failedcontacts,'retained_inputs_checked':len(retained),'retained_inputs_changed':changed,'aquatic_files_checked':len(aq['files']),'aquatic_changed':aqchanged,'floor_policy':'Additive polygon ownership; top triangle areas independently match the approved proposal boundaries with holes','errors':errors,'exports':stats,'limits':['Cloud consolidated main integration still required','Plan hull per-height section unresolved in retained source','No exhaustive routes, full species/cart ergonomics, gameplay or visual-quality acceptance']}
for name,data in [('qa/source_export_validation.json',output),('docs/RUNTIME_NODE_POLICY.json',policies),('docs/CHUNK_LOCAL_BOUNDS.json',all_bounds)]: (P/name).write_text(json.dumps(data,indent=2)+'\n')
print('EXPORT_CHECK',output['passed'],len(stats),maxerror,'errors',len(errors))
assert output['passed'],str(errors[:10])+str(changed)+str(aqchanged)+str(failedcontacts[:3])
