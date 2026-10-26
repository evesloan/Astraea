extends RefCounted
# Preserve receiving-edited walls as independent contacts; consolidate only static source triangles.
const RECEIVERS:={"D12_directory_02":"library_receiving", "D11_directory_08":"music_receiving", "D11_directory_09":"performers_receiving", "D11_directory_02":"cinema1_receiving", "D10_directory_09":"moonfruit_service"}
static func wall_names(key:String)->Dictionary:
	var names:Dictionary={}
	if RECEIVERS.has(key):
		var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/"+str(RECEIVERS[key])+"_20261016/NATIVE_VERIFICATION.json"))
		for row in p.walls:names[str(row.source_name)]=true
	return names
static func visual_border(mesh:MeshInstance3D,key:String)->bool:
	var n:=str(mesh.name).replace(".","_")
	return key=="D11_directory_02" and (n.begins_with("WP13_C1_R01_P01_bay_") or n.begins_with("WP13_C1_R01_P20_bay_")) and (n.ends_with("bay_front") or n.ends_with("bay_side") or n.ends_with("bay_side_001"))
static func attach(source:Node3D,meshes:Array[Node],key:String)->void:
	var walls:=wall_names(key)
	var immutable:Array[Node]=[]
	for mesh:MeshInstance3D in meshes:
		if visual_border(mesh,key):
			mesh.set_meta("receiving_collision_policy","visual bay border")
			continue
		var independent:=walls.has(str(mesh.name))
		var ancestor:Node=mesh
		while ancestor!=source:
			if ancestor.get_script()!=null or ancestor is CollisionObject3D or (ancestor is Node3D and ancestor.top_level):independent=true
			ancestor=ancestor.get_parent()
			assert(ancestor!=null)
		if independent:load("res://scripts/static_contact_cache.gd").attach(mesh)
		else:immutable.append(mesh)
	# Existing implementation leaves translucent/glass meshes independently queryable.
	load("res://scripts/static_contact_cache.gd").attach_group(source,immutable)
