extends "res://tests/validate_d04_port_forward_commons_service.gd"
var gateway_walks:Array=[]
var gateway_ops:Array=[]
func event_key(code:Key,pressed:bool)->void:
    var event:=InputEventKey.new();event.keycode=code;event.physical_keycode=code;event.pressed=pressed
    Input.parse_input_event(event);Input.flush_buffered_events()
func rmb(pressed:bool)->void:
    var event:=InputEventMouseButton.new();event.button_index=MOUSE_BUTTON_RIGHT;event.pressed=pressed
    Input.parse_input_event(event);Input.flush_buffered_events()
func operate(player:CharacterBody3D,door:Node3D,want:bool)->bool:
    var marker:Node3D=door.find_child("DATUM_call_button",true,false)
    record("retained_call_datum_"+str(gateway_ops.size()),marker!=null)
    if marker==null:return false
    var targets:Array[Vector3]=[marker.global_position]
    for leaf in door.leaves:
        for mesh:MeshInstance3D in leaf.find_children("*","MeshInstance3D",true,false):
            var bounds:AABB=mesh.global_transform*mesh.get_aabb()
            var at:=bounds.get_center();targets.append(at)
            at.x+=.32 if at.x<door.global_position.x else -.32
            targets.append(at)
    var selected:Node=null
    var focus_witnesses:Array=[]
    for target in targets:
        player.camera.look_at(target,Vector3.UP);rmb(true)
        for frame in range(6):await physics_frame
        selected=player.interaction_target
        var q:=PhysicsRayQueryParameters3D.create(player.camera.global_position,player.camera.global_position-player.camera.global_basis.z*2.5)
        q.exclude=[player.get_rid()];q.collide_with_areas=true
        var hit=player.get_world_3d().direct_space_state.intersect_ray(q)
        focus_witnesses.append({"source_target":str(target),"selected":str(selected.get_path())if selected!=null else"none","hit":str(hit.collider.get_path())if not hit.is_empty()else"none"})
        if selected==door:break
    print("GATEWAY_SOURCE_FOCUS ",JSON.stringify(focus_witnesses))
    record("normal_RMB_selection_"+str(gateway_ops.size()),selected==door)
    if selected!=door:
        print("GATEWAY_FOCUS_HOLD target=",selected," datum=",marker.global_position," eye=",player.camera.global_position)
        rmb(false);return false
    event_key(KEY_E,true)
    for frame in range(3):await physics_frame
    event_key(KEY_E,false)
    for frame in range(150):await physics_frame
    rmb(false);player.camera.rotation=Vector3.ZERO
    var reached:bool=door.desired_open==want and (door.open_fraction>.999 if want else door.open_fraction<.001)
    gateway_ops.append({"wanted_open":want,"desired_open":door.desired_open,"fraction":door.open_fraction,"obstructed":door.obstructed,"normal_RMB_E":true})
    record("actual_gateway_motion_"+str(gateway_ops.size()),reached)
    return reached
func finish()->void:
    var result={"status":"PASS"if errors.is_empty()else"HOLD","checks":checks,"errors":errors,"walks":gateway_walks,"normal_gateway_operations":gateway_ops,"supported_initial_fixture_count":1,"route_teleports":0,"controller_changes":false,"scope":"Actual construction main public/fore street gateway continuous normal input entry/return and both-side RMB/E;human source receiving only,private admission/species/engineering/full-ship/final visuals held"}
    FileAccess.open("/workspace/astraea-protected-integration-evidence-20261012/D17_GATEWAY_RECEIVING001.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  ")+"\n")
    print("D17_GATEWAY_RECEIVING ",result.status," checks=",checks.size()," errors=",errors)
    quit(0 if errors.is_empty()else 1)
func run()->void:
    var main=(load("res://scenes/main.tscn")as PackedScene).instantiate();root.add_child(main)
    for frame in range(40):await physics_frame
    var ship=main.get_node("World360/Astraea");var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
    var module=ship.get_node_or_null("ShipSpace/Districts/StarAtlasD17StandardBatch")
    record("one_installed_batch",module!=null)
    if module==null:finish();return
    var door:Node3D=module.get_node("ForeHouseReceivingDoor")
    record("gateway_initially_closed",door.open_fraction<.001 and not door.desired_open)
    var start:=Vector3(-65,102.03,-12.7)
    var query:=PhysicsRayQueryParameters3D.create(start+Vector3.UP*.4,start-Vector3.UP*.4)
    query.exclude=[player.get_rid()];var hit=ship.get_world_3d().direct_space_state.intersect_ray(query)
    record("real_public_fixture_floor",not hit.is_empty() and absf(hit.position.y-102)<.1)
    if not errors.is_empty():finish();return
    ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(start)
    player.global_position=start;player.velocity=Vector3.ZERO;player.set_controls_enabled(true)
    for frame in range(30):await physics_frame
    record("supported_fixture_on_floor",player.is_on_floor())
    if not await operate(player,door,true):finish();return
    for goal in [Vector3(-65,102,-16),Vector3(-61.5,102,-16),Vector3(-61.5,102,-22),Vector3(-61.5,102,-16),Vector3(-65,102,-16)]:
        var walk=await walk_to(player,goal);gateway_walks.append(walk);record("continuous_gateway_leg_"+str(gateway_walks.size()),walk.reached and walk.floor_contact)
        if not errors.is_empty():finish();return
    if not await operate(player,door,false):finish();return
    if not await operate(player,door,true):finish();return
    var back=await walk_to(player,Vector3(-65,102,-12.7));gateway_walks.append(back);record("normal_public_return",back.reached and back.floor_contact)
    if not errors.is_empty():finish();return
    if not await operate(player,door,false):finish();return
    finish()
