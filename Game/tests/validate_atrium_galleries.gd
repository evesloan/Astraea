extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	var ship:Node3D=main.get_node("World360/Astraea")
	for i in range(6):await physics_frame
	var registry:Node=ship.get_node("ShipSystems/ReceivedRoomResidency");registry.enabled=false
	var rooms:Dictionary={}
	for entry in registry.entries:
		if str(entry.parent.name)=="AtriumGalleryFittings":
			if entry.room.get_parent()==null:entry.parent.add_child(entry.room)
			rooms[str(entry.room.name)]=entry.room
	assert(rooms.size()==15)
	for i in range(4):await physics_frame
	paused=true
	var exclusions:Array[RID]=[]
	for body in ship.find_children("*","CharacterBody3D",true,false):exclusions.append(body.get_rid())
	for body in ship.find_children("*","RigidBody3D",true,false):exclusions.append(body.get_rid())
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/ATRIUM_GALLERY_RECEIVING.json"))
	var physics:=ship.get_world_3d().direct_space_state
	var errors:Array=[];var floors:=0;var contacts:=0;var lights:=0;var solid_meshes:=0
	var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
	for item in data.rooms:
		var room:Node3D=rooms[str(item.id)];assert(not room.get_meta("finished"))
		for mesh:MeshInstance3D in room.find_children("*","MeshInstance3D",true,false):
			var solid:bool=str(mesh.get_meta("extras",{}).get("contact_category",""))=="solid"
			assert((not mesh.find_children("*","StaticBody3D",true,false).is_empty())==solid)
			if solid:solid_meshes+=1
		for light in room.find_children("*","Light3D",true,false):
			assert(light in budget.sources);lights+=1
		for z in [1.0,3.0,5.0]:
			var p:Vector3=room.global_position+Vector3(.4,0,z);floors+=1
			var ray:=PhysicsRayQueryParameters3D.create(p+Vector3.UP*.2,p-Vector3.UP*.35);ray.exclude=exclusions
			var hit:=physics.intersect_ray(ray)
			if hit.is_empty() or absf(hit.position.y-p.y)>.035:errors.append({"kind":"floor","room":item.id,"point":str(p)})
			var q:=PhysicsShapeQueryParameters3D.new();var cap:=CapsuleShape3D.new();cap.radius=.3;cap.height=1.8;q.shape=cap;q.exclude=exclusions;q.margin=.001;q.transform.origin=p+Vector3.UP*.925
			for collision in physics.intersect_shape(q,8):errors.append({"kind":"standing","room":item.id,"point":str(p),"collider":str(collision.collider.get_path())})
		for foot in item.foot_contacts:
			var centre:=Vector3.ZERO
			for v in foot.boundary:centre+=Vector3(v[0],0,v[1])
			centre/=foot.boundary.size();var p:Vector3=room.global_position+centre;contacts+=1
			var ray:=PhysicsRayQueryParameters3D.create(p+Vector3.UP*.008,p-Vector3.UP*.035);ray.exclude=exclusions
			var hit:=physics.intersect_ray(ray)
			if hit.is_empty() or absf(hit.position.y-p.y)>.02:errors.append({"kind":"bearing_floor","room":item.id,"object":foot.object})
	assert(lights==30 and solid_meshes>0)
	var result:Dictionary={"status":"PASS" if errors.is_empty() else "FAIL","installed_galleries":15,"registered_lights":lights,"solid_meshes":solid_meshes,"floor_capsule_points":floors,"bearing_probes":contacts,"errors":errors,"limits":"Actual-main bounded source contacts and residency/light registration; no complete route, interaction, target-GPU or final visual acceptance"}
	FileAccess.open("res://artifacts/atrium_galleries.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print("ATRIUM_GALLERIES ",JSON.stringify(result));quit(0 if errors.is_empty() else 1)
