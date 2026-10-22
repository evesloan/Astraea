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
 var gallery:Node3D=load(P+"package.gd").build(host)
 var count:=0
 for m:MeshInstance3D in district.find_children("*","MeshInstance3D",true,false):
  if m.material_override is ShaderMaterial and m.material_override.shader.resource_path==P+"private_view.gdshader":
   assert(m.material_override.get_shader_parameter("interior_sign") in [-1.0,1.0]);count+=1
 assert(count==46)
 for entry in manager.entries:
  if str(entry.record.model_file)=="NightGardenD15Specialty_404_r002.glb":manager._load_entry(entry)
 await physics_frame
 var path:=P+"evidence/ActualBoundedGalleryContext.glb";assert(not FileAccess.file_exists(path))
 var doc:=GLTFDocument.new();var state:=GLTFState.new();assert(doc.append_from_scene(host,state)==OK);assert(doc.write_to_filesystem(state,path)==OK)
 var f:=FileAccess.open(P+"evidence/PRIVACY_EXPORT.json",FileAccess.WRITE);f.store_string(JSON.stringify({"privacy_panes":count,"policy":"inside alpha0.12/outside alpha1, camera-side plane; GPU visual acceptance pending","export_sha256":FileAccess.get_sha256(path),"scope":"Actual bounded Godot fixture with current gallery adapter and404 private furnishings; not full main"},"  ")+"\n");f.close()
 print("PRIVACY_CONTEXT 46 panes, actual bounded scene exported")
 quit()
