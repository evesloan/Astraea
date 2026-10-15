extends SceneTree
const D="/workspace/astraea-integration-cutoff-20261013/dining_service_receiving_20261015/"
func _initialize()->void:call_deferred("run")
func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func run()->void:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(D+"NATIVE_RECEIVER_VERIFICATION.json"));assert(FileAccess.get_sha256("res://assets/models/AST-AQU-016.glb")==str(p.source_pins["assets/models/AST-AQU-016.glb"]));var world:=Node3D.new();root.add_child(world);var old:Node3D=(load("res://assets/models/AST-AQU-016.glb")as PackedScene).instantiate();world.add_child(old);var shapes:Array=[]
 for name in["GPM_CELL_-3_-22_6_ASTRAEA_ivory_enamel_concave_static_surface","GPM_CELL_-2_-21_7_ASTRAEA_ivory_enamel_concave_static_surface"]:
  var mesh:MeshInstance3D=old.find_child(name,true,false);assert(mesh!=null);load("res://scripts/static_contact_cache.gd").attach(mesh);var collision:CollisionShape3D=mesh.get_node("StaticContact/SharedShape");var a:AABB=mesh.global_transform*mesh.get_aabb();shapes.append({"name":name,"shape_margin":collision.shape.margin,"max_y":a.end.y})
 for i in range(4):await physics_frame
 var rows:Array=[];var space:=world.get_world_3d().direct_space_state
 for row in p.bounds:
  if not str(row.name).begins_with("D10S_01_")or not"RetainedFloorUnderlap"in str(row.name):continue
  var shape:=BoxShape3D.new();shape.size=v(row.max)-v(row.min);shape.margin=0.;var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.margin=0.;q.transform.origin=(v(row.max)+v(row.min))/2;var hits:=space.intersect_shape(q,16);rows.append({"part":row.name,"min_y":row.min[1],"max_y":row.max[1],"old_ceiling_contacts":hits.size()})
 var ok:bool=rows.size()==6 and rows.all(func(a):return a.old_ceiling_contacts==0);FileAccess.open(D+"SOURCE_PLATE_CLEARANCE_LOCAL.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS"if ok else"FAIL","original_shapes":shapes,"plates":rows},"  "));print("PASS_D10_PLATE_EXACT_OLD_CEILING_CLEARANCE"if ok else"FAIL_D10_PLATE_EXACT_OLD_CEILING_CLEARANCE");quit(0 if ok else 1)
