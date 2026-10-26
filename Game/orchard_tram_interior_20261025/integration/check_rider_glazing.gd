extends SceneTree
const P:="res://orchard_tram_interior_20261025/integration/"
func _initialize()->void:call_deferred("run")
func argument(key:String)->String:
	for arg:String in OS.get_cmdline_user_args():
		if arg.begins_with(key+"="):return arg.substr(key.length()+1)
	return ""
func run()->void:
	var report:={"scope":"Decision view after two exact end-glazing bindings; actual unchanged player camera/ship/light budget, verified diagnostic arrival, no tram movement or repeat sweeps"}
	var presentation:Node=load(P+"main.tscn").instantiate();root.add_child(presentation);presentation.set_world_resolution(2)
	var ship:Node3D=presentation.world_view.get_node("Astraea");var start:=Time.get_ticks_msec()
	while not ship.get_meta("runtime_ready",false):
		assert(Time.get_ticks_msec()-start<180000);await process_frame
	var assembly:Node3D=ship.get_node("ShipSpace/Districts/Group4Completion")
	var body:AnimatableBody3D=assembly.get_node("Group4OwnedTram_Source024")
	assert(body.get_meta("retained_end_glazing_bound")==2)
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	report.ready_seconds=(Time.get_ticks_msec()-start)/1000.
	report.verified_arrival=ship.arrive_at(Vector3(17.42596,56.20032,-236.1),0.)
	assert(report.verified_arrival);actor.set_controls_enabled(false);actor.camera.current=true
	report.views=[]
	for row in [["rider_forward_glazing",0.],["rider_grand_room_side",-PI/2]]:
		actor.rotation.y=row[1]
		for i in range(12):await process_frame
		await RenderingServer.frame_post_draw
		var image:Image=presentation.world_view.get_texture().get_image()
		var err:=image.save_png(argument("--result").get_base_dir()+"/"+str(row[0])+".png")
		assert(err==OK);report.views.append({"name":row[0],"position":str(actor.camera.global_position),"yaw":row[1]})
	report.visual_acceptance="Requires pixel review; no automated artistic approval"
	var path:=argument("--result");assert(not FileAccess.file_exists(path));var file:=FileAccess.open(path,FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t")+"\n");file.close();print(JSON.stringify(report));quit()
