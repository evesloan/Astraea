extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/d04_starboard_forward_remaining_courts_20261011/PLAN.json"))
 var doc:=GLTFDocument.new();var state:=GLTFState.new();assert(doc.append_from_file("res://assets/models/D04_STARBOARD_SOUTH_COURTSANDTRANSFER_r001.glb",state,8)==OK);var fresh:Node3D=doc.generate_scene(state);root.add_child(fresh);var faces:Dictionary={}
 for row in p.moves:
  var mesh:MeshInstance3D=fresh.find_child(row.name,true,false);var vs:Array=[]
  for at in mesh.mesh.get_faces():var q:Vector3=mesh.global_transform*at;vs.append([q.x,q.y,q.z])
  faces[row.name]=vs
 FileAccess.open("/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/d04_starboard_forward_remaining_courts_20261011/FRESH_IMPORT_FACES001.json",FileAccess.WRITE).store_string(JSON.stringify({"selected_flags":8,"source_sha256":FileAccess.get_sha256("res://assets/models/D04_STARBOARD_SOUTH_COURTSANDTRANSFER_r001.glb"),"faces":faces},"  "));print("Fresh unchanged source import triangles retained");quit()
