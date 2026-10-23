extends SceneTree
func _initialize()->void:
 var p:=PCKPacker.new();var ok:bool=p.pck_start("/tmp/route-activation-overlay.pck")==OK
 var base:="/workspace/Astraea-recovered-e6274e77-20261021/recovery/route_activation_fix_20261023/payload/Game/"
 for path in ["scripts/route_activation_20261023/scheduler.gd","scripts/route_activation_20261023/private_visual.gd","scripts/startup_residency_20261020/private_detail_residency.gd","scripts/received_homes_20261015/residency.gd"]:
  ok=ok and p.add_file("res://"+path,base+path)==OK
 ok=ok and p.flush()==OK
 if not ok:quit(1);return
 if not ProjectSettings.load_resource_pack("/tmp/route-activation-overlay.pck"):quit(1);return
 for path in ["scripts/route_activation_20261023/scheduler.gd","scripts/route_activation_20261023/private_visual.gd","scripts/startup_residency_20261020/private_detail_residency.gd","scripts/received_homes_20261015/residency.gd"]:
  var s:Script=load("res://"+path);ok=ok and s!=null and s.can_instantiate()
 print("ROUTE_PATCH_PARSE ",ok);quit(0 if ok else 1)
