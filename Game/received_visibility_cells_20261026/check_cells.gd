extends SceneTree
const CELLS=preload("res://received_visibility_cells_20261026/cells.gd")
var failures:Array=[]
var checks:=0
func require(ok:bool,label:String)->void:
	checks+=1
	if not ok:failures.append(label);push_error(label)
func _initialize()->void:call_deferred("run")
func settle()->void:
	for frame in 32:await RenderingServer.frame_post_draw
func run()->void:
	for box:AABB in [AABB(Vector3(-12,-4,-40),Vector3(24,8,10)),AABB(Vector3(8,-3,398),Vector3(46,12,68)),AABB(Vector3(-54,-3,-460),Vector3(108,108,920)),AABB(Vector3.ZERO,Vector3.ONE)]:
		var parts:Array[AABB]=CELLS.partition(box);var volume:=0.0
		for part:AABB in parts:
			require(box.encloses(part),"Every cell inside original conservative bounds")
			volume+=part.get_volume()
		require(absf(volume-box.get_volume())<.001,"Exact partition volume")
		for i in parts.size():
			for j in range(i):require(not parts[i].intersects(parts[j]),"No interior overlap")
		for x in 7:
			for y in 7:
				for z in 7:
					var point:=box.position+box.size*Vector3(x/6.0,y/6.0,z/6.0);var covered:=false
					for part:AABB in parts:
						if point==point.clamp(part.position,part.end):covered=true;break
					require(covered,"Original volume sampled through all faces and interior")
	var world:=Node3D.new();root.add_child(world);root.use_occlusion_culling=true
	var camera:=Camera3D.new();world.add_child(camera);camera.current=true
	var box:=AABB(Vector3(-12,-4,-40),Vector3(24,8,10))
	var coarse:=VisibleOnScreenNotifier3D.new();coarse.aabb=box;world.add_child(coarse)
	var cells:Array[VisibleOnScreenNotifier3D]=CELLS.install(world,box,"ExactBounds",func()->void:pass)
	var entry:Dictionary={"witness":coarse,"visibility_cells":cells}
	await settle();require(coarse.is_on_screen() and CELLS.visible(entry),"Unobstructed distant room remains visible")
	var occluder:=OccluderInstance3D.new();var wall:=BoxOccluder3D.new();wall.size=Vector3(40,40,1);occluder.occluder=wall;occluder.position=Vector3(0,0,-10);world.add_child(occluder)
	await settle();require(not CELLS.visible(entry),"Opaque intervening wall rejects only hidden room")
	var manager:Node=load("res://scripts/received_homes_20261015/residency.gd").new();world.add_child(manager);manager.set_process(false);manager.set_physics_process(false);manager.host=world
	var actor:=Node3D.new();world.add_child(actor);manager.actor=actor
	var room:=Node3D.new();entry.merge({"room":room,"parent":world,"bounds":AABB(Vector3(1000,0,0),Vector3.ONE),"attached":false,"hidden_seconds":0.0})
	require(not manager._attach_visible_room(entry),"Hidden distant request rejected before source activation")
	actor.position=Vector3(1000,0,0);require(manager._attach_visible_room(entry),"Near collision preparation overrides hidden cells")
	occluder.position.x=-22
	var right:=OccluderInstance3D.new();right.occluder=wall;right.position=Vector3(22,0,-10);world.add_child(right)
	await settle();require(CELLS.visible(entry),"Actual central opening preserves distant sightline")
	var result:Dictionary={"checks":checks,"failures":failures,"cell_count":cells.size(),"renderer":RenderingServer.get_video_adapter_name(),"scope":"Conservative complete-volume partition and actual renderer visibility/occlusion plus synchronous near eligibility; not whole-ship acceptance"}
	for arg:String in OS.get_cmdline_user_args():
		if arg.begins_with("--output="):
			var f:=FileAccess.open(arg.substr(9),FileAccess.WRITE);f.store_string(JSON.stringify(result,"\t"));f.close()
	world.queue_free();await process_frame;await process_frame;print(JSON.stringify(result));quit(0 if failures.is_empty() else 1)
