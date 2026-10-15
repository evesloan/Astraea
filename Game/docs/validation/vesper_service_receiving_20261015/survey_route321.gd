extends "res://tests/validate_d04_port_forward_commons_service.gd"
const D="/workspace/astraea-integration-cutoff-20261013/vesper_service_receiving_20261015/"
func _initialize()->void:
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/DINING_SERVICE_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/ORCHARD_RECEIVING_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/SYNTHESIS_EXTERNAL_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/D09_RETAIL_SERVICE_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/AQUATIC_EXTERNAL_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/ARRIVALS_STAFF_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/THREAD_SUCCESSOR_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/ARRIVALS_UPPER_STAFF_ADOPTION_OVERLAY.zip", "/workspace/astraea-integration-cutoff-20261013/PORT_FORE404_ADOPTION_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func volume(space:PhysicsDirectSpaceState3D,x0:float,x1:float,z0:float,z1:float)->Array:
 var q:=PhysicsShapeQueryParameters3D.new();var shape:=BoxShape3D.new();shape.size=Vector3(x1-x0,4.44,z1-z0);shape.margin=0.;q.shape=shape;q.margin=0.;q.transform.origin=Vector3((x0+x1)/2,62.76,(z0+z1)/2);var result:Array=[]
 for hit in space.intersect_shape(q,1024):result.append(str(hit.collider.get_path()))
 return result
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(30);var ship:Node3D=main.get_node("World360/Astraea");var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");player.set_physics_process(false);player.global_position=Vector3(-2,61.03,176);await frames(4);var space:=ship.get_world_3d().direct_space_state;var samples:Array=[]
 for z in[166.,168.,170.,172.,174.,228.3,229.,230.,231.,231.7,233.,234.8,237.]:
  for x in[2.,3.7,4.01,12.,20.,28.,36.,44.,46.2,48.,50.,51.,53.7,54.01,58.,60.,62.,64.]:
   var at:=Vector3(x,61,z);var floor:=ray(space,at+Vector3.UP*.03,at-Vector3.UP*.03);samples.append({"at":[x,61,z],"floor":str(floor.collider.get_path())if not floor.is_empty()else"","floor_y":floor.position.y if not floor.is_empty()else null,"clear":capsule_clear(space,at)})
 var boundaries:Array=[];var all_rows:Array=[]
 for node:MeshInstance3D in ship.get_node("ShipSpace/Districts/GentleWaters_LivingGifts_Vesper_Section_WIP").find_children("*","MeshInstance3D",true,false):
  var b:AABB=node.global_transform*node.get_aabb();var row:Dictionary={"path":str(node.get_path()),"min":[b.position.x,b.position.y,b.position.z],"max":[b.end.x,b.end.y,b.end.z],"model":node.get_parent().scene_file_path,"mesh":node.mesh.resource_path};all_rows.append(row)
  if b.end.x>48.4 and b.position.y<65 and b.end.y>61:boundaries.append(row)
 var volumes:Array=[]
 for r in[[4.001,60.,166.,168.],[4.001,60.,168.,170.],[4.001,60.,170.,172.],[4.001,60.,172.,174.],[60.,64.,166.,231.7],[54.001,60.,228.3,231.7]]:volumes.append({"rect":r,"contacts":volume(space,r[0],r[1],r[2],r[3])})
 var contact_bounds:Array=[]
 for node:MeshInstance3D in ship.get_node("ShipSpace/Districts/AftCrownPlatform_WIP").find_children("*","MeshInstance3D",true,false):
  var b:AABB=node.global_transform*node.get_aabb()
  if b.position.y<65 and b.end.y>60.5 and b.position.z<178 and b.end.z>164:contact_bounds.append({"name":str(node.name),"min":[b.position.x,b.position.y,b.position.z],"max":[b.end.x,b.end.y,b.end.z]})

 var doors:Array=[]
 for n:Node3D in ship.get_node("ShipSpace/Districts/GentleWaters_LivingGifts_Vesper_Section_WIP").find_children("*","Node3D",true,false):
  if n.get_script()!=null and "door" in n.get_script().resource_path:doors.append({"name":str(n.name),"at":str(n.global_position),"script":n.get_script().resource_path})
 FileAccess.open(D+"VESPER_ROUTE_PREIMAGES321.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"SURVEY_CURRENT_UNCHANGED_VESPER","samples":samples,"outer_boundary_meshes":boundaries,"source_mesh_bounds":all_rows,"proposed_volume_preimages":volumes,"original_doors":doors,"aft_crown_actual_bounds":contact_bounds,"production_changed":false},"  "));print("PASS_VESPER_CURRENT_RECEIVING_SURVEY");quit(0)
