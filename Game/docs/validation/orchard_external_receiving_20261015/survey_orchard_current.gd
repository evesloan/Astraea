extends "res://tests/validate_d04_port_forward_commons_service.gd"
const D="/workspace/astraea-integration-cutoff-20261013/orchard_external_receiving_20261015/"
func _initialize()->void:
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/DINING_SERVICE_ADOPTION_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func volume(space:PhysicsDirectSpaceState3D,x0:float,x1:float,z0:float,z1:float)->Array:
 var q:=PhysicsShapeQueryParameters3D.new();var shape:=BoxShape3D.new();shape.size=Vector3(x1-x0,4.06,z1-z0);shape.margin=0.;q.shape=shape;q.margin=0.;q.transform.origin=Vector3((x0+x1)/2,62.57,(z0+z1)/2);var result:Array=[]
 for hit in space.intersect_shape(q,1024):result.append(str(hit.collider.get_path()))
 return result
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(30);var ship:Node3D=main.get_node("World360/Astraea");var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");player.set_physics_process(false);player.global_position=Vector3(51,61.03,-221);var stream:Node=ship.get_node("ShipSystems/RemainingBatchStreaming");stream.prepare_position(player.global_position);await frames(4);var space:=ship.get_world_3d().direct_space_state;var samples:Array=[]
 for z in[-228.,-222.,-214.,-209.,-176.]:
  for x in[0.,3.5,4.5,8.,24.,40.,48.,50.,52.,53.1,53.8,54.1,55.,56.,58.,60.,62.,64.,68.]:
   var at:=Vector3(x,61,z);var floor:=ray(space,at+Vector3.UP*.03,at-Vector3.UP*.03);var cross:=ray(space,Vector3(52,62,z),Vector3(56,62,z));samples.append({"at":[x,61,z],"floor":str(floor.collider.get_path())if not floor.is_empty()else"","clear":capsule_clear(space,at),"cross_wall":str(cross.collider.get_path())if not cross.is_empty()else"","cross_at":str(cross.position)if not cross.is_empty()else""})
 var boundaries:Array=[]
 for node:MeshInstance3D in ship.get_node("ShipSpace/Districts/D10_OrchardFoodHall_WIP").find_children("*","MeshInstance3D",true,false):
  var b:AABB=node.global_transform*node.get_aabb()
  if b.end.x>53.8 and b.position.y<65 and b.end.y>61:boundaries.append({"path":str(node.get_path()),"min":[b.position.x,b.position.y,b.position.z],"max":[b.end.x,b.end.y,b.end.z]})
 var volumes:Array=[]
 for r in[[54.001,60.,-232.,-203.],[60.,64.,-232.,-173.85],[4.001,64.,-178.15,-173.85]]:volumes.append({"rect":r,"contacts":volume(space,r[0],r[1],r[2],r[3])})
 var door_rows:Array=[]
 for n:Node3D in ship.get_node("ShipSpace/Districts/D10_OrchardFoodHall_WIP").find_children("OrchardFood_*","Node3D",true,false):door_rows.append({"name":str(n.name),"at":str(n.global_position),"script":n.get_script().resource_path if n.get_script()!=null else ""})
 FileAccess.open(D+"ORCHARD_SOURCE_RECEIVING_SURVEY.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"SURVEY_CURRENT_UNCHANGED_ORCHARD","samples":samples,"outer_boundary_meshes":boundaries,"proposed_volume_preimages":volumes,"original_doors":door_rows,"production_changed":false},"  "));print("PASS_ORCHARD_CURRENT_RECEIVING_SURVEY");quit(0)
