extends SceneTree
const P:="res://night_garden_receiving_courts_20261022/"
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
	for frame in range(1100):
		var delta:=target-actor.global_position;delta.y=0
		if delta.length()<.13:
			key(false)
			for settle in range(8):await physics_frame
			routes.append({"target":str(target),"actual":str(actor.global_position)})
			return actor.is_on_floor() and absf(actor.global_position.y-target.y)<.10
		actor.rotation.y=atan2(-delta.x,-delta.z);key(true);await physics_frame
	key(false);routes.append({"target":str(target),"actual":str(actor.global_position),"timeout":true});return false
func run()->void:
	var host:Node3D=load("res://scripts/atrium_interior_integration_20261022/fixture_host.gd").new();root.add_child(host)
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
	await host._construction_step("central_homes/night_garden_residency_20261022")
	var courts:Node3D=load(P+"adapter.gd").build(host)
	await physics_frame;await physics_frame
	var rows:Array=[]
	for z in [-35.5,35.5]:
		for y in [93.15,94.0,94.7]:
			var hit:=host.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(84,y,z),Vector3(55.8,y,z)))
			rows.append({"z":z,"y":y,"hit":str(hit.get("position")),"owner":str(hit.collider.get_path()) if not hit.is_empty() else "none"})
		for x in [84,82,81.8,80,70,60,58,56.1]:
			var hit:=host.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(x,93.1,z),Vector3(x,92.5,z)))
			rows.append({"floor_x":x,"z":z,"hit":str(hit.get("position")),"owner":str(hit.collider.get_path()) if not hit.is_empty() else "none"})
	var out:=FileAccess.open(P+"evidence/SEAM_CONTACT.json",FileAccess.WRITE);out.store_string(JSON.stringify(rows,"\t")+"\n");out.close();print(JSON.stringify(rows));quit()
