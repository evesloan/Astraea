extends SceneTree
# Validate actual load references and detached scene instances; never start ship construction.
func _initialize()->void:
 var scene_names:=["bootstrap","launcher","main","ship"]
 var checked:=0
 for suffix in ["tidal_arrival_finish_20261024","tram_section_integrated_20261024"]:
  for kind in scene_names:
   var path:String="res://scenes/"+str(kind)+"_"+str(suffix)+".tscn"
   if not ResourceLoader.exists(path):push_error("Missing launch scene: "+path);quit(1);return
   var pack:=load(path)as PackedScene
   if pack==null or not pack.can_instantiate():push_error("Cannot instantiate launch scene: "+path);quit(1);return
   var instance:=pack.instantiate()
   if instance==null or instance.get_script()==null:push_error("Missing launch script: "+path);quit(1);return
   # Do not add to SceneTree: _ready starts the full ship and is a separate gate.
   if kind=="ship" and (not instance.has_node("ShipSpace/Districts") or not instance.has_node("ShipSpace/PersistentActors") or not instance.has_node("ReceivedSectionInstallation")):
    push_error("Ship hierarchy incomplete: "+path);instance.free();quit(1);return
   instance.free();checked+=1
 var regex:=RegEx.new();regex.compile('"(res://[^"\\n]+\\.(?:tscn|gd|gdshader))"')
 var refs:=0
 for file in ["bootstrap.gd","launcher.gd","presentation.gd","ship_r003.gd"]:
  var text:=FileAccess.get_file_as_string("res://scripts/tram_section_integration_20261024/"+file)
  for hit in regex.search_all(text):
   var path:=hit.get_string(1)
   if not ResourceLoader.exists(path):push_error("Entry reference missing: "+path);quit(1);return
   refs+=1
 if str(ProjectSettings.get_setting("application/run/main_scene"))!="res://scenes/bootstrap_tram_section_integrated_20261024.tscn":push_error("Selected main differs");quit(1);return
 print("TRAM_SECTION_ENTRY_CLOSURE PASS ",checked," detached scene instances, ",refs," literal script/scene/shader references; no full startup")
 quit(0)
