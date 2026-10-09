extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 var args:=OS.get_cmdline_user_args();assert(args.size()==1)
 var cache=load(args[0]);var parent:=Node3D.new();root.add_child(parent)
 var mesh:=BoxMesh.new();var repeated:Array[MeshInstance3D]=[]
 for i in range(2):
  var m:=MeshInstance3D.new();m.mesh=mesh;parent.add_child(m);cache.attach(m);repeated.append(m)
 var shape0:Shape3D=repeated[0].get_node("StaticContact/SharedShape").shape
 assert(shape0==repeated[1].get_node("StaticContact/SharedShape").shape)
 assert(cache.contacts_created==2 and cache.shapes_reused==1)
 var began:=Time.get_ticks_usec();var all:Array[MeshInstance3D]=[]
 for i in range(5000):
  var m:=MeshInstance3D.new();m.mesh=BoxMesh.new();parent.add_child(m);cache.attach(m);all.append(m)
 var elapsed:=Time.get_ticks_usec()-began
 var faces:PackedVector3Array=shape0.get_faces();assert(faces.size()==36)
 for m in all:
  assert(m.get_node("StaticContact/SharedShape").shape.get_faces()==faces)
 var retired:Array=[]
 for i in range(0,5000,2):
  retired.append(all[i].mesh.get_instance_id());all[i].free()
 for i in range(256):
  var m:=MeshInstance3D.new();m.mesh=mesh;parent.add_child(m);cache.attach(m)
 for key in retired:assert(not cache.shapes.has(key),"Expired weak references must be reclaimed by the next scheduled sweep")
 assert(cache.contacts_created==5258 and cache.shapes_reused==257)
 assert(cache.live_shape_count()==2501)
 assert(repeated[0].get_node("StaticContact/SharedShape").shape==shape0)
 var result:={"status":"PASS","cache_script":args[0],"unique_meshes":5000,"build_us":elapsed,"retired_entries":2500,"live_shapes":cache.live_shape_count(),"exact_triangle_geometry":true,"same_mesh_shape_reuse":true,"contacts_created":cache.contacts_created,"shapes_reused":cache.shapes_reused}
 print(JSON.stringify(result));parent.free();quit()
