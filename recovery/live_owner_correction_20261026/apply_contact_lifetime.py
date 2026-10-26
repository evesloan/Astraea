from pathlib import Path
p=Path('Game/remaining_batch_activation_20261026/contact_partition.gd');s=p.read_text()
s=s.replace('static var bodies:Dictionary={}','static var bodies:Dictionary={}\nstatic var release_enabled:=false\nstatic var pending_key:=""\nstatic var loads:=0\nstatic var releases:=0')
s=s.replace('static func release_room(key:String)->void:\n\tif bodies.has(key):bodies[key].collision_layer=0;bodies[key].collision_mask=0', '''static func release_room(key:String)->void:
 if not bodies.has(key):return
 bodies[key].collision_layer=0;bodies[key].collision_mask=0
 if release_enabled and prepared.has(key):
  bodies[key].get_node("SharedRoomTriangles").shape=null
  prepared.erase(key);releases+=1
static func enable_release()->void:
 if release_enabled:return
 release_enabled=true
 for key:String in bodies:
  if bodies[key].collision_layer==0:release_room(key)
static func _install_prepared(key:String,shape:ConcavePolygonShape3D)->void:
 assert(shape!=null and bodies.has(key) and bodies[key].collision_layer==0)
 prepared[key]=shape;bodies[key].get_node("SharedRoomTriangles").shape=shape;loads+=1
static func ensure_prepared(key:String)->void:
 if prepared.has(key):return
 assert(FileAccess.get_sha256(index[key].resource)==index[key].sha256,"Exact contact source changed")
 var shape:ConcavePolygonShape3D
 if pending_key==key:
  shape=ResourceLoader.load_threaded_get(index[key].resource);pending_key=""
 else:shape=load(index[key].resource)
 _install_prepared(key,shape)
static func prefetch(key:String)->bool:
 if prepared.has(key):return true
 if not pending_key.is_empty() and pending_key!=key:
  var stale_status:=ResourceLoader.load_threaded_get_status(index[pending_key].resource)
  if stale_status==ResourceLoader.THREAD_LOAD_IN_PROGRESS:return false
  if stale_status==ResourceLoader.THREAD_LOAD_LOADED:ResourceLoader.load_threaded_get(index[pending_key].resource)
  pending_key=""
 if pending_key.is_empty():
  assert(FileAccess.get_sha256(index[key].resource)==index[key].sha256,"Exact contact source changed")
  var error:=ResourceLoader.load_threaded_request(index[key].resource,"ConcavePolygonShape3D",false)
  assert(error==OK,"Cannot prefetch exact contact source")
  pending_key=key
 var status:=ResourceLoader.load_threaded_get_status(index[key].resource)
 if status==ResourceLoader.THREAD_LOAD_IN_PROGRESS:return false
 assert(status==ResourceLoader.THREAD_LOAD_LOADED,"Exact contact prefetch failed")
 ensure_prepared(key);return true
static func statistics()->Dictionary:
 return {"retained_shapes":prepared.size(),"finite_bodies":bodies.size(),"pending_key":pending_key,"loads":loads,"releases":releases,"release_enabled":release_enabled}''')
s=s.replace('bodies.clear();prepared.clear()','bodies.clear();prepared.clear();pending_key="";release_enabled=false')
s=s.replace('assert(bodies.has(key),"Contact bodies must be prepared before player admission")','assert(bodies.has(key),"Contact bodies must be prepared before player admission")\n\tensure_prepared(key)')
p.write_text(s)
p=Path('Game/scripts/remaining_batch_receiving.gd');s=p.read_text();s=s.replace('var frame:=Engine.get_process_frames()','load("res://remaining_batch_activation_20261026/contact_partition.gd").enable_release()\n\tvar frame:=Engine.get_process_frames()',1)
needle='\t\tlast_visible_dispatch_frame=frame\n\t\tvar start:=Time.get_ticks_usec()'
replacement='''\t\tif not load("res://remaining_batch_activation_20261026/contact_partition.gd").prefetch(str(request.key)):
\t\t\tpending_visible.push_front(request);queued_visible[request.key]=true
\t\t\treturn
\t\tlast_visible_dispatch_frame=frame
\t\tvar start:=Time.get_ticks_usec()'''
assert needle in s;s=s.replace(needle,replacement);p.write_text(s)
