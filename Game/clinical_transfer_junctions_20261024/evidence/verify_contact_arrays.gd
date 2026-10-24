extends SceneTree
func _initialize()->void:
 var rows:Array=JSON.parse_string(FileAccess.get_file_as_string("res://clinical_transfer_junctions_20261024/evidence/WALL_SUCCESSORS.json"));var total:=0;var failures:Array=[];var quantized_zero:=0
 for row:Dictionary in rows:
  var mesh:=ArrayMesh.new()
  for surface:Dictionary in row.surfaces:
   var points:=PackedVector3Array();var ids:=PackedInt32Array()
   for p:Array in surface.positions:points.append(Vector3(p[0],p[1],p[2]))
   for i:int in surface.indices:ids.append(i)
   var arrays:Array=[];arrays.resize(Mesh.ARRAY_MAX);arrays[Mesh.ARRAY_VERTEX]=points
   if not ids.is_empty():arrays[Mesh.ARRAY_INDEX]=ids
   mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arrays)
  if mesh.get_surface_count()==0:continue
  var shape:ConcavePolygonShape3D=load("res://clinical_transfer_junctions_20261024/adapter.gd").exact_contact(mesh);var actual:PackedVector3Array=shape.get_faces()
  for i in range(0,actual.size(),3):
   if (actual[i+1]-actual[i]).cross(actual[i+2]-actual[i]).length_squared()==0.0:failures.append(row.name)
  var snapped:PackedVector3Array=mesh.get_faces()
  for i in range(0,snapped.size(),3):
   if (snapped[i+1]-snapped[i]).cross(snapped[i+2]-snapped[i]).length_squared()==0.0:quantized_zero+=1
  total+=actual.size()/3
 var result:={"status":"PASS"if failures.is_empty()else"FAIL","source":"Actual installed WALL_SUCCESSORS captured at attempt006","owners":rows.size(),"exact_triangles":total,"exact_zero_area_failures":failures,"mesh_get_faces_snapped_zero_area_triangles":quantized_zero,"primary_source":"https://raw.githubusercontent.com/godotengine/godot/4.6.3-stable/core/math/triangle_mesh.cpp","scope":"Replay of captured production arrays to verify exact contact construction, not a new demonstration scene or ship acceptance"}
 FileAccess.open("res://clinical_transfer_junctions_20261024/evidence/CONTACT_ARRAY_PROOF.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  ")+"\n");print(JSON.stringify(result));quit(0 if failures.is_empty()else 1)
