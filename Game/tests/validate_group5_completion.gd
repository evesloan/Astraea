extends SceneTree
var errors:Array=[]
var counts:Dictionary={"doors":0,"moving_panels":0,"closed_contacts":0,"open_thresholds":0,"floor_contacts":0,"operating_cycles":0,"sampled_poses":0,"moving_contact_rays":0}
func _initialize()->void:call_deferred("run")
func check(label:String,condition:bool)->void:
	if not condition:errors.append(label)
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	for i in range(12):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var manager:Node=ship.get_node("ShipSystems/ReceivedRoomResidency")
	manager.enabled=false
	actor.set_controls_enabled(false)
	load("res://scripts/group5_completion.gd").build(ship)
	var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group5/CONSTRUCTION.json"))
	var state:PhysicsDirectSpaceState3D=ship.get_world_3d().direct_space_state
	for row in d.doors:
		var chunk:Node3D=load("res://scripts/group5_completion.gd")._chunk(ship,ship.get_node("ShipSpace/Districts/ShoppingPromenadeChunks"),str(row.chunk_id))
		actor.global_position=chunk.position+Vector3(0,.03,0)
		manager.prepare_position(actor.global_position)
		manager.refresh(9.0)
		for i in range(3):await physics_frame
		var door:Node3D=chunk.get_node(str(row.local_name))
		counts.doors+=1
		check(str(row.physical_id)+" identity",String(door.persistent_id)==str(row.physical_id))
		check(str(row.physical_id)+" source",FileAccess.get_sha256(str(row.model_path))==str(row.model_sha256))
		check(str(row.physical_id)+" closed default",door.fraction==0 and not door.desired_open)
		check(str(row.physical_id)+" four panels",door.panels.size()==4)
		counts.moving_panels+=door.panels.size()
		# Centre-seam rays can run down tiny physical clearances. Probe a true panel centre.
		var local:=Vector3(float(row.width)/8.0,1.2,0)
		var from:Vector3=door.to_global(local+Vector3(0,0,-.4))
		var to:Vector3=door.to_global(local+Vector3(0,0,.4))
		var query:=PhysicsRayQueryParameters3D.create(from,to)
		query.exclude=[actor.get_rid()]
		var hit:Dictionary=state.intersect_ray(query)
		check(str(row.physical_id)+" closed physical contact",not hit.is_empty() and hit.collider in door.panels)
		counts.closed_contacts+=1
		# Existing interaction method advances actual animatable physics bodies.
		door.interact(actor)
		for i in range(82):
			await physics_frame
			await process_frame
			if i%4==0:
				counts.sampled_poses+=1
				for n in range(4):
					check(str(row.physical_id)+" moving pose",absf(door.panels[n].position.x-door.displacement[n]*door.fraction)<.0001)
					var collision:CollisionShape3D=door.panels[n].get_child(1)
					var center:Vector3=collision.global_position
					var normal:Vector3=door.global_basis.z
					var moving_hit:Dictionary=state.intersect_ray(PhysicsRayQueryParameters3D.create(center-normal*.15,center+normal*.15))
					check(str(row.physical_id)+" actual moving contact",not moving_hit.is_empty() and moving_hit.collider in door.panels)
					counts.moving_contact_rays+=1
		check(str(row.physical_id)+" open endpoint",door.fraction==1 and door.desired_open)
		var shape:=CapsuleShape3D.new()
		shape.radius=.3;shape.height=2.2
		var capsule:=PhysicsShapeQueryParameters3D.new()
		capsule.shape=shape;capsule.margin=0
		capsule.transform=Transform3D(Basis.IDENTITY,door.global_position+Vector3.UP*1.102)
		capsule.exclude=[actor.get_rid()]
		var contacts:Array=state.intersect_shape(capsule,16)
		check(str(row.physical_id)+" open worker threshold",contacts.is_empty())
		counts.open_thresholds+=1
		for depth in [-.35,.35]:
			var point:Vector3=door.to_global(Vector3(0,.15,depth))
			var floor_hit:Dictionary=state.intersect_ray(PhysicsRayQueryParameters3D.create(point,point-Vector3.UP*.6))
			check(str(row.physical_id)+" supported approach",not floor_hit.is_empty() and absf(floor_hit.position.y-52.5)<.04)
			counts.floor_contacts+=1
		door.interact(actor)
		for i in range(82):await physics_frame
		check(str(row.physical_id)+" closed endpoint",door.fraction==0 and not door.desired_open)
		counts.operating_cycles+=1
		if counts.doors%30==0:print("GROUP5_PROGRESS ",counts.doors," errors ",errors.size())
		if not errors.is_empty():break
	check("preserved original R070",FileAccess.get_sha256("res://assets/models/AST-RTL-005.glb")=="dda0ea75fa8d2363ac4f61292018271f2032b896d0669eccc097d58017e45497")
	check("identity joins remain unresolved",d.unresolved_address_joins==84)
	var result:Dictionary={"status":"PASS" if errors.is_empty() else "HOLD","counts":counts,"errors":errors,"source_door_controller":"group5_retail_slider.gd","fixture":"actual production main.tscn plus exact scoped group5 builder; shared root files unchanged","scope":"Actual main floor contacts, stationary worker thresholds, animatable-panel operating cycles and source pins. Not normal-input walking, largest-species, cart, save/load, permissions, structural or final visual acceptance.","whole_group_accepted":false}
	FileAccess.open("res://artifacts/group5_completion.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("PASS: Group5 completion" if errors.is_empty() else "HOLD: Group5 completion",JSON.stringify(result))
	quit(0 if errors.is_empty() else 1)
