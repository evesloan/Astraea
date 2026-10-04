"""Bake a matching left end for the existing collection profile, retaining editable source."""
from pathlib import Path
import bpy,hashlib,json
r=Path(__file__).resolve().parents[1]/'assets/library_structure'
bpy.ops.wm.open_mainfile(filepath=str(r/'source/AST-LIB-STR-003.blend'))
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  for v in o.data.vertices:v.co.x=-v.co.x
  # Reflection reverses winding; recalculate outward normals once in authoring.
  import bmesh
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
  o.location.x=-o.location.x
  o.name='Start_'+o.name
source=r/'source/AST-LIB-STR-003_start.blend';export=r/'exports/AST-LIB-STR-003_start.glb'
bpy.ops.wm.save_as_mainfile(filepath=str(source))
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_apply=True,export_yup=True)
(r/'AST-LIB-STR-003_start.manifest.json').write_text(json.dumps({'parent_design_id':'AST-LIB-STR-003','representation':'start_cap','new_unique_design_count':0,'source':str(source.relative_to(r)),'export':str(export.relative_to(r)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'status':'Baked opposite end, no negative runtime transform. Source/export and assembled seam validation pending.'},indent=2)+'\n')
