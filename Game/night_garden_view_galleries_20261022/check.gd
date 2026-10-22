extends SceneTree
const P="res://night_garden_view_galleries_20261022/"
var checks:Array=[]
var route:Array=[]
var player:CharacterBody3D
func _initialize():call_deferred("run")
func check(label:String,ok:bool):checks.append({"check":label,"pass":ok});print(label,": ",ok)
func raw(file:String)->Node3D:return load(P+"package.gd").raw("res://assets/models/"+file)
func ray(a:Vector3,b:Vector3,exclude:Array[RID]=[])->Dictionary:
 var q:=PhysicsRayQueryParameters3D.create(a,b);q.exclude=exclude;return player.get_world_3d().direct_space_state.intersect_ray(q)
func key(down:bool):
 var e:=InputEventKey.new();e.physical_keycode=KEY_W;e.pressed=down;Input.parse_input_event(e)
func walk(target:Vector3)->bool:
 for frame in range(1800):
  var d:=target-player.global_position;d.y=0
  if d.length()<.16:
   key(false)
   for settle in range(12):await physics_frame
   route.append({"target":str(target),"actual":str(player.global_position)})
   return absf(player.global_position.y-target.y)<.16
  player.rotation.y=atan2(-d.x,-d.z);key(true);await physics_frame
 key(false);route.append({"target":str(target),"actual":str(player.global_position),"timeout":true});return false
func run():
 var host=load("res://tools/night_garden_residency_20261022/fixture_host.gd").new();root.add_child(host)
 var space:=Node3D.new();space.name="ShipSpace";host.add_child(space)
 var districts:=Node3D.new();districts.name="Districts";space.add_child(districts)
 var systems:=Node.new();systems.name="ShipSystems";host.add_child(systems)
 var actors:=Node3D.new();actors.name="PersistentActors";space.add_child(actors)
 player=load("res://scripts/player.gd").new();player.name="Player";player.position=Vector3(84,93.03,94);actors.add_child(player)
 var lower:=Node3D.new();lower.name="D13_D14_StarboardCommons_WIP";districts.add_child(lower)
 var upper:=Node3D.new();upper.name="D15_D17_StarboardHouseUpper_WIP";lower.add_child(upper)
 var wrapper:=Node3D.new();wrapper.name="StarboardHouseUpperArchitecture";upper.add_child(wrapper);wrapper.position=Vector3(63,84,0)
 var commons:=raw("AST-COM-003.glb");wrapper.add_child(commons)
 for mesh:MeshInstance3D in commons.find_children("*","MeshInstance3D",true,false):load("res://scripts/static_contact_cache.gd").attach(mesh)
 var manager=load(P+"manager.gd").new();host.add_child(manager);manager.setup(host);manager.set_physics_process(false);host.private_detail_residency=manager
 var district:Node3D=load("res://scripts/night_garden_residency_20261022/district.gd").build(host)
 var budget=load("res://scripts/lighting_budget.gd").new();budget.name="LocalShadowSourceBudget";systems.add_child(budget);budget.configure(host,player)
 var initial_lights:int=budget.sources.size()
 var gallery:Node3D=load(P+"package.gd").build(host)
 check("30_original_allocations",manager.entries.size()==30 and manager.index.size()==68)
 check("16_gallery_source_lights_once",budget.sources.size()==initial_lights+16)
 var package:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/night_garden_specialty_d15_20261020/PACKAGE_R003.json"))
 var original:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/night_garden_partition_20261021/index.json")).rooms
 for r in package.rooms:
  var id:int=r.allocation.source_envelope_index
  var home:Node3D=district.get_node(r.allocation.proposed_runtime_id)
  check("rest_identity_"+str(id),home.get_meta("rest_slot_ids")==r.allocation.proposed_rest_slot_ids)
  check("private_source_"+str(id),manager.index[r.model_file].detail_sha256==original[r.model_file].detail_sha256)
  if r.allocation.allocation_x[0]<84:
   check("existing_atrium_shell_"+str(id),manager.index[r.model_file].shell_sha256==original[r.model_file].shell_sha256 and home.find_child("NG"+str(id)+"_OvalAtriumGlass",true,false)!=null)
  else:
   var pane:MeshInstance3D=home.find_child("NVG_"+str(id)+"_PrivateViewPane",true,false)
   check("private_window_"+str(id),pane!=null and pane.material_override is ShaderMaterial and pane.material_override.get_shader_parameter("interior_sign")==-1.0)
 for settle in range(24):await physics_frame
 for row in JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/BUILD_r002.json")).rooms:
  var cz:float=row.window_center_z
  var hit:=ray(Vector3(98.5,95,cz),Vector3(99.5,95,cz))
  check("glazed_aperture_"+str(int(row.index)),not hit.is_empty() and "PrivateViewPane" in str(hit.collider.get_parent().name))
  if not hit.is_empty():check("real_wall_opening_"+str(int(row.index)),ray(Vector3(98.5,95,cz),Vector3(99.5,95,cz),[hit.rid]).is_empty())
 for sign in [-1,1]:
  check("terminal_portal_"+str(sign),ray(Vector3(84,94.2,97.1*sign),Vector3(84,94.2,97.7*sign)).is_empty())
  for x in [84,90,100]:check("new_link_support_"+str(sign)+"_"+str(x),not ray(Vector3(x,93.2,99*sign),Vector3(x,92.8,99*sign)).is_empty())
 var targets:Array[Vector3]=[Vector3(84,93,99),Vector3(100,93,99),Vector3(100,93,93),Vector3(100,93,42),Vector3(100,93,99),Vector3(84,93,99),Vector3(84,93,94)]
 for target in targets:
  var ok:=await walk(target);check("connected_gallery_leg_"+str(route.size()),ok)
  if not ok:break
 var failures:=checks.filter(func(r):return not r.pass)
 var result:={"scope":"Changed outer16 window shells, preserved inner14 atrium shells, same30 private-detail sources; bounded receiving fixture", "checks":checks,"failures":failures.size(),"route":route,"main_hook_applied":false,"visual_acceptance":false,"engineering_acceptance":false}
 var path:=OS.get_cmdline_user_args()[0];assert(not FileAccess.file_exists(path));var f:=FileAccess.open(path,FileAccess.WRITE);f.store_string(JSON.stringify(result,"  ")+"\n");f.close()
 print("VIEW_INTEGRATION checks=",checks.size()," failures=",failures.size())
 quit(0 if failures.is_empty() else 1)
