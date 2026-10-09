extends SceneTree
# One combined default-scene fitment pass after all focused section installations.
# Uses real production hierarchy and collision world. It is not a visual/cart/full-room acceptance.
func _initialize()->void:
 print("RECEIVED_COMBINED initialize")
 call_deferred("run")
func run()->void:
 var began:=Time.get_ticks_msec()
 print("RECEIVED_COMBINED load default main scene")
 var main:Node=load("res://scenes/main.tscn").instantiate()
 print("RECEIVED_COMBINED build default main scene")
 root.add_child(main)
 var ship:=main.get_node("World360/Astraea") as Node3D
 for frame in range(12):await physics_frame
 print("RECEIVED_COMBINED production ready ",Time.get_ticks_msec()-began)
 assert(ship.get_node("ReceivedSectionInstallation").get_meta("installation_ready",false))
 var definitions:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/received_sections.json"))
 assert(definitions.sections.size()==58,"The two pre-existing D12 installations are preserved separately")
 var received:Node3D=ship.get_node("ShipSpace/Districts/ReceivedSections")
 assert(received.get_child_count()==58)
 var original:Node=ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms")
 assert(original.get_child_count()==303)
 var extra:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/received_structural_meshes.json"))
 assert(FileAccess.get_sha256("res://data/generated/structural_meshes.json")==str(extra.source_checks.baseline_structural_sha256))
 var floors:Node=ship.get_node("ShipSpace/ReceivedSectionStructuralFloors")
 assert(floors.get_child_count()==extra.regions.size())
 for i in range(extra.regions.size()):
  load("res://tests/medical_triage_successor_guard.gd")._botanical_validate_slab(floors.get_child(i),extra.regions[i])
 var exclusions:Array[RID]=[]
 for actor in main.find_children("*","CharacterBody3D",true,false):exclusions.append(actor.get_rid())
 for body in main.find_children("*","RigidBody3D",true,false):exclusions.append(body.get_rid())
 var physics:=ship.get_world_3d().direct_space_state
 var capsule:=CapsuleShape3D.new();capsule.radius=.3;capsule.height=1.8
 var results:Array=[];var blocked_sections:=0;var total_samples:=0
 for section in definitions.sections:
  var key:String=section.programme_key
  var room:Node3D=received.get_node(NodePath(key))
  var translation:Array=section.translation_xyz
  assert(room.position.is_equal_approx(Vector3(translation[0],translation[1],translation[2])))
  assert(room.get_meta("programme_key")==key)
  assert(FileAccess.get_sha256("res://assets/models/"+str(section.model_file))==str(section.source_sha256))
  assert(room.find_children("*","MeshInstance3D",true,false).size()==int(section.source_mesh_count))
  var portal:Array=section.portal_xyz;var origin:=Vector3(portal[0],portal[1],portal[2])
  var sign_x:float=float(section.get("inward_direction_x",1.0 if origin.x>0 else -1.0))
  var start:=origin-Vector3(sign_x*2,0,0)
  if section.has("approach_start_xyz"):
   var a:Array=section.approach_start_xyz;start=Vector3(a[0],a[1],a[2])
  var path:Array[Vector3]=[start,origin+Vector3(sign_x*10,0,0)]
  if section.has("entry_walk_waypoints_xyz"):
   path=[start]
   for point in section.entry_walk_waypoints_xyz:path.append(Vector3(point[0],point[1],point[2]))
  var failures:Array=[];var sampled:=0
  for segment in range(path.size()-1):
   var count:=int(ceil(path[segment].distance_to(path[segment+1])/.25))+1
   for step in range(count):
    var p:Vector3=path[segment].lerp(path[segment+1],float(step)/float(count-1));sampled+=1
    var ray:=PhysicsRayQueryParameters3D.create(p+Vector3.UP*.15,p-Vector3.UP*.4);ray.exclude=exclusions
    var support:=physics.intersect_ray(ray)
    if support.is_empty() or absf(support.position.y-origin.y)>.025:failures.append({"kind":"unsupported_or_wrong_height","xyz":[p.x,p.y,p.z],"collider":"" if support.is_empty() else str(support.collider.get_path())})
    var query:=PhysicsShapeQueryParameters3D.new();query.shape=capsule;query.transform=Transform3D(Basis.IDENTITY,p+Vector3.UP*.925);query.exclude=exclusions
    for hit in physics.intersect_shape(query,32):failures.append({"kind":"static_capsule_obstruction","xyz":[p.x,p.y,p.z],"collider":str(hit.collider.get_path())})
  total_samples+=sampled
  if not failures.is_empty():blocked_sections+=1
  results.append({"programme_key":key,"status":"PASS" if failures.is_empty() else "FAIL","samples":sampled,"source_mesh_count":section.source_mesh_count,"failures":failures})
  print("RECEIVED_COMBINED_SECTION ",key," ","PASS" if failures.is_empty() else "FAIL"," samples=",sampled," failures=",failures.size())
 var receipt:={"status":"PASS" if blocked_sections==0 else "FAIL","scope":"Actual default main scene; exact received identities/counts/transforms/hashes and additive slab geometry, full-world static entry support and capsule clearance. Dynamic actors excluded from static fitment. Local walking receipts remain separate. No visual, whole-room, cart/species, performance or full regression acceptance.","new_sections":58,"preserved_existing_D12_sections":2,"original_floor_owners":303,"new_floor_owners":extra.regions.size(),"entry_samples":total_samples,"blocked_sections":blocked_sections,"elapsed_ms":Time.get_ticks_msec()-began,"results":results}
 var f:=FileAccess.open("res://artifacts/received_sections_combined.json",FileAccess.WRITE);f.store_string(JSON.stringify(receipt,"  "));print("RECEIVED_COMBINED_FINISHED ",receipt.status," blocked=",blocked_sections," ms=",receipt.elapsed_ms)
 quit(0 if blocked_sections==0 else 1)
