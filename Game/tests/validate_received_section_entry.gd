extends SceneTree
func _initialize()->void:call_deferred("run")
func fail(message:String)->void:
 print("FAIL: ",message);quit(1)
func run()->void:
 var args:=OS.get_cmdline_user_args()
 assert(args.size()==1,"Pass one programme key after --")
 var key:String=args[0]
 var definition:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/received_sections.json"))
 var section:Dictionary={}
 for row in definition.sections:
  if str(row.programme_key)==key:section=row
 assert(not section.is_empty())
 var portal:Array=section.portal_xyz
 var origin:=Vector3(float(portal[0]),float(portal[1]),float(portal[2]))
 var sign_x:float=1.0 if origin.x>0 else -1.0
 sign_x=float(section.get("inward_direction_x",sign_x))
 var world:=Node3D.new();root.add_child(world)
 var helper:Node3D=load("res://scripts/ship.gd").new()
 if section.has("receiving_core_contract"):
  var core:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/"+str(section.receiving_core_contract)))
  var o:Array=core.origin
  helper.model(world,str(core.enclosure_file),"ExistingCore",Vector3(o[0],o[1],o[2]))
 elif absf(origin.z)>400:
  var contract_path:String="res://data/architecture/AFT_PUBLIC_CORE.json" if origin.z>0 else "res://data/architecture/FORWARD_PUBLIC_CORE.json"
  var core:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(contract_path))
  var o:Array=core.origin
  helper.model(world,str(core.enclosure_file),"ExistingCore",Vector3(o[0],o[1],o[2]))
 elif absf(origin.x)>40 and absf(origin.z)<5:
  helper.model(world,"AST-ATR-001_botanical_nursery_open001.glb","BotanicalReceiving",Vector3.ZERO)
  helper.model(world,"AST-ATR-001.glb","AtriumGuards",Vector3.ZERO)
 var translation:Array=section.translation_xyz
 assert(FileAccess.get_sha256("res://assets/models/"+str(section.model_file))==str(section.source_sha256))
 var model:Node3D=helper.model(world,str(section.model_file),"Section",Vector3(translation[0],translation[1],translation[2]),float(section.rotation_y))
 assert(model.find_children("*","MeshInstance3D",true,false).size()==int(section.source_mesh_count))
 var base:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
 var extra:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/received_structural_meshes.json"))
 var rows:Array=[]
 for row in base.regions+extra.regions:
  if absf(float(row.floor_y)-origin.y)<.001:rows.append(row)
 var mat:=StandardMaterial3D.new()
 load("res://scripts/structural_floor_builder.gd").build_regions(world,mat,mat,rows)
 for frame in range(4):await physics_frame
 var physics:=world.get_world_3d().direct_space_state
 var capsule:=CapsuleShape3D.new();capsule.radius=.3;capsule.height=1.8
 var start:=origin-Vector3(sign_x*2,0,0)
 if section.has("approach_start_xyz"):
  var a:Array=section.approach_start_xyz
  start=Vector3(a[0],a[1],a[2])
 var path:Array[Vector3]=[start,origin+Vector3(sign_x*10,0,0)]
 if section.has("entry_walk_waypoints_xyz"):
  path=[start]
  for point in section.entry_walk_waypoints_xyz:path.append(Vector3(point[0],point[1],point[2]))
 var sample_count:=0
 var hits:Array=[]
 for segment in range(path.size()-1):
  var count:=int(ceil(path[segment].distance_to(path[segment+1])/.25))+1
  for step in range(count):
   var p:Vector3=path[segment].lerp(path[segment+1],float(step)/float(count-1))
   sample_count+=1
   var query:=PhysicsShapeQueryParameters3D.new();query.shape=capsule;query.transform=Transform3D(Basis.IDENTITY,p+Vector3.UP*.925)
   for hit in physics.intersect_shape(query,32):hits.append({"xyz":[p.x,p.y,p.z],"collider":str(hit.collider.get_path())})
 if not hits.is_empty():
  var f:=FileAccess.open("res://artifacts/received_entry_"+key+"_blocked.json",FileAccess.WRITE);f.store_string(JSON.stringify(hits,"  "))
  fail(JSON.stringify(hits));return
 var actor:CharacterBody3D=load("res://scripts/player.gd").new()
 actor.spawn_position=start+Vector3.UP*.1;actor.position=actor.spawn_position;world.add_child(actor)
 for frame in range(20):await physics_frame
 var walking_frames:=0
 var destinations:Array[Vector3]=[]
 for i in range(1,path.size()):destinations.append(path[i])
 for i in range(path.size()-2,-1,-1):destinations.append(path[i])
 for target in destinations:
  var direction:Vector3=target-actor.position
  actor.rotation.y=atan2(-direction.x,-direction.z)
  var down:=InputEventKey.new();down.physical_keycode=KEY_W;down.keycode=KEY_W;down.pressed=true;Input.parse_input_event(down)
  var reached:=false
  var segment_budget:=int(ceil(actor.position.distance_to(target)/.05))+90
  for frame in range(segment_budget):
   var before:Vector3=actor.position
   await physics_frame
   walking_frames+=1
   if actor.position.distance_to(before)>.15 or absf(actor.position.y-origin.y)>.08:fail("Unsupported player movement");return
   var ray:=PhysicsRayQueryParameters3D.create(actor.position+Vector3.UP*.15,actor.position-Vector3.UP*.2);ray.exclude=[actor.get_rid()]
   var support:=physics.intersect_ray(ray)
   if support.is_empty() or absf(support.position.y-origin.y)>.02:fail("Missing floor support");return
   if Vector2(actor.position.x-target.x,actor.position.z-target.z).length()<.08:reached=true;break
  var up:=InputEventKey.new();up.physical_keycode=KEY_W;up.keycode=KEY_W;up.pressed=false;Input.parse_input_event(up)
  if not reached:fail("Entry target unreachable: "+str(actor.position));return
  for frame in range(12):await physics_frame
 var result:={"status":"PASS","section":key,"source_sha256":section.source_sha256,"scope":"Focused current production builders and source interface with unchanged player; combined default scene and visual review separate","walking_frames":walking_frames,"support_samples":walking_frames,"capsule_samples":sample_count,"post_start_teleports":0}
 var receipt:=FileAccess.open("res://artifacts/received_entry_"+key+".json",FileAccess.WRITE);receipt.store_string(JSON.stringify(result,"  "))
 print("PASS: ",JSON.stringify(result));helper.free();quit()
