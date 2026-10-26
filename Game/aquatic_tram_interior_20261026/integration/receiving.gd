extends RefCounted
const P:="res://aquatic_tram_interior_20261026/"

static func build(assembly:Node3D)->void:
	assert(not assembly.has_node("AquaticInteriorReceiving"))
	var receiving:Node3D=load(P+"integration/assembly.gd").raw_model(P+"r007/AquaticIntegratedReceiving.glb")
	assert(receiving!=null);receiving.name="AquaticInteriorReceiving";assembly.add_child(receiving)
	var fixed:Array[Node]=[];var rolling:Array[Node]=[];var meshes:=0;var plants:=0
	var glass:=ShaderMaterial.new();glass.shader=load("res://shaders/hospitality_glass.gdshader")
	var metal:Material=null
	for mesh:MeshInstance3D in receiving.find_children("*","MeshInstance3D",true,false):
		meshes+=1;var label:=str(mesh.name)
		if label.begins_with("Aquatic_Rail") or label=="Aquatic_ContinuousWeb":rolling.append(mesh);continue
		if label.begins_with("NorthCanopy_") or label.begins_with("NorthShrub_") or label.begins_with("NorthGroundcover_") or label.begins_with("RefugeShrub_") or label.begins_with("RefugeGroundcover_"):
			plants+=1
			# Retained canopy trunks remain physical; leaves/flowers are detail.
			if label.begins_with("NorthCanopy_") and "bark" in mesh.get_active_material(0).resource_name.to_lower():fixed.append(mesh)
			continue
		if "Source_Lamp_" in label:
			if "Opal" in label:mesh.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			continue
		if "GuardGlass" in label:mesh.material_override=glass
		if label.begins_with("AquaticRouteBearing_"):metal=mesh.get_active_material(0)
		fixed.append(mesh)
	assert(meshes==555 and plants>100 and metal!=null,"Complete authored guest receiving required")
	# Close the retired lower access edges without fabricating the unsupported
	# remainder of the original lift recess. Original route overlap is restored
	# separately by the exact named floor successor.
	var guards:=[
		[Vector3(3.94,53.10,230.4),Vector3(.12,1.2,4.0)],
		[Vector3(5.9,53.10,228.34),Vector3(3.8,1.2,.12)],
		[Vector3(7.74,53.10,219.7),Vector3(.12,1.2,17.4)]]
	for i in range(guards.size()):
		var mesh:=MeshInstance3D.new();mesh.name="RetiredAftDockLowerEdgeGuard_"+str(i)
		var box:=BoxMesh.new();box.size=guards[i][1];box.material=metal;mesh.mesh=box
		receiving.add_child(mesh);mesh.position=guards[i][0];fixed.append(mesh)
	for row in [["FixedReceivingContacts",fixed],["RollingGuidewayContacts",rolling]]:
		var owner:=Node3D.new();owner.name=row[0];receiving.add_child(owner)
		for mesh:Node3D in row[1]:mesh.reparent(owner,true)
		load("res://scripts/static_contact_cache.gd").attach_group(owner,row[1])
	var receipt:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"r002/BUILD.json"))
	assert(receipt.lights.size()==2)
	for item:Dictionary in receipt.lights:
		var light:=OmniLight3D.new();light.name=item.source_fixture+"_OperatingLight";receiving.add_child(light)
		# Emission point clears the original east-facing lens; the lens is not
		# allowed to shadow itself. Source energy/range and selector stay intact.
		light.position=Vector3(item.xyz[0]+.08,item.xyz[1],item.xyz[2]);light.omni_range=item.range
		light.light_energy=item.energy;light.light_color=Color(item.color[0],item.color[1],item.color[2])
		light.shadow_enabled=true;light.visible=false;light.omni_shadow_mode=OmniLight3D.SHADOW_CUBE
		light.set_meta("source_fixture",item.source_fixture);light.set_meta("fixture_powered",true)
	receiving.set_meta("authored_meshes",meshes);receiving.set_meta("retained_plant_placements",35)
	receiving.set_meta("retained_benches",3);receiving.set_meta("final_visual_acceptance",false)
