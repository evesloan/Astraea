extends SceneTree
var checks:Dictionary={}
var errors:Array=[]
func record(key:String,ok:bool)->void:
	checks[key]=ok
	if not ok:errors.append(key)
func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func ray(space:PhysicsDirectSpaceState3D,a:Vector3,b:Vector3)->Dictionary:
	return space.intersect_ray(PhysicsRayQueryParameters3D.create(a,b))
func capsule_clear(space:PhysicsDirectSpaceState3D,at:Vector3)->bool:
	var q:=PhysicsShapeQueryParameters3D.new();var shape:=CapsuleShape3D.new();shape.radius=.3;shape.height=1.8;shape.margin=.001
	q.shape=shape;q.transform=Transform3D(Basis.IDENTITY,at+Vector3.UP*.925)
	if not space.intersect_shape(q,32).is_empty():return false
	# Opposite cross-rays also catch a stance placed wholly inside an opaque
	# closed mesh; concave surface queries alone can miss that case.
	for delta in [Vector3(.3,0,0),Vector3(0,0,.3)]:
		if not ray(space,at+Vector3.UP-delta,at+Vector3.UP+delta).is_empty():return false
	return true
func cart_clear(space:PhysicsDirectSpaceState3D,at:Vector3,yaw:float)->bool:
	var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/cleaning_cart_contacts.json"))
	var pose:=Transform3D(Basis(Vector3.UP,yaw),at+Vector3.UP*.005)
	for item in d.boxes:
		var shape:=BoxShape3D.new();shape.size=vec(item.size);shape.margin=.001
		var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform=pose*Transform3D(Basis.IDENTITY,vec(item.center))
		if not space.intersect_shape(q,32).is_empty():return false
	for item in d.wheel_contacts:
		var shape:=SphereShape3D.new();shape.radius=float(item.radius);shape.margin=.001
		var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform=pose*Transform3D(Basis.IDENTITY,vec(item.center))
		if not space.intersect_shape(q,32).is_empty():return false
	return true
func physical_key(down:bool)->void:
	var e:=InputEventKey.new();e.keycode=KEY_W;e.physical_keycode=KEY_W;e.pressed=down;Input.parse_input_event(e)
func walk_to(player:CharacterBody3D,goal:Vector3)->Dictionary:
	var start:=player.global_position;var delta:=goal-start;delta.y=0
	player.rotation.y=atan2(-delta.x,-delta.z);physical_key(true)
	var budget:=int(delta.length()/3.1*60)+150;var frames:=0;var reached:=false;var route_contacts:Dictionary={}
	for i in range(budget):
		await physics_frame;frames+=1
		for j in range(player.get_slide_collision_count()):route_contacts[str(player.get_slide_collision(j).get_collider().get_path())]=true
		var now:=goal-player.global_position;now.y=0
		if now.dot(delta.normalized())<.16:reached=true;break
	physical_key(false)
	for i in range(20):await physics_frame
	var contacts:Array=[]
	for i in range(player.get_slide_collision_count()):contacts.append(str(player.get_slide_collision(i).get_collider().get_path()))
	if not reached:print("WALK_BLOCKED_CONTACTS ",contacts," ALL ",route_contacts.keys())
	var at:=player.global_position;var horizontal:=Vector2(at.x-goal.x,at.z-goal.z).length()
	return {"reached":reached and horizontal<.55 and absf(at.y-goal.y)<.12,"frames":frames,"start":str(start),"goal":str(goal),"final":str(at),"floor_contact":player.is_on_floor(),"existing_player_controller":true}
func _initialize()->void:call_deferred("run")
func run()->void:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_SOCIAL_DAYROOM.json"))
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(90):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
 if ship.find_child("D04SocialDayroom",true,false)==null:load("res://scripts/d04_social_dayroom.gd").build(ship)
 for i in range(10):await physics_frame
 var space:=ship.get_world_3d().direct_space_state
 for f in p.source_pins:
  if not p.open_gallery_connection or f not in p.integration_exceptions:record("source_"+str(f),FileAccess.get_sha256("/workspace/astraea-recovered-532087b9-20261010T083844Z/"+str(f))==p.source_pins[f])
 for f in p.model_pins:record("model_"+str(f),FileAccess.get_sha256("res://assets/models/"+str(f))==p.model_pins[f])
 var owner:Node3D=ship.find_child("D04SocialDayroom",true,false)
 record("capacity_preserved",p.units.size()==20 and p.new_rest_places==0)
 for part in p.parts:
  var mesh:MeshInstance3D=owner.find_child(str(part.name),true,false);record("owned_mesh_"+str(part.name),mesh!=null)
  if mesh!=null:
   var lo:=Vector3(INF,INF,INF);var hi:=-lo
   for v in part.verts:lo=lo.min(vec(v));hi=hi.max(vec(v))
   var bounds:=mesh.global_transform*mesh.get_aabb();record("exact_owned_bounds_"+str(part.name),bounds.position.distance_to(lo)<.00004 and bounds.end.distance_to(hi)<.00004)
 for i in range(p.foundation_feet.size()):
  for dx in[-.44,0,.44]:
   for dz in[-.44,0,.44]:
    var at:=vec(p.foundation_feet[i].at)+Vector3(dx,-.3,dz);var h:=ray(space,at-Vector3.UP*.02,at+Vector3.UP*.02);record("keel_"+str(i)+"_"+str(dx)+"_"+str(dz),not h.is_empty() and str(h.collider.get_parent().name)=="HUL_KeelPan"and absf(h.position.y+3.5)<.002)
 var start:int=0 if p.open_gallery_connection else 1
 var sample_count:=0
 for j in range(start,p.route.size()-1):
  var a:=vec(p.route[j]);var b:=vec(p.route[j+1]);var steps:=int(ceil(a.distance_to(b)/.2))
  for k in range(steps+1):
   var at:=a.lerp(b,float(k)/steps);record("capsule_"+str(sample_count),capsule_clear(space,at));var h:=ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02);record("bearing_"+str(sample_count),not h.is_empty() and absf(h.position.y-16.5)<.002);sample_count+=1
 # Preserve enclosing walls and original garden screen, and prove aperture state.
 for item in [["west",Vector3(-84.5,18,-370),Vector3(-85,18,-370)],["south",Vector3(-78,18,-375.5),Vector3(-78,18,-376.1)],["garden_privacy",Vector3(-73.2,18,-370),Vector3(-72.7,18,-370)],["roof",Vector3(-80,20.3,-368),Vector3(-80,20.8,-368)]]:record(str(item[0])+"_enclosed",not ray(space,item[1],item[2]).is_empty())
 record("gallery_aperture_state",ray(space,Vector3(-78.5,18,-364.3),Vector3(-78.5,18,-363.5)).is_empty()==bool(p.open_gallery_connection))
 var walks:Array=[]
 if p.open_gallery_connection:
  player.global_position=vec(p.route[0])+Vector3.UP*.03;player.velocity=Vector3.ZERO;player.set_controls_enabled(true);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position)
  for i in range(15):await physics_frame
  for goal in p.route.slice(1):
   var result:Dictionary=await walk_to(player,vec(goal));walks.append(result);record("actual_controller_walk_"+str(walks.size()),result.reached and result.floor_contact)
  for goal in [p.route[2],p.route[1],p.route[0]]:
   var result:Dictionary=await walk_to(player,vec(goal));walks.append(result);record("actual_controller_return_"+str(walks.size()),result.reached and result.floor_contact)
 physical_key(false)
 var result={"status":"PASS"if errors.is_empty()else"FAIL","checks":checks.size(),"errors":errors,"source_pins":p.source_pins.size(),"route_samples":sample_count,"controller_walks":walks,"connected":p.open_gallery_connection,"cart_operation_accepted":false,"final_graphics_accepted":false}
 FileAccess.open("res://artifacts/d04_social_dayroom_"+("connected"if p.open_gallery_connection else"sealed")+".json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":checks.size(),"errors":errors}));quit(0 if errors.is_empty()else 1)
