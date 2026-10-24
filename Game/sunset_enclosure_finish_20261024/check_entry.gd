extends SceneTree
func _initialize()->void:
 var checked:=0
 for suffix in ["tram_section_integrated_20261024","sunset_enclosure_integrated_20261024"]:
  for kind in ["bootstrap","launcher","main","ship"]:
   var path:String="res://scenes/"+kind+"_"+suffix+".tscn"
   var pack:=load(path)as PackedScene
   if pack==null or not pack.can_instantiate():push_error("Missing entry scene: "+path);quit(1);return
   var instance:=pack.instantiate()
   if instance==null or instance.get_script()==null:push_error("Missing entry script");quit(1);return
   if kind=="ship" and (not instance.has_node("ShipSpace/Districts") or not instance.has_node("ShipSpace/PersistentActors") or not instance.has_node("ReceivedSectionInstallation")):push_error("Ship hierarchy differs");instance.free();quit(1);return
   instance.free();checked+=1
 if str(ProjectSettings.get_setting("application/run/main_scene"))!="res://scenes/bootstrap_sunset_enclosure_integrated_20261024.tscn":push_error("Selected main differs");quit(1);return
 var regex:=RegEx.new();regex.compile('"(res://[^"\\n]+\\.(?:tscn|gd|gdshader))"');var refs:=0
 for name in ["bootstrap","launcher","presentation","ship"]:
  for hit in regex.search_all(FileAccess.get_file_as_string("res://scripts/sunset_enclosure_integration_20261024/"+name+".gd")):
   if not ResourceLoader.exists(hit.get_string(1)):push_error("Unresolved entry reference: "+hit.get_string(1));quit(1);return
   refs+=1
 print("SUNSET_ENTRY PASS ",checked," detached scene instances; ",refs," references; no full startup")
 quit(0)
