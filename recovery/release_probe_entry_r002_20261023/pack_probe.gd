extends SceneTree
func _initialize()->void:
 var p:=PCKPacker.new();var code:=p.pck_start("/tmp/release-probe-r002/release-operations-probe.pck")
 if code!=OK:quit(1);return
 var base:="/workspace/Astraea-recovered-e6274e77-20261021/recovery/release_operations_fix_20261023/"
 var files:Array=JSON.parse_string(FileAccess.get_file_as_string("/tmp/release-payload-paths.json"))
 for path:String in files:
  code=p.add_file("res://"+path.trim_prefix("Game/"),base+"payload/"+path)
  if code!=OK:push_error(path);quit(1);return
 code=p.add_file("res://release_fixture.gd","/workspace/Astraea-recovered-e6274e77-20261021/recovery/release_probe_entry_r002_20261023/release_fixture.gd")
 if code!=OK:quit(1);return
 code=p.add_file("res://project.godot","/workspace/Astraea-recovered-e6274e77-20261021/recovery/release_probe_entry_r002_20261023/probe_project.godot")
 if code!=OK:quit(1);return
 code=p.add_file("res://probe.tscn","/workspace/Astraea-recovered-e6274e77-20261021/recovery/release_probe_entry_r002_20261023/probe.tscn")
 if code!=OK:quit(1);return
 code=p.flush();print("RELEASE_PROBE_PACK ",files.size()," result=",code);quit(0 if code==OK else 1)
