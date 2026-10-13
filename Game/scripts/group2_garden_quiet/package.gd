extends RefCounted
static func build_source_fixture(parent:Node3D,kind:String)->Node3D:
	assert(parent.has_meta("group2_isolated_source_fixture"))
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_garden_quiet/COMPONENTS_r002.json"))
	var section:=Node3D.new();section.name=kind;parent.add_child(section)
	var visual:Node3D=(load("res://assets/group2_garden_quiet/"+kind+"_r002.glb")as PackedScene).instantiate();section.add_child(visual)
	load("res://scripts/static_contact_cache.gd").attach_group(visual,visual.find_children("*","MeshInstance3D",true,false))
	for row in data.lights:
		if row.kind!=kind:continue
		assert(visual.find_child(str(row.source_mesh),true,false)!=null)
		var light:=OmniLight3D.new();light.position=Vector3(row.world_xyz[0],row.world_xyz[1],row.world_xyz[2]);light.omni_range=row.range;light.light_energy=row.energy;light.light_color=Color(1,.86,.68);light.shadow_enabled=true;light.visible=false;section.add_child(light)
	section.set_meta("production_adoption",false);return section

# Consumer admission wrapper; source build_source_fixture remains unchanged.
static func build_on_current_receivers(ship:Node3D)->Node3D:
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_garden_quiet/COMPONENTS_r002.json"))
	var space:Node3D=ship.get_node("ShipSpace");assert(space.get_node_or_null("Group2GardenQuietReceiving")==null)
	var scenes:Dictionary={}
	for row in data.exports:
		var path:String="res://"+str(row.path).trim_prefix("Game/");assert(FileAccess.get_sha256(path)==str(row.sha256))
		var packed:PackedScene=load(path);assert(packed!=null);scenes[row.kind]=packed
	var receivers:Dictionary={"family_hydroponics":"ShipSpace/Districts/FamilyTerraceReceivingCandidate","quiet_meditation":"ShipSpace/Districts/QuietGroveReceivingCandidate"}
	for row in data.rows:
		assert(FileAccess.get_sha256("res://assets/models/"+str(row.source_model))==str(row.source_sha256))
		var receiver:Node3D=ship.get_node_or_null(str(receivers[row.kind]));assert(receiver!=null and receiver.global_transform.is_equal_approx(Transform3D.IDENTITY))
	var root:=Node3D.new();root.name="Group2GardenQuietReceiving";space.add_child(root)
	root.set_meta("default_main_adoption",true);root.set_meta("new_floor_owners",0);root.set_meta("new_room_or_berth_capacity",0);root.set_meta("agricultural_service_operation",false);root.set_meta("programme_admission_accepted",false);root.set_meta("source_receiver_paths",receivers)
	var lights:Array[Light3D]=[]
	for row in data.rows:
		var section:=Node3D.new();section.name=str(row.kind);root.add_child(section)
		var visual:Node3D=scenes[row.kind].instantiate();visual.name=str(row.kind)+"_r002";section.add_child(visual)
		load("res://scripts/static_contact_cache.gd").attach_group(visual,visual.find_children("*","MeshInstance3D",true,false))
		for emitter in data.lights:
			if str(emitter.kind)!=str(row.kind):continue
			assert(visual.find_child(str(emitter.source_mesh),true,false)!=null)
			var light:=OmniLight3D.new();light.name=str(emitter.source_mesh)+"_PhysicalSource";light.position=Vector3(emitter.world_xyz[0],emitter.world_xyz[1],emitter.world_xyz[2]);light.omni_range=emitter.range;light.light_energy=emitter.energy;light.light_color=Color(1,.86,.68);light.shadow_enabled=false;light.visible=false;section.add_child(light);light.set_meta("fixture_powered",true);lights.append(light)
		section.set_meta("agriculture_body_acoustic_egress_structural_or_final_art_accepted",false)
	load("res://scripts/receiving_source_lights.gd").register(lights,ship)
	return root
