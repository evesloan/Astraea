extends SceneTree
const P:="res://night_garden_atrium_interiors_20261022/"
var checks:Array=[]
var routes:Array=[]
var actor:CharacterBody3D
func _initialize()->void:call_deferred("run")
func check(ok:bool,label:String)->void:
	checks.append({"pass":ok,"label":label})
	if not ok:push_error(label)
func raw(file:String)->Node3D:
	var doc:=GLTFDocument.new();var state:=GLTFState.new();assert(doc.append_from_file("res://assets/models/"+file,state)==OK);return doc.generate_scene(state)
func key(down:bool)->void:
	var event:=InputEventKey.new();event.physical_keycode=KEY_W;event.pressed=down;Input.parse_input_event(event)
func walk(target:Vector3)->bool:
	for frame in range(500):
		var delta:=target-actor.global_position;delta.y=0
		if delta.length()<.13:
			key(false)
			for settle in range(8):await physics_frame
			routes.append({"target":str(target),"actual":str(actor.global_position)})
			return actor.is_on_floor() and absf(actor.global_position.y-93)<.08
		actor.rotation.y=atan2(-delta.x,-delta.z);key(true);await physics_frame
	key(false);routes.append({"target":str(target),"actual":str(actor.global_position),"timeout":true});return false
func run()->void:
	var host:Node3D=load(P+"fixture_host.gd").new();root.add_child(host)
	var space:=Node3D.new();space.name="ShipSpace";host.add_child(space)
	var districts:=Node3D.new();districts.name="Districts";space.add_child(districts)
	var actors:=Node3D.new();actors.name="PersistentActors";space.add_child(actors)
	actor=load("res://scripts/player.gd").new();actor.name="Player";actor.position=Vector3(10000,10000,10000);actors.add_child(actor);actor.set_physics_process(false)
	var lower:=Node3D.new();lower.name="D13_D14_StarboardCommons_WIP";districts.add_child(lower)
	var upper:=Node3D.new();upper.name="D15_D17_StarboardHouseUpper_WIP";lower.add_child(upper)
	var wrapper:=Node3D.new();wrapper.name="StarboardHouseUpperArchitecture";upper.add_child(wrapper);wrapper.position=Vector3(63,84,0)
	var commons:=raw("AST-COM-003.glb");wrapper.add_child(commons)
	for mesh:MeshInstance3D in commons.find_children("*","MeshInstance3D",true,false):load("res://scripts/static_contact_cache.gd").attach(mesh)
	var manager:Node=load("res://scripts/night_garden_residency_20261022/manager.gd").new();host.add_child(manager);manager.setup(host);manager.set_physics_process(false);host.private_detail_residency=manager
	var district:Node3D=load("res://scripts/night_garden_residency_20261022/district.gd").build(host)
	var door_before:Dictionary={}
	for door:Node3D in district.find_children("CocoonPrivacyDoor_*","Node3D",true,false):
		door_before[door.get_instance_id()]={"position":door.position,"desired_open":door.desired_open,"open_fraction":door.open_fraction,"id":str(door.persistent_id),"script":door.get_script(),"leaf":door.leaves[0].get_instance_id()}
	load("res://night_garden_warm_interiors_20261022/adapter.gd").finish(host)
	load(P+"adapter.gd").finish(host)
	var build:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/BUILD_R002.json"))
	var original:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/night_garden_partition_20261021/index.json")).rooms
	var changed:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/INDEX_R002.json"))
	check(manager.entries.size()==30 and manager.index.size()==68,"30 rooms and38 previous records retained")
	check(district.get_meta("reserved_rest_count")==40,"Reserved rest count preserved")
	var retained_outer:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://night_garden_warm_interiors_20261022/evidence/INDEX.json"))
	var inner:=0
	for file in original:
		if changed.has(file):continue
		check(manager.index[file]==retained_outer[file],"Preserved outer warm record "+file);inner+=1
	check(inner==16,"All16 outer warm suites unchanged")
	for entry in manager.entries:
		if changed.has(str(entry.record.model_file)):manager._load_entry(entry)
	await physics_frame;await physics_frame
	for row in build.rooms:
		var home:Node3D=district.get_node(str(row.room_id))
		check(home.get_meta("rest_slot_ids")==row.rest_slot_ids,"Same rest identities "+str(int(row.index)))
		var pane:MeshInstance3D=home.find_child("NG"+str(int(row.index))+"_OvalAtriumGlass",true,false)
		check(pane!=null and pane.material_override is ShaderMaterial,"Directional privacy glazing "+str(int(row.index)))
		check(home.get_meta("atrium_interior_applied",false),"Atrium interior hook applied "+str(int(row.index)))
		check(home.find_children("AtriumCoveSource", "SpotLight3D", false, false).size()==1,"One authored cove source "+str(int(row.index)))
		var lamp:SpotLight3D=home.get_node(str(row.view_light_name))
		check(lamp.position.is_equal_approx(Vector3(row.view_light_position[0],row.view_light_position[1],row.view_light_position[2])),"Original light follows its native fixture "+str(int(row.index)))
		for finish_name in row.finish_meshes:
			var mesh:MeshInstance3D=home.find_child(str(finish_name),true,false)
			check(mesh!=null and mesh.mesh!=null,"Authored finish installed "+str(finish_name))
		var box:AABB=pane.global_transform*pane.get_aabb()
		check(absf(box.size.z-6.0)<.01 and absf(box.size.y-2.96)<.01,"Preserved oval-window dimensions "+str(int(row.index)))
		for dz in [-.4,0,.4]:
			var eye:=Vector3(row.seated_eye[0],row.seated_eye[1],row.seated_eye[2])
			var target:=Vector3(68.5,eye.y,eye.z+dz)
			var query:=PhysicsRayQueryParameters3D.create(eye,target);query.exclude=[actor.get_rid()]
			var hit:=host.get_world_3d().direct_space_state.intersect_ray(query)
			check(not hit.is_empty() and pane.is_ancestor_of(hit.collider),"Resident ray reaches actual glazing "+str(int(row.index))+" / "+str(dz))
		for door:Node3D in home.find_children("CocoonPrivacyDoor_*","Node3D",false,false):
			var before:Dictionary=door_before[door.get_instance_id()]
			check(door.position.is_equal_approx(before.position+Vector3(row.rest_moves[int(str(door.name).get_slice("_",1))-1].delta[0],0,0)) and door.desired_open==before.desired_open and door.open_fraction==before.open_fraction and str(door.persistent_id)==before.id and door.get_script()==before.script and door.leaves[0].get_instance_id()==before.leaf,"Cocoon privacy control and existing state preserved "+str(int(row.index))+"/"+str(door.name))
	var moved_doors:Array[Node]=[]
	for row in build.rooms:
		moved_doors.append_array(district.get_node(str(row.room_id)).find_children("CocoonPrivacyDoor_*","Node3D",false,false))
	for door in moved_doors:door.interact(actor)
	for frame in range(120):await physics_frame
	for door in moved_doors:check(door.open_fraction<.001 and not door.desired_open,"Original privacy controller closes "+str(door.persistent_id));door.interact(actor)
	for frame in range(120):await physics_frame
	for door in moved_doors:check(door.open_fraction>.999 and door.desired_open,"Original privacy controller reopens "+str(door.persistent_id))
	for number in [416,440,422,542]:
		var row:Dictionary={}
		for item in build.rooms:
			if int(item.index)==number:row=item
		var center:float=(float(original[row.model_file].bounds_min[2])+float(original[row.model_file].bounds_max[2]))*.5
		var sign:float=signf(float(row.seated_eye[2])-center)
		actor.position=Vector3(76.0 if number in [416,440] else 76.75,93.03,center-2.1 if number==422 else center);actor.velocity=Vector3.ZERO;actor.set_physics_process(true)
		for frame in range(12):await physics_frame
		var targets:Array[Vector3]=[]
		if number in [416,440]:
			targets=[Vector3(76.0,93,center+1.7),Vector3(72.1,93,center+1.7),Vector3(72.1,93,center+1.0),Vector3(69.85,93,center+1.0),Vector3(69.85,93,row.seated_eye[2])]
		elif number==422:
			targets=[Vector3(71.95,93,center-2.1),Vector3(71.95,93,center-1.0),Vector3(69.85,93,center-1.0),Vector3(69.85,93,row.seated_eye[2])]
		else:
			targets=[Vector3(72.35,93,center),Vector3(72.35,93,center+sign*1.0),Vector3(69.85,93,center+sign*1.0),Vector3(69.85,93,row.seated_eye[2])]
		for target in targets:check(await walk(target),"Original-controller atrium-bay route "+str(number)+" "+str(target))
		actor.set_physics_process(false)
	var passed:=true
	for item in checks:passed=passed and item.pass
	var out:=FileAccess.open(P+"evidence/CHECK_attempt003.json",FileAccess.WRITE);out.store_string(JSON.stringify({"pass":passed,"checks":checks,"routes":routes,"full_startup":false,"visual_accepted":false},"\t")+"\n");out.close()
	print("ATRIUM_INTERIOR_CHECK ",checks.size()," pass=",passed," route_legs=",routes.size())
	quit(0 if passed else 1)
