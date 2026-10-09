"""Independent GLB geometry/resource checks plus retained-input protection checks."""
import json,struct,math,hashlib,sys,itertools
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[1];sys.path.insert(0,str(R.parent/'AstraeaTools/pythondeps'))
import numpy as np
DT={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1',5122:'<i2',5120:'i1'};NC={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
def read_glb(p):
 b=p.read_bytes();assert b[:4]==b'glTF';assert struct.unpack_from('<I',b,8)[0]==len(b);pos=12;d=None;binary=None
 while pos<len(b):
  n,t=struct.unpack_from('<II',b,pos);chunk=b[pos+8:pos+8+n];pos+=8+n
  if t==0x4e4f534a:d=json.loads(chunk)
  elif t==0x004e4942:binary=chunk
 assert d and binary is not None
 def accessor(k):
  a=d['accessors'][k];v=d['bufferViews'][a['bufferView']];ty=np.dtype(DT[a['componentType']]);c=NC[a['type']];off=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',ty.itemsize*c)
  return np.ndarray((a['count'],c),dtype=ty,buffer=binary,offset=off,strides=(stride,ty.itemsize)).copy()
 def tr(n):
  if 'matrix' in n:return np.array(n['matrix']).reshape((4,4)).T
  x,y,z,w=n.get('rotation',[0,0,0,1]);q=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
  a=np.eye(4);a[:3,:3]=q@np.diag(n.get('scale',[1,1,1]));a[:3,3]=n.get('translation',[0,0,0]);return a
 rows=[]
 def walk(i,parent):
  n=d['nodes'][i];mat=parent@tr(n)
  if 'mesh' in n:
   v=[]
   for p in d['meshes'][n['mesh']]['primitives']:
    assert 'TEXCOORD_0' in p['attributes'],n.get('name')
    pts=accessor(p['attributes']['POSITION']);v.append((mat@np.concatenate([pts,np.ones((len(pts),1))],axis=1).T).T[:,:3])
   rows.append({'name':n.get('name'),'extras':n.get('extras',{}),'positions':np.concatenate(v)})
  for k in n.get('children',[]):walk(k,mat)
 for k in d['scenes'][d.get('scene',0)]['nodes']:walk(k,np.eye(4))
 return d,rows
if __name__=='__main__':
 source=json.loads((P/'qa/source_geometry.json').read_text());mapping=json.loads((P/'qa/export_batch_parts.json').read_text());out=[];covered=set();maxerr=0
 for filename in ['AQD_architecture.glb','AQD_floor_proposals.glb']:
  d,rows=read_glb(P/'exports'/filename)
  for a in rows:
   key=a['name'];names=a['extras'].get('source_parts_json') or mapping.get(key) or mapping.get(key.rsplit('.00',1)[0])
   if isinstance(names,str):names=json.loads(names)
   assert names,(filename,key,a['extras'])
   expected=np.concatenate([np.array(source[n]['world_vertices_xyz']) for n in names]);actual=a['positions'];assert np.all(np.isfinite(actual))
   # glTF UV/normal seams duplicate vertices; compare unique positions in both directions.
   def mismatch(v,w):
    w=np.unique(np.round(w,6),axis=0);v=np.unique(np.round(v,6),axis=0);keys={tuple(q) for q in np.round(w,3)};miss=[q for q in v if tuple(np.round(q,3)) not in keys];err=0
    for q in miss:err=max(err,float(np.min(np.linalg.norm(w-q,axis=1))))
    return err
   err=max(mismatch(actual,expected),mismatch(expected,actual));maxerr=max(maxerr,err);assert err<1e-4,(key,err)
   assert np.max(np.abs(actual.min(axis=0)-expected.min(axis=0)))<1e-4
   assert np.max(np.abs(actual.max(axis=0)-expected.max(axis=0)))<1e-4
   covered.update(names)
  assert not any('uri' in q for q in d.get('images',[])),'External texture dependency'
  out.append({'file':filename,'sha256':hashlib.sha256((P/'exports'/filename).read_bytes()).hexdigest(),'bytes':(P/'exports'/filename).stat().st_size,'mesh_nodes':len(rows),'triangles':sum(d['accessors'][q['indices']]['count']//3 for m in d['meshes'] for q in m['primitives']),'embedded_images':len(d.get('images',[])),'UVs_present':True})
 assert covered==set(source),(len(covered),len(source))
 baseline=json.loads((P/'qa/retained_input_hashes.json').read_text());changed=[n for n,h in baseline.items() if hashlib.sha256((R/n).read_bytes()).hexdigest()!=h]
 assert not changed,changed
 # Source/export world-fit and reservations, excluding the explicit old cascade interface.
 bad=[]
 for n,a in source.items():
  if 'cascade_' in n:continue
  if a['bounds_min'][1]<43.7599 or a['bounds_max'][1]>51.9501:bad.append(n)
 assert not bad,bad
 report={'passed':True,'source_meshes_covered':len(covered),'max_checked_vertex_position_error_m':maxerr,'embedded_resources_and_UVs':True,'exports':out,'retained_input_files_unchanged':len(baseline),'annex_vertical_bounds_pass':True,'scope':'Actual source/world-GLB geometry, embedded resources, vertical bounds and retained bytes. No runtime navigation, pressure/load, ride physics, broad-body or final-art acceptance.'}
 (P/'qa/source_export_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
 # Read actual retained runtime exports as source baseline; no import or mutation.
 retained={}
 for key,origin in [('AST-AQU-016',(0,0,0)),('AST-AQU-014',(8,44,210)),('AST-AQU-015',(21.5,61,207))]:
  q=R/'Game/assets/models'/(key+'.glb');d,rows=read_glb(q);v=np.concatenate([a['positions'] for a in rows])+np.array(origin);retained[key]={'path':str(q.relative_to(R)),'sha256':hashlib.sha256(q.read_bytes()).hexdigest(),'meshes':len(rows),'world_min':v.min(axis=0).tolist(),'world_max':v.max(axis=0).tolist(),'scope':'Actual binary GLB inspected; retained native evidence recorded separately.'}
 (P/'qa/retained_export_inspection.json').write_text(json.dumps(retained,indent=2))
