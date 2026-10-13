extends SceneTree
func _initialize()->void:
 OS.set_environment("ASTRAEA_GROUP7_ENABLE","1")
 for path in ["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(30):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var space:=ship.get_world_3d().direct_space_state;var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/astraea-integration-cutoff-20261013/g2_last_three_pairs_20261013/CENTRAL_LOWER_SUPPORT_AND_ROUTE_PLAN.json"));var rows:Array=[]
 for part in p.parts:
  var a:Array=part.bounds;var q:=PhysicsShapeQueryParameters3D.new();var shape:=BoxShape3D.new();shape.size=Vector3(a[1]-a[0],a[3]-a[2],a[5]-a[4]);shape.margin=.001;q.shape=shape;q.margin=.0001;q.transform=Transform3D(Basis.IDENTITY,Vector3((a[0]+a[1])/2.,(a[2]+a[3])/2.,(a[4]+a[5])/2.));var contacts:Array=[]
  for h in space.intersect_shape(q,128):
   var mesh:MeshInstance3D=h.collider.get_parent()as MeshInstance3D;contacts.append({"path":str(h.collider.get_path()),"mesh":str(mesh.name)if mesh!=null else"OTHER","declared":str(mesh.name)in part.allowed if mesh!=null else false})
  rows.append({"part":part,"contacts":contacts})
 FileAccess.open("/workspace/astraea-integration-cutoff-20261013/g2_last_three_pairs_20261013/CENTRAL_LOWER_CLEARANCE_SURVEY.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_COMPLETE_CHANGED_CENTRAL_SUPPORT_CLEARANCE_SURVEY","base":p.base,"rows":rows,"new_geometry_adopted":false},"  "));print("CENTRAL_LOWER_CLEARANCE_SURVEY_PASS");quit(0)
