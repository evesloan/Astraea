"""Prepared Court-only adaptation of retained source-corner normal repack.
No engines. New output only; no position, UV, material, image or node edits.
"""
from pathlib import Path
import argparse,json,struct,hashlib,copy,shutil,sys
import numpy as np
sys.dont_write_bytecode=True

def repack():
 R=Path(__file__).resolve().parent;I=R/'raw_export001';O=R/'packed_export001';assert not O.exists();O.mkdir()
 sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();receipt=json.loads((I/'EXPORT_RECEIPT.json').read_text());assert sha(I/'source_triangle_attributes.npz')==receipt['source_attribute_archive_sha256'];arrays=np.load(I/'source_triangle_attributes.npz')
 records=[]
 for item in receipt['export_records']:
  path=Path(item['path']);assert sha(path)==item['sha256'];raw=path.read_bytes();off=12;chunks={}
  while off<len(raw):
   length,kind=struct.unpack_from('<II',raw,off);chunks[kind]=raw[off+8:off+8+length];off+=8+length
  doc=json.loads(chunks[0x4e4f534a]);original_doc=copy.deepcopy(doc);binary=bytearray(chunks[0x004e4942]);nodes={};mesh_uses={}
  def walk(index,parent):
   node=doc['nodes'][index]
   if 'matrix'in node:matrix=np.array(node['matrix']).reshape(4,4).T
   else:
    x,y,z,w=node.get('rotation',[0,0,0,1]);rot=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
    matrix=np.eye(4);matrix[:3,:3]=rot@np.diag(node.get('scale',[1,1,1]));matrix[:3,3]=node.get('translation',[0,0,0])
   matrix=parent@matrix
   if 'mesh'in node:
    assert node['mesh']not in mesh_uses;mesh_uses[node['mesh']]=(node['name'],matrix)
   for c in node.get('children',[]):walk(c,matrix)
  for n in doc['scenes'][doc.get('scene',0)]['nodes']:walk(n,np.eye(4))
  types={5120:'i1',5121:'u1',5122:'<i2',5123:'<u2',5125:'<u4',5126:'<f4'};counts={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
  def read_accessor(i):
   a=doc['accessors'][i];assert 'sparse'not in a;v=doc['bufferViews'][a['bufferView']];dtype=types[a['componentType']];width=counts[a['type']];size=np.dtype(dtype).itemsize
   return np.ndarray((a['count'],width),dtype=dtype,buffer=binary,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',size*width),size)).copy()
  def append_accessor(values,template,target,position=False):
   while len(binary)%4:binary.append(0)
   data=values.astype(types[template['componentType']]).tobytes();view=len(doc['bufferViews']);doc['bufferViews'].append({'buffer':0,'byteOffset':len(binary),'byteLength':len(data),'target':target});binary.extend(data)
   a={k:copy.deepcopy(v)for k,v in template.items()if k not in ['bufferView','byteOffset','min','max','count']};a.update(bufferView=view,count=len(values))
   if position:a.update(min=values.min(axis=0).tolist(),max=values.max(axis=0).tolist())
   i=len(doc['accessors']);doc['accessors'].append(a);return i
  replaced=0
  for mesh_index,(name,matrix)in mesh_uses.items():
   mesh=doc['meshes'][mesh_index];assert len(mesh['primitives'])==1;prim=mesh['primitives'][0];assert prim.get('mode',4)==4
   indices=read_accessor(prim['indices']).reshape(-1).astype(int);source_normal=arrays[name+'_normal'].reshape(-1,3);assert len(source_normal)==len(indices)
   local_normal=source_normal@matrix[:3,:3];local_normal/=np.linalg.norm(local_normal,axis=1)[:,None]
   oldattrs=dict(prim['attributes']);expanded={a:read_accessor(i)[indices]for a,i in oldattrs.items()}
   # Exact positions/order must already match source. This correction has no
   # authority to move vertices, change UVs, omit attributes, or edit materials.
   world=(np.c_[expanded['POSITION'],np.ones(len(indices))]@matrix.T)[:,:3]
   if item['kind']=='authored':world+=np.array(receipt['court_origin_native'])
   assert np.max(abs(world-arrays[name+'_xyz'].reshape(-1,3)))<=1e-4
   for attr,old_index in oldattrs.items():
    value=local_normal if attr=='NORMAL' else expanded[attr];prim['attributes'][attr]=append_accessor(value,doc['accessors'][old_index],34962,attr=='POSITION')
   seq=np.arange(len(indices),dtype=np.uint32).reshape(-1,1);prim['indices']=append_accessor(seq,{'componentType':5125,'type':'SCALAR'},34963);replaced+=len(indices)
  assert doc['materials']==original_doc['materials'] and doc['images']==original_doc['images'] and doc['nodes']==original_doc['nodes']
  doc['buffers'][0]['byteLength']=len(binary)
  encoded=json.dumps(doc,separators=(',',':'),ensure_ascii=False).encode();encoded+=b' '*((-len(encoded))%4);binary+=b'\0'*((-len(binary))%4);result=struct.pack('<III',0x46546c67,2,12+8+len(encoded)+8+len(binary))+struct.pack('<II',len(encoded),0x4e4f534a)+encoded+struct.pack('<II',len(binary),0x004e4942)+binary
  out=O/path.name;out.write_bytes(result);records.append({'kind':item['kind'],'input_sha256':item['sha256'],'output_sha256':sha(out),'repacked_source_corners':replaced,'all_other_attributes_preserved':True});item.update(path=str(out),sha256=sha(out))
 shutil.copyfile(I/'source_triangle_attributes.npz',O/'source_triangle_attributes.npz');assert sha(O/'source_triangle_attributes.npz')==receipt['source_attribute_archive_sha256'];receipt['source_normal_packing_correction']={'cause_report':'Retained firstpass_003/NORMAL_STORAGE_DIAGNOSIS.json; corner storage quantization, not permission to change geometry','method':'Direct float32 native corner normals; expanded vertices preserve distinct source loops; positions/UVs/other attributes/materials/nodes unchanged','input_receipt_sha256':sha(I/'EXPORT_RECEIPT.json'),'script_sha256':sha(Path(__file__)),'results':records};receipt['status']='REPACKED_COURT_EXPORT_INDEPENDENT_QA_PENDING';(O/'EXPORT_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(records,indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--repack',action='store_true');a=p.parse_args()
 if a.repack:repack()
 else:print('PREPARED_NOT_RUN: requires successful raw_export001 and an explicit --repack; writes new packed_export001 only')
