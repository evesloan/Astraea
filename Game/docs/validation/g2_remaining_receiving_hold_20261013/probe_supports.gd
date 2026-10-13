extends SceneTree
func _initialize()->void:
 for path in ["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func ray(space:PhysicsDirectSpaceState3D,a:Vector3,b:Vector3)->Dictionary:
 return space.intersect_ray(PhysicsRayQueryParameters3D.create(a,b))
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(30):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var space:=ship.get_world_3d().direct_space_state
 var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/astraea-integration-cutoff-20261013/g2_remaining_receiving/ADJUNCT_RECEIVING_INPUTS.json"));var rows:Array=[]
 for row in data.rows:
  var samples:Array=[]
  for f in row.floor_rows:
   for t in f.triangles:
    var at:=Vector3((t[0][0]+t[1][0]+t[2][0])/3.,f.floor_y,(t[0][1]+t[1][1]+t[2][1])/3.);var h:=ray(space,at+Vector3.UP*.02,at-Vector3.UP*.3)
    samples.append({"at":[at.x,at.y,at.z],"floor_present":not h.is_empty(),"source":str(h.collider.get_path())if not h.is_empty()else""})
  rows.append({"key":row.key,"floor_samples":samples})
 var receiver:Array=[]
 for at:Vector3 in [Vector3(80,102,-13.99),Vector3(84,102,-13.99),Vector3(88,102,-13.99),Vector3(-80,102,-13.99),Vector3(-84,102,-13.99),Vector3(-88,102,-13.99)]:
  var h:=ray(space,at+Vector3.UP*.1,at-Vector3.UP*.3);receiver.append({"at":[at.x,at.y,at.z],"floor_present":not h.is_empty(),"source":str(h.collider.get_path())if not h.is_empty()else""})
 FileAccess.open("/workspace/astraea-integration-cutoff-20261013/g2_remaining_receiving/CURRENT_SUPPORT_SURVEY.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"CURRENT_SOURCE_SUPPORT_SURVEY_COMPLETE","baseline":data.baseline,"adjuncts":rows,"central_receivers":receiver,"no_geometry_or_operational_state_adopted":true},"  "));print("G2_CURRENT_SUPPORT_SURVEY_COMPLETE");quit(0)
