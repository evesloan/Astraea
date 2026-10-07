from pathlib import Path
import json,struct,hashlib,math
import numpy as np
R=Path(__file__).resolve().parents[1];C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');manifest=json.loads((R/'qa/SOURCE_MANIFEST_008.json').read_text());pins=json.loads((R/'qa/INPUT_PINS.json').read_text())
def glb(path):
 raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);start=20+n;size,typ=struct.unpack_from('<II',raw,start);assert typ==0x004e4942;binary=raw[start+8:start+8+size]
 def access(i):
  a=d['accessors'][i];v=d['bufferViews'][a['bufferView']];assert a['componentType']==5126 and a['type']=='VEC3';off=v.get('byteOffset',0)+a.get('byteOffset',0);step=v.get('byteStride',12);return np.array([struct.unpack_from('<fff',binary,off+j*step)for j in range(a['count'])])
 def matrix(node):
  if 'matrix'in node:return np.array(node['matrix']).reshape((4,4),order='F')
  x,y,z,w=node.get('rotation',[0,0,0,1]);m=np.eye(4);m[:3,:3]=np.array([[1-2*y*y-2*z*z,2*x*y-2*z*w,2*x*z+2*y*w],[2*x*y+2*z*w,1-2*x*x-2*z*z,2*y*z-2*x*w],[2*x*z-2*y*w,2*y*z+2*x*w,1-2*x*x-2*y*y]])@np.diag(node.get('scale',[1,1,1]));m[:3,3]=node.get('translation',[0,0,0]);return m
 found={}
 def visit(i,parent):
  node=d['nodes'][i];m=parent@matrix(node)
  if 'mesh'in node:
   pts=np.concatenate([access(p['attributes']['POSITION'])for p in d['meshes'][node['mesh']]['primitives']]);pts=np.c_[pts,np.ones(len(pts))]@m.T;found[node['name']]=np.c_[pts[:,0],-pts[:,2],pts[:,1]]
  for child in node.get('children',[]):visit(child,m)
 for i in d['scenes'][d.get('scene',0)]['nodes']:visit(i,np.eye(4))
 return found
arch=glb(Path(manifest['architecture_export']));sources={};rows=[]
for item in manifest['planting_instances']:
 id_=item['id'];row=pins['retained_assets'][id_];path=C/row['export'];assert hashlib.sha256(path.read_bytes()).hexdigest()==row['export_sha256']
 if id_ not in sources:sources[id_]=np.concatenate(list(glb(path).values()))
 v=sources[id_];root=v[np.abs(v[:,2])<1e-6];assert len(root)>=3
 t=np.array(item['translation_source_xyz']);a=item['yaw_source_z_radians'];rot=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);root=root@rot.T+t;whole=v@rot.T+t;soil=arch[item['soil_receiver']];lo=soil.min(axis=0);hi=soil.max(axis=0)
 assert np.all(root[:,:2]>=lo[:2]-1e-5)and np.all(root[:,:2]<=hi[:2]+1e-5),(item['instance'],'root footprint outside actual soil',root.min(axis=0),root.max(axis=0),lo,hi)
 assert np.max(np.abs(root[:,2]-hi[2]))<1e-5,(item['instance'],'root/soil height mismatch')
 rows.append({'instance':item['instance'],'catalogue_id':id_,'root_contact_vertices':len(root),'actual_soil_node':item['soil_receiver'],'soil_top':float(hi[2]),'root_height_error_m':float(np.max(np.abs(root[:,2]-hi[2]))),'bounds_source_xyz':[whole.min(axis=0).tolist(),whole.max(axis=0).tolist()]})
out={'status':'ALL_RETAINED_PLANT_ROOTS_SUPPORTED','source_sha256':manifest['source_sha256'],'architecture_export_sha256':manifest['export_sha256'],'instances':len(rows),'root_contact_vertices':sum(r['root_contact_vertices']for r in rows),'rows':rows,'scope':'Pinned native component root footprints versus actual exported soil receiver geometry; no runtime robot or clinical fit claim.'};(R/'qa/PLANT_RECEIVERS_008.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k!='rows'}))
