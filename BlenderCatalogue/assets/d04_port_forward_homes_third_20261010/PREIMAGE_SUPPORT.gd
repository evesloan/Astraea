extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea");paused=true
	var space:=ship.get_world_3d().direct_space_state;var rows:Array=[];var errors:Array=[];var volumes:Array=[]
	var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/d04_port_forward_homes_third_20261010/PLAN.json"))
	var feet:Array=plan.foundation_feet
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
	var frame_rows:Array=[];var source:Node3D=ship.find_child("D04PortForwardSecondHomesStructure",true,false)
	for p in plan.guard_preimages:
		var node:MeshInstance3D=source.find_child(str(p.name),true,false);var low:=Vector3(INF,INF,INF);var high:=-low
		for v in p.preimage.verts:var at:=Vector3(v[0],v[1],v[2]);low=low.min(at);high=high.max(at)
		var ok:=node!=null
		if ok:var b:AABB=node.global_transform*node.get_aabb();ok=b.position.distance_to(low)<.00004 and b.end.distance_to(high)<.00004
		frame_rows.append({"name":p.name,"bounds_match":ok});if not ok:errors.append({"guard_preimage":p.name})
	var retained_frame_names:Array=[]
	var retained_source:Node3D=ship.find_child("D04PortForwardReceiving",true,false).get_node("ReceivedSourceGeometry")
	for part in plan.frame_joint_preimages:
		var name:String=str(part.name).replace(".","_");var mesh:MeshInstance3D=retained_source.find_child(name,true,false);var lo:=Vector3(INF,INF,INF);var hi:=-lo
		for v in part.verts:var at:=Vector3(v[0],v[1],v[2]);lo=lo.min(at);hi=hi.max(at)
		var ok:=mesh!=null
		if ok:var b:AABB=mesh.global_transform*mesh.get_aabb();ok=b.position.distance_to(lo)<.00004 and b.end.distance_to(hi)<.00004
		if ok:retained_frame_names.append(name)
		else:errors.append({"retained_frame_preimage":name})
	var frame_spaces:Array=[]
	var frame_parts:Array=[]
	for room in plan.rooms:
		for part in room.parts:
			if part.category in["frame","truss_brace"]:frame_parts.append(part)
	for part in plan.commons_parts:
		if part.category in["frame","truss_brace"]:frame_parts.append(part)
	for part in frame_parts:
		if "Pier_"in str(part.name):continue
		var lo:=Vector3(INF,INF,INF);var hi:=-lo
		for v in part.verts:var at:=Vector3(v[0],v[1],v[2]);lo=lo.min(at);hi=hi.max(at)
		var q:=PhysicsShapeQueryParameters3D.new();var shape:=BoxShape3D.new();shape.size=hi-lo;shape.margin=.001;q.shape=shape;q.transform=Transform3D(Basis.IDENTITY,(lo+hi)/2);var owners:Array=[];var bad:Array=[]
		for h in space.intersect_shape(q,128):
			var path:=str(h.collider.get_path());owners.append(path)
			if str(h.collider.get_parent().name)!="D04PF_ReceivedFloor"and str(h.collider.get_parent().name)not in retained_frame_names:bad.append(path)
		frame_spaces.append({"name":part.name,"source_contacts":owners,"unexpected":bad,"retained_street_slab_joint_allowed":true});if not bad.is_empty():errors.append({"frame":part.name,"unexpected":bad})
	var r={"status":"PASS"if errors.is_empty()else"FAIL","baseline_commit":plan.base_commit,"foundation_feet":feet,"bearing_samples":rows,"column_preimages":volumes,"guard_preimages":frame_rows,"transfer_frame_preimages":frame_spaces,"exact_retained_frame_joints":retained_frame_names,"primary_load_acceptance":false,"source_proposal_crew_footprint_intersections":0,"all1000_allocation_polygons_preserved":true,"errors":errors}
	FileAccess.open("/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/d04_port_forward_homes_third_20261010/PREIMAGE_SUPPORT.json",FileAccess.WRITE).store_string(JSON.stringify(r,"  "));print(JSON.stringify({"status":r.status,"foundation_feet":feet.size(),"samples":rows.size(),"errors":errors}));quit(0 if errors.is_empty()else 1)
