extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea");paused=true
	var space:=ship.get_world_3d().direct_space_state;var errors:Array=[];var witnesses:Array=[]
	var owner:Node3D=ship.get_node("ShipSpace/CentralResidentialStreetFloors/D16_STAR_ATLAS_MISSING_STREET_1")
	for x in [-62.75,-60.25]:
		for z in [29.2,31.0]:
			for dx in [-.16,0,.16]:
				for dz in [-.16,0,.16]:
					var p:=Vector3(x+dx,97.5,z+dz)
					var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(p+Vector3.UP*.04,p-Vector3.UP*.04))
					var ok:bool=not hit.is_empty()and owner.is_ancestor_of(hit.collider)and absf(hit.position.y-97.5)<.002
					witnesses.append({"point":str(p),"owner":str(owner.name),"matched":ok,"excludes":0})
					if not ok:errors.append({"kind":"D16_source_footprint","point":str(p),"hit":str(hit.get("position","none"))})
			var q:=PhysicsShapeQueryParameters3D.new();var box:=BoxShape3D.new();box.size=Vector3(.32,4.18,.32);box.margin=.001;q.shape=box;q.transform=Transform3D(Basis.IDENTITY,Vector3(x,99.62,z))
			var occupied:=space.intersect_shape(q,32)
			if not occupied.is_empty():errors.append({"kind":"pier_column_clearance","position":str(q.transform.origin),"hits":str(occupied)})
	for item in [{"name":"SA_LongBeam_-64.2_106.26","at":Vector3(-64.02,106.12,12.6),"delta":Vector3(.03,0,0)},{"name":"SA_CrossBeam_12.7_106.26","at":Vector3(-66.7,106.12,12.88),"delta":Vector3(0,0,.03)}]:
		var node:Node3D=ship.find_child(str(item.name).replace(".","_"),true,false);var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(item.at+item.delta,item.at-item.delta))
		var ok:bool=node!=null and not hit.is_empty()and node.is_ancestor_of(hit.collider)
		witnesses.append({"point":str(item.at),"owner":item.name,"matched":ok,"excludes":0})
		if not ok:errors.append({"kind":"retained_top_frame","expected":item.name,"hit":str(hit),"actual_owner":str(hit.collider.get_parent().get_path())if not hit.is_empty()else"none"})
	var roofs:Array=[]
	for at in [Vector3(-65,106.26,15.8),Vector3(-61.5,106.26,22),Vector3(-61.5,106.26,30),Vector3(-61.5,106.26,35.6)]:
		var h:=space.intersect_ray(PhysicsRayQueryParameters3D.create(at-Vector3.UP*.03,at+Vector3.UP*.03))
		roofs.append({"at":str(at),"hit":str(h.get("position","none")),"owner":str(h.collider.get_path())if not h.is_empty()else"none"})
	var report={"status":"PASS"if errors.is_empty()else"FAIL","stage":"actual baseline before receiving construction","source_witnesses":witnesses,"source_roof_receiving":roofs,"pier_volume_clearance_checks":4,"errors":errors,"limits":"Geometric source bearings/clearance only; primary engineering load design remains open"}
	FileAccess.open("/tmp/astraea_d17_receiving_preimage.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "));print(JSON.stringify(report));quit(0 if errors.is_empty()else 1)
