extends SceneTree
var output:String
func _initialize()->void:
 for arg:String in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.substr(9)
 call_deferred("run")
func run()->void:
 var definition:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/received_sections.json"))
 var rows:Array=[]
 for section:Dictionary in definition.sections:
  var path:="res://assets/models/"+str(section.model_file)
  var packed:PackedScene=load(path);var visual:Node3D=packed.instantiate();root.add_child(visual)
  var row:Dictionary={"owner":section.programme_key,"source":path,"meshes":0,"accepted_triangles":0,"discarded_triangles":0,"accepted_area_m2":0.0,"discarded_area_m2":0.0}
  for part:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
   if not part.mesh is ArrayMesh or not part.visible:continue
   var size:=part.mesh.get_aabb().size
   if size.x*size.y+size.x*size.z+size.y*size.z<4:continue
   row.meshes+=1
   for s in part.mesh.get_surface_count():
    var mat:Material=part.get_active_material(s)
    if not mat is BaseMaterial3D or mat.transparency!=BaseMaterial3D.TRANSPARENCY_DISABLED or mat.albedo_color.a<.999:continue
    if part.mesh.surface_get_primitive_type(s)!=Mesh.PRIMITIVE_TRIANGLES:continue
    var a:Array=part.mesh.surface_get_arrays(s);var v:PackedVector3Array=a[Mesh.ARRAY_VERTEX];var ix:PackedInt32Array=a[Mesh.ARRAY_INDEX] if a[Mesh.ARRAY_INDEX]!=null else PackedInt32Array()
    var count:=ix.size() if not ix.is_empty() else v.size()
    for i in range(0,count-2,3):
     var x:Vector3=part.global_transform*v[ix[i] if not ix.is_empty() else i]
     var y:Vector3=part.global_transform*v[ix[i+1] if not ix.is_empty() else i+1]
     var z:Vector3=part.global_transform*v[ix[i+2] if not ix.is_empty() else i+2]
     var area:float=(y-x).cross(z-x).length()*.5
     if area>=2:row.accepted_triangles+=1;row.accepted_area_m2+=area
     elif area>0:row.discarded_triangles+=1;row.discarded_area_m2+=area
  rows.append(row);visual.free();packed=null
  await process_frame
 var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify({"scope":"Retained received-section source faces before later runtime receiving edits; lead only, not installed occluder coverage","rows":rows},"\t"));f.close();quit()
