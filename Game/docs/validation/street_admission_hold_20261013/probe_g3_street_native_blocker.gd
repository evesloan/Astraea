extends SceneTree
func _initialize()->void:
 OS.set_environment("ASTRAEA_GROUP7_ENABLE","1")
 for p in ["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(p,true))
 call_deferred("run")
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(30):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var row:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/astraea-integration-cutoff-20261013/G3_STREET_FAILING_NATIVE_WITNESS.json"));var point:=Vector3(row.point[0],row.point[1],row.point[2])
 var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");actor.global_position=point+Vector3(0,.03,2);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(false)
 ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(point);ship.get_node("ShipSystems/RemainingBatchStreaming").prepare_position(point)
 for i in range(2):await physics_frame
 var state:PhysicsDirectSpaceState3D=ship.get_world_3d().direct_space_state;var hit:Dictionary=state.intersect_ray(PhysicsRayQueryParameters3D.create(point+Vector3.UP*.02,point-Vector3.UP*.02));var result:Dictionary={"status":"PASS_BOUNDED_NATIVE_CONTACT_IDENTIFICATION","point":row.point,"missing_floor_part":row.part,"triangle":row.triangle,"street_assembly_adopted":false}
 assert(not hit.is_empty());result.collider_path=str(hit.collider.get_path());result.hit_position=[hit.position.x,hit.position.y,hit.position.z];result.normal=[hit.normal.x,hit.normal.y,hit.normal.z]
 var mesh:MeshInstance3D=hit.collider.get_parent()as MeshInstance3D
 if mesh!=null:
  var bounds:AABB=mesh.global_transform*mesh.get_aabb();result.mesh_name=str(mesh.name);result.mesh_world_min=[bounds.position.x,bounds.position.y,bounds.position.z];result.mesh_world_max=[bounds.end.x,bounds.end.y,bounds.end.z]
 var owner:Node=hit.collider
 var ancestry:Array=[]
 while owner!=null:
  ancestry.append({"name":str(owner.name),"scene_file":owner.scene_file_path});owner=owner.get_parent()
 result.ancestry=ancestry
 FileAccess.open("/workspace/astraea-integration-cutoff-20261013/G3_STREET_NATIVE_CONTACT_BLOCKER.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print("G3_STREET_NATIVE_CONTACT_PROBE_PASS ",result.collider_path);quit(0)
