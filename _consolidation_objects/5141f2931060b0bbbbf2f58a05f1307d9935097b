extends SceneTree
func _initialize():call_deferred("run")
func run():
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(12):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var annex:Node3D=ship.get_node("ShipSpace/Districts/AquaticRiverSlideAnnex_WIP")
	assert(annex.global_transform==Transform3D.IDENTITY)
	assert(annex.get_node("ExactAquaticArchitecture").find_children("*","MeshInstance3D",true,false).size()==79)
	assert(annex.get_node("AquaticAnnexOwnedSlabs").get_child_count()==4)
	assert(annex.find_children("*","OmniLight3D",true,false).size()==14)
	var failures:Array=[];var results:Array=[]
	var space=annex.get_world_3d().direct_space_state
	var probes:Array=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/AQUATIC_ANNEX_PROBES.json"))
	probes.append({"id":"retained_public_seam","xyz":[53.99,44,240]})
	for p in probes:
		var xyz:Array=p.xyz;var point:=Vector3(xyz[0],xyz[1],xyz[2])
		var ray:=PhysicsRayQueryParameters3D.create(point+Vector3.UP*.16,point-Vector3.UP*.44)
		ray.hit_back_faces=false
		var hit=space.intersect_ray(ray)
		var ok:bool=not hit.is_empty() and absf(hit.position.y-point.y)<.06
		var capsule:=CapsuleShape3D.new();capsule.radius=.3;capsule.height=2.2
		var query:=PhysicsShapeQueryParameters3D.new();query.shape=capsule;query.transform=Transform3D(Basis.IDENTITY,point+Vector3.UP*1.15);query.margin=.001
		var obstruction=space.intersect_shape(query,8)
		results.append({"id":p.id,"floor":ok,"obstructions":obstruction.size()})
		if not ok or not obstruction.is_empty():failures.append(p.id)
	for mesh:MeshInstance3D in annex.get_node("ExactAquaticArchitecture").find_children("*","MeshInstance3D",true,false):
		var kind:String=mesh.get_meta("aquatic_contact_role")
		if kind in ["water_visual","tube_static_visual","plant_static","fixture_lens"]:assert(mesh.get_node_or_null("StaticContact")==null)
	var report={"status":"PASS" if failures.is_empty() else "FAIL","checks":results,"failures":failures,"meshes":79,"owned_floor_regions":4,"physical_light_sources":14,"scope":"Actual integrated main scene, imported identity/collision policy, 17 stationary floor/clearance probes; not full traversal, service route, water gameplay or final art acceptance."}
	FileAccess.open("res://artifacts/aquatic_annex_install.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
	print("AQUATIC ANNEX ",report.status," ",failures)
	quit(0 if failures.is_empty() else 1)
