extends "res://tests/validate_d04_port_forward_commons_service.gd"
const D="/workspace/astraea-integration-cutoff-20261013/fore404_receiving_preparation_20261015/"
func _initialize()->void:
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/DINING_SERVICE_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ORCHARD_RECEIVING_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/SYNTHESIS_EXTERNAL_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/D09_RETAIL_SERVICE_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/AQUATIC_EXTERNAL_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ARRIVALS_STAFF_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/THREAD_SUCCESSOR_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ARRIVALS_UPPER_STAFF_ADOPTION_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func top_faces(space:PhysicsDirectSpaceState3D,x0:float,x1:float,z0:float,z1:float)->Array:
 var box:=BoxShape3D.new();box.size=Vector3(x1-x0,.28,z1-z0);box.margin=0.;var q:=PhysicsShapeQueryParameters3D.new();q.shape=box;q.margin=0.;q.transform.origin=Vector3((x0+x1)/2,52.39,(z0+z1)/2);var rows:Array=[];var seen:Dictionary={}
 for hit in space.intersect_shape(q,1024):
  var body:Node=hit.collider
  for shape:CollisionShape3D in body.find_children("*","CollisionShape3D",true,false):
   if not shape.shape is ConcavePolygonShape3D or seen.has(shape.get_instance_id()):continue
   seen[shape.get_instance_id()]=true;var faces:PackedVector3Array=shape.shape.get_faces();var triangles:Array=[]
   for i in range(0,faces.size(),3):
    var a:Vector3=shape.global_transform*faces[i];var b:Vector3=shape.global_transform*faces[i+1];var c:Vector3=shape.global_transform*faces[i+2]
    if absf(a.y-52.5)>.0002 or absf(b.y-52.5)>.0002 or absf(c.y-52.5)>.0002:continue
    if maxf(a.x,maxf(b.x,c.x))<x0 or minf(a.x,minf(b.x,c.x))>x1 or maxf(a.z,maxf(b.z,c.z))<z0 or minf(a.z,minf(b.z,c.z))>z1:continue
    triangles.append([[a.x,a.z],[b.x,b.z],[c.x,c.z]])
   if not triangles.is_empty():rows.append({"source_shape":str(shape.get_path()),"shape_faces_sha256":digest(faces.to_byte_array()),"triangles_xz":triangles})
 return rows
func digest(bytes:PackedByteArray)->String:
 var h:=HashingContext.new();h.start(HashingContext.HASH_SHA256);h.update(bytes);return h.finish().hex_encode()
func source_ray(space:PhysicsDirectSpaceState3D,a:Vector3,b:Vector3,actor:CharacterBody3D)->Dictionary:
 var q:=PhysicsRayQueryParameters3D.create(a,b);q.exclude=[actor.get_rid()];return space.intersect_ray(q)
func source_clear(space:PhysicsDirectSpaceState3D,at:Vector3,actor:CharacterBody3D)->bool:
 var q:=PhysicsShapeQueryParameters3D.new();var shape:=CapsuleShape3D.new();shape.radius=.3;shape.height=1.8;shape.margin=.001;q.shape=shape;q.transform=Transform3D(Basis.IDENTITY,at+Vector3.UP*.925);q.exclude=[actor.get_rid()]
 if not space.intersect_shape(q,32).is_empty():return false
 for delta in[Vector3(.3,0,0),Vector3(0,0,.3)]:
  if not source_ray(space,at+Vector3.UP-delta,at+Vector3.UP+delta,actor).is_empty():return false
 return true
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(60);var ship:Node3D=main.get_node("World360/Astraea");var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");player.set_physics_process(false);var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency");var streaming:Node=ship.get_node("ShipSystems/RemainingBatchStreaming");var space:=ship.get_world_3d().direct_space_state;var rows:Array=[]
 for side in[-1.,1.]:
  var at:=Vector3(side*60.5,52.53,-404);player.global_position=at;player.force_update_transform();residency.prepare_position(at);streaming.prepare_position(at);await frames(4);var samples:Array=[]
  for x in[3.,7.,46.,48.,50.,52.,53.,53.5,54.,54.5,55.,56.,57.,58.,58.5,59.,60.,60.5,61.,62.,64.,66.]:
   for z in[-411.,-408.,-406.,-404.,-402.,-400.,-398.,-396.]:
    var p:=Vector3(side*x,52.5,z);var hit:=source_ray(space,p+Vector3.UP*.03,p-Vector3.UP*.03,player);samples.append({"at":[p.x,p.y,p.z],"source_floor":str(hit.collider.get_path())if not hit.is_empty()else"","clear":source_clear(space,p+Vector3.UP*.03,player)})
  rows.append({"socket":[at.x,52.5,at.z],"samples":samples,"actual_source_floor_triangles":top_faces(space,minf(side*40,side*67),maxf(side*40,side*67),-412,-395)})
 var lifts:Array=[]
 for node:Node3D in ship.find_children("*","Node3D",true,false):
  if node.get_script()==load("res://scripts/commons_lift.gd"):lifts.append({"path":str(node.get_path()),"id":str(node.persistent_id),"at":str(node.global_position),"floor_heights":node.floor_heights})
 var group:Node=ship.get_node("ShipSpace/Districts/ShoppingPromenadeChunks");var unresolved=group.get_meta("unresolved_address_joins");FileAccess.open(D+"CURRENT_RUNTIME_FORE404_RECEIVING_PREIMAGES308.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_READONLY_FORE404_CURRENT_RUNTIME_PREIMAGES","production_changed":false,"protected_base":"79a8f9b25b7b498857a75d95630533926bdc0236","source_query_excludes_original_player_only":true,"original_controller_collision_and_source_bodies_unchanged":true,"sockets":rows,"actual_existing_lifts":lifts,"all_address_joins_still_unresolved":unresolved,"target_admission_or_new_construction":false},"  "));print("PASS_FORE404_CURRENT_RUNTIME_PREIMAGES");quit()
