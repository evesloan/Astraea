extends SceneTree
var failures:Array=[]
var checks:=0
var details:Array=[]
const OUT="/workspace/crew-bank-receiving-20261019/INSTALLED_RUNTIME.json"
func _initialize()->void:call_deferred("run")
func frames(n:int)->void:
 for i in n:await physics_frame
func check(ok:bool,label:String,detail:Variant=null)->void:
 checks+=1
 if not ok:failures.append({"check":label,"detail":detail})
func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func save_result()->void:
 FileAccess.open(OUT,FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_PHYSICAL_RECEIVING" if failures.is_empty() else "HOLD","checks":checks,"failures":failures,"details":details,"registered_berths_added":0,"final_art_acceptance":false},"  "))
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
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(20)
 var ship:Node3D=main.get_node("World360/Astraea")
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_remaining_crew_20261019/PACKAGE.json"))
 var old_count:int=ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms").get_child_count()
 var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget");var old_lights:int=budget.sources.size()-549
 var bank:Node3D=ship.get_node("ShipSpace/Group3RemainingCrewBank");await frames(5)
 var space:PhysicsDirectSpaceState3D=ship.get_world_3d().direct_space_state
 var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");actor.set_physics_process(false)
 check(p.instances.size()==183 and p.rest_surfaces.size()==366,"Source allocation/rest counts")
 check(budget.sources.size()==old_lights+549,"549 source light bindings exactly once")
 check(ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms").get_child_count()==old_count,"No compiled floor owners added")
 for q in p.fixtures:check(budget.sources.count(bank.get_node(str(q.name)+"_PhysicalSource"))==1,"Fixture "+str(q.name))
 for q in p.rest_surfaces:
  var at:Vector3=v(q.surface);var hit:Dictionary=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.035,at-Vector3.UP*.035))
  check(not hit.is_empty() and bank.is_ancestor_of(hit.collider),"Source rest contact "+q.allocation_key+q.place, str(hit.collider.get_path()) if not hit.is_empty() else "none")
 for q in p.instances:
  var pos:Vector3=v(q.position);var basis:=Basis(Vector3.UP,q.yaw)
  for local in [Vector3(0,0,0),Vector3(5,0,0),Vector3(7,0,0),Vector3(9,0,0),Vector3(11,0,0),Vector3(13.9,0,0)]:
   var sample:Vector3=local
   if q.allocation_key=="D03_crew_atlas_drawing_210" and local==Vector3.ZERO:sample=Vector3(.7,0,0) # Original PCW_Column47 occupies the centre; inspect adjacent actual walking floor.
   var at:Vector3=pos+basis*sample;var hit:Dictionary=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.025,at-Vector3.UP*.025))
   check(not hit.is_empty() and abs(hit.position.y-12)<.002,"Floor seam "+q.allocation_key+str(local.x),str(hit.collider.get_path()) if not hit.is_empty() else "none")
 for q in p.service_doors:
  var door:Node3D=bank.get_node(q.name)
  check(door.open_fraction==0 and not door.desired_open and str(door.persistent_id)==q.physical_component_id,"Closed physical gate "+q.name)
  actor.global_position=door.to_global(Vector3(0,.03,-2.2));door.interact(actor)
  check(door.authorization_denied and not door.desired_open,"Unknown external permission refused "+q.name)
 # Independent inside actor setup for opposite banks; normal existing door interaction API.
 for idx in [0,49,100,160]:
  var door:Node3D=bank.get_node(p.service_doors[idx].name);actor.global_position=door.to_global(Vector3(0,.03,2.2));door.interact(actor);await frames(90)
  check(not door.authorization_denied and door.desired_open and door.open_fraction>.99,"Inside egress "+str(idx))
 # Physical aperture test only: explicitly open all entries, without granting external authority.
 actor.global_position=Vector3(0,12.03,0)
 for q in p.service_doors:bank.get_node(q.name).desired_open=true
 await frames(90)
 var capsule:=CapsuleShape3D.new();capsule.radius=.3;capsule.height=1.8
 for q in p.instances:
  var pos:Vector3=v(q.position);var basis:=Basis(Vector3.UP,q.yaw)
  for step in range(21):
   var at:Vector3=pos+basis*Vector3(4.5+step*.5,.92,0)
   var query:=PhysicsShapeQueryParameters3D.new();query.shape=capsule;query.transform=Transform3D(Basis.IDENTITY,at);query.margin=.001;query.exclude=[actor.get_rid()]
   var hits:Array=space.intersect_shape(query,12)
   if not hits.is_empty():
    var names:Array=[]
    for h in hits:names.append(str(h.collider.get_path()))
    check(false,"Open source passage "+q.allocation_key+" localX="+str(4.5+step*.5),names)
   else:check(true,"Open source passage")
 actor.set_physics_process(true);actor.set_controls_enabled(true)
 for idx in [0,49,100,160]:
  var door:Node3D=bank.get_node(p.service_doors[idx].name)
  actor.global_position=door.to_global(Vector3(0,.03,2.2));actor.velocity=Vector3.ZERO
  ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position)
  ship.get_node("ShipSystems/RemainingBatchStreaming").prepare_position(actor.global_position)
  await frames(20)
  var goal:Vector3=door.to_global(Vector3(0,0,-2.2))
  var leg:Dictionary=await walk_to(actor,goal);details.append(leg);check(leg.reached and leg.floor_contact,"Original player entry-egress walk "+str(idx),leg)
 save_result();print("REMAINING_CREW checks=",checks," failures=",failures.size());quit(0 if failures.is_empty() else 1)
