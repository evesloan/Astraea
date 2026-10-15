extends "res://tests/validate_d04_port_forward_commons_service.gd"
const D="/workspace/astraea-integration-cutoff-20261013/d09_retail_service_receiving_20261015/"
func _initialize()->void:
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/DINING_SERVICE_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ORCHARD_RECEIVING_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/SYNTHESIS_EXTERNAL_ADOPTION_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
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
func occupants(space:PhysicsDirectSpaceState3D,at:Vector3)->Array:
 var shape:=CapsuleShape3D.new();shape.radius=.3;shape.height=1.8;shape.margin=.001;var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform.origin=at+Vector3.UP*.925;var out:Array=[]
 for hit in space.intersect_shape(q,128):out.append(str(hit.collider.get_path()))
 for delta in[Vector3(.3,0,0),Vector3(0,0,.3)]:
  var h:=ray(space,at+Vector3.UP-delta,at+Vector3.UP+delta)
  if not h.is_empty()and not str(h.collider.get_path())in out:out.append(str(h.collider.get_path()))
 return out
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(60);var ship:Node3D=main.get_node("World360/Astraea");var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");player.set_physics_process(false);var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency");var space:=ship.get_world_3d().direct_space_state;var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://docs/group5/STAFF_RISER_INTERFACE_CONTRACT.json"));var rows:Array=[]
 for spec in d.rows:
  var at:=vec(spec.endpoints[0].world_xyz);player.global_position=at+Vector3.UP*.03;player.force_update_transform();residency.prepare_position(player.global_position);await frames(4);var probes:Array=[]
  for dx in[-.5,0.,.5,1.5]:
   for dz in[-2.,0.,2.]:
    for dy in[0.,.03]:
     var point:=at+Vector3(dx,dy,dz);var h:=ray(space,point+Vector3.UP*.08,point-Vector3.UP*.08);probes.append({"at":[point.x,point.y,point.z],"occupants":occupants(space,point),"floor":str(h.collider.get_path())if not h.is_empty()else"","floor_y":h.position.y if not h.is_empty()else null})
  rows.append({"chunk":spec.existing_chunk_id,"probes":probes})
 var living:Array=[]
 for point in[Vector3(52.9,52.53,240.9),Vector3(53.485,52.53,244),Vector3(52.9,52.53,242.4),Vector3(51.5,52.53,247)]:
  player.global_position=point;residency.prepare_position(point);await frames(3);living.append({"at":[point.x,point.y,point.z],"occupants":occupants(space,point)})
 var aquatic:Array=[]
 for y in[44.,45.45]:
  for x in[99.2,100.1,101.5,103.35,105.,108.]:
   for z in[208.6,210.,211.4]:
    var point:=Vector3(x,y,z);var h:=ray(space,point+Vector3.UP*.08,point-Vector3.UP*2.);aquatic.append({"at":[x,y,z],"occupants":occupants(space,point),"floor":str(h.collider.get_path())if not h.is_empty()else"","floor_y":h.position.y if not h.is_empty()else null})
 FileAccess.open(D+"EXACT_SOCKET_BLOCKERS_AND_NEXT_AQUATIC_DATUM.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"READ_ONLY_IMMEDIATE_INTERFACE_QUERY","production_changed":false,"staff_sockets":rows,"living_receiving":living,"aquatic_next_preimages":aquatic},"  "));print("PASS_EXACT_RETAIL_SOCKET_BLOCKERS_AND_AQUATIC_DATUM");quit(0)
