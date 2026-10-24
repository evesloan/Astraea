extends SceneTree
const P:="res://clinical_return_links_20261024/"
var checks:=0
var failures:Array=[]
func _initialize()->void:call_deferred("run")
func check(ok:bool,label:String)->void:
 checks+=1
 if not ok:failures.append(label);push_error(label)
func v(p:Array)->Vector3:return Vector3(p[0],p[1],p[2])
func a(p:Vector3)->Array:return[p.x,p.y,p.z]
func run()->void:
 var main:Node=load("res://scenes/main_clinical_return_links_integrated_20261024.tscn").instantiate();root.add_child(main);var ship:Node3D=main.get_node("World360/Astraea")
 while not ship.get_meta("runtime_ready",false):await process_frame
 for i in range(5):await physics_frame
 paused=true
 var manager:Node=ship.get_node("ShipSystems/ReceivedRoomResidency")
 for entry:Dictionary in manager.entries:
  if str(entry.room.name).begins_with("D05_directory_")and not entry.attached:manager._attach_visible_room(entry)
 for i in range(3):await physics_frame
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PLAN.json"));var group:Node3D=ship.get_node("ShipSpace/ClinicalReturnThroughLinks20261024");var clinic:Node=ship.get_node("ShipSpace/Group3CompleteClinical");var space:=ship.get_world_3d().direct_space_state;var excluded:Array[RID]=[]
 for body:CollisionObject3D in ship.get_node("ShipSpace/PersistentActors").find_children("*","CollisionObject3D",true,false):excluded.append(body.get_rid())
 check(group.get_meta("changed_partitions")==10 and group.get_meta("new_capacity")==0,"Ten named clinical partition resources only; zero capacity")
 check(not clinic.get_meta("operating_gates_or_dispatch_admitted",true)and clinic.get_meta("held_starboard_return_spans")==2 and group.get_meta("transfer_junctions_held",false),"Original clinical admission and transfer holds unchanged")
 var results:Array=[]
 for route:Dictionary in plan.routes:
  var points:Array=[]
  for i in range(route.path.size()-1):
   var first:=Vector3(route.path[i][0],21,route.path[i][1]);var last:=Vector3(route.path[i+1][0],21,route.path[i+1][1]);var count:int=maxi(1,ceili(first.distance_to(last)/.9))
   for j in range(count):points.append(first.lerp(last,float(j)/count))
  points.append(Vector3(route.path[-1][0],21,route.path[-1][1]));var blockers:Array=[]
  for point:Vector3 in points:
   for offset:Vector3 in [Vector3.ZERO,Vector3(1.7,0,1.7),Vector3(-1.7,0,1.7),Vector3(1.7,0,-1.7),Vector3(-1.7,0,-1.7)]:
    var witness:=point+offset;var ray:=PhysicsRayQueryParameters3D.create(witness+Vector3.UP*.12,witness-Vector3.UP*.35);ray.exclude=excluded;var hit:=space.intersect_ray(ray)
    check(not hit.is_empty()and absf(hit.position.y-21)<.05,"Through-route floor "+str(route.id)+" "+str(witness))
   var shape:=BoxShape3D.new();shape.size=Vector3(3.6,3.2,3.6);var query:=PhysicsShapeQueryParameters3D.new();query.shape=shape;query.margin=.001;query.exclude=excluded;query.transform.origin=point+Vector3.UP*1.62;var hits:=space.intersect_shape(query,16);var names:Array=[]
   for hit:Dictionary in hits:names.append(str(hit.collider.get_path()))
   if not hits.is_empty():blockers.append({"point":a(point),"owners":names})
   check(hits.is_empty(),"3.6m route envelope "+str(route.id)+" "+str(point)+" "+str(names))
  results.append({"route":route.id,"points":points.size(),"clearance_box_m":[3.6,3.2,3.6],"blockers":blockers})
 # Retained bearings remain solid contacts. These are not removed collision
 # exclusions: every route envelope above queries the actual complete world.
 for row:Array in [[Vector3(107.2,22,29.6),Vector3(108.6,22,29.6),"RoyaltyPier_Fore"],[Vector3(107.2,22,50.4),Vector3(108.6,22,50.4),"RoyaltyPier_Aft"],[Vector3(-61.35,22,-405),Vector3(-59.7,22,-405),"GPM_CELL_-4_-21_2"]]:
  var ray:=PhysicsRayQueryParameters3D.create(row[0],row[1]);ray.exclude=excluded;var hit:=space.intersect_ray(ray);check(not hit.is_empty()and str(hit.collider.get_path()).contains(row[2]),"Protected bearing contact "+str(row[2]))
 check(group.get_meta("retained_gate_bindings")==5 and group.get_meta("duplicate_gate_meshes_removed")==105,"Five duplicate cassettes rebound to retained fittings")
 for row:Dictionary in plan.retained_gate_bindings:
  var proxy:Node=ship.get_node("ShipSpace/Districts/ReceivedSections/"+str(row.room)+"/ClinicalRoomReceiving20261024/"+str(row.receiver));check(proxy.get_child_count()==0 and proxy.get_meta("retained_closed_gate_meshes",[]).size()==21,"Receiving reference owns no duplicate visual/contact: "+str(row.room))
  for path:String in proxy.get_meta("retained_closed_gate_meshes"):
   var mesh:MeshInstance3D=ship.get_node_or_null(path);check(mesh!=null and not mesh.find_children("*","CollisionShape3D",true,false).is_empty(),"Canonical closed fitting retained: "+path)
 var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget");var original:Vector3=budget.actor.global_position;var light_counts:Array=[]
 for route:Dictionary in plan.routes:
  var local:Node=group.get_node(route.id);var lights:Array=local.find_children("*","Light3D",true,false);check(lights.size()==route.lights.size(),"Physical fixture count: "+str(route.id));budget.actor.global_position=lights[0].global_position-Vector3.UP*3.5;budget.refresh();var active:=0
  for light in budget.previously_active:
   if local.is_ancestor_of(light):active+=1
  check(active>0 and budget.previously_active.size()<=8,"Unchanged source budget: "+str(route.id));light_counts.append({"route":route.id,"local_active":active,"total_active":budget.previously_active.size()})
 budget.actor.global_position=original;budget.refresh()
 var exports:Array=[]
 for row:Dictionary in plan.wall_preimages:
  var mesh:MeshInstance3D=clinic.get_node("AST-MED-G3-007/"+str(row.name));var surfaces:Array=[]
  for si in range(mesh.mesh.get_surface_count()):
   var arrays:Array=mesh.mesh.surface_get_arrays(si);var positions:Array=[];var normals:Array=[];var uv:Array=[];var indices:Array=[]
   for q:Vector3 in arrays[Mesh.ARRAY_VERTEX]:positions.append(a(mesh.global_transform*q))
   for q:Vector3 in arrays[Mesh.ARRAY_NORMAL]:normals.append(a((mesh.global_basis.inverse().transposed()*q).normalized()))
   for q:Vector2 in arrays[Mesh.ARRAY_TEX_UV]:uv.append([q.x,q.y])
   if arrays[Mesh.ARRAY_INDEX]!=null:
    for index:int in arrays[Mesh.ARRAY_INDEX]:indices.append(index)
   surfaces.append({"positions":positions,"normals":normals,"uvs":uv,"indices":indices,"material":mesh.get_active_material(si).resource_name})
  exports.append({"name":row.name,"surfaces":surfaces})
 var result:={"status":"PASS"if failures.is_empty()else"FAIL","checks":checks,"failures":failures,"runtime_ready":true,"parts":plan.parts.size(),"new_floor_m2":plan.new_floor_m2,"batches":group.get_meta("batches"),"original_clinical_meshes":group.get_meta("original_clinical_meshes"),"changed_partitions":10,"route_checks":results,"lights":light_counts,"canonical_gate_bindings":5,"new_capacity":0,"clinical_operation":false,"transfer_junctions_accepted":false,"visual_accepted":false,"whole_gameplay_performance_accepted":false}
 FileAccess.open(P+"evidence/INSTALLED_CHECK.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  ")+"\n");FileAccess.open(P+"evidence/WALL_SUCCESSORS.json",FileAccess.WRITE).store_string(JSON.stringify(exports)+"\n");print("CLINICAL_THROUGH_ROUTES ",JSON.stringify(result));main.free();await process_frame;quit(0 if failures.is_empty()else 1)
