extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea");paused=true
	var space:=ship.get_world_3d().direct_space_state;var rows:Array=[]
	for x in [-80.0,-65.0,-57.0,-53.0,-44.0,-27.0,-8.0]:
		for z in [-449.0,-440.0,-432.0,-398.0,-370.0,-342.0]:
			var q:=PhysicsRayQueryParameters3D.create(Vector3(x,20.5,z),Vector3(x,-.5,z));var hit:=space.intersect_ray(q)
			rows.append({"x":x,"z":z,"hit":str(hit.get("position","none")),"owner":str(hit.collider.get_path())if not hit.is_empty()else"none","ray_excludes":0})
	var near:Array=[]
	for part:MeshInstance3D in ship.find_children("*","MeshInstance3D",true,false):
		var b:AABB=part.global_transform*part.get_aabb()
		if b.end.y<11.9 or b.position.y>21.0 or b.end.x< -100 or b.position.x> -7.0 or b.end.z< -454 or b.position.z> -341:continue
		near.append({"name":str(part.name),"path":str(part.get_path()),"min":[b.position.x,b.position.y,b.position.z],"max":[b.end.x,b.end.y,b.end.z]})
	var j={"status":"SURVEY_ONLY","baseline_commit":"e6ec477987fa1f3a973ec81e8a6c0729717d4737","rays":rows,"mesh_bounds":near,"scope":"Read-only selected port-forward D04 construction interfaces; no support or acceptance claim"}
	FileAccess.open("/tmp/d04_port_forward_preimage.json",FileAccess.WRITE).store_string(JSON.stringify(j,"  "));print(JSON.stringify({"status":"SURVEY_ONLY","rays":rows.size(),"near_meshes":near.size()}));quit()
