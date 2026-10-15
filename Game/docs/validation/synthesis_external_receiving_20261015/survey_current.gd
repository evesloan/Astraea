extends "res://tests/validate_d04_port_forward_commons_service.gd"
const D="/workspace/astraea-integration-cutoff-20261013/synthesis_external_receiving_20261015/"
func _initialize()->void:
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/DINING_SERVICE_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ORCHARD_RECEIVING_ADOPTION_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func volume(space:PhysicsDirectSpaceState3D,x0:float,x1:float,z0:float,z1:float)->Array:
 var q:=PhysicsShapeQueryParameters3D.new();var shape:=BoxShape3D.new();shape.size=Vector3(x1-x0,3.62,z1-z0);shape.margin=0.;q.shape=shape;q.margin=0.;q.transform.origin=Vector3((x0+x1)/2,1.69,(z0+z1)/2);var result:Array=[]
 for hit in space.intersect_shape(q,1024):result.append(str(hit.collider.get_path()))
 return result
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(60);var ship:Node3D=main.get_node("World360/Astraea");var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");player.set_physics_process(false);player.global_position=Vector3(0,0,0);var space:=ship.get_world_3d().direct_space_state;var rows:Array=[]
 for z in[-27.,27.]:
  var samples:Array=[]
  for x in[-65.,-62.,-58.,-56.3,-56.,-55.7,-54.,-52.,-50.,-48.1,-47.9,-46.,-44.1]:
   var at:=Vector3(x,0,z);var f:=ray(space,at+Vector3.UP*.03,at-Vector3.UP*.03);var cross:=ray(space,Vector3(-58,1,z),Vector3(-54,1,z));samples.append({"at":[x,0,z],"floor":str(f.collider.get_path())if not f.is_empty()else"","clear":capsule_clear(space,at),"cross_wall":str(cross.collider.get_path())if not cross.is_empty()else""})
  rows.append({"z":z,"samples":samples,"volume_preimages":volume(space,-55.88,-48.001,z-2.15,z+2.15)})
 FileAccess.open(D+"SYNTHESIS_EXTERNAL_SOURCE_SURVEY.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"CURRENT_UNCHANGED_SOURCE_SURVEY","production_changed":false,"receiving_links":rows},"  "));print("PASS_SYNTHESIS_EXTERNAL_SOURCE_SURVEY");quit(0)
