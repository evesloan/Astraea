extends SceneTree
func _initialize()->void:call_deferred("run")
func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(90):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea")
 var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");player.global_position=Vector3(-44,16.53,-441.6);player.velocity=Vector3.ZERO;ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position)
 for i in range(15):await physics_frame
 paused=true
 var space:=ship.get_world_3d().direct_space_state;var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PORT_FORWARD_HOMES_THIRD.json"));var rows:Array=[]
 for r in p.rooms:
  var out:Vector3=vec(r.outlook_world);var sign:float=-1 if r.court_side=="west"else 1
  var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(out+Vector3.UP*1.65,out+Vector3(sign*8,1.65,0)))
  rows.append({"room":r.source_index,"original_outlook":str(out),"ray_hit":str(hit.collider.get_path())if not hit.is_empty()else"none","ray_at":str(hit.get("position","none"))})
  var points:Array=[]
  if r.source_index==976:points=[[-52.95,16.5,-440],[-52.75,16.5,-441.1],[-57.95,16.5,-441.6],[-57.95,16.5,-441.25],[-57.95,16.5,-440.75]]
  else:points=[[-33.05,16.5,-443.75],[-34.3,16.5,-442.7],[-30.4,16.5,-443.7],[-30.4,16.5,-441.4]]
  for at in points:
   var q:=PhysicsShapeQueryParameters3D.new();var shape:=CapsuleShape3D.new();shape.radius=.3;shape.height=1.8;shape.margin=.001;q.shape=shape;q.transform=Transform3D(Basis.IDENTITY,vec(at)+Vector3.UP*.925);var paths:Array=[]
   for h in space.intersect_shape(q,64):paths.append(str(h.collider.get_path()))
   var cross:Array=[]
   for d in[Vector3(.3,0,0),Vector3(0,0,.3)]:
    var h:=space.intersect_ray(PhysicsRayQueryParameters3D.create(vec(at)+Vector3.UP-d,vec(at)+Vector3.UP+d))
    if not h.is_empty():cross.append(str(h.collider.get_path()))
   rows.append({"room":r.source_index,"at":at,"contacts":paths,"cross_ray_contacts":cross})
 FileAccess.open("/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/d04_port_forward_homes_third_20261010/STANCE_DIAGNOSTIC.json",FileAccess.WRITE).store_string(JSON.stringify(rows,"  "));print(JSON.stringify(rows));quit(0)
