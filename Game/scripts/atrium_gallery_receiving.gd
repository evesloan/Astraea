extends RefCounted
static func build(ship:Node3D)->Node3D:
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/ATRIUM_GALLERY_RECEIVING.json"))
	var parent:=Node3D.new();parent.name="AtriumGalleryFittings";ship.get_node("ShipSpace/Districts").add_child(parent)
	for item in data.rooms:
		var path:String="res://assets/models/"+str(item.model_file)
		assert(FileAccess.get_sha256(path)==item.export_sha256)
		var room:=Node3D.new();room.name=str(item.id);parent.add_child(room)
		room.position=Vector3(item.origin_world_xyz[0],item.origin_world_xyz[1],item.origin_world_xyz[2])
		room.set_meta("catalogue_id",item.catalogue_id);room.set_meta("finished",false)
		room.set_meta("source_commit",data.source_commit)
		var visual:Node3D=load(path).instantiate();visual.name="SourceVisual";room.add_child(visual)
		for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
			if str(mesh.get_meta("extras",{}).get("contact_category",""))=="solid":load("res://scripts/static_contact_cache.gd").attach(mesh)
		for binding in item.lights:
			var light:=SpotLight3D.new();light.name=str(item.id)+"_"+str(binding.id);room.add_child(light)
			light.position=Vector3(binding.position_local_xyz[0],binding.position_local_xyz[1],binding.position_local_xyz[2])
			light.rotation.x=-PI/2;light.spot_range=float(binding.range_m);light.spot_angle=float(binding.spot_angle_deg)
			light.light_energy=float(binding.energy_proposal);light.light_color=Color(binding.color_rgb[0],binding.color_rgb[1],binding.color_rgb[2]);light.shadow_enabled=true
	return parent
