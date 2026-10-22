extends RefCounted
const P:="res://quiet_grove_bank_20261022/"
static func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D)->Node3D:
	var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"ENCLOSURES_R002.json"))
	assert(FileAccess.get_sha256(P+"PACKAGE.json")==plan.package_sha256)
	var district:Node3D=load(P+"adapter.gd").build(ship)
	var manager:Node=ship.private_detail_residency
	var package:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PACKAGE.json"))
	for room in plan.rooms:
		var entries:Array=manager.entries.filter(func(e):return str(e.record.model_file)==str(room.model_file));assert(entries.size()==1)
		var entry:Dictionary=entries[0];var home:Node3D=entry.home.get_ref()
		var shells:Array=home.get_children().filter(func(c):return c.scene_file_path==str(entry.record.shell_path));assert(shells.size()==1)
		var shell:Node3D=shells[0]
		assert(not shell.has_meta("complete_enclosure_r002"))
		# Rebuild exact contacts and occluders after relocating the complete fixed assembly.
		for body in shell.find_children("*","StaticBody3D",true,false):
			assert(body.name=="RoomStaticContacts" or body.name=="StaticContact");body.free()
		var old_occluders:=shell.get_node_or_null("VerifiedStaticOpaqueFaceOccluders")
		if old_occluders!=null:old_occluders.free()
		if shell.has_meta("static_occlusion_registered"):shell.remove_meta("static_occlusion_registered")
		for part in room.parts:
			var mesh:=shell.find_child(str(part.name),true,false)as MeshInstance3D
			assert(mesh!=null and mesh.mesh!=null and mesh.get_meta("extras",{}).get("construction_role","")=="cocoon_privacy")
			var delta:=Transform3D(Basis(Vector3.UP,float(part.yaw_delta)),v(part.target)) * Transform3D(Basis.IDENTITY,-v(part.source))
			mesh.transform=delta*mesh.transform
			var bounds:AABB=shell.global_transform.affine_inverse()*mesh.global_transform*mesh.get_aabb()
			assert(bounds.position.distance_to(v(part.expected_min))<.001 and bounds.end.distance_to(v(part.expected_max))<.001,"Native/runtime complete enclosure bounds disagree")
		manager.contacts(shell)
		var source_room:Dictionary=package.rooms.filter(func(r):return str(r.model_file)==str(room.model_file))[0]
		load(P+"adapter.gd").decorate_shell(shell,source_room)
		load("res://scripts/static_room_occlusion.gd").install(shell)
		shell.set_meta("complete_enclosure_r002",true);home.set_meta("complete_enclosure_view_clearance_m",room.complete_liner_view_clearance_m)
	district.set_meta("complete_enclosures_corrected",23);district.set_meta("fixed_enclosure_parts_corrected",217)
	return district
