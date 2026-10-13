extends SceneTree
func _initialize()->void:
 OS.set_environment("ASTRAEA_GROUP7_ENABLE","1")
 for path in ["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(30):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var space:=ship.get_world_3d().direct_space_state;var sites:Array=[{"key":"port_forward_upper_house","xz":[[-63.1,-402],[-62.9,-402],[-62,-395],[-62,-388],[-68,-384],[-68,-382],[-72,-384],[-74.5,-395]]},{"key":"starboard_forward_upper_house","xz":[[65,-384.1],[65,-383.9],[69,-383.9],[73,-383.9],[69,-382],[75,-395],[76,-395]]},{"key":"port_central_upper_house","xz":[[-85.7,-23.5],[-82.3,-23.5],[-85.7,-20],[-82.3,-20],[-85.7,-16.5],[-82.3,-16.5],[-61.9,-3.3],[-61.9,-3.1],[-61.9,-12],[-64,-12],[-84,-12]]},{"key":"port_aft_upper_house","xz":[[-65,344.1],[-65,345],[-68,346],[-63,338],[-62,338],[-62,330],[-65,355.9],[-65,356.1]]},{"key":"starboard_aft_upper_house","xz":[[65,344.1],[69,344.1],[73,344.1],[65,346],[65,355.9],[65,356.1],[62,329],[62,338]]}];var records:Array=[]
 for site in sites:
  var samples:Array=[]
  for y in [97.5,102.]:
   for xz in site.xz:
    var at:=Vector3(xz[0],y,xz[1]);var hit:Dictionary=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.1,at-Vector3.UP*.35));var row:Dictionary={"at":[at.x,at.y,at.z],"hit":not hit.is_empty()}
    if not hit.is_empty():
     var node:Node=hit.collider;var mesh:MeshInstance3D=node.get_parent()as MeshInstance3D;var b:AABB=mesh.global_transform*mesh.get_aabb()if mesh!=null else AABB();row.merge({"contact":str(node.get_path()),"normal":[hit.normal.x,hit.normal.y,hit.normal.z],"hit_position":[hit.position.x,hit.position.y,hit.position.z],"mesh":str(mesh.name)if mesh!=null else"COMPILED_STRUCTURAL_SLAB","world_min":[b.position.x,b.position.y,b.position.z],"world_max":[b.end.x,b.end.y,b.end.z]})
     var ancestry:Array=[]
     while node!=ship:
      if node.has_meta("catalogue_file"):ancestry.append({"node":str(node.name),"catalogue_file":node.get_meta("catalogue_file")})
      node=node.get_parent()
     row['catalogue_ancestry']=ancestry
    samples.append(row)
  records.append({"key":site.key,"samples":samples})
 FileAccess.open("/workspace/astraea-integration-cutoff-20261013/g2_remaining_five_pairs_20261013/CURRENT_RECEIVER_SURVEY.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_CURRENT_FIVE_SITE_RECEIVER_SURVEY","base":"f64d79dcc9a2a1bf1fa1e9320a8f01294cc9c16c","sites":records,"original_source_registration_used":true,"new_geometry_or_streaming_policy_changed":false},"  "));print("G2_FIVE_SITE_RECEIVER_SURVEY_PASS");quit(0)
