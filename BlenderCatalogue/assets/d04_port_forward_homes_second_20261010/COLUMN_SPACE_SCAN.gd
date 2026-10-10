extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea");paused=true
	var space:=ship.get_world_3d().direct_space_state;var rows:Array=[];var errors:Array=[];var volumes:Array=[]
	var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/d04_port_forward_homes_second_20261010/PLAN.json"))
	var scans:Array=[]
	for x in[-54.5,-52.0,-50.0,-49.0,-48.5,-47.8,-46.35,-45.5,-44.3]:
		for z in[-422.6,-421.5,-423.6,-425.0,-427.0,-430.0,-431.0,-432.5,-434.0,-435.5,-437.4]:
			var q:=PhysicsShapeQueryParameters3D.new();var shape:=BoxShape3D.new();shape.size=Vector3(.28,4.24,.28);shape.margin=.001;q.shape=shape;q.transform=Transform3D(Basis.IDENTITY,Vector3(x,14.13,z));var paths:Array=[]
			for h in space.intersect_shape(q,64):paths.append(str(h.collider.get_path()))
			scans.append({"x":x,"z":z,"clear":paths.is_empty(),"paths":paths})
	FileAccess.open("/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/d04_port_forward_homes_second_20261010/COLUMN_SPACE_SCAN.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"READ_ONLY_SCAN","rows":scans},"  "));print("COLUMN_SPACE_SCAN_DONE ",scans.size());quit(0)
