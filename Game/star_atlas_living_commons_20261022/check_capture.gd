extends SceneTree
const P:="res://star_atlas_living_commons_20261022/"
var checks:Array=[]
var actor:CharacterBody3D
func _initialize()->void:call_deferred("run")
func check(ok:bool,label:String)->void:
 checks.append({"pass":ok,"label":label})
 if not ok:push_error(label)
func walk(target:Vector3)->bool:
 for frame in range(180):
  var delta:=target-actor.global_position;delta.y=0
  if delta.length()<.15:
   var stop:=InputEventKey.new();stop.physical_keycode=KEY_W;stop.pressed=false;Input.parse_input_event(stop)
   for settle in range(8):await physics_frame
   return actor.is_on_floor() and absf(actor.global_position.y-target.y)<.12
  actor.rotation.y=atan2(-delta.x,-delta.z);var key:=InputEventKey.new();key.physical_keycode=KEY_W;key.pressed=true;Input.parse_input_event(key);await physics_frame
 var stop:=InputEventKey.new();stop.physical_keycode=KEY_W;stop.pressed=false;Input.parse_input_event(stop);return false
func run()->void:
 assert(ProjectSettings.load_resource_pack("/tmp/astraea-laptop-contract-1bc13d51/Astraea-1bc13d51.pck"))
 var host:Node3D=load("res://scripts/star_atlas_living_integration_20261022/fixture_host.gd").new();root.add_child(host)
 var space:=Node3D.new();space.name="ShipSpace";host.add_child(space);var districts:=Node3D.new();districts.name="Districts";space.add_child(districts);var systems:=Node.new();systems.name="ShipSystems";host.add_child(systems)
 var upper:Node3D=load("res://scripts/star_atlas_upper.gd").build(districts,host)
 var vip:Node3D=load("res://scripts/group2_vip_dry_club/package.gd").build_on_current_receiver(upper)
 var originals:Array=[]
 for mesh:MeshInstance3D in upper.find_children("*","MeshInstance3D",true,false):originals.append({"object":mesh,"transform":mesh.global_transform,"mesh":mesh.mesh})
 var structural:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"));var regions:Array=[]
 for row:Dictionary in structural.regions:
  if row.id=="D15_star_atlas_protected_cover_0":regions.append(row)
 assert(regions.size()==1)
 var stone:=StandardMaterial3D.new();stone.albedo_color=Color(.53,.46,.35);var ivory:=StandardMaterial3D.new();ivory.albedo_color=Color(.74,.70,.61)
 load("res://scripts/structural_floor_builder.gd").build_regions(space,stone,ivory,regions)
 await host._construction_step("star_atlas_d17_standard_batch.gd")
 for row:Dictionary in originals:check(is_instance_valid(row.object) and row.object.mesh==row.mesh and row.object.global_transform.is_equal_approx(row.transform),"Retained upper/VIP mesh and transform unchanged")
 check(upper.get_meta("source_part_count")==514 and upper.get_meta("new_guest_units")==0,"Original514 upper parts and zero new guest capacity")
 check(vip==upper.get_node("VIPDryClub_Source"),"Original D17 VIP owner retained")
 actor=load("res://scripts/player.gd").new();host.add_child(actor);actor.position=Vector3(-74,93.06,-4.7);actor.set_physics_process(false)
 for frame in range(6):await physics_frame
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PLAN.json"));var physics:=host.get_world_3d().direct_space_state
 for p:Dictionary in plan.placements:
  if not bool(p.collision):continue
  var pos:=Vector3(p.position[0],p.position[1],p.position[2]);var query:=PhysicsRayQueryParameters3D.create(pos+Vector3.UP*.05,pos-Vector3.UP*.12);query.exclude=[actor.get_rid()];var hit:=physics.intersect_ray(query);check(not hit.is_empty() and absf(hit.position.y-pos.y)<.006,"Actual retained floor below "+str(p.name))
 for y in [93.0,97.5]:
  actor.position=Vector3(-74,y+.06,-4.7);actor.velocity=Vector3.ZERO;actor.set_physics_process(true)
  for frame in range(20):await physics_frame
  check(await walk(Vector3(-70,y,-4.7)),"D15/D16 study approach original-player traversal")
  actor.set_physics_process(false)
 actor.position=Vector3(-65.8,93,1)
 var budget:Node=load("res://night_garden_court_completion_20261022/lighting_budget.gd").new();budget.name="LocalShadowSourceBudget";systems.add_child(budget);await physics_frame;budget.configure(host,actor);budget.set_process(false)
 check(budget.previously_active.size()>0 and budget.previously_active.size()<=8,"Existing fixture illumination retained within eight-source selector")
 for light in budget.sources:light.set_meta("fixture_powered",false)
 budget.refresh();check(budget.previously_active.is_empty(),"Power-off releases all active sources")
 for light in budget.sources:light.remove_meta("fixture_powered")
 budget.refresh()
 root.size=Vector2i(1400,900)
 var environment:=Environment.new();environment.background_mode=Environment.BG_COLOR;environment.background_color=Color(.025,.034,.046);environment.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;environment.ambient_light_color=Color(.75,.81,.86);environment.ambient_light_energy=.2;environment.reflected_light_source=Environment.REFLECTION_SOURCE_DISABLED
 var world:=WorldEnvironment.new();world.environment=environment;host.add_child(world)
 var camera:=Camera3D.new();host.add_child(camera);camera.position=Vector3(-65.8,94.65,1);camera.look_at(Vector3(-83,94.3,-5));camera.fov=86;camera.current=true
 var layer:=CanvasLayer.new();root.add_child(layer);var label:=Label.new();layer.add_child(label);label.position=Vector2(22,18);label.add_theme_color_override("font_shadow_color",Color.BLACK);label.add_theme_constant_override("shadow_offset_x",2);label.add_theme_constant_override("shadow_offset_y",2);label.text="STAR ATLAS / D15–D16 LIVING COMMONS / SHARED STUDY + WINDOW LOUNGE\nBounded named-hook assembly — UNFINISHED / NOT WHOLE-SHIP ACCEPTANCE"
 for frame in range(12):await process_frame
 await RenderingServer.frame_post_draw
 var passed:bool=checks.all(func(c):return bool(c.pass))
 var path:=P+"evidence/STAR_ATLAS_LIVING_COMMONS_UNFINISHED.png";assert(not FileAccess.file_exists(path));assert(root.get_texture().get_image().save_png(path)==OK)
 var receipt:={"status":"PASS" if passed else "FAIL","checks":checks,"created_utc":Time.get_datetime_string_from_system(true),"image_sha256":FileAccess.get_sha256(path),"main_hook_used":true,"new_guest_units":0,"new_reserved_rests":0,"retained_upper_parts":514,"D17_VIP_preserved":true,"source_fixtures_rebound":12,"added_lights":0,"active_lights":budget.previously_active.size(),"light_budget":8,"full_ship_started":false,"context":"Exact upper-commons owner, D17 VIP geometry and original compiler D15 cover; lower library, adjacent homes and later outlying receiving patches omitted","visual_accepted":false}
 var f:=FileAccess.open(P+"evidence/CAPTURE.json",FileAccess.WRITE);f.store_string(JSON.stringify(receipt,"\t")+"\n");f.close();print("STAR_ATLAS_LIVING_CHECK ","PASS" if passed else "FAIL"," checks=",checks.size());host.free();await process_frame;quit(0 if passed else 1)
