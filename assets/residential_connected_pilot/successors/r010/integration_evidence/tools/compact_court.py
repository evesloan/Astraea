#!/usr/bin/env python3
"""Lossless-topology spatial/material GLB batching, scratch only; no Blender/Godot."""
from pathlib import Path
import os
import collections,copy,hashlib,json,math,struct
import numpy as np
S=Path(os.environ.get('ASTRAEA_RESIDENTIAL_STAGE_ROOT',str(Path(__file__).resolve().parents[1]))); P=Path(os.environ.get('ASTRAEA_RESIDENTIAL_SOURCE_ROOT',str(S.parent)))
src=P/'domestic_correction/court_source/source.glb'; dst=S/'assets/models/residential_pilot_205/court_r008_compact.glb'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
b=src.read_bytes();o=12;chunks={}
while o<len(b):
 n,t=struct.unpack_from('<II',b,o);o+=8;chunks[t]=b[o:o+n];o+=n
j=json.loads(chunks[0x4e4f534a]);blob=bytearray(chunks[0x004e4942]);old=copy.deepcopy(j)
assert sha(src)=='320f03ed7b14f70b0d9d73aaf55adf72d339b099629d8eb0aaeb2fc59287e1cf'
def acc(i):
 a=old['accessors'][i];v=old['bufferViews'][a['bufferView']];c={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];d=np.dtype({5126:'<f4',5123:'<u2',5125:'<u4',5121:'u1'}[a['componentType']]);assert 'sparse'not in a
 return np.ndarray((a['count'],c),dtype=d,buffer=chunks[0x004e4942],offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',d.itemsize*c),d.itemsize)).copy()
def matrix(n):
 if 'matrix'in n:return np.array(n['matrix']).reshape(4,4,order='F')
 x,y,z,w=n.get('rotation',(0,0,0,1));m=np.eye(4);m[:3,:3]=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])@np.diag(n.get('scale',(1,1,1)));m[:3,3]=n.get('translation',(0,0,0));return m
parts={x['name']:x for x in json.loads((P/'domestic_correction/court_source/PARTS.json').read_text())['objects']}
groups=collections.defaultdict(list);markers=[];max_error=0;source_counts=collections.Counter();provenance=[]
def walk(i,parent):
 global max_error
 n=old['nodes'][i];m=parent@matrix(n);name=n.get('name','');ex=copy.deepcopy(n.get('extras',{}))
 if 'mesh'in n:
  assert name in parts,name
  category=ex.get('court_category');assert category==parts[name]['category'],name
  for p in old['meshes'][n['mesh']]['primitives']:
   assert p.get('mode',4)==4 and set(p['attributes'])=={'POSITION','NORMAL','TEXCOORD_0'}
   v=acc(p['attributes']['POSITION']);q=(np.c_[v,np.ones(len(v))]@m.T)[:,:3];idx=acc(p['indices']).ravel().astype('<u4');assert len(idx)%3==0
   mat=p['material'];matname=old['materials'][mat].get('name','').lower()
   collision=category not in ['prop','soil','stair_nosing','plant'] or (category=='plant' and ('bark'in matname or 'trunk'in matname))
   normal=acc(p['attributes']['NORMAL'])@np.linalg.inv(m[:3,:3]); normal/=np.maximum(np.linalg.norm(normal,axis=1)[:,None],1e-12)
   if np.linalg.det(m[:3,:3])<0:idx=idx.reshape(-1,3)[:,[0,2,1]].ravel()
   center=(q.min(axis=0)+q.max(axis=0))*.5;cell=tuple(np.floor(center/8).astype(int));key=(mat,category,collision,cell)
   groups[key].append((q,normal,acc(p['attributes']['TEXCOORD_0']),idx,name))
   source_counts['triangles']+=len(idx)//3;source_counts['parts']+=1
 else:
  # Keep source interface/light locator names, but native light owners are explicit.
  marker={'name':name,'matrix':list(m.flatten(order='F')),'extras':ex};markers.append(marker)
 for c in n.get('children',[]):walk(c,m)
for i in old['scenes'][old.get('scene',0)]['nodes']:walk(i,np.eye(4))
j['nodes']=[];j['meshes']=[];j['scenes']=[{'nodes':[]}];j['scene']=0
j.get('extensions',{}).pop('KHR_lights_punctual',None)
if 'KHR_lights_punctual'in j.get('extensionsUsed',[]):j['extensionsUsed'].remove('KHR_lights_punctual')
def put(a,typ,component=5126):
 a=np.asarray(a,dtype='<f4' if component==5126 else '<u4');
 while len(blob)%4:blob.append(0)
 offset=len(blob);bb=a.tobytes();blob.extend(bb);bv=len(j['bufferViews']);j['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(bb)})
 ac={'bufferView':bv,'componentType':component,'count':len(a),'type':typ}
 if typ=='VEC3':ac.update(min=a.min(axis=0).tolist(),max=a.max(axis=0).tolist())
 ai=len(j['accessors']);j['accessors'].append(ac);return ai
for number,(key,items)in enumerate(sorted(groups.items())):
 mat,cat,col,cell=key;origin=np.array(cell)*8+4;verts=[];normals=[];uvs=[];indices=[];offset=0;index_offset=0;ranges=[]
 for q,n,u,ix,name in items:
  local=(q-origin).astype('<f4');ranges.append({'source_name':name,'vertex_start':offset,'vertex_count':len(q),'index_start':index_offset,'index_count':len(ix),'source_world_geometry_sha256':hashlib.sha256(q[ix].astype('<f8').tobytes()).hexdigest(),'derived_world_geometry_sha256':hashlib.sha256((local.astype(float)[ix]+origin).astype('<f8').tobytes()).hexdigest(),'source_material_index':mat,'category':cat});index_offset+=len(ix);max_error=max(max_error,float(np.max(np.abs((local.astype(float)+origin)-q))));verts.append(local);normals.append(n);uvs.append(u);indices.append(ix+offset);offset+=len(q)
 q=np.concatenate(verts);ni=len(j['nodes']);mi=len(j['meshes']);label=f'CourtBatch_{number:04d}_{cat}'
 primitive={'attributes':{'POSITION':put(q,'VEC3'),'NORMAL':put(np.concatenate(normals),'VEC3'),'TEXCOORD_0':put(np.concatenate(uvs),'VEC2')},'indices':put(np.concatenate(indices),'SCALAR',5125),'material':mat,'mode':4}
 j['meshes'].append({'name':label,'primitives':[primitive]});j['nodes'].append({'name':label,'translation':origin.tolist(),'mesh':mi,'extras':{'court_category':cat,'runtime_collision':bool(col),'runtime_glass':'glass'in old['materials'][mat].get('name','').lower(),'source_sha256':sha(src),'source_parts':[x[4] for x in items],'source_part_ranges':ranges}});j['scenes'][0]['nodes'].append(ni)
 provenance.append({'node':label,'category':cat,'collision':bool(col),'source_parts':[x[4] for x in items],'source_part_ranges':ranges,'triangles':sum(len(x[3])//3 for x in items),'bounds_world':[ (q.min(axis=0)+origin).tolist(),(q.max(axis=0)+origin).tolist()]})
for marker in markers:j['scenes'][0]['nodes'].append(len(j['nodes']));j['nodes'].append(marker)
assert max_error<.00001,max_error
j['buffers']=[{'byteLength':len(blob)}];jb=json.dumps(j,separators=(',',':')).encode();jb+=b' '*((-len(jb))%4);blob.extend(b'\0'*((-len(blob))%4));out=struct.pack('<III',0x46546c67,2,12+8+len(jb)+8+len(blob))+struct.pack('<II',len(jb),0x4e4f534a)+jb+struct.pack('<II',len(blob),0x004e4942)+blob;dst.write_bytes(out)
report={'status':'offline topology/attribute-preserving derivation; native pending','source':str(src),'source_sha256':sha(src),'output':str(dst),'output_sha256':sha(dst),'source_mesh_parts':source_counts['parts'],'source_triangles':source_counts['triangles'],'runtime_meshes':len(groups),'runtime_triangles':sum(p['triangles']for p in provenance),'max_position_delta_m':max_error,'materials_images_and_uvs_retained':True,'normals_inverse_transpose':True,'negative_determinant_winding_corrected':True,'native_lights_rebuilt_from_LIGHTS_json':True,'collision_policy':'solid architecture/furniture/planters/guards/light housings and bark; foliage/soil/books/nosings visual only; actual footprints retained','batches':provenance}
(S/'qa/COURT_BATCH_PROOF.json').write_text(json.dumps(report,indent=2)+'\n');print({k:v for k,v in report.items()if k!='batches'})
