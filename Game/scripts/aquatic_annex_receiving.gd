extends RefCounted
# Source-faithful aquatic annex construction. Water/tubes remain visual, not ride gameplay.
static func build(parent:Node3D, ship:Node3D)->Node3D:
	var root:=Node3D.new()
	root.name="AquaticRiverSlideAnnex_WIP"
	root.set_meta("programme_key","D08_directory_08")
	root.set_meta("persistent_id","aquatic_river_slide_annex_001")
	root.set_meta("source_commit","014bc41cac4c80175773f28de466868206ff23a9")
	root.set_meta("final_art_accepted",false)
	root.set_meta("water_gameplay_implemented",false)
	root.set_meta("service_onward_connection","unresolved")
	parent.add_child(root)
	var floors:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/AQUATIC_ANNEX_FLOORS.json"))
	for path in floors.source_checks.retained_input_hashes:
		assert(FileAccess.get_sha256("res://"+str(path))==str(floors.source_checks.retained_input_hashes[path]))
	load("res://scripts/structural_floor_builder.gd").build_regions(root,ship.stone,ship.ivory,floors.regions,{},"AquaticAnnexOwnedSlabs")
	var path:="res://assets/models/AST-AQU-ANNEX-001.glb"
	assert(FileAccess.get_sha256(path)=="19636ebb0fcc7832143927f61bdbecda3d85a07c07386057c7eda91f5320b76d")
	var visual:Node3D=(load(path) as PackedScene).instantiate()
	visual.name="ExactAquaticArchitecture"
	root.add_child(visual)
	var policy:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/AQUATIC_ANNEX_COLLISION_POLICY.json"))
	var contacts:=0
	for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
		var key:=str(mesh.name)
		assert(policy.has(key),"Unreviewed aquatic contact: "+key)
		var kind:=str(policy[key])
		mesh.set_meta("aquatic_contact_role",kind)
		if kind not in ["water_visual","tube_static_visual","plant_static","fixture_lens"]:
			load("res://scripts/static_contact_cache.gd").attach(mesh)
			contacts+=1
		if kind=="fixture_lens":mesh.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	root.set_meta("collidable_meshes",contacts)
	var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/AQUATIC_ANNEX_PLAN.json"))
	for item in plan.lights:
		var source:=OmniLight3D.new()
		source.name=str(item.id)+"_PhysicalSource"
		root.add_child(source)
		source.position=Vector3(item.xyz[0],item.xyz[1],item.xyz[2])
		source.light_energy=float(item.energy)
		source.omni_range=float(item.range_m)
		source.light_color=Color(1,.95,.86)
		source.shadow_enabled=true
		source.omni_shadow_mode=OmniLight3D.SHADOW_CUBE
		source.set_meta("illumination_anchor",Vector3(item.receiver_xyz[0],item.receiver_xyz[1],item.receiver_xyz[2]))
	return root
