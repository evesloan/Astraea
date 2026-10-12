extends SceneTree
var errors:Array=[]
var checks:=0
var samples:Array=[]
var fixture_contacts:=0
var receiver_contacts:=0
var contact_diagnostics:Array=[]
func check(label:String,condition:bool)->void:
	checks+=1
	if not condition:errors.append(label)
func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	for i in range(20):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency")
	var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
	var builder=load("res://scripts/group5_large_venue_lighting.gd")
	var definition:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group5/LARGE_VENUE_LIGHTING.json"))
	var startup_attached:bool=ship.get_meta("group5_large_venue_lighting_attached",false)
	var lights:Array=builder.build(ship)
	check("source_count109",lights.size()==109)
	var registrations:int=budget.sources.size()
	check("repeat_build_reuses109",builder.build(ship)==lights and budget.sources.size()==registrations)
	check("existing_global_budget",budget.shadow_source_budget==8 and budget.MAX_VISIBILITY_CANDIDATES==32)
	actor.set_controls_enabled(false)
	actor.set_physics_process(false)
	budget.set_process(false)
	residency.enabled=false
	var state:PhysicsDirectSpaceState3D=ship.get_world_3d().direct_space_state
	for row in definition.venues:
		check(str(row.programme_key)+" exact_export",FileAccess.get_sha256(str(row.model_path))==str(row.model_sha256))
		var owner:Node3D=builder._owner(ship,str(row.programme_key))
		var at:Vector3=owner.position+Vector3(0,.03,34)
		actor.global_position=at
		residency.prepare_position(at)
		for i in range(3):await physics_frame
		var sources:Node3D=owner.get_node("Group5SourceLighting")
		check(str(row.programme_key)+" owner_same_cached_room",owner.get_meta("programme_key")==str(row.programme_key))
		if row.has("fixture_clearance"):
			check(str(row.programme_key)+" exact_fixture_derivative",owner.get_meta("group5_fixture_source_pin")==str(row.fixture_clearance.model_sha256))
			check(str(row.programme_key)+" unchanged_unselected_meshes",int(owner.get_meta("group5_fixture_preserved_meshes",0))>400)
			for item in row.fixtures:
				if float(item.fixture_drop_m)==0:continue
				var housing:MeshInstance3D=owner.find_child(str(item.name)+"_housing",true,false)
				var rib:MeshInstance3D=owner.find_child("Rib_"+str(item.name).split("_")[1]+"_3",true,false)
				var housing_box:AABB=builder._relative_transform(housing,owner)*housing.get_aabb()
				var rib_box:AABB=builder._relative_transform(rib,owner)*rib.get_aabb()
				check(str(row.programme_key)+str(item.name)+" 30mm_below_original_rib",rib_box.position.y-housing_box.end.y>.0299)
		for item in row.fixtures:
			var lamp:OmniLight3D=sources.get_node(str(item.name))
			var lens:MeshInstance3D=owner.find_child(str(item.lens_mesh),true,false)
			check(str(row.programme_key)+str(item.name)+" original_position",lamp.position.distance_to(vec(item.local_xyz))<.00001)
			check(str(row.programme_key)+str(item.name)+" registered_exactly_once",budget.sources.count(lamp)==1 and budget.requested_shadow[lamp.get_instance_id()])
			check(str(row.programme_key)+str(item.name)+" bounded_profile",lamp.omni_range==float(item.range_m) and absf(lamp.light_energy-float(item.energy))<.00001)
			check(str(row.programme_key)+str(item.name)+" source_color",lamp.light_color.is_equal_approx(Color(item.color[0],item.color[1],item.color[2])))
			check(str(row.programme_key)+str(item.name)+" supported_cubemap",lamp.omni_shadow_mode==OmniLight3D.SHADOW_CUBE)
			var ray:=PhysicsRayQueryParameters3D.create(lamp.global_position,lamp.global_position+Vector3.UP*.12)
			ray.exclude=[actor.get_rid()]
			var hit:=state.intersect_ray(ray)
			check(str(row.programme_key)+str(item.name)+" actual_fixture_lens_contact",not hit.is_empty() and hit.collider.get_parent()==lens)
			if hit.is_empty() or hit.collider.get_parent()!=lens:
				contact_diagnostics.append({"programme_key":row.programme_key,"fixture":item.name,"emitter":[lamp.global_position.x,lamp.global_position.y,lamp.global_position.z],"hit_owner":str(hit.collider.get_parent().get_path()) if not hit.is_empty() else "missing","hit_xyz":[hit.position.x,hit.position.y,hit.position.z] if not hit.is_empty() else [],"expected_lens":str(lens.get_path())})
			fixture_contacts+=1
			# Five bounded receiver rays per source seek a real owned room surface.
			# No ray origin substitutes for a player traversal or rendered light sample.
			var receivers:=0
			var downward:float=-sqrt(pow(lamp.omni_range-.01,2)-pow(1.2,2))
			for delta in [Vector3(0,downward,0),Vector3(1.2,downward,0),Vector3(-1.2,downward,0),Vector3(0,downward,1.2),Vector3(0,downward,-1.2)]:
				var q:=PhysicsRayQueryParameters3D.create(lamp.global_position,lamp.global_position+delta)
				q.exclude=[actor.get_rid()]
				var receiver:=state.intersect_ray(q)
				if not receiver.is_empty() and lamp.global_position.distance_to(receiver.position)<lamp.omni_range:
					receivers+=1
					receiver_contacts+=1
			check(str(row.programme_key)+str(item.name)+" physical_receiver_in_range",receivers>0)
		# One entry and two interior optical fixtures per venue. Explicit placement
		# isolates source admission; no walking or public-route result is claimed.
		var sign_x:float=1.0 if float(row.translation_xyz[0])>0 else -1.0
		for local in [Vector3(sign_x*3,.03,34),Vector3(sign_x*14,.03,34),Vector3(sign_x*36,.03,34)]:
			actor.global_position=owner.position+local
			residency.prepare_position(actor.global_position)
			for i in range(3):await physics_frame
			budget.refresh()
			var active_global:=0
			var active_venue:=0
			var reaching_viewer:=0
			for light in budget.sources:
				if is_instance_valid(light) and light.is_inside_tree() and light.visible and light.shadow_enabled:active_global+=1
			for lamp:Light3D in sources.get_children():
				if lamp.visible and lamp.shadow_enabled:
					active_venue+=1
					for offset in [Vector3(0,1.5,0),Vector3(0,.4,0),Vector3(.65,1,0),Vector3(-.65,1,0)]:
						var receiver:Vector3=actor.global_position+offset
						if lamp.global_position.distance_to(receiver)<lamp.omni_range and budget._clear_sample(lamp.global_position,receiver):
							reaching_viewer+=1
							break
				check(str(row.programme_key)+str(lamp.name)+" no_unshadowed_leak",not lamp.visible or lamp.shadow_enabled)
			check(str(row.programme_key)+str(local)+" admitted_venue_sources",active_venue>=1)
			check(str(row.programme_key)+str(local)+" global_budget_bound",active_global<=8)
			check(str(row.programme_key)+str(local)+" actual_visible_sample_within_range",reaching_viewer>=1)
			samples.append({"programme_key":row.programme_key,"at":[actor.global_position.x,actor.global_position.y,actor.global_position.z],"active_venue_sources":active_venue,"active_global_shadow_sources":active_global,"active_venue_sources_reaching_visible_viewer_sample":reaching_viewer})
		var ids:Array=[]
		for lamp:Light3D in sources.get_children():ids.append(lamp.get_instance_id())
		actor.global_position=Vector3(1000,1000,1000)
		residency.refresh(9.0)
		check(str(row.programme_key)+" actual_cached_detach",not owner.is_inside_tree())
		budget.refresh()
		for lamp:Light3D in sources.get_children():
			check(str(row.programme_key)+str(lamp.name)+" detached_source_not_active",not budget.previously_active.has(lamp))
		actor.global_position=at
		residency.prepare_position(at)
		for i in range(3):await physics_frame
		budget.refresh()
		var returned_ids:Array=[]
		for lamp:Light3D in sources.get_children():returned_ids.append(lamp.get_instance_id())
		check(str(row.programme_key)+" same_source_nodes_return",ids==returned_ids and owner.is_inside_tree())
		check(str(row.programme_key)+" no_duplicate_after_return",budget.sources.size()==registrations)
	var out:Dictionary={"status":"PASS" if errors.is_empty() else "HOLD","checks":checks,"errors":errors,"contact_diagnostics":contact_diagnostics,"venues":5,"sources":109,"fixture_contact_rays":fixture_contacts,"physical_receiver_rays_hit":receiver_contacts,"optical_samples":samples,"builder_attached_during_main_startup":startup_attached,"global_shadow_budget":8,"scope":"Actual current main plus scoped source-light builder;literal fixture rays,profiles,registration,budget admission,real receiver contacts and five cached detach/returns. Optical fixture placements are explicit;no traversal,pixel-lighting,commerce,full-venue or hardware acceptance.","whole_group_accepted":false,"pixel_lighting_and_hardware_accepted":false}
	FileAccess.open("res://artifacts/group5_large_venue_lighting.json",FileAccess.WRITE).store_string(JSON.stringify(out,"  "))
	print("GROUP5_LARGE_VENUE_LIGHTING ",JSON.stringify(out))
	quit(0 if errors.is_empty() else 1)
