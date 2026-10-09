#!/usr/bin/env python3
"""Independent GLB triangle/bounds/contact and native Blender checks.
Run with system Python for GLB checks, or Blender --background --python this_file.py
for the native mesh checks (then run system Python to merge the receipts).
No game import, code changes, or external dependency downloads.
"""
import json, struct, math, hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parent
try:
 import bpy
except ImportError:
 bpy=None
if bpy:
 import bmesh
 bpy.ops.wm.open_mainfile(filepath=str(OUT/'AST-RST-QC-001.blend'))
 errors=[]; rows=[]
 for ob in bpy.data.objects:
  if ob.type!='MESH' or ob.get('asset_id')!='AST-RST-QC-001':continue
  bm=bmesh.new();bm.from_mesh(ob.data)
  manifold=sum(not e.is_manifold for e in bm.edges)
  degenerate=sum(f.calc_area()<1e-10 for f in bm.faces)
  volume=bm.calc_volume(signed=True)
  if manifold or degenerate or volume<=0:errors.append(ob.name)
  rows.append({'name':ob.name,'non_manifold_edges':manifold,'degenerate_faces':degenerate,'signed_volume_m3':volume})
  bm.free()
 receipt={'scope':'Native editable fixture meshes only','all_meshes_editable':True,'mesh_objects':len(rows),'non_manifold_objects':len(errors),'objects_with_errors':errors,'results':rows,'pass':not errors}
 (OUT/'native_mesh_validation.json').write_text(json.dumps(receipt,indent=2)+'\n')
 assert not errors,errors
 print('NATIVE_MESH_VALIDATION_PASS',len(rows))
else:
 import numpy as np
 raw=(OUT/'AST-RST-QC-001.glb').read_bytes();magic,ver,length=struct.unpack_from('<III',raw,0)
 assert magic==0x46546c67 and ver==2 and length==len(raw)
 chunks=[];offset=12
 while offset<len(raw):
  n,t=struct.unpack_from('<II',raw,offset);chunks.append((t,raw[offset+8:offset+8+n]));offset+=8+n
 doc=json.loads(next(x for t,x in chunks if t==0x4e4f534a));buf=next(x for t,x in chunks if t==0x004e4942)
 components={5120:('b',1),5121:('B',1),5122:('h',2),5123:('H',2),5125:('I',4),5126:('f',4)}
 counts={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
 def accessor(idx):
  a=doc['accessors'][idx];bv=doc['bufferViews'][a['bufferView']];fmt,size=components[a['componentType']];n=counts[a['type']]
  stride=bv.get('byteStride',size*n);o=bv.get('byteOffset',0)+a.get('byteOffset',0)
  return np.array([struct.unpack_from('<'+fmt*n,buf,o+i*stride) for i in range(a['count'])])
 def transform(n):
  if 'matrix'in n:return np.array(n['matrix']).reshape(4,4).T
  x,y,z,w=n.get('rotation',[0,0,0,1]);r=np.array([[1-2*y*y-2*z*z,2*x*y-2*z*w,2*x*z+2*y*w],[2*x*y+2*z*w,1-2*x*x-2*z*z,2*y*z-2*x*w],[2*x*z-2*y*w,2*y*z+2*x*w,1-2*x*x-2*y*y]])
  m=np.eye(4);m[:3,:3]=r@np.diag(n.get('scale',[1,1,1]));m[:3,3]=n.get('translation',[0,0,0]);return m
 meshes=[];markers={}
 def visit(i,parent):
  node=doc['nodes'][i];mat=parent@transform(node)
  if 'mesh'in node:
   for p in doc['meshes'][node['mesh']]['primitives']:
    pos=accessor(p['attributes']['POSITION']);v=(mat@np.c_[pos,np.ones(len(pos))].T).T[:,:3]
    ind=accessor(p['indices']).reshape(-1,3);meshes.append((node.get('name'),v,ind))
  elif node.get('extras',{}).get('datum_kind'):
   markers[node['name']]=mat[:3,3]
  for child in node.get('children',[]):visit(child,mat)
 for i in doc['scenes'][doc.get('scene',0)]['nodes']:visit(i,np.eye(4))
 allv=np.concatenate([v for _,v,_ in meshes]);lo=allv.min(axis=0);hi=allv.max(axis=0)
 meta=json.loads((OUT/'component_metadata.json').read_text());assert np.allclose(lo,meta['bounds_gltf']['min'],atol=2e-6);assert np.allclose(hi,meta['bounds_gltf']['max'],atol=2e-6)
 assert np.all(hi-lo<=np.array([2.4,2.4,3.2])+1e-6)
 def triangle_aabb(t,low,high):
  c=(low+high)/2;half=(high-low)/2;t=t-c
  es=[t[1]-t[0],t[2]-t[1],t[0]-t[2]]
  axes=[np.eye(3)[i] for i in range(3)]+[np.cross(es[0],es[1])]+[np.cross(e,np.eye(3)[i]) for e in es for i in range(3)]
  for axis in axes:
   if np.linalg.norm(axis)<1e-10:continue
   proj=t@axis;r=half@np.abs(axis)
   if proj.max() < -r-1e-7 or proj.min() > r+1e-7:return False
  return True
 def clearance(low,high):
  low=np.array(low);high=np.array(high);hits=[];tested=0
  for name,v,idx in meshes:
   if np.any(v.max(axis=0)<low) or np.any(v.min(axis=0)>high):continue
   for ti in idx:
    t=v[ti];tested+=1
    if triangle_aabb(t,low,high):hits.append(name);break
  return {'min':low.tolist(),'max':high.tolist(),'intersections':hits,'broadphase_candidate_triangles':tested,'pass':not hits}
 ext=clearance([-.7,.005,-2.54],[.7,2.05,-1.50]);inside=clearance([-.67,.045,-1.50],[.67,1.9,-1.27]);assert ext['pass'] and inside['pass'],[ext,inside]
 # Actual triangle interpolation at each contact: choose uppermost membrane hit at X/Z.
 def surface_y(x,z):
  heights=[]
  for name,v,idx in meshes:
   if name!='Concave stretched rest membrane':continue
   for indices in idx:
    t=v[indices];p=t[:,[0,2]];a,b,c=p
    M=np.column_stack((b-a,c-a))
    if abs(np.linalg.det(M))<1e-10:continue
    u,w=np.linalg.solve(M,np.array([x,z])-a)
    if u>=-1e-7 and w>=-1e-7 and u+w<=1+1e-7:heights.append(float(t[0,1]+u*(t[1,1]-t[0,1])+w*(t[2,1]-t[0,1])))
  assert heights,(x,z)
  return max(heights)
 contacts=[]
 for record in meta['support']['sample_contacts']:
  name=record['name'];pos=np.array(record['position']);assert np.allclose(markers[name],pos,atol=2e-6)
  actual=surface_y(pos[0],pos[2]);err=abs(actual-pos[1]);assert err<.003
  contacts.append({'marker':name,'world_gltf':markers[name].tolist(),'actual_support_y_m':actual,'vertical_contact_error_m':err,'pass':True})
 assert not doc.get('cameras') and 'KHR_lights_punctual' not in doc.get('extensions',{})
 assert not any('Preview' in n.get('name','') for n in doc['nodes'])
 native=json.loads((OUT/'native_mesh_validation.json').read_text()) if (OUT/'native_mesh_validation.json').exists() else {'pass':False,'not_run':True}
 report={'scope':'Bounded native/GLB component geometry only','asset_id':meta['asset_id'],'glb_bytes':len(raw),'bounds_actual_gltf':{'min':lo.tolist(),'max':hi.tolist(),'size':(hi-lo).tolist()},'triangles_actual':sum(len(i) for _,_,i in meshes),'mesh_primitives':len(meshes),'support_contact_probes':contacts,'external_approach':ext,'internal_front_approach':inside,'native_mesh_pass':native['pass'],'no_preview_nodes_lights_cameras_exported':True,'validation_limits':meta['validation_limits'],'pass':native['pass'] and ext['pass'] and inside['pass']}
 (OUT/'validation_report.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
