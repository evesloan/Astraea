extends RefCounted
# Exact omitted native image/Mix multipliers; original resources remain immutable.
static func build(ship:Node3D)->Dictionary:
	var definition:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group5/LARGE_VENUE_MATERIAL_FACTORS.json"))
	var result:Dictionary={"venues":0,"selected_surfaces":0,"unselected_surfaces":0,"source_material_bindings":int(definition.material_bindings)}
	for row in definition.venues:
		assert(FileAccess.get_sha256(str(row.model_path))==str(row.model_sha256))
		var owner:Node3D=load("res://scripts/group5_large_venue_lighting.gd")._owner(ship,str(row.programme_key))
		assert(owner!=null)
		if owner.has_meta("group5_source_materials_applied"):
			var previous:Dictionary=owner.get_meta("group5_source_materials_applied")
			result.venues+=1;result.selected_surfaces+=int(previous.selected_surfaces);result.unselected_surfaces+=int(previous.unselected_surfaces)
			continue
		var by_name:Dictionary={}
		for item in row.materials:by_name[str(item.material_name)]=item
		var copies:Dictionary={}
		var selected:=0
		var untouched:=0
		for mesh:MeshInstance3D in owner.find_children("*","MeshInstance3D",true,false):
			for surface in range(mesh.mesh.get_surface_count()):
				var original:Material=mesh.get_active_material(surface)
				var name:String=str(original.resource_name)
				if not by_name.has(name):untouched+=1;continue
				assert(original is BaseMaterial3D,"Original venue material is no longer a compatible PBR material")
				var spec:Dictionary=by_name[name]
				var expected:Color=_color(spec.original_export_factor).linear_to_srgb()
				assert(original.albedo_color.is_equal_approx(expected),"Current source factor preimage changed")
				var key:int=original.get_instance_id()
				if not copies.has(key):
					var revised:BaseMaterial3D=original.duplicate(false)
					revised.resource_name=name
					# Match Godot's glTF baseColorFactor import conversion exactly.
					revised.albedo_color=(original.albedo_color.srgb_to_linear()*_color(spec.factor_linear_rgba)).linear_to_srgb()
					revised.set_meta("group5_source_original_material",original)
					revised.set_meta("group5_source_material_factor",_color(spec.factor_linear_rgba))
					revised.set_meta("group5_native_material_name",str(spec.native_material))
					copies[key]=revised
				mesh.set_surface_override_material(surface,copies[key])
				selected+=1
		assert(selected>0 and copies.size()==by_name.size(),"Expected exact-source material bindings missing")
		var state:Dictionary={"selected_surfaces":selected,"unselected_surfaces":untouched,"material_copies":copies.size()}
		owner.set_meta("group5_source_materials_applied",state)
		result.venues+=1;result.selected_surfaces+=selected;result.unselected_surfaces+=untouched
	ship.set_meta("group5_large_venue_materials_attached",true)
	return result

static func _color(a:Array)->Color:return Color(a[0],a[1],a[2],a[3])
