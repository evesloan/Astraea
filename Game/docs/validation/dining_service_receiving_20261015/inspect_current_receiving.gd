extends "res://tests/validate_d04_port_forward_commons_service.gd"
const D="/workspace/astraea-integration-cutoff-20261013/dining_service_receiving_20261015/"
func _initialize()->void:
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(30);var ship:Node3D=main.get_node("World360/Astraea");var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");player.set_physics_process(false);var stream:Node=ship.get_node("ShipSystems/RemainingBatchStreaming");var space:=ship.get_world_3d().direct_space_state;var sites:Array=[]
 for spec in[["D10_directory_01",-1.,-457.,-417.],["D10_directory_02",1.,-457.,-417.],["D10_directory_03",-1.,-241.,-201.]]:
  player.global_position=Vector3(spec[1]*50.,61.03,(spec[2]+spec[3])/2);player.force_update_transform();stream.prepare_position(player.global_position);await frames(3);var samples:Array=[]
  for z in[spec[2],spec[3]]:
   for dx in[53.2,53.8,54.1,55.,56.,58.,60.,62.,64.,66.,68.]:
    for dz in[-1.2,0.,1.2]:
     var point:=Vector3(spec[1]*dx,61,z+dz);var h:=ray(space,point+Vector3.UP*.03,point-Vector3.UP*.03);samples.append({"at":[point.x,point.y,point.z],"old_floor":str(h.collider.get_path())if not h.is_empty()else"","floor_y":h.position.y if not h.is_empty()else null,"capsule_clear":capsule_clear(space,point)})
  var room:Node3D=stream.rooms[str(spec[0])];var related:Array=[]
  for node:Node in room.find_children("*","Node3D",true,false):
   if node.has_method("interact"):related.append({"node":str(node.get_path()),"script":node.get_script().resource_path,"persistent_id":str(node.get("persistent_id"))})
  sites.append({"programme_key":spec[0],"samples":samples,"existing_interaction_nodes":related})
 FileAccess.open(D+"CURRENT_EXTERNAL_SERVICE_RECEIVING.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"CURRENT_SIX_SERVICE_OPENING_FLOOR_AND_CAPSULE_INVENTORY","sites":sites,"production_changed":false},"  "));print("PASS_CURRENT_SIX_DINING_SERVICE_RECEIVING_INVENTORY");quit(0)
