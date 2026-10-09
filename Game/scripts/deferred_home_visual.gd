extends RefCounted
# Retain room/door identities; instantiate immutable interior geometry only while resident.
static var occluders:Dictionary={}
static func bounds(scene:PackedScene)->AABB:
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
	if not room.has_meta("deferred_visual_scene") or room.has_meta("resident_visual"):return
	var scene:PackedScene=room.get_meta("deferred_visual_scene")
	var visual:Node3D=scene.instantiate()
	visual.name="ResidentAuthoredInterior"
	room.add_child(visual)
	var meshes:=visual.find_children("*","MeshInstance3D",true,false)
	assert(meshes.size()==int(room.get_meta("deferred_visual_meshes")))
	load("res://scripts/static_contact_cache.gd").attach_group(visual,meshes)
	for body:Node3D in visual.find_children("*","StaticBody3D",true,false):body.force_update_transform()
	room.set_meta("resident_visual",visual)
static func release(room:Node3D)->void:
	if not room.has_meta("resident_visual"):return
	var visual:Node3D=room.get_meta("resident_visual")
	room.remove_meta("resident_visual")
	visual.free()
