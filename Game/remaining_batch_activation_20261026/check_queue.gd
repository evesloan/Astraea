extends SceneTree
class Witness extends Node3D:
 var shown:=true
 func is_on_screen()->bool:return shown
var checks:Array[String]=[]
func require(ok:bool,label:String)->void:
 checks.append(label)
 assert(ok,label)
func _initialize()->void:call_deferred("run")
func run()->void:
 var host:=Node3D.new();root.add_child(host);host.set_meta("runtime_ready",true)
 var space:=Node3D.new();space.name="ShipSpace";host.add_child(space)
 var actors:=Node3D.new();actors.name="PersistentActors";space.add_child(actors)
 var actor:=Node3D.new();actors.add_child(actor)
 var manager=load("res://remaining_batch_activation_20261026/test_manager.gd").new();host.add_child(manager);manager.set_process(false);manager.set_physics_process(false);manager.host=host;manager.actor=actor
 for i in range(2):
  var item:={"key":str(i),"bounds_min":[100.+100.*i,0.,0.],"bounds_max":[101.+100.*i,2.,1.]}
  manager.entries.append(item)
  var room:=Node3D.new();host.add_child(room);room.set_meta("stream_loaded",false);manager.rooms[item.key]=room
  var witness:=Witness.new();host.add_child(witness);manager.witnesses[item.key]=witness
 manager.refresh()
 require(manager.installed_keys.is_empty(),"Far visible refresh never synchronously installs a burst")
 require(manager.pending_visible.size()==2,"Far visible requests queued once")
 manager._queue_restore(manager.entries[0]);manager._restore_visible(manager.entries[0])
 require(manager.pending_visible.size()==2,"Signal and deferred compatibility requests deduplicated")
 manager._process(0)
 require(manager.installed_keys.is_empty(),"Fresh requests wait for renderer observation frames")
 manager.witnesses["0"].shown=false
 for i in range(3):await process_frame
 manager._process(0)
 require(manager.installed_keys==["1"],"Stale visibility rejected; current wanted room dispatched")
 require(manager.visible_requests_rejected==1,"Stale request rejection counted")
 manager.rooms["0"].set_meta("stream_loaded",false);manager.rooms["1"].set_meta("stream_loaded",false);manager.witnesses["0"].shown=true
 manager._queue_restore(manager.entries[0]);manager._queue_restore(manager.entries[1])
 for i in range(3):await process_frame
 var before:int=manager.installed_keys.size();manager._process(0);manager._process(0)
 require(manager.installed_keys.size()==before+1,"At most one activation even if called twice in same frame")
 await process_frame
 manager._process(0)
 require(manager.installed_keys.size()==before+2,"Next visible room progresses on following frame")
 manager.rooms["0"].set_meta("stream_loaded",false);manager.witnesses["0"].shown=false
 before=manager.installed_keys.size();manager.prepare_position(Vector3(100.5,1,.5))
 require(manager.installed_keys.size()==before+1,"Explicit near preparation remains synchronous without visibility")
 manager.rooms["0"].set_meta("stream_loaded",false);actor.position=Vector3(100.5,1,.5);before=manager.installed_keys.size();manager.refresh()
 require(manager.installed_keys.size()==before+1,"Near actor refresh remains synchronous")
 manager.rooms["0"].set_meta("stream_loaded",false);actor.position=Vector3.ZERO
 var body:=RigidBody3D.new();body.freeze=true;actors.add_child(body);body.position=Vector3(100.5,1,.5);before=manager.installed_keys.size();manager.refresh()
 require(manager.installed_keys.size()==before+1,"Near persistent rigid-body preparation remains synchronous")
 var output:=""
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--result="):output=arg.substr(9)
 require(not output.is_empty() and not FileAccess.file_exists(output),"New result destination only")
 var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify({"passed":checks,"statistics":manager.visibility_activation_statistics(),"scope":"Actual production scheduling logic with instrumented install; unchanged native/content install path verified separately, not performance acceptance"},"\t"));f.close();print("REMAINING_QUEUE_PASS ",checks.size());quit()
