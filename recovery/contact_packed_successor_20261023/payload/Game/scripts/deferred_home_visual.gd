extends RefCounted
# Retain room/door identities; instantiate immutable interior geometry only while resident.
static var occluders:Dictionary={}
static func bounds(scene:PackedScene,policy:Dictionary={})->AABB:
	var visual:Node3D=scene.instantiate()
	var box:=AABB()
	var first:=true
	var opaque_faces:Array[Vector3]=[]
	for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
		var pose:Transform3D=mesh.transform
		var parent:Node3D=mesh.get_parent()
		while parent!=visual:
			pose=parent.transform*pose
			parent=parent.get_parent()
		var part:AABB=pose*mesh.get_aabb()
		box=part if first else box.merge(part)
		first=false
		var opaque:=true
		for surface in range(mesh.mesh.get_surface_count()):
			var material:Material=mesh.get_active_material(surface)
			if not material is BaseMaterial3D or material.transparency!=BaseMaterial3D.TRANSPARENCY_DISABLED or material.albedo_color.a<.999:opaque=false
		if policy.has(str(mesh.name)):opaque=opaque and bool(policy[str(mesh.name)].opaque)
		if opaque:
			var faces:PackedVector3Array=mesh.mesh.get_faces()
			for i in range(0,faces.size()-2,3):
				var a:Vector3=pose*faces[i]
				var b:Vector3=pose*faces[i+1]
				var c:Vector3=pose*faces[i+2]
				if (b-a).cross(c-a).length()*.5>=2.0:opaque_faces.append_array([a,b,c])

	visual.free()
	var indices:=PackedInt32Array()
	indices.resize(opaque_faces.size())
	for i in range(indices.size()):indices[i]=i
	var shape:=ArrayOccluder3D.new()
	shape.set_arrays(PackedVector3Array(opaque_faces),indices)
	occluders[scene.get_instance_id()]=shape
	return box
static func install_occluder(ship:Node3D,room:Node3D,scene:PackedScene)->void:
	var witness:=OccluderInstance3D.new()
	witness.name=str(room.name)+"_RetainedOpaqueOccluder"
	witness.occluder=occluders[scene.get_instance_id()]
	ship.get_node("ShipSpace").add_child(witness)
	witness.global_transform=room.global_transform

static func ensure(room:Node3D)->void:
	var measure:=OS.get_environment("ASTRAEA_ROOM_ACTIVATION_METRICS")=="1"
	var begin:=Time.get_ticks_usec() if measure else 0
	if (not room.has_meta("deferred_visual_scene") and not room.has_meta("deferred_visual_path")) or room.has_meta("resident_visual"):return
	var scene:PackedScene=room.get_meta("deferred_visual_scene") if room.has_meta("deferred_visual_scene") else load(str(room.get_meta("deferred_visual_path")))
	var visual:Node3D=scene.instantiate()
	var instantiated:=Time.get_ticks_usec() if measure else 0
	visual.name="ResidentAuthoredInterior"
	room.add_child(visual)
	var meshes:=visual.find_children("*","MeshInstance3D",true,false)
	assert(meshes.size()==int(room.get_meta("deferred_visual_meshes")))
	var policy:Dictionary=room.get_meta("deferred_visual_collision_policy",{})
	var collidable:Array[Node]=[]
	for mesh in meshes:
		if not policy.is_empty():assert(policy.has(str(mesh.name)))
		if policy.is_empty() or bool(policy[str(mesh.name)].collide):collidable.append(mesh)
	var contact_begin:=Time.get_ticks_usec() if measure else 0
	load("res://scripts/route_activation_20261023/packed_contacts.gd").attach_group(visual,collidable)
	var contact_end:=Time.get_ticks_usec() if measure else 0
	for body:Node3D in visual.find_children("*","StaticBody3D",true,false):body.force_update_transform()
	room.set_meta("resident_visual",visual)
	if measure:
		room.set_meta("last_activation_metrics",{"room":str(room.name),"prototype":scene.resource_path,"instantiate_us":instantiated-begin,"attach_filter_us":contact_begin-instantiated,"contact_us":contact_end-contact_begin,"force_update_us":Time.get_ticks_usec()-contact_end,"mesh_count":meshes.size(),"collidable_mesh_count":collidable.size()})
static func release(room:Node3D)->void:
	if not room.has_meta("resident_visual"):return
	var visual:Node3D=room.get_meta("resident_visual")
	room.remove_meta("resident_visual")
	visual.free()
