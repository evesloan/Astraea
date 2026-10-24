extends SceneTree
const P:="res://clinical_room_receiving_20261024/"
var checks:=0
var failures:Array=[]
func _initialize()->void:call_deferred("run")
func check(ok:bool,label:String)->void:
 checks+=1
 if not ok:failures.append(label);push_error(label)
func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func arr(p:Vector3)->Array:return [p.x,p.y,p.z]
func run()->void:
 var main:Node=load("res://scenes/main_clinical_room_receiving_integrated_20261024.tscn").instantiate();root.add_child(main)
 var ship:Node3D=main.get_node("World360/Astraea")
 while not ship.get_meta("runtime_ready",false):await process_frame
 for i in range(8):await physics_frame
 paused=true
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PLAN.json"));var receipt:Node3D=ship.get_node("ShipSpace/ClinicalRoomReceiving20261024")
 check(receipt.get_meta("rooms")==8 and receipt.get_meta("interfaces")==16,"Eight original rooms / sixteen interfaces")
 check(receipt.get_meta("changed_original_meshes")==3 and receipt.get_meta("new_capacity")==0,"Only three enclosure resources change; no new capacity")
 var manager:Node=ship.get_node("ShipSystems/ReceivedRoomResidency");var entries:={}
 for entry:Dictionary in manager.entries:
  if str(entry.room.name).begins_with("D05_directory_"):entries[str(entry.room.name)]=entry
 var original_actor:Vector3=manager.actor.global_position
 for row:Dictionary in plan.rooms:
  check(entries.has(row.key),"Existing residency entry retained: "+str(row.key))
  var entry:Dictionary=entries[row.key]
  if not entry.attached:manager._attach_visible_room(entry)
 for i in range(3):await physics_frame
 var space:=ship.get_world_3d().direct_space_state;var excluded:Array[RID]=[];var gate_bodies:Array[RID]=[];var routes:Array=[]
 for body:CollisionObject3D in ship.get_node("ShipSpace/PersistentActors").find_children("*","CollisionObject3D",true,false):excluded.append(body.get_rid())
 var clinical:Node3D=ship.get_node("ShipSpace/Group3CompleteClinical")
 check(not clinical.get_meta("operating_gates_or_dispatch_admitted",true),"Original clinical admission stays closed")
 check(clinical.get_meta("held_starboard_return_spans")==2,"Both Royalty return support holds preserved")
 var original_gates:Node=clinical.get_node("AST-MED-G3-010")
 for body:CollisionObject3D in original_gates.find_children("*","CollisionObject3D",true,false):gate_bodies.append(body.get_rid())
 for port:Dictionary in plan.ports:
  var gate:Node=entries[port.room].room.get_node("ClinicalRoomReceiving20261024/"+str(port.id)+"_ClosedSourceCassette")
  for body:CollisionObject3D in gate.find_children("*","CollisionObject3D",true,false):gate_bodies.append(body.get_rid())
 for port:Dictionary in plan.ports:
  var room:Node3D=entries[port.room].room;var group:Node3D=room.get_node("ClinicalRoomReceiving20261024");var gate:Node3D=group.get_node(str(port.id)+"_ClosedSourceCassette")
  var other_gates:Array[RID]=gate_bodies.duplicate()
  for body:CollisionObject3D in gate.find_children("*","CollisionObject3D",true,false):other_gates.erase(body.get_rid())
  other_gates.append_array(excluded)
  check(not gate.get_meta("clinical_operation_admitted",true)and not gate.get_meta("persistent_id_assigned",true),"No invented clinical permission or persistent ID")
  var center:Vector3=v(port.gate_position)+Vector3.UP*1.2;var ray:=PhysicsRayQueryParameters3D.create(center+Vector3.RIGHT*.6,center-Vector3.RIGHT*.6);ray.exclude=other_gates;var hit:=space.intersect_ray(ray)
  check(not hit.is_empty()and gate.is_ancestor_of(hit.collider),"Original source cassette is physically closed: "+str(port.id))
 # Closed clinical cassettes remain in the actual ship. Excluding their RIDs in
 # these geometric queries checks the underlying aperture without operating them.
 var structural_excluded:Array[RID]=excluded.duplicate();structural_excluded.append_array(gate_bodies)
 for port:Dictionary in plan.ports:
  var points:Array=[]
  for i in range(port.path.size()-1):
   var a:=Vector3(port.path[i][0],21,port.path[i][1]);var b:=Vector3(port.path[i+1][0],21,port.path[i+1][1]);var count:int=maxi(1,ceili(a.distance_to(b)/2.0))
   for j in range(count):points.append(a.lerp(b,float(j)/count))
  points.append(Vector3(port.path[-1][0],21,port.path[-1][1]));var obstructed:Array=[]
  for point:Vector3 in points:
   var ray:=PhysicsRayQueryParameters3D.create(point+Vector3.UP*.12,point-Vector3.UP*.35);ray.exclude=structural_excluded;var hit:=space.intersect_ray(ray)
   check(not hit.is_empty()and absf(hit.position.y-21)<.05,"Receiving floor: "+str(port.id)+" "+str(point)+" "+str(hit))
   var shape:=CapsuleShape3D.new();shape.radius=.3;shape.height=1.8;var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.margin=.001;q.exclude=structural_excluded;q.transform.origin=point+Vector3.UP*.925;var hits:=space.intersect_shape(q,8);var names:Array=[]
   for item in hits:names.append(str(item.collider.get_path()))
   if not hits.is_empty():obstructed.append({"position":arr(point),"owners":names})
   check(hits.is_empty(),"Receiving clearance: "+str(port.id)+" "+str(point)+" "+str(names))
  routes.append({"interface":port.id,"points":points.size(),"obstructions":obstructed})
 var wall_exports:Array=[]
 for row:Dictionary in plan.walls:
  var mesh:MeshInstance3D=entries[row.room].room.find_child(row.source_name,true,false)
  check(mesh.get_meta("clinical_receiving_openings")==2,"Two fitted openings: "+str(row.room))
  var surfaces:Array=[]
  for si in range(mesh.mesh.get_surface_count()):
   var arrays:Array=mesh.mesh.surface_get_arrays(si);var positions:Array=[];var normals:Array=[];var uvs:Array=[]
   for point:Vector3 in arrays[Mesh.ARRAY_VERTEX]:positions.append(arr(mesh.global_transform*point))
   for normal:Vector3 in arrays[Mesh.ARRAY_NORMAL]:normals.append(arr((mesh.global_basis.inverse().transposed()*normal).normalized()))
   for uv:Vector2 in arrays[Mesh.ARRAY_TEX_UV]:uvs.append([uv.x,uv.y])
   var indices:Array=[]
   if arrays[Mesh.ARRAY_INDEX]!=null:
    for index:int in arrays[Mesh.ARRAY_INDEX]:indices.append(index)
   surfaces.append({"positions":positions,"normals":normals,"uvs":uvs,"indices":indices,"material":mesh.mesh.surface_get_material(si).resource_name})
  wall_exports.append({"room":row.room,"source_name":row.source_name,"surfaces":surfaces})
 var budget:=ship.get_node("ShipSystems/LocalShadowSourceBudget");var light_counts:Array=[]
 for row:Dictionary in plan.rooms:
  var room:Node3D=entries[row.key].room;var group:Node3D=room.get_node("ClinicalRoomReceiving20261024");var lights:Array=group.find_children("*","Light3D",true,false)
  check(lights.size()==4,"Four source-profile task lights: "+str(row.key));budget.actor.global_position=lights[0].global_position-Vector3.UP*3;budget.refresh();check(budget.previously_active.size()<=8,"Original eight-source selector preserved")
  var active:=0
  for light in budget.previously_active:
   if group.is_ancestor_of(light):active+=1
  check(active>0,"Receiving fixture selected: "+str(row.key));light_counts.append({"room":row.key,"receiving_active":active,"all_active":budget.previously_active.size()})
 # The existing manager caches these exact nodes. A detach/reattach must neither
 # rebuild cuts nor duplicate floor contacts, cassettes or registered lights.
 for row:Dictionary in plan.rooms:
  var entry:Dictionary=entries[row.key];var room:Node3D=entry.room;var count:int=room.find_children("*","Node",true,false).size();var group:Node3D=room.get_node("ClinicalRoomReceiving20261024");var id:int=group.get_instance_id()
  entry.parent.remove_child(room);entry.attached=false;manager._attach_visible_room(entry)
  check(room.find_children("*","Node",true,false).size()==count and room.get_node("ClinicalRoomReceiving20261024").get_instance_id()==id,"Exact cached receiver survives reattachment: "+str(row.key))
 budget.actor.global_position=original_actor;budget.refresh()
 var result:={"status":"PASS"if failures.is_empty()else"FAIL","checks":checks,"failures":failures,"runtime_ready":true,"rooms":8,"interfaces":16,"new_floor_m2":plan.new_floor_m2,"parts":plan.parts.size(),"architecture_batches":receipt.get_meta("batches"),"original_meshes":receipt.get_meta("original_meshes"),"changed_original_meshes":3,"routes":routes,"lights":light_counts,"query_scope":"Reference-body structural route queries exclude closed gate contacts; gates themselves separately verified closed. Not operational crossing or loaded-cart acceptance.","clinical_operation_accepted":false,"visual_accepted":false,"whole_gameplay_performance_accepted":false}
 FileAccess.open(P+"evidence/INSTALLED_CHECK.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  ")+"\n")
 FileAccess.open(P+"evidence/WALL_SUCCESSORS.json",FileAccess.WRITE).store_string(JSON.stringify(wall_exports,"  ")+"\n")
 print("CLINICAL_RECEIVING_INSTALLED ",JSON.stringify(result));main.free();await process_frame;quit(0 if failures.is_empty()else 1)
