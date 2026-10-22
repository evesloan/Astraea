extends SceneTree
const P="res://royalty790_integration_20261022/"
var ship:Node3D
var player:CharacterBody3D
var checks:Array=[]
var route:Array=[]
func _initialize():call_deferred("run")
func check(label:String,ok:bool):checks.append({"check":label,"pass":ok});print(label,": ",ok)
func key(down:bool):
 var e:=InputEventKey.new();e.physical_keycode=KEY_W;e.pressed=down;Input.parse_input_event(e)
func walk(target:Vector3)->bool:
 for frame in range(800):
  var d:=target-player.global_position;d.y=0
  if d.length()<.12:
   key(false)
   for settle in range(12):await physics_frame
   route.append({"target":str(target),"actual":str(player.global_position)})
   return absf(player.position.y-target.y)<.23
  player.rotation.y=atan2(-d.x,-d.z);key(true);await physics_frame
 key(false);route.append({"target":str(target),"actual":str(player.global_position),"timeout":true});return false
func run():
 ship=load(P+"fixture_host.gd").new();root.add_child(ship)
 var space:=Node3D.new();space.name="ShipSpace";ship.add_child(space)
 var districts:=Node3D.new();districts.name="Districts";space.add_child(districts)
 var systems:=Node.new();systems.name="ShipSystems";ship.add_child(systems)
 var floors:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
 var regions:Array=floors.regions.filter(func(r):return r.id in ["D17_connected_house_floor_00","D17_starboard_house_extension"])
 assert(regions.size()==2)
 var slab:Node3D=load("res://scripts/structural_floor_builder.gd").build_regions(space,StandardMaterial3D.new(),StandardMaterial3D.new(),regions)
 ship.model(districts,"AST-COM-003.glb","ExistingUpperCommons",Vector3(63,84,0))
 load("res://scripts/d17_connected_house.gd").build(districts,ship)
 var owner:Node3D=districts.get_node("D17ConnectedHouse_WIP");var architecture:Node3D=owner.get_node("D17ConnectedArchitecture")
 # Reproduce the exact four later aft cuts using their current source mesh; no substitute geometry.
 var definition:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D17_STARBOARD_STANDARD_CANDIDATE_20261019.json"))
 var standard:=Node3D.new();standard.name="D17StarboardStandardReceiving";space.add_child(standard)
 var model:Node3D=load(P+"package.gd").raw("res://assets/models/"+str(definition.structure_file));standard.add_child(model)
 for row in definition.walls:
  var replacement:MeshInstance3D=model.find_child(str(row.replacement_name).replace(".","_"),true,false)
  if row.owner!="fore":
   var old:MeshInstance3D=architecture.find_child(row.name,true,false);assert(old.mesh.get_faces().size()==int(row.source_triangles)*3)
   var shape:CollisionShape3D=old.find_children("*","CollisionShape3D",true,false)[0]
   old.mesh=replacement.mesh.duplicate();var margin:float=shape.shape.margin;shape.shape=old.mesh.create_trimesh_shape();shape.shape.margin=margin
  replacement.free()
 var solids:Array[Node]=[]
 for m:MeshInstance3D in model.find_children("*","MeshInstance3D",true,false):
  if definition.structure.collision_policy[str(m.name)].collide:solids.append(m)
 load("res://scripts/static_contact_cache.gd").attach_group(model,solids)
 player=load("res://scripts/player.gd").new();player.position=Vector3(80,102.03,12);ship.add_child(player)
 var budget:Node=load("res://scripts/lighting_budget.gd").new();budget.name="LocalShadowSourceBudget";systems.add_child(budget);budget.configure(ship,player)
 var ids:Dictionary={};var original_meshes:Dictionary={};var original_lights:Dictionary={}
 for m:MeshInstance3D in architecture.find_children("*","MeshInstance3D",true,false):ids[str(m.name)]=m.get_instance_id();original_meshes[str(m.name)]=var_to_bytes(m.mesh.get_faces()).hex_encode().sha256_text()
 for l:Light3D in owner.find_children("*","Light3D",true,false):original_lights[str(l.name)]={"id":l.get_instance_id(),"position":l.global_position}
 var slab_id:=slab.get_instance_id();var original_owner_id:=owner.get_instance_id()
 var delta:Node3D=load(P+"package.gd").build(ship)
 var patched:Array=[]
 for row in JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/RUNTIME_DELTA.json")).patches:patched.append(row.name)
 for m:MeshInstance3D in architecture.find_children("*","MeshInstance3D",true,false):
  check("node_identity_"+str(m.name),ids[str(m.name)]==m.get_instance_id())
  if not str(m.name) in patched:check("unchanged_mesh_"+str(m.name),original_meshes[str(m.name)]==var_to_bytes(m.mesh.get_faces()).hex_encode().sha256_text())
 check("same_floor_owner",slab.get_instance_id()==slab_id and owner.get_instance_id()==original_owner_id)
 for name in original_lights:
  var lamp:Light3D=owner.get_node(name);check("same_lamp_"+name,lamp.get_instance_id()==original_lights[name].id)
  if "CourtView" not in name:check("same_lamp_pose_"+name,lamp.global_position==original_lights[name].position)
 check("court_fixture_rebound",owner.get_node("D17HouseSource_DATUM_light_CourtView").global_position.distance_to(Vector3(99,105.88,38.5))<.002)
 check("original_nine_plus_six_lights",owner.find_children("*","Light3D",true,false).size()==15)
 var lift:Node3D=delta.get_node("Royalty790PrivateLift")
 check("private_lift_held",not lift.operation_ready and not lift.request_floor(1) and lift.phase=="held_receivers_and_private_access")
 check("no_extra_stops",lift.floor_heights==[102.2,106.5] and lift.deck_numbers==[17,17])
 for settle in range(24):await physics_frame
 var targets:Array[Vector3]=[Vector3(80,102,21.5),Vector3(82,102,25),Vector3(88,102,25),Vector3(92,102,25.9),Vector3(92.4,102,30),Vector3(95,102,32.4),Vector3(101,102,33),Vector3(102.5,102,38),Vector3(102.5,102,42.2),Vector3(99,102,42.2),Vector3(95.7,102,40.7),Vector3(95.7,102,41.9),Vector3(95.7,104.25,47.1),Vector3(97.8,104.25,47.1),Vector3(97.8,106.5,41.5),Vector3(100.5,106.5,41.5),Vector3(106.5,106.5,42)]
 var forward_ok:=true
 for target in targets:
  var ok:=await walk(target);check("connected_leg_"+str(route.size()),ok)
  if not ok:forward_ok=false;break
 if forward_ok:
  targets.reverse();targets.append(Vector3(80,102,12))
  for target in targets:
   var ok:=await walk(target);check("return_leg_"+str(route.size()),ok)
   if not ok:break
 check("still_held_after_route",not lift.operation_ready and lift.current_floor==0 and lift.cabin_gate.open_fraction==0)
 var failures:=checks.filter(func(r):return not r.pass)
 var result:={"scope":"Exact current aft-owner patches, compiler slabs, commons and royalty upper bounded fixture; no full-main or admission acceptance","checks":checks,"failures":failures.size(),"route":route,"route_teleports":0,"main_hook_applied":false,"final_visual_acceptance":false}
 var path:=OS.get_cmdline_user_args()[0];assert(not FileAccess.file_exists(path));var f:=FileAccess.open(path,FileAccess.WRITE);f.store_string(JSON.stringify(result,"  ")+"\n");f.close()
 # Export actual instantiated construction for one fresh review view; no collision nodes are made into visible geometry.
 var output:=P+"evidence/BoundedIntegratedContext.glb"
 if failures.is_empty() and not FileAccess.file_exists(output):
  var doc:=GLTFDocument.new();var state:=GLTFState.new();assert(doc.append_from_scene(ship,state)==OK);assert(doc.write_to_filesystem(state,output)==OK)
 print("ROYALTY_INTEGRATION checks=",checks.size()," failures=",failures.size()," routelegs=",route.size())
 quit(0 if failures.is_empty() else 1)
