extends "res://tests/validate_d04_court_controls_staff_candidate.gd"
func _initialize()->void:
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/DINING_SERVICE_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ORCHARD_RECEIVING_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/SYNTHESIS_EXTERNAL_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/D09_RETAIL_SERVICE_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/AQUATIC_EXTERNAL_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ARRIVALS_STAFF_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/thread_successor_receiving_20261015/CANDIDATE_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
var legs:Array=[]
var operations:Array=[]
var guard_count:=0
var changed_interface_contacts:Array=[]
var fixture_apertures:Array=[]
func leg(actor:CharacterBody3D,goal:Vector3,label:String)->bool:
    var result:Dictionary=await walk_to(actor,goal);result.scope=label;legs.append(result)
    record("stock_route_"+str(legs.size()),result.reached and result.floor_contact)
    return result.reached and result.floor_contact
func operate(actor:CharacterBody3D,door:Node3D,want:bool)->bool:
    await aim(actor,door.to_global(Vector3(1.19,1.35,0)))
    if actor.interaction_target!=door:
        var query:=PhysicsRayQueryParameters3D.create(actor.camera.global_position,actor.camera.global_position-actor.camera.global_basis.z*2.5);query.exclude=[actor.get_rid()]
        var hit:=actor.get_world_3d().direct_space_state.intersect_ray(query)
        print("THREAD_STOCK_TARGET_HOLD ",JSON.stringify({"door":str(door.name),"actor":str(actor.global_position),"target":str(actor.interaction_target),"hit":str(hit.collider.get_path()) if not hit.is_empty() else "missing"}))
    record("stock_normal_RMB_"+str(operations.size()),actor.interaction_target==door)
    await key_e()
    for i in range(100):await physics_frame
    var ok:bool=door.desired_open==want and door.open_fraction==(1.0 if want else 0.0)
    operations.append({"door":str(door.persistent_id),"desired_open":want,"normal_RMB_E":true,"fraction":door.open_fraction,"obstructed":door.obstructed,"actor_world":str(actor.global_position),"passed":ok})
    record("stock_normal_E_"+str(operations.size()),ok);return ok
func run()->void:
    var spec:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group5/THREAD_STOCK_REPAIR.json"))
    var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
    for i in range(20):await physics_frame
    var ship:Node3D=main.get_node("World360/Astraea")
    var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
    var owner:Node3D=ship.find_child("D09_ThreadAndShell_WIP",true,false)
    var original_ids:Dictionary={}
    for mesh:MeshInstance3D in owner.find_children("*","MeshInstance3D",true,false):
        if not str(mesh.get_path()).contains("Group5ThreadStockAndRepair"):
            original_ids[mesh.get_instance_id()]=[mesh.mesh.get_instance_id(),mesh.global_transform]
    var startup:bool=ship.get_meta("group5_thread_stock_attached",false)
    var builder=load("res://scripts/group5_thread_stock.gd")
    var construction:Node3D=builder.build(ship)
    record("idempotent_existing_owner",builder.build(ship)==construction)
    record("identity_preserved",owner.get_meta("programme_key")==spec.programme_key and owner.get_meta("historical_room_id")==spec.historical_room_id)
    record("source_pins",FileAccess.get_sha256(str(spec.original_model))==spec.original_model_sha256 and FileAccess.get_sha256(str(spec.model_path))==spec.model_sha256)
    var kept:=0
    for mesh:MeshInstance3D in owner.find_children("*","MeshInstance3D",true,false):
        if original_ids.has(mesh.get_instance_id()):
            var before:Array=original_ids[mesh.get_instance_id()]
            record("unchanged_original_"+str(mesh.get_instance_id()),mesh.mesh.get_instance_id()==before[0] and mesh.global_transform.is_equal_approx(before[1]));kept+=1
    record("all_original_meshes_preserved",kept==original_ids.size())
    actor.global_position=Vector3(3,52.53,-194.5);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true)
    ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position)
    for i in range(15):await physics_frame
    var space:PhysicsDirectSpaceState3D=ship.get_world_3d().direct_space_state
    for row in spec.generic_support_contacts:
        var mesh:MeshInstance3D=construction.find_child(str(row.godot_mesh_name),true,false)
        var point:=Vector3(row.world_contact_xyz[0],row.world_contact_xyz[1],row.world_contact_xyz[2])
        var query:=PhysicsRayQueryParameters3D.create(point+Vector3.UP*.015,point-Vector3.UP*.025)
        query.exclude=[mesh.get_node("StaticContact").get_rid()]
        var hit:=space.intersect_ray(query)
        record("generic_stock_support_"+str(row.mesh),not hit.is_empty() and str(hit.collider.get_parent().name)==str(row.godot_support_name) and absf(hit.position.y-point.y)<.00005)

    # Focused changed-interface checks; all unchanged r004 native geometry is independently pinned.
    var excluded:Array[RID]=[actor.get_rid()]
    for body:CollisionObject3D in construction.find_children("*","CollisionObject3D",true,false):excluded.append(body.get_rid())
    for mesh:MeshInstance3D in construction.find_children("*","MeshInstance3D",true,false):
        if not str(mesh.name).begins_with("East_"):continue
        var shape:=mesh.mesh.create_convex_shape(true,false);shape.margin=0.;var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.margin=0.;q.transform=mesh.global_transform;q.exclude=excluded;var paths:Array=[]
        for hit in space.intersect_shape(q,256):
            if "ThreadShellArchitecture"in str(hit.collider.get_path()):paths.append(str(hit.collider.get_path()))
        changed_interface_contacts.append({"new_trim":str(mesh.name),"original_source_contacts":paths});record("exact_original_trim_clearance_"+str(mesh.name),paths.is_empty())
    for z in[-227.,-209.]:
        for dx in[-.35,0.,.35]:
            for dz in[-.27,0.,.27]:
                var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(40+dx,56.194,z+dz),Vector3(40+dx,56.199,z+dz)));var path:=str(hit.collider.get_path())if not hit.is_empty()else"";fixture_apertures.append({"point":str(Vector3(40+dx,56.197,z+dz)),"owner":path});record("retained_fixture_housing_aperture_"+str(fixture_apertures.size()),not"Group5VisualFinish_ThreadCeiling"in path)
        var positive:=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(40.40,56.194,z),Vector3(40.40,56.199,z)));record("retained_candidate_ceiling_positive_control_"+str(z),not positive.is_empty()and"Group5VisualFinish_ThreadCeiling"in str(positive.collider.get_path()))
    var stock_bodies:Array[RID]=[]
    for body:StaticBody3D in construction.find_children("*","StaticBody3D",true,false):stock_bodies.append(body.get_rid())
    for i in range(spec.foundation_contacts_world_xyz.size()):
        var p:Array=spec.foundation_contacts_world_xyz[i];var point:=Vector3(p[0],p[1],p[2])
        var query:=PhysicsRayQueryParameters3D.create(point+Vector3.UP*.02,point-Vector3.UP*.02);query.exclude=stock_bodies
        var hit:=space.intersect_ray(query)
        record("literal_stock_floor_"+str(i),not hit.is_empty() and absf(hit.position.y-52.5)<.00005)
    var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
    var optical_samples:Array=[]
    for row in spec.modules:
        # Separate explicit optical fixtures precede the continuous walking route.
        actor.global_position=Vector3(row.staff_stance_world_xyz[0],row.staff_stance_world_xyz[1],row.staff_stance_world_xyz[2])
        for i in range(3):await physics_frame
        budget.refresh();var reaches:=0;var active:=0
        for light:Light3D in budget.sources:
            if not is_instance_valid(light) or not light.is_inside_tree():continue
            if light.visible and light.shadow_enabled:active+=1
            if construction.is_ancestor_of(light):
                record("no_unshadowed_stock_leak_"+str(row.name)+"_"+str(light.name),not light.visible or light.shadow_enabled)
                if light.visible and light.shadow_enabled and light.global_position.distance_to(actor.global_position+Vector3.UP)<light.omni_range and budget._clear_sample(light.global_position,actor.global_position+Vector3.UP):reaches+=1
        record("stock_light_reaches_"+str(row.name),reaches>0 and active<=8 and budget.shadow_source_budget==8)
        optical_samples.append({"module":str(row.name),"active_stock_sources_reaching_worker":reaches,"total_active_shadow_sources":active})
    actor.global_position=Vector3(3,52.53,-194.5);actor.velocity=Vector3.ZERO
    for i in range(15):await physics_frame
    var entry:Node3D=owner.find_child("ThreadShell_staff_entry_door",true,false)
    var service:Node3D=owner.find_child("ThreadShell_service_door",true,false)
    record("original_four_closed_doors",owner.find_children("*","AnimatableBody3D",true,false).size()==8 and not entry.desired_open and not service.desired_open)
    var route_ok:=true
    if not await leg(actor,Vector3(4.5,52.53,-194.5),"main receiving floor to original staff door"):route_ok=false
    if route_ok and not await operate(actor,entry,true):route_ok=false
    var goals:Array=[Vector3(8,52.53,-194.5),Vector3(22,52.53,-194.5),Vector3(40,52.53,-194.5),Vector3(40,52.53,-204.15),Vector3(40.7,52.53,-204.15),Vector3(40,52.53,-204.15),Vector3(40,52.53,-212.7),Vector3(40.7,52.53,-212.7),Vector3(40,52.53,-212.7),Vector3(40,52.53,-215.5),Vector3(39.1,52.53,-215.5)]
    for goal:Vector3 in goals:
        if not route_ok:break
        if not await leg(actor,goal,"continuous original staff lane to reserve/repair stations and consultation door"):route_ok=false
    if route_ok and not await operate(actor,service,true):route_ok=false
    for goal in [Vector3(35.7,52.53,-215.5),Vector3(35.7,52.53,-219.8),Vector3(35.7,52.53,-215.5)]:
        if not route_ok:break
        if not await leg(actor,goal,"original consultation work counter approach and return"):route_ok=false
    if route_ok:
        # Guard witness is a separate named fixture; worker remains at supported control stance.
        var witness:=CharacterBody3D.new();var col:=CollisionShape3D.new();var cap:=CapsuleShape3D.new();cap.radius=.3;cap.height=1.8;col.shape=cap;col.position=Vector3.UP*.9;witness.add_child(col);owner.add_child(witness)
        witness.global_position=service.to_global(Vector3(0,.02,-.7))
        for i in range(3):await physics_frame
        await aim(actor,service.to_global(Vector3(1.19,1.35,0)));record("guard_normal_RMB",actor.interaction_target==service);await key_e()
        for i in range(5):await physics_frame
        record("occupied_original_service_guard",service.desired_open and service.open_fraction==1 and service.obstructed);guard_count+=1;witness.queue_free()
        for i in range(3):await physics_frame
    if route_ok and not await operate(actor,service,false):route_ok=false
    if route_ok and not await operate(actor,service,true):route_ok=false
    for goal in [Vector3(39.1,52.53,-215.5),Vector3(40,52.53,-215.5)]:
        if not route_ok:break
        if not await leg(actor,goal,"continuous return through opened consultation door"):route_ok=false
    if route_ok:
        if not await leg(actor,Vector3(39.1,52.53,-215.5),"original outside service close stance"):route_ok=false
    if route_ok and not await operate(actor,service,false):route_ok=false
    for goal in [Vector3(40,52.53,-215.5),Vector3(40,52.53,-226.6),Vector3(40.7,52.53,-226.6),Vector3(40,52.53,-226.6),Vector3(40,52.53,-194.5),Vector3(8,52.53,-194.5)]:
        if not route_ok:break
        if not await leg(actor,goal,"continuous textile stock approach and original supported return lane"):route_ok=false
    if route_ok and not await operate(actor,entry,false):route_ok=false
    if route_ok and not await operate(actor,entry,true):route_ok=false
    if route_ok and not await leg(actor,Vector3(4.5,52.53,-194.5),"continuous original staff door egress"):route_ok=false
    if route_ok and not await operate(actor,entry,false):route_ok=false
    if route_ok and not await leg(actor,Vector3(3,52.53,-194.5),"retained main floor finish"):route_ok=false
    physical_key(false)
    record("complete_original_staff_stock_route",route_ok and legs.size()==26 and operations.size()==8 and guard_count==1)
    record("both_original_staff_doors_end_closed",not entry.desired_open and not service.desired_open and entry.open_fraction==0 and service.open_fraction==0)
    var out:Dictionary={"status":"PASS" if errors.is_empty() else "HOLD","checks":checks.size(),"errors":errors,"startup_attached":startup,"original_meshes_preserved":kept,"new_source_meshes":construction.find_children("*","MeshInstance3D",true,false).size(),"r005_changed_interface_contacts":changed_interface_contacts,"r005_retained_fixture_apertures":fixture_apertures,"generic_stock_supports":spec.generic_support_contacts.size(),"optical_samples":optical_samples,"continuous_original_controller_legs":legs,"normal_RMB_E_operations":operations,"occupied_guard_fixtures":guard_count,"teleports_inside_walking_route":0,"scope":"Actual original staff entry/rear-lane/three stock-repair stations/consultation counter and return using ordinary W/RMB/E;optical fixtures separately named;generic goods only,no inventory/refill/sales,persistence,species/cart,engineering,Game/CRT/pixel or whole-group acceptance"}
    FileAccess.open("/workspace/astraea-integration-cutoff-20261013/thread_successor_receiving_20261015/CANDIDATE_RUNTIME298.json",FileAccess.WRITE).store_string(JSON.stringify(out,"  "))
    print("GROUP5_THREAD_STOCK ",JSON.stringify({"status":out.status,"checks":checks.size(),"legs":legs.size(),"operations":operations.size(),"guards":guard_count,"errors":errors}))
    quit(0 if errors.is_empty() else 1)
