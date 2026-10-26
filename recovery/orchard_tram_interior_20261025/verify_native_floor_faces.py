"""Verify native floor face orientation; save corrections in a new source only."""
from pathlib import Path
import bpy,bmesh,json,hashlib
import numpy as np
R=Path(__file__).resolve().parents[2];D=R/'Game/orchard_tram_interior_20261025/integration'
source=R/'BlenderCatalogue/assets/orchard_tram_interior_20261025/integration/OrchardIntegratedReceiving.blend'
out=source.with_name('OrchardIntegratedReceiving_r002.blend');assert not out.exists()
source_sha=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source))
proof=json.loads((D/'PIT_AND_BINDING.json').read_text());rows=[]
for region in [proof['after'],proof['old_pit_infill']]:
 o=bpy.data.objects[region['id']];before=[tuple(v.co) for v in o.data.vertices]
 triangles=np.array(region['triangles'],float)
 def inside(p):
  a=triangles[:,0];b=triangles[:,1];c=triangles[:,2]
  def cross(x,y):return x[:,0]*y[:,1]-x[:,1]*y[:,0]
  u=cross(b-a,p-a);v=cross(c-b,p-b);w=cross(a-c,p-c)
  return bool(np.any(((u>=-1e-8)&(v>=-1e-8)&(w>=-1e-8))|((u<=1e-8)&(v<=1e-8)&(w<=1e-8))))
 bm=bmesh.new();bm.from_mesh(o.data);bm.normal_update();flip=[]
 for face in bm.faces:
  center=face.calc_center_median();normal=face.normal
  if all(abs(v.co.z-region['floor_y'])<1e-5 for v in face.verts):
   if normal.z<0:flip.append(face)
  elif all(abs(v.co.z-(region['floor_y']-region['thickness']))<1e-5 for v in face.verts):
   if normal.z>0:flip.append(face)
  else:
   point=np.array([center.x,-center.y]);n=np.array([normal.x,-normal.y])
   if inside(point+n*.001) and not inside(point-n*.001):flip.append(face)
 bmesh.ops.reverse_faces(bm,faces=flip);bm.to_mesh(o.data);bm.free();o.data.update()
 assert before==[tuple(v.co) for v in o.data.vertices]
 rows.append({'region':region['id'],'faces_reoriented':len(flip),'vertex_positions_unchanged':True})
bpy.ops.wm.save_as_mainfile(filepath=str(out))
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_sha
receipt={'source_sha256':source_sha,'output':out.relative_to(R).as_posix(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bytes':out.stat().st_size,'regions':rows,'runtime_geometry_unchanged':True}
(D/'NATIVE_FACE_RECEIPT.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode());print(json.dumps(receipt))
