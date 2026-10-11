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
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_COMMONS_CART_DOCKING.json"));var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(90):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea")
 if ship.find_child("D04CommonsCartDocks",true,false)==null:load("res://scripts/d04_commons_cart_docking.gd").build(ship)
 for i in range(10):await physics_frame
 var owner:Node3D=ship.find_child("D04CommonsCartDocks",true,false);var space:=ship.get_world_3d().direct_space_state
 for f in p.source_pins:
  if not p.active or f not in ["Game/scripts/ship.gd","Game/data/programme_ledger.json"]:record("source_"+str(f),FileAccess.get_sha256("/workspace/astraea-recovered-532087b9-20261010T083844Z/"+str(f))==p.source_pins[f])
 for f in p.model_pins:record("model_"+str(f),FileAccess.get_sha256("res://assets/models/"+str(f))==p.model_pins[f])
 for part in p.parts:
  var mesh:MeshInstance3D=owner.find_child(str(part.name),true,false);record("owned_"+str(part.name),mesh!=null);var lo:=Vector3(INF,INF,INF);var hi:=-lo
  for v in part.verts:lo=lo.min(vec(v));hi=hi.max(vec(v))
  if mesh!=null:var bounds:=mesh.global_transform*mesh.get_aabb();record("bounds_"+str(part.name),bounds.position.distance_to(lo)<.00004 and bounds.end.distance_to(hi)<.00004)
 for dock in p.docks:
  var at:=vec(dock.position);record(str(dock.name)+"_operator_dock",capsule_clear(space,vec(dock.operator_dock)))
  for offset in[-1.5,1.5]:record(str(dock.name)+"_side_service_stance_"+str(offset),capsule_clear(space,at+Vector3(offset,0,-.4)))
  for yaw in range(9):record(str(dock.name)+"_retained_station_turn_"+str(yaw),cart_clear(space,Vector3(at.x,16.5,-358.7),yaw*PI/4))
  for i in range(25):
   var pos:=vec(dock.approach).lerp(at,float(i)/24);record(str(dock.name)+"_cart_approach_"+str(i),cart_clear(space,pos,PI));record(str(dock.name)+"_capsule_approach_"+str(i),capsule_clear(space,pos+Vector3(0,0,-1.62)))
 var result={"status":"PASS"if errors.is_empty()else"FAIL","checks":checks.size(),"errors":errors,"new_floor_m2":0,"models":p.model_pins,"source_pins":p.source_pins.size(),"loaded_operation_accepted":false,"vertical_accepted":false};FileAccess.open("res://artifacts/d04_commons_docks_"+("connected"if p.active else"sealed")+".json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":checks.size(),"errors":errors}));quit(0 if errors.is_empty()else 1)
