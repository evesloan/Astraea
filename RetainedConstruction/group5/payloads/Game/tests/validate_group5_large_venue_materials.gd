extends SceneTree
var errors:Array=[]
var checks:=0
func check(label:String,ok:bool)->void:
	checks+=1
	if not ok:errors.append(label)
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(20):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency")
	residency.enabled=false;actor.set_controls_enabled(false);actor.set_physics_process(false)
	var lighting=load("res://scripts/group5_large_venue_lighting.gd")
	if not ship.get_meta("group5_large_venue_lighting_attached",false):lighting.build(ship)
	var definition:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group5/LARGE_VENUE_MATERIAL_FACTORS.json"))
	var startup_attached:bool=ship.get_meta("group5_large_venue_materials_attached",false)
	var originals:Dictionary={}
	var poses:Dictionary={}
	for row in definition.venues:
		var owner:Node3D=lighting._owner(ship,str(row.programme_key))
		for mesh:MeshInstance3D in owner.find_children("*","MeshInstance3D",true,false):
			poses[mesh.get_instance_id()]={"mesh":mesh,"pose":lighting._relative_transform(mesh,owner),"owner":owner,"geometry":mesh.mesh}
			for s in range(mesh.mesh.get_surface_count()):
				var current:Material=mesh.get_active_material(s)
				originals[str(mesh.get_instance_id())+":"+str(s)]=current.get_meta("group5_source_original_material",current)
	var builder=load("res://scripts/group5_large_venue_materials.gd")
	var changed:Dictionary=builder.build(ship)
	check("five_original_venues",int(changed.venues)==5)
	check("eight_exact_source_bindings",int(changed.source_material_bindings)==8)
	check("repeat_build_reuses_materials",builder.build(ship)==changed)
	var selected:=0;var unselected:=0;var properties:=0
	var references:Array=[]
	for row in definition.venues:
		var owner:Node3D=lighting._owner(ship,str(row.programme_key))
		var importer:=GLTFDocument.new();var state:=GLTFState.new()
		var result:int=importer.append_from_file("/tmp/group5-native-factor-importer-references/"+str(row.programme_key)+".glb",state)
		check(str(row.programme_key)+" independent_reference_import",result==OK)
		var reference:Node3D=importer.generate_scene(state);references.append(reference)
		var imported:Dictionary={}
		for mesh:MeshInstance3D in reference.find_children("*","MeshInstance3D",true,false):
			for s in range(mesh.mesh.get_surface_count()):
				var m:Material=mesh.get_active_material(s);imported[str(m.resource_name)]=m
		var names:Array=[]
		for spec in row.materials:names.append(str(spec.material_name))
		var revised_ids:Array=[]
		for mesh:MeshInstance3D in owner.find_children("*","MeshInstance3D",true,false):
			var retained:Dictionary=poses[mesh.get_instance_id()]
			check(str(mesh.get_instance_id())+" unchanged_geometry_pose",mesh.mesh==retained.geometry and lighting._relative_transform(mesh,owner).is_equal_approx(retained.pose))
			for s in range(mesh.mesh.get_surface_count()):
				var original:Material=originals[str(mesh.get_instance_id())+":"+str(s)]
				var actual:Material=mesh.get_active_material(s)
				if not str(original.resource_name) in names:
					check(str(mesh.get_instance_id())+str(s)+" unselected_original_resource",actual==original);unselected+=1;continue
				selected+=1
				check(str(mesh.get_instance_id())+str(s)+" exact_native_factor_importer_color",actual.albedo_color.is_equal_approx(imported[str(original.resource_name)].albedo_color))
				check(str(mesh.get_instance_id())+str(s)+" immutable_original_color",original.albedo_color.is_equal_approx(Color.WHITE))
				for prop in original.get_property_list():
					var name:String=str(prop.name)
					if not int(prop.usage)&PROPERTY_USAGE_STORAGE or name in ["albedo_color","resource_path"] or name.begins_with("metadata/"):continue
					check(str(mesh.get_instance_id())+str(s)+" original_property_"+name,actual.get(name)==original.get(name));properties+=1
				revised_ids.append(actual.get_instance_id())
		actor.global_position=Vector3(1000,1000,1000);residency.refresh(9)
		check(str(row.programme_key)+" cached_detach",not owner.is_inside_tree())
		residency.prepare_position(owner.position+Vector3(0,.03,34))
		for i in range(3):await physics_frame
		check(str(row.programme_key)+" cached_return",owner.is_inside_tree())
		var returned:Array=[]
		for mesh:MeshInstance3D in owner.find_children("*","MeshInstance3D",true,false):
			for s in range(mesh.mesh.get_surface_count()):
				var material:Material=mesh.get_active_material(s)
				if material.has_meta("group5_source_material_factor"):returned.append(material.get_instance_id())
		check(str(row.programme_key)+" exact_material_instances_return",revised_ids==returned)
	for reference:Node in references:reference.free()
	var out:Dictionary={"status":"PASS" if errors.is_empty() else "HOLD","checks":checks,"errors":errors,"venues":5,"source_material_bindings":8,"selected_surfaces":selected,"unselected_surfaces":unselected,"unchanged_material_properties_checked":properties,"builder_attached_during_main_startup":startup_attached,"fixture":"Actual main with source lighting plus scoped material correction;independent native-factor glTF importer references", "scope":"Native image/Mix factors,importer-equivalent color conversion,all other original material properties and texture resource identities,unselected materials,unchanged meshes/poses and five cached returns;not full shader,pixel,CRT,commerce,hardware or whole-group acceptance.","whole_group_accepted":false}
	FileAccess.open("res://artifacts/group5_large_venue_materials.json",FileAccess.WRITE).store_string(JSON.stringify(out,"  "))
	print("GROUP5_LARGE_VENUE_MATERIALS ",JSON.stringify(out));quit(0 if errors.is_empty() else 1)
