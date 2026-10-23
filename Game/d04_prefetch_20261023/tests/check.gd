extends SceneTree
var failures:=0
func check(ok:bool,label:String)->void:
 if not ok:failures+=1;push_error(label)
func _initialize()->void:call_deferred("run")
func run()->void:
 var host:=Node3D.new();root.add_child(host);host.set_meta("runtime_ready",true)
 var manager:Node=load("res://d04_prefetch_20261023/tests/probe_manager.gd").new();host.add_child(manager);manager.host=host;manager.set_process(false);manager.set_physics_process(false)
 var generated:Array[String]=[]
 for i in range(3):
  var source:=Node3D.new();source.name="Detail"+str(i)
  var mesh:=MeshInstance3D.new();mesh.name="OriginalGeometry";mesh.mesh=BoxMesh.new();source.add_child(mesh);mesh.owner=source
  var packed:=PackedScene.new();check(packed.pack(source)==OK,"Fixture pack");source.free()
  var path:="/tmp/d04-prefetch-fixture-"+str(OS.get_process_id())+"-"+str(i)+".tscn";generated.append(path);check(ResourceSaver.save(packed,path)==OK,"Fixture save")
  var home:=Node3D.new();host.add_child(home)
  var entry:={"home":weakref(home),"record":{"detail_path":path,"detail_sha256":FileAccess.get_sha256(path),"room_id":"test"+str(i)},"detail":null,"hidden":0.0,"bounds":AABB(),"wanted":true,"prefetch":true};manager.entries.append(entry);manager._load_entry(entry)
 check(manager.requests.size()==2 and manager.activation_queue.size()==3,"Two request cap and deduplicated queue")
 manager._load_entry(manager.entries[0]);check(manager.activation_queue.size()==3,"Repeated visibility deduplicated")
 manager.entries[0].wanted=false;manager.entries[0].prefetch=false
 var deadline:=Time.get_ticks_msec()+5000
 while manager.activation_count<2 and Time.get_ticks_msec()<deadline:
  var before:int=manager.activation_count;manager._process(0)
  check(manager.activation_count-before<=1,"At most one queued activation per tick")
  check(manager.requests.size()<=2,"Pending plus ready cap")
  await create_timer(.005).timeout
 check(manager.activation_count==2,"Remaining visible requests eventually activate")
 check(manager.entries[0].detail==null,"Stale request never instantiated")
 check(manager.stale_drops>=1,"Completed stale resource drained")
 for i in [1,2]:
  var detail:Node3D=manager.entries[i].detail
  check(detail!=null and detail.get_node("OriginalGeometry").mesh is BoxMesh,"Original geometry retained")
  manager._release_entry(manager.entries[i]);check(manager.entries[i].detail==null,"Inherited release clears ownership")
 manager.entries[1].wanted=false;manager.entries[1].prefetch=true;manager.entries[2].wanted=false;manager.entries[2].prefetch=false
 manager._request(manager.entries[1]);deadline=Time.get_ticks_msec()+5000
 while manager.requests.size()>0 and manager.requests.values()[0].scene==null and Time.get_ticks_msec()<deadline:manager._poll();await create_timer(.005).timeout
 check(manager.requests.size()==1 and manager.entries[1].detail==null,"Prefetch holds resource without hidden node")
 manager.entries[1].prefetch=false;manager._poll();check(manager.requests.is_empty(),"Out-of-neighborhood ready resource evicted")
 print("D04_PREFETCH_FOCUSED ",JSON.stringify({"failures":failures,"stats":manager.prefetch_statistics(),"ship_run":false,"RID_cause":"UNKNOWN"}))
 host.free()
 for path in generated:DirAccess.remove_absolute(path)
 quit(1 if failures else 0)
