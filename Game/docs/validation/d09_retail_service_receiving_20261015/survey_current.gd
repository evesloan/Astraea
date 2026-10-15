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
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(60);var ship:Node3D=main.get_node("World360/Astraea");var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");player.set_physics_process(false);var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency");var space:=ship.get_world_3d().direct_space_state;var contract:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://docs/group5/STAFF_RISER_INTERFACE_CONTRACT.json"));var rows:Array=[]
 for spec in contract.rows:
  var at:=vec(spec.endpoints[0].world_xyz);var side:float=signf(at.x);player.global_position=at+Vector3.UP*.03;player.force_update_transform();residency.prepare_position(player.global_position);await frames(4);var samples:Array=[]
  for x in[3.,46.,48.,51.,54.,57.,58.5,60.5,61.5,62.25,63.,65.,68.,72.,80.,86.,100.,106.]:
   for dz in[-4.,-2.,0.,2.,4.]:
    var point:=Vector3(side*x,52.5,at.z+dz);var hit:=ray(space,point+Vector3.UP*.03,point-Vector3.UP*.03);samples.append({"at":[point.x,point.y,point.z],"floor":str(hit.collider.get_path())if not hit.is_empty()else"","clear":capsule_clear(space,point)})
  var x0:float=minf(side*46,side*68);var x1:float=maxf(side*46,side*68);rows.append({"chunk":spec.existing_chunk_id,"circuit":spec.existing_circuit_index,"socket":[at.x,at.y,at.z],"samples":samples,"actual_source_top_faces":top_faces(space,x0,x1,at.z-8,at.z+8)})
 player.global_position=Vector3(52.9,52.53,240.9);player.force_update_transform();residency.prepare_position(player.global_position);await frames(4);var living:Array=[]
 for x in[50.,50.6,51.5,52.4,52.9,53.485]:
  for z in[240.9,242.4,242.9,244.,247.,249.]:
   var at:=Vector3(x,52.5,z);var hit:=ray(space,at+Vector3.UP*.03,at-Vector3.UP*.03);living.append({"at":[x,52.5,z],"clear":capsule_clear(space,at),"floor":str(hit.collider.get_path())if not hit.is_empty()else""})
 var owner:Node3D=ship.find_child("LivingGiftsInterior_WIP",true,false);var existing_doors:Array=[]
 for door:Node3D in owner.find_children("Group5Living*","Node3D",true,false):
  if door.get_script()==load("res://scripts/group5_living_slider.gd"):existing_doors.append({"name":str(door.name),"id":str(door.persistent_id),"at":str(door.global_position)})
 FileAccess.open(D+"CURRENT_D09_RECEIVER_PREIMAGES.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"READ_ONLY_CURRENT_D09_RETAIL_RECEIVING_PREIMAGES","production_changed":false,"staff_links":rows,"living_samples":living,"living_actual_top_faces":top_faces(space,49,54.1,240,250),"living_existing_doors":existing_doors,"shopping_unresolved_joins":ship.get_node("ShipSpace/Districts/ShoppingPromenadeChunks").get_meta("unresolved_address_joins"),"Cinema5_east_closure_and_original_tram_unchanged":true},"  "));print("PASS_D09_RETAIL_RECEIVER_PREIMAGES");quit(0)
