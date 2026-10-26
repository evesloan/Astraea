extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var selected:String=ProjectSettings.get_setting("application/run/main_scene")
	assert(selected=="res://orchard_tram_interior_20261025/integration/bootstrap.tscn")
	var boot:Node=load(selected).instantiate();root.add_child(boot)
	await process_frame
	assert(boot.get_child_count()==1)
	var launcher:Node=boot.get_child(0)
	assert(launcher.MAIN=="res://orchard_tram_interior_20261025/integration/main.tscn")
	assert(launcher.presentation==null and not launcher.launching and not launcher.ready_seen)
	assert(launcher.launch_button!=null and launcher.settings_panel!=null)
	assert(load("res://orchard_tram_interior_20261025/integration/assembly.gd").verify())
	var output:=""
	for arg:String in OS.get_cmdline_user_args():
		if arg.begins_with("--result="):output=arg.substr(9)
	assert(not FileAccess.file_exists(output))
	var result:={"selected_main":selected,"original_menu_settings_built":true,"ship_started":false,"exact_integration_pins":true,"scope":"Selected menu path and exact pins only; installed ship checks029/030/032 remain separate"}
	var file:=FileAccess.open(output,FileAccess.WRITE);file.store_string(JSON.stringify(result,"\t")+"\n");file.close();print(JSON.stringify(result));quit()
