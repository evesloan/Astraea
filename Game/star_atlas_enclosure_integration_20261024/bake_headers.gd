extends SceneTree
const P:="res://star_atlas_enclosure_integration_20261024/"
func _initialize()->void:call_deferred("run")
func run()->void:
 var delta:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"HEADER_DELTA.json"))
 var original:Node3D=load("res://star_atlas_enclosure_20261022/runtime/StarAtlasEnclosure_r001.scn").instantiate()
 var rows:Array=[]
 for row in delta.parts:
  var prior:MeshInstance3D=original.find_child(row.name,true,false)
  if prior==null:push_error("Retained frieze absent");quit(1);return
  var tool:=SurfaceTool.new();tool.begin(Mesh.PRIMITIVE_TRIANGLES)
  for face in row.faces:
   for i in range(1,face.size()-1):
    var a:Array=row.verts[int(face[0])];var b:Array=row.verts[int(face[i+1])];var c:Array=row.verts[int(face[i])]
    var av:=Vector3(a[0],a[1],a[2]);var bv:=Vector3(b[0],b[1],b[2]);var cv:=Vector3(c[0],c[1],c[2]);tool.set_normal((bv-av).cross(cv-av).normalized())
    for index in [face[0],face[i+1],face[i]]:
     var v:Array=row.verts[int(index)];tool.add_vertex(Vector3(v[0],v[1],v[2]))
  tool.set_material(prior.get_active_material(0));var mesh:=tool.commit();var contact:=ConcavePolygonShape3D.new();contact.set_faces(mesh.get_faces())
  var old_contacts:Array=prior.find_children("*","CollisionShape3D",true,false)
  if old_contacts.size()!=1:push_error("Retained frieze contact interface differs");quit(1);return
  contact.margin=old_contacts[0].shape.margin
  var mesh_path:=P+"runtime/"+str(row.name)+".res";var shape_path:=P+"runtime/"+str(row.name)+"_contact.res"
  if FileAccess.file_exists(mesh_path)or FileAccess.file_exists(shape_path):push_error("Immutable delta resources exist");quit(1);return
  var e1:=ResourceSaver.save(mesh,mesh_path);var e2:=ResourceSaver.save(contact,shape_path)
  if e1!=OK or e2!=OK:push_error("Header delta save failed");quit(1);return
  rows.append({"name":row.name,"mesh":mesh_path,"mesh_sha256":FileAccess.get_sha256(mesh_path),"contact":shape_path,"contact_sha256":FileAccess.get_sha256(shape_path),"min_y":mesh.get_aabb().position.y,"original_triangle_count":prior.mesh.get_faces().size()/3,"new_triangle_count":mesh.get_faces().size()/3})
 var f:=FileAccess.open(P+"HEADER_RESOURCES.json",FileAccess.WRITE);f.store_string(JSON.stringify(rows,"  ")+"\n");f.close();print("HEADER_DELTA_SAVED ",rows.size());original.free();quit(0)
