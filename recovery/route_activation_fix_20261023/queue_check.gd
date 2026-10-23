extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 if not ProjectSettings.load_resource_pack("/tmp/route-activation-overlay.pck"):quit(2);return
 var base:="/workspace/Astraea-recovered-e6274e77-20261021/recovery/route_activation_fix_20261023/"
 OS.set_environment("ASTRAEA_ROOM_ACTIVATION_QUEUE","1")
 var host:=Node3D.new();root.add_child(host);host.set_meta("runtime_ready",true);var systems:=Node.new();systems.name="ShipSystems";host.add_child(systems)
 var private_manager:Node=load("res://scripts/startup_residency_20261020/private_detail_residency.gd").new();host.add_child(private_manager);private_manager.host=host;private_manager.set_physics_process(false)
 var received:Node=load("res://scripts/received_homes_20261015/residency.gd").new();host.add_child(received);received.host=host;received.set_physics_process(false)
 var privates:Array=[]
 for i in 11:
  var home:=Node3D.new();host.add_child(home);var witness:RefCounted=load(base+"witness.gd").new();var entry:={"home":weakref(home),"witness":witness,"detail":null};private_manager._load_visible(entry);privates.append(entry)
 var rooms:Array=[]
 for i in 81:
  var room:=Node3D.new();var witness:RefCounted=load(base+"witness.gd").new();var entry:={"room":room,"parent":host,"witness":witness,"attached":false,"hidden_seconds":0.0};rooms.append(entry);received._attach_visible_room(entry);received._attach_visible_room(entry)
 var queue:Node=systems.get_node("VisibilityActivationQueue");queue.set_process(false)
 var valid:bool=queue.pending.size()==92 and queue.duplicates==81 and received.changes==0
 for entry in privates:entry.witness.visible=false
 for i in 81:
  var before:int=queue.completed;queue._process(0);valid=valid and queue.completed-before<=1
 # A time-budget tick may consume only stale work; drain a bounded number of ticks.
 for i in 100:
  if queue.pending.is_empty():break
  var before:int=queue.completed;queue._process(0);valid=valid and queue.completed-before<=1
 valid=valid and queue.completed==81 and queue.stale==11 and received.changes==81 and queue.pending.is_empty()
 print("ROUTE_QUEUE_CHECK ",JSON.stringify({"pass":valid,"shared_private_received_queue":true,"calls":173,"unique_requests":92,"stats":queue.statistics(),"ship_run":false}))
 OS.unset_environment("ASTRAEA_ROOM_ACTIVATION_QUEUE");host.free();quit(0 if valid else 1)
