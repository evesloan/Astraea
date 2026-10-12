extends "res://tests/group6_completion/validate_optical_profile.gd"
var cascade_evidence:Dictionary={}
func cascade_checks(host:Node3D,proposal:Node3D,actor:CharacterBody3D,feature:Node3D)->void:
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group6_completion/CASCADE_PROPOSAL001.json"));var originals:Array=feature.find_children("*","MeshInstance3D",true,false);var snapshots:Array=[]
	for mesh:MeshInstance3D in originals:snapshots.append([mesh.get_instance_id(),mesh.global_transform])
	var space:=host.get_world_3d().direct_space_state
	record("cascade_stance_supported",actor.is_on_floor() and absf(actor.position.y-44)<.01)
	record("cascade_stance_original_capsule_clear",operator_capsule_clear(space,actor))
	var witness:=MotionWitness.new();witness.process_physics_priority=1000;root.add_child(witness);witness.reset(actor);var moved:Array=[]
	var w:Dictionary=await walk_to(actor,vec(p.operator_stance_xyz));legs.append(w);record("cascade_operator_original_walk",w.reached and w.floor_contact)
	for i in range(2):
		var control:Node3D=proposal.get_node(str(p.valves[i].id));var point:=vec(p.valves[i].pivot_xyz)+Vector3(0,.14,.02)
		await aim(actor,point);record("cascade_original_RMB_target_"+str(i),actor.interaction_target==control);var before:Transform3D=control.source_mesh.global_transform
		await key_e();for frame in range(60):await physics_frame
		record("cascade_original_E_turns_"+str(i),control.open_fraction>.999 and absf(control.body.rotation.z-PI/2)<.001)
		record("cascade_actual_source_wheel_moves_"+str(i),not control.source_mesh.global_transform.is_equal_approx(before))
		record("cascade_no_fluid_claim_"+str(i),not control.get_meta("water_operation_implemented"))
		await key_e();for frame in range(60):await physics_frame
		record("cascade_original_E_returns_"+str(i),control.open_fraction<.001 and control.source_mesh.global_transform.is_equal_approx(before));moved.append(str(control.name))
	w=await walk_to(actor,vec(p.west_approach_xyz));legs.append(w);record("cascade_operator_original_return",w.reached and w.floor_contact);physical_key(false)
	var own:Array[RID]=[]
	for body:CollisionObject3D in proposal.find_children("*","CollisionObject3D",true,false):own.append(body.get_rid())
	var branch:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://docs/group6_completion/interfaces/CASCADE_BRANCH_ENVELOPES001.json"));var spheres:=0
	for path in branch.routes:
		var points:Array=path.points_xyz
		for index in range(points.size()-1):
			var a:=vec(points[index]);var b:=vec(points[index+1]);var count:=ceili(a.distance_to(b)/.04)
			for j in range(count+1):
				var shape:=SphereShape3D.new();shape.radius=float(branch.pipe_radius_trial_m);shape.margin=.001;var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.margin=.001;q.transform=Transform3D(Basis.IDENTITY,a.lerp(b,float(j)/count));q.exclude=own+[actor.get_rid()];var hits:=space.intersect_shape(q,32)
				record("cascade_proposed_branch_clear_"+str(spheres),hits.is_empty());spheres+=1
	var curtain:=BoxShape3D.new();var samples:=0
	var drops:Array=[]
	for i in range(61):drops.append(18.5*i/60.0)
	for i in range(51):drops.append(i*.01)
	for drop:float in drops:
		var t:=drop/18.5;curtain.size=Vector3(.04,.04,.65+.15*t);var q:=PhysicsShapeQueryParameters3D.new();q.shape=curtain;q.transform=Transform3D(Basis.IDENTITY,Vector3(25+.12*sin(minf(drop/.12,1)*PI/2),62.36-drop,215));var hits:=space.intersect_shape(q,32)
		record("original_cascade_curtain_clear_"+str(samples),hits.is_empty());samples+=1
	for i in range(originals.size()):record("same_original_watercourse_mesh_"+str(i),originals[i].get_instance_id()==snapshots[i][0] and originals[i].global_transform==snapshots[i][1])
	witness.active=false;record("cascade_continuous_original_movement",witness.maximum_step<.12 and witness.minimum_y>43.9);cascade_evidence={"mechanical_wheels":moved,"branch_envelope_sphere_samples":spheres,"original_curtain_samples":samples,"physics_samples":witness.samples,"maximum_frame_motion_m":witness.maximum_step,"minimum_y":witness.minimum_y,"scope":"Mechanical console on existing shoulder, exact original source/input, no connected network/stream/spine edit. Own new console contacts excluded only from onward-envelope checks; original architecture remains checked. Engineering/support/channel ownership and shared adoption remain held."};witness.queue_free()
func operator_capsule_clear(space:PhysicsDirectSpaceState3D,actor:CharacterBody3D)->bool:
	var shape:=CapsuleShape3D.new();shape.radius=.3;shape.height=1.8;shape.margin=.001
	var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform=Transform3D(Basis.IDENTITY,actor.global_position+Vector3.UP*.925);q.exclude=[actor.get_rid()]
	if not space.intersect_shape(q,32).is_empty():return false
	for delta in [Vector3(.3,0,0),Vector3(0,0,.3)]:
		var ray:=PhysicsRayQueryParameters3D.create(actor.global_position+Vector3.UP-delta,actor.global_position+Vector3.UP+delta);ray.exclude=[actor.get_rid()]
		if not space.intersect_ray(ray).is_empty():return false
	return true
func run()->void:
	var helper:Node3D=load("res://scripts/ship.gd").new();helper.stone=helper.surface("warm_stone",Color.WHITE);helper.ivory=helper.surface("ivory_enamel",Color.WHITE)
	var host:=LocalHost.new();root.add_child(host);var annex:Node3D=load("res://scripts/aquatic_annex_receiving.gd").build(host,host);load("res://scripts/group6_completion/completion.gd").build(annex,host)
	var floor_data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"));var regions:Array=[]
	for r in floor_data.regions:
		if str(r.id) in ["D08_aquatic_district_arrival","D08_gentle_waters_basin"]:regions.append(r)
	load("res://scripts/structural_floor_builder.gd").build_regions(host,host.stone,host.ivory,regions,{},"ExactRetainedGentleWatersFloors")
	load("res://scripts/vesper_watercourse.gd").build(host,helper);var feature:Node3D=host.get_node("VesperWatercourse_WIP")
	var proposal:Node3D=load("res://scripts/group6_completion/cascade_proposal.gd").build(annex)
	var actor:CharacterBody3D=load("res://scripts/player.gd").new();host.add_child(actor);actor.global_position=Vector3(21.5,44.03,215.2);actor.set_controls_enabled(true)
	for i in range(20):await physics_frame
	record("cascade_proposal_build_succeeded",proposal!=null)
	if proposal!=null:await cascade_checks(host,proposal,actor,feature)
	record("cascade_two_legs_exercised",legs.size()==2)
	var result:Dictionary={"status":"PASS" if errors.is_empty() else "HOLD","checks":checks,"errors":errors,"legs":legs,"cascade_evidence":cascade_evidence,"supported_fixture_count":1,"traversal_position_or_velocity_writes":0,"scope":"Local exact source annex/shoulder/watercourse and retained basin floor. Original player, mechanical isolators, real source fit/branch envelopes and unchanged112 curtain criteria. Actual-main/shared owner, connected hydraulic/acoustic network, species/chair, engineering and final art remain separate."}
	FileAccess.open("res://docs/group6_completion/CASCADE_LOCAL002.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));helper.free();print("GROUP6 CASCADE LOCAL ",result.status," ",errors," LEGS ",legs.size());quit(0 if errors.is_empty() else 1)
