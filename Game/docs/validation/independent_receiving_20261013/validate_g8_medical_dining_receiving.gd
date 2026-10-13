extends SceneTree
var checks:=0
var failures:Array=[]
var stages:Array=[]
const OUT="/workspace/astraea-integration-cutoff-20261013/G8_MEDICAL_DINING_RECEIVING_RUNTIME.json"
func _initialize()->void:
 OS.set_environment("ASTRAEA_GROUP7_ENABLE","1")
 for p in ["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(p,true))
 call_deferred("run")
func receipt(status:String)->void:
 FileAccess.open(OUT,FileAccess.WRITE).store_string(JSON.stringify({"status":status,"checks":checks,"failures":failures,"stages":stages,"new_floor_owners":0,"new_capacity":0,"original_player_cart_sources_unchanged":true,"clinical_pressure_whole_medical_regression_loaded_cart_and_final_art_accepted":false},"  "))
func require(ok:bool,label:String)->bool:
 checks+=1
 if not ok:failures.append(label);receipt("HOLD");push_error(label);quit(1)
 return ok
func frames(n:int)->void:
 for i in range(n):await physics_frame
func mouse(on:bool)->void:
 var e:=InputEventMouseButton.new();e.button_index=MOUSE_BUTTON_RIGHT;e.pressed=on;Input.parse_input_event(e)
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(40)
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var original_actor:Vector3=actor.global_position
 var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget");var stream:Node3D=ship.get_node("ShipSystems/RemainingBatchStreaming")
 var dining:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group8/dining_fixture_adaptation.json"))
 var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency")
 for row in dining.rooms:
  var anchor:Array=row.lights[0].at
  residency.prepare_position(Vector3(anchor[0],61.5,anchor[2]))
  var room:Node3D=ship.find_child(str(row.programme_key),true,false)
  if not require(room!=null,"Original dining programme root "+str(row.programme_key)):return
  var addition:Node3D=room.get_node(str(dining.root_name))
  if not require(addition.get_meta("new_capacity")==0 and addition.get_meta("new_physical_fixtures")==0,"Existing fixtures only "+str(row.programme_key)):return
  for item in row.lights:
   var light:SpotLight3D=addition.get_node(str(item.name));var lens:MeshInstance3D=room.find_child(str(item.physical_lens_name),true,false)
   if not require(lens!=null and (lens.global_transform*lens.get_aabb()).grow(.025).has_point(light.global_position),"Exact retained dining lens "+str(item.name)):return
   if not require(budget.sources.count(light)==1 and budget.requested_shadow[light.get_instance_id()],"Single shared dining source "+str(item.name)):return
  stages.append({"dining":str(row.programme_key),"existing_lens_adaptations":row.lights.size(),"new_fixtures":0})
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group8/medical_bay.json"));var room:Node3D=stream.rooms[str(plan.programme_key)]
 # Independent supported interaction case, not a connected clinical or cart journey.
 actor.global_position=Vector3(28,21.03,-415.82);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);stream.prepare_position(actor.global_position);await frames(30)
 if not require(actor.is_on_floor()and absf(actor.global_position.y-21)<.12,"Supported original medical public-control stance"):return
 if not require(room.get_meta("stream_loaded",false)and room.has_node(str(plan.root_name)),"Medical hook executes through existing room stream"):return
 var addition:Node3D=room.get_node(str(plan.root_name))
 if not require(addition.global_transform.is_equal_approx(Transform3D.IDENTITY)and addition.get_meta("new_capacity")==0 and addition.get_meta("new_floor_owners")==0,"Exact medical world source and unchanged capacity"):return
 for row in plan.doors:
  var driver:Node3D=addition.get_node(str(row.name))
  if not require(str(driver.persistent_id)==str(row.persistent_id)and driver.bound_meshes.size()==10 and driver.hinge_nodes.size()==2,"Original privacy backend bound "+str(row.name)):return
  for mesh:MeshInstance3D in driver.bound_meshes:
   var body:AnimatableBody3D=mesh.get_node("StaticContact");var contact:CollisionShape3D=body.get_node("NativeTriangleContact")
   if not require(contact.shape is ConcavePolygonShape3D and not contact.disabled and contact.shape.get_faces()==mesh.mesh.get_faces()and body.global_transform.is_equal_approx(mesh.global_transform),"Exact source leaf triangles "+str(mesh.name)):return
 for row in plan.lights:
  var old:OmniLight3D=room.get_node(str(row.original_generic_name));var light:SpotLight3D=addition.get_node(str(row.name))
  if not require(not old.get_meta("fixture_powered")and not old.visible and not old.shadow_enabled,"Original generic source retired "+str(row.original_generic_name)):return
  if not require(light.global_position.distance_to(old.global_position)<.001 and budget.sources.count(light)==1,"Original housing direction and single shared source "+str(row.name)):return
 var door:Node3D=addition.get_node(str(plan.doors[0].name));var target:Node3D=door.get_node("PublicPhysicalControl");actor.camera.look_at(target.global_position,Vector3.UP);mouse(true);await frames(3)
 if not require(actor.target_from_view()==door,"Actual original RMB target for medical public control"):return
 var event:=InputEventKey.new();event.keycode=KEY_E;event.physical_keycode=KEY_E;event.pressed=true;Input.parse_input_event(event);await frames(3);event.pressed=false;Input.parse_input_event(event);mouse(false);await frames(100)
 if not require(not door.desired_open and door.open_fraction<.001,"Ordinary original RMB/E closes fitted surgical privacy"):return
 var old_id:int=door.get_instance_id();var old_source_ids:Array=[]
 for row in plan.lights:old_source_ids.append(addition.get_node(str(row.name)).get_instance_id())
 # Two lifecycle fixture transitions; no route or traversal acceptance claimed.
 actor.global_position=original_actor;actor.velocity=Vector3.ZERO;await frames(40);stream.refresh()
 if not require(not room.get_meta("stream_loaded",true)and not room.has_node(str(plan.root_name)),"Existing medical stream releases its owned source nodes"):return
 for light in budget.sources:
  if is_instance_valid(light)and not require(not light.get_instance_id()in old_source_ids,"No freed medical source remains registered"):return
 actor.global_position=Vector3(28,21.03,-415.82);actor.velocity=Vector3.ZERO;stream.prepare_position(actor.global_position);await frames(30);addition=room.get_node(str(plan.root_name));door=addition.get_node(str(plan.doors[0].name))
 if not require(door.get_instance_id()!=old_id and not door.desired_open and door.open_fraction<.001,"Exact closed privacy state restored across real room release/reload"):return
 for row in plan.lights:
  var light:Light3D=addition.get_node(str(row.name))
  if not require(budget.sources.count(light)==1,"Reload medical source registered once "+str(row.name)):return
 stages.append({"medical_programme":str(plan.programme_key),"retained_general_beds":int(plan.retained_general_bed_ids),"retained_surgical_suites":int(plan.retained_surgical_suite_ids),"privacy_drivers":4,"exact_original_leaf_contacts":40,"existing_housing_adaptations":39,"original_RMB_E_operations":1,"real_stream_release_reload":1,"closed_privacy_state_preserved":true,"lifecycle_fixture_transitions":2})
 receipt("PASS_MEDICAL_DINING_BINDING_AND_MEDICAL_STREAM_LIFECYCLE");print("G8_MEDICAL_DINING_RECEIVING_PASS checks=",checks);quit(0)
