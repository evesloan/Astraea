extends SceneTree
const POOL=preload("res://visible_resource_budget_20261026/exact_contact_pool.gd")
const CACHE=preload("res://scripts/static_contact_cache.gd")
var output:String
var checks:=0
func ok(value:bool)->void:
 if not value:push_error("Production contact guard failed at check "+str(checks));quit(1);assert(value)
 checks+=1
func _initialize()->void:
 for arg:String in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.substr(9)
 call_deferred("run")
func cycle()->void:
 var host:=Node3D.new();root.add_child(host)
 var refs:Array[WeakRef]=[]
 for i in 2:
  var mesh:=MeshInstance3D.new();mesh.mesh=BoxMesh.new();mesh.position.x=i*4
  var mat:=StandardMaterial3D.new();mat.albedo_color=Color.RED if i==0 else Color.BLUE
  mesh.material_override=mat;host.add_child(mesh);CACHE.attach(mesh)
  var shape:ConcavePolygonShape3D=mesh.get_node("StaticContact/SharedShape").shape
  refs.append(weakref(shape));ok(shape.get_faces()==mesh.mesh.get_faces())
  ok(mesh.material_override==mat);ok(mesh.get_node("StaticContact").collision_layer==1)
 ok(refs[0].get_ref()==refs[1].get_ref())
 await physics_frame
 await physics_frame
 for x in [0.0,4.0]:
  var query:=PhysicsRayQueryParameters3D.create(Vector3(x,4,0),Vector3(x,-4,0))
  var hit:=host.get_world_3d().direct_space_state.intersect_ray(query)
  ok(not hit.is_empty());ok(abs(hit.position.y-.5)<.0001)
 host.free()
 await process_frame
 await process_frame
 for reference:WeakRef in refs:ok(reference.get_ref()==null)
 POOL.prune();ok(POOL.entries.is_empty())
func mutation()->void:
 var mesh:=BoxMesh.new();var faces:=mesh.get_faces()
 var original:=POOL.intern(faces);original.margin=.08
 var next:=POOL.intern(faces);ok(original!=next);ok(is_equal_approx(next.margin,.04))
 next.backface_collision=true
 var third:=POOL.intern(faces);ok(next!=third);ok(not third.backface_collision)
 var changed:=faces.duplicate();changed[0].x+=.25;third.set_faces(changed)
 var fourth:=POOL.intern(faces);ok(third!=fourth);ok(fourth.get_faces()==faces)
func run()->void:
 await cycle();await cycle();mutation()
 await process_frame
 POOL.prune();ok(POOL.entries.is_empty())
 var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify({"checks":checks,"failures":0,"two_cycles":true,"physics_rays":4,"mutation_guards":3}));f.close();quit()
