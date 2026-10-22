extends SceneTree
const P:="res://sunset_specialty_bank_20261022/"
var checks:Array=[]
var routes:Array=[]
var actor:CharacterBody3D
func _initialize()->void:call_deferred("run")
func check(ok:bool,label:String)->void:
 checks.append({"pass":ok,"label":label})
 if not ok:push_error(label)
func key(down:bool)->void:
 var e:=InputEventKey.new();e.physical_keycode=KEY_W;e.pressed=down;Input.parse_input_event(e)
func walk(target:Vector3)->bool:
 for frame in range(240):
  var delta:=target-actor.global_position;delta.y=0
  if delta.length()<.12:
   key(false)
   for settle in range(8):await physics_frame
   return actor.is_on_floor() and absf(actor.global_position.y-target.y)<.12
  actor.rotation.y=atan2(-delta.x,-delta.z);key(true);await physics_frame
 key(false);return false
func run()->void:
 assert(ProjectSettings.load_resource_pack("/tmp/astraea-laptop-contract-1bc13d51/Astraea-1bc13d51.pck"))
 var host:Node3D=load("res://scripts/sunset_court_finish_integration_20261022/fixture_host.gd").new();root.add_child(host)
 var space:=Node3D.new();space.name="ShipSpace";host.add_child(space)
 var districts:=Node3D.new();districts.name="Districts";space.add_child(districts)
 var systems:=Node.new();systems.name="ShipSystems";host.add_child(systems)
 var actors:=Node3D.new();actors.name="PersistentActors";space.add_child(actors)
 actor=load("res://scripts/player.gd").new();actor.position=Vector3(10000,10000,10000);actors.add_child(actor);actor.set_physics_process(false)
 var manager:Node=load("res://scripts/night_garden_residency_20261022/manager.gd").new();host.add_child(manager);manager.setup(host);manager.set_physics_process(false);host.private_detail_residency=manager
 var house:Node3D=load("res://scripts/sunset_adoption.gd").build(host)
 var before_meshes:=house.find_children("*","MeshInstance3D",true,false).size()
 var ordinary:Node3D=districts.get_node("SunsetRoomCandidates");var original_ids:Array=[]
 for n in ordinary.get_children():original_ids.append(n.get_instance_id())
 check(original_ids.size()==83,"83 retained ordinary homes present")
 await host._construction_step("sunset_adoption.gd")
 var district:Node3D=districts.get_node("SunsetSpecialty47_20261022")
 var package:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PACKAGE_R002.json"))
 check(district.get_meta("reserved_rests")==59 and district.get_meta("new_capacity")==0,"59 unchanged reserved rest IDs; no new capacity")
 check(manager.entries.size()==47,"47 rooms registered in existing residency owner")
 check(house.find_children("*","MeshInstance3D",true,false).size()==before_meshes-18+68,"18 prior receiving batches replaced;68 bounded finish parts added; floors unchanged")
 for id in original_ids:check(instance_from_id(id)!=null,"Original ordinary home object retained")
 for frame in range(100):await physics_frame
 var room:Dictionary=package.rooms.filter(func(r):return int(r.allocation.source_envelope_index)==402)[0]
 var entry:Dictionary=manager.entries.filter(func(e):return str(e.record.model_file)==str(room.model_file))[0];manager._load_entry(entry);assert(is_instance_valid(entry.detail))
 actor.position=Vector3(-57,93,328);actor.set_physics_process(false)
 for home in ordinary.get_children():load("res://scripts/deferred_home_visual.gd").ensure(home)
 root.size=Vector2i(1400,900)
 var environment:=Environment.new();environment.background_mode=Environment.BG_COLOR;environment.background_color=Color(.025,.034,.046);environment.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;environment.ambient_light_color=Color(.75,.81,.86);environment.ambient_light_energy=.2;environment.reflected_light_source=Environment.REFLECTION_SOURCE_DISABLED
 var world:=WorldEnvironment.new();world.environment=environment;host.add_child(world)
 var budget:Node=load("res://night_garden_court_completion_20261022/lighting_budget.gd").new();systems.add_child(budget);await physics_frame;await physics_frame;budget.configure(host,actor);budget.set_process(false)
 assert(budget.previously_active.size()<=8)
 for light in budget.sources:light.set_meta("fixture_powered",false)
 budget.refresh();assert(budget.previously_active.is_empty())
 for light in budget.sources:light.remove_meta("fixture_powered")
 budget.refresh()
 var camera:=Camera3D.new();host.add_child(camera);camera.position=Vector3(-57,94.65,328);camera.look_at(Vector3(-80,94.5,340));camera.fov=82;camera.far=900;camera.current=true
 var layer:=CanvasLayer.new();root.add_child(layer);var label:=Label.new();layer.add_child(label);label.position=Vector2(22,18);label.add_theme_color_override("font_shadow_color",Color.BLACK);label.add_theme_constant_override("shadow_offset_x",2);label.add_theme_constant_override("shadow_offset_y",2);label.text="SUNSET CONSERVATORY / RECEIVING COURT FINISH / RESIDENT402 OUTLOOK\nActual main-hook bounded assembly — UNFINISHED / NOT WHOLE-SHIP ACCEPTANCE"
 for frame in range(12):await process_frame
 await RenderingServer.frame_post_draw
 assert(checks.all(func(c):return bool(c.pass)))
 var path:="res://sunset_court_finish_20261022/evidence/SUNSET_COURT_RESIDENT402_R002_UNFINISHED.png";assert(not FileAccess.file_exists(path));assert(root.get_texture().get_image().save_png(path)==OK)
 assert(checks.all(func(c):return bool(c.pass)))
 var court:Node3D=house.get_node("SunsetCourtFinish20261022")
 assert(court.find_children("*","MeshInstance3D",true,false).size()==68)
 assert(court.find_children("*","MultiMeshInstance3D",true,false).size()==413)
 assert(house.get_node("RetainedLandscapeAndSeating").get_child_count()==133)
 var receipt:={"checks":checks.size(),"court_finish":house.get_meta("sunset_court_finish_20261022"),"active_fixture_names":budget.previously_active.map(func(l):return str(l.name)),"status":"PASS","created_utc":Time.get_datetime_string_from_system(true),"image_sha256":FileAccess.get_sha256(path),"main_hook_used":true,"bounded_source_assembly":true,"ordinary_homes":83,"specialty_rooms":47,"reserved_rests":59,"room":402,"camera":[-57,94.65,328],"target":[-80,94.5,340],"light_budget":8,"active_lights":budget.previously_active.size(),"power_off_pass":true,"existing_house_fixtures_enrolled":district.get_meta("existing_house_fixtures_enrolled"),"whole_ship_runtime":false,"visual_accepted":false}
 var f:=FileAccess.open("res://sunset_court_finish_20261022/evidence/CAPTURE.json",FileAccess.WRITE);f.store_string(JSON.stringify(receipt,"\t")+"\n");f.close();print("SUNSET_CAPTURE ",JSON.stringify(receipt));host.free();await process_frame;quit()
