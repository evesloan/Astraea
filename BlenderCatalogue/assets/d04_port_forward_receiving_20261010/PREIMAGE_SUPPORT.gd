extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea");paused=true
	var space:=ship.get_world_3d().direct_space_state;var rows:Array=[];var errors:Array=[];var volumes:Array=[]
	var feet:Array=[]
	for x in [-43.7,-32.0,-20.0,-8.5]:
		for z in [-406.65,-403.75]:feet.append({"x":x,"z":z,"y":12.0,"owner":"D03_protected_crew_cover","wall_contact_allowed":false})
	for x in [-58.62,-55.38]:
		for z in [-442.0,-424.0,-406.0,-388.0,-370.0]:feet.append({"x":x,"z":z,"y":12.0,"owner":"D03_port_forward_staff_floor_0","wall_contact_allowed":true})
	for x in [-58.62,-55.38]:
		for z in [-379.5,-373.5,-367.5]:feet.append({"x":x,"z":z,"y":12.0,"owner":"D03_port_forward_staff_floor_0","wall_contact_allowed":true})
	for f in feet:
		var owner:Node=ship.find_child(f.owner,true,false);var at:=Vector3(f.x,f.y,f.z)
		for dx in [-.14,0,.14]:
			for dz in [-.14,0,.14]:
				var p:=at+Vector3(dx,0,dz);var h:=space.intersect_ray(PhysicsRayQueryParameters3D.create(p+Vector3.UP*.035,p-Vector3.UP*.035))
				var ok:bool=owner!=null and not h.is_empty()and owner.is_ancestor_of(h.collider)and absf(h.position.y-f.y)<.002
				rows.append({"at":str(p),"owner":f.owner,"matched":ok,"ray_excludes":0});if not ok:errors.append({"foot":f,"at":str(p),"hit":str(h.get("position","none"))})
		var q:=PhysicsShapeQueryParameters3D.new();var shape:=BoxShape3D.new();shape.size=Vector3(.28,16.24-f.y,.28);shape.margin=.001;q.shape=shape;q.transform=Transform3D(Basis.IDENTITY,Vector3(f.x,(16.26+f.y)/2,f.z));var hits:=space.intersect_shape(q,64);var paths:Array=[];var bad:Array=[]
		for h in hits:
			var path:=str(h.collider.get_path());paths.append(path)
			if not f.wall_contact_allowed or not("LowerStaffEnclosure"in path or "D03_port_forward_staff_floor_0"in path or "D02_port_forward_staff_floor_0"in path):bad.append(path)
		volumes.append({"foot":f,"contact_owners":paths,"unexpected_owners":bad,"source_wall_joints_explicit":f.wall_contact_allowed});if not bad.is_empty():errors.append({"volume":f,"unexpected":bad})
	var core:Node=ship.find_child("D04_fore_route",true,false);var h:=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(-3.98,16.53,-405.2),Vector3(-3.98,16.47,-405.2)));var ok:bool=core!=null and not h.is_empty()and core.is_ancestor_of(h.collider);if not ok:errors.append({"public_floor":str(h)})
	var r={"status":"PASS"if errors.is_empty()else"FAIL","foundation_feet":feet,"bearing_samples":rows,"column_preimages":volumes,"public_existing_axial_arrival_floor":ok,"new_public_core_aperture_required":false,"staff_shaft_D04_D07_blank_preserved":true,"primary_load_acceptance":false,"errors":errors}
	FileAccess.open("/tmp/d04_port_forward_support.json",FileAccess.WRITE).store_string(JSON.stringify(r,"  "));print(JSON.stringify({"status":r.status,"foundation_feet":feet.size(),"samples":rows.size(),"errors":errors}));quit(0 if errors.is_empty()else 1)
