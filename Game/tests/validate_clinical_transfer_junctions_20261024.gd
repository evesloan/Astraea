extends SceneTree
const P:="res://clinical_transfer_junctions_20261024/"
var checks:=0
var failures:Array=[]
func _initialize()->void:call_deferred("run")
func check(ok:bool,label:String)->void:
 checks+=1
 if not ok:failures.append(label);push_error(label)
func a(p:Vector3)->Array:return[p.x,p.y,p.z]
func v(p:Array)->Vector3:return Vector3(p[0],p[1],p[2])
func dump_mesh(mesh:MeshInstance3D)->Dictionary:
 var rows:Array=[]
 for si in range(mesh.mesh.get_surface_count()):
  var data:Array=mesh.mesh.surface_get_arrays(si);var positions:Array=[];var normals:Array=[];var uvs:Array=[];var indices:Array=[]
  for q:Vector3 in data[Mesh.ARRAY_VERTEX]:positions.append(a(mesh.global_transform*q))
  for q:Vector3 in data[Mesh.ARRAY_NORMAL]:normals.append(a((mesh.global_basis.inverse().transposed()*q).normalized()))
  for q:Vector2 in data[Mesh.ARRAY_TEX_UV]:uvs.append([q.x,q.y])
  if data[Mesh.ARRAY_INDEX]!=null:
   for i:int in data[Mesh.ARRAY_INDEX]:indices.append(i)
  rows.append({"positions":positions,"normals":normals,"uvs":uvs,"indices":indices,"material":mesh.get_active_material(si).resource_name})
 return {"name":str(mesh.name),"surfaces":rows}
func run()->void:
 var main:Node=load("res://scenes/main_clinical_transfer_junctions_integrated_20261024.tscn").instantiate();root.add_child(main);var ship:Node3D=main.get_node("World360/Astraea")
 while not ship.get_meta("runtime_ready",false):await process_frame
 for i in range(5):await physics_frame
 paused=true
 var manager:Node=ship.get_node("ShipSystems/ReceivedRoomResidency")
 for entry:Dictionary in manager.entries:
  if str(entry.room.name)=="D05_directory_06"and not entry.attached:manager._attach_visible_room(entry)
 var stream:Node=ship.get_node("ShipSystems/RemainingBatchStreaming");var target:Dictionary={}
 for row:Dictionary in stream.entries:
  if row.key=="D05_directory_01":target=row
 stream._ensure_room(target)
 for i in range(3):await physics_frame
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PLAN.json"));var group:Node3D=ship.get_node("ShipSpace/ClinicalTransferJunctions20261024");var clinic:Node=ship.get_node("ShipSpace/Group3CompleteClinical");var space:=ship.get_world_3d().direct_space_state;var actors:Array[RID]=[];var leaves:Array[RID]=[]
 for body:CollisionObject3D in ship.get_node("ShipSpace/PersistentActors").find_children("*","CollisionObject3D",true,false):actors.append(body.get_rid())
 var bindings:Array=group.get_meta("gate_bindings");var meshes_seen:={};var shared_meshes:={};var shared_shapes:={};var closed:Array=[]
 for row:Dictionary in bindings:
  check(row.paths.size()==21,"Complete21-part cassette: "+row.name)
  for path:String in row.paths:
   var mesh:MeshInstance3D=ship.get_node(path);check(not meshes_seen.has(path),"Unique canonical gate ownership: "+path);meshes_seen[path]=true;shared_meshes[mesh.mesh.get_instance_id()]=true
   var contacts:Array=mesh.find_children("*","CollisionShape3D",true,false);check(contacts.size()==1,"One gate contact: "+path);shared_shapes[contacts[0].shape.get_instance_id()]=true
   if str(mesh.name).contains("__LEFT_")or str(mesh.name).contains("__RIGHT_"):leaves.append(contacts[0].get_parent().get_rid())
  var center:=v(row.position)+Vector3.UP*1.5;var normal:=Basis(Vector3.UP,row.yaw)*Vector3.FORWARD;var ray:=PhysicsRayQueryParameters3D.create(center-normal*.3,center+normal*.3);ray.exclude=actors;var hit:=space.intersect_ray(ray);var valid:bool=not hit.is_empty()and str(hit.collider.get_parent().name).begins_with(row.name+"__");check(valid,"Gate remains physically closed: "+row.name);closed.append({"gate":row.name,"blocked":valid})
 check(shared_meshes.size()==21 and shared_shapes.size()==21,"Eight cassettes share21 exact successor meshes/shapes")
 check(not clinic.get_meta("operating_gates_or_dispatch_admitted",true)and not group.get_meta("clinical_operation_admitted",true),"All operating admission held")
 check(group.get_meta("existing_gate_meshes_reused")==84 and group.get_meta("new_gate_meshes")==84 and group.get_meta("new_capacity")==0,"Original84 gate nodes reused; onlymissing84 Pool parts added; zero capacity")
 # Architectural envelope proof excludes only the eight CLOSED leaf pairs. It
 # does not move doors, admit operation, or exclude frames/supports/other scenery.
 var excluded:Array[RID]=actors.duplicate();excluded.append_array(leaves);var route_results:Array=[]
 for zone:Dictionary in plan.zones:
  var points:Array=[]
  for path:Array in zone.paths:
   for i in range(path.size()-1):
    var first:=Vector3(path[i][0],21,path[i][1]);var last:=Vector3(path[i+1][0],21,path[i+1][1]);var count:int=maxi(1,ceili(first.distance_to(last)/.75));var direction:Vector3=(last-first).normalized()
    for j in range(count):points.append({"p":first.lerp(last,float(j)/count),"d":direction})
   var last:Vector3=Vector3(path[-1][0],21,path[-1][1]);points.append({"p":last,"d":(last-Vector3(path[-2][0],21,path[-2][1])).normalized()})
  var blockers:Array=[]
  for sample:Dictionary in points:
   var point:Vector3=sample.p;var transverse:=Vector3(-sample.d.z,0,sample.d.x)
   for offset:float in [-1.7,0,1.7]:
    var p:Vector3=point+transverse*offset;var ray:=PhysicsRayQueryParameters3D.create(p+Vector3.UP*.12,p-Vector3.UP*.35);ray.exclude=actors;var hit:=space.intersect_ray(ray);check(not hit.is_empty()and absf(hit.position.y-21)<.05,"Receiving floor "+zone.id+" "+str(p))
   var shape:=BoxShape3D.new();shape.size=Vector3(.12,3.2,3.6)if absf(sample.d.x)>.5 else Vector3(3.6,3.2,.12);var query:=PhysicsShapeQueryParameters3D.new();query.shape=shape;query.margin=.001;query.exclude=excluded;query.transform.origin=point+Vector3.UP*1.62;var hits:=space.intersect_shape(query,32);var names:Array=[]
   for hit:Dictionary in hits:names.append(str(ship.get_path_to(hit.collider)))
   if not names.is_empty():blockers.append({"point":a(point),"owners":names})
   check(names.is_empty(),"3.6×3.2 architectural envelope "+zone.id+" "+str(point)+" "+str(names))
  route_results.append({"zone":zone.id,"samples":points.size(),"blockers":blockers})
 # The original support contacts must remain solid, including the western pier.
 for row:Array in [[Vector3(99.2,22,29.6),Vector3(100.6,22,29.6),"RoyaltyPier_WestFore"],[Vector3(107.2,22,29.6),Vector3(108.6,22,29.6),"RoyaltyPier_Fore"],[Vector3(107.2,22,50.4),Vector3(108.6,22,50.4),"RoyaltyPier_Aft"],[Vector3(-61.35,22,-405),Vector3(-59.7,22,-405),"GPM_CELL_-4_-21_2"],[Vector3(-54,22,-410),Vector3(-53.1,22,-410),"A_soiled_back_edge_pier1"]]:
  var ray:=PhysicsRayQueryParameters3D.create(row[0],row[1]);ray.exclude=actors;var hit:=space.intersect_ray(ray);check(not hit.is_empty()and str(hit.collider.get_path()).contains(row[2]),"Protected original support contact "+row[2])
 var wall_exports:Array=[]
 for row:Dictionary in plan.patches:
  var mesh:MeshInstance3D=ship.get_node(row.path);wall_exports.append(dump_mesh(mesh));var contact:CollisionShape3D=mesh.find_children("*","CollisionShape3D",true,false)[0];var faces:PackedVector3Array=contact.shape.get_faces();var degenerate:=0
  for i in range(0,faces.size(),3):
   if (faces[i+1]-faces[i]).cross(faces[i+2]-faces[i]).length_squared()==0.0:degenerate+=1
  check(degenerate==0,"No degenerate contact triangles "+row.path)
 var room:Node3D=stream.rooms[plan.room_key]
 for row:Dictionary in plan.room_cuts:
  var mesh:MeshInstance3D=room.find_child(row.name,true,false);check(mesh.get_meta("transfer_source_triangles",0)==row.triangles and mesh.find_children("*","CollisionShape3D",true,false).size()==1,"Streamed source/contact successor "+row.name);wall_exports.append(dump_mesh(mesh))
  var contact:CollisionShape3D=mesh.find_children("*","CollisionShape3D",true,false)[0];var faces:PackedVector3Array=contact.shape.get_faces();var degenerate:=0
  for i in range(0,faces.size(),3):
   if (faces[i+1]-faces[i]).cross(faces[i+2]-faces[i]).length_squared()==0.0:degenerate+=1
  check(degenerate==0 and contact.shape==mesh.get_meta("transfer_contact_lease"),"Streamed precise shape uses existing weak cache "+row.name)
 var gate_exports:Array=[]
 for path:String in bindings[0].paths:gate_exports.append(dump_mesh(ship.get_node(path)))
 # Exercise the actual existing stream release/reload path, then recheck both
 # raised head contacts and the physical protected back-edge partition.
 var actor:Node3D=stream.actor;var original_position:Vector3=actor.global_position;actor.global_position=Vector3(0,180,0);stream.refresh();check(not room.get_meta("stream_loaded",true),"Existing stream releases D01 source normally");stream._ensure_room(target)
 for i in range(3):await physics_frame
 for row:Dictionary in plan.room_cuts:
  var mesh:MeshInstance3D=room.find_child(row.name,true,false);check(mesh!=null and mesh.get_meta("transfer_source_triangles",0)==row.triangles and mesh.find_children("*","CollisionShape3D",true,false).size()==1,"Reload reinstalls one exact receiver successor "+row.name)
 for x:float in [-52.7,-50.0]:
  var ray:=PhysicsRayQueryParameters3D.create(Vector3(x,24.1,-402),Vector3(x,24.5,-402));ray.exclude=actors;var hit:=space.intersect_ray(ray);check(not hit.is_empty()and absf(hit.position.y-24.3)<.002,"Raised receiving soffit remains solid "+str(x))
 actor.global_position=original_position
 var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget");var lighting:Array=[]
 for zone:Dictionary in plan.zones:
  var lights:Array=group.get_node(zone.id).find_children("*","Light3D",true,false);check(lights.size()==4,"Four physicaltasklights "+zone.id);actor.global_position=lights[0].global_position-Vector3.UP*3.5;budget.refresh();var active:=0
  for light in budget.previously_active:
   if group.is_ancestor_of(light):active+=1
  check(active>0 and budget.previously_active.size()<=8,"Existing8-source budget "+zone.id);lighting.append({"zone":zone.id,"total_active":budget.previously_active.size()})
 actor.global_position=original_position;budget.refresh()
 var result:={"status":"PASS"if failures.is_empty()else"FAIL","checks":checks,"failures":failures,"runtime_ready":true,"routes":route_results,"closed_gates":closed,"gate_meshes":meshes_seen.size(),"unique_gate_meshes":shared_meshes.size(),"unique_gate_shapes":shared_shapes.size(),"parts":plan.parts.size(),"batches":group.get_meta("batches"),"new_floor_m2":plan.new_floor_m2,"lights":lighting,"query_exclusions":"Persistent actors and80 closed leaf-part contacts only; all frames, pockets, walls and bearings included","clinical_operation":false,"loaded_cart_turning_accepted":false,"visual_accepted":false,"whole_gameplay_performance_accepted":false}
 FileAccess.open(P+"evidence/INSTALLED_CHECK.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  ")+"\n");FileAccess.open(P+"evidence/WALL_SUCCESSORS.json",FileAccess.WRITE).store_string(JSON.stringify(wall_exports)+"\n");FileAccess.open(P+"evidence/GATE_SUCCESSORS.json",FileAccess.WRITE).store_string(JSON.stringify(gate_exports)+"\n");print("CLINICAL_TRANSFER_CHECK ",JSON.stringify(result));main.free();await process_frame;quit(0 if failures.is_empty()else 1)
