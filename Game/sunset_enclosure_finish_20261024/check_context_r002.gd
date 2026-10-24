extends SceneTree
const P:="res://sunset_enclosure_finish_20261024/"
var checks:Array=[]
func _initialize()->void:call_deferred("run")
func check(ok:bool,label:String)->void:
 checks.append({"pass":ok,"label":label})
 if not ok:push_error(label)
func run()->void:
 var capture:=OS.get_cmdline_user_args().has("--capture")
 var adapter=load(P+"adapter_r002.gd")
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PLAN_r002.json"))
 var host:Node3D=load("res://scripts/sunset_enclosure_integration_20261024/fixture_host.gd").new();root.add_child(host)
 var space:=Node3D.new();space.name="ShipSpace";host.add_child(space)
 var districts:=Node3D.new();districts.name="Districts";space.add_child(districts)
 var systems:=Node.new();systems.name="ShipSystems";host.add_child(systems)
 var actors:=Node3D.new();actors.name="PersistentActors";space.add_child(actors)
 var actor:CharacterBody3D=load("res://scripts/player.gd").new();actor.position=Vector3(-57,93,328);actor.spawn_position=actor.position;actors.add_child(actor);actor.set_physics_process(false)
 var manager:Node=load("res://scripts/night_garden_residency_20261022/manager.gd").new();host.add_child(manager);manager.setup(host);manager.set_physics_process(false);host.private_detail_residency=manager
 var house:Node3D=load("res://scripts/sunset_adoption.gd").build(host)
 var ordinary:Node3D=districts.get_node("SunsetRoomCandidates");var ids:Array=[]
 for n in ordinary.get_children():ids.append(n.get_instance_id())
 var before:Dictionary=adapter.parts(house,plan);var floors:={};var preserved:={}
 for key in before:
  var mesh:MeshInstance3D=before[key]
  if str(mesh.get_meta("extras",{}).category) in ["floor","stair","stair_landing"]:floors[key]={"id":mesh.get_instance_id(),"mesh":mesh.mesh,"transform":mesh.transform}
 for row in plan.surface_assignments:preserved[row.node]={"id":before[row.node].get_instance_id(),"mesh":before[row.node].mesh,"transform":before[row.node].transform}
 await host._construction_step("sunset_adoption.gd")
 var result:=house.get_node_or_null("SunsetEnclosure_r002")as Node3D
 check(result!=null,"new enclosure built through actual inherited main hook")
 if result==null:host.free();quit(1);return
 check(adapter.receiving_error(host,plan).is_empty(),"exact receiving owners/bounds and identity guard passes")
 check(ids.size()==83,"83 original ordinary home objects")
 for id in ids:check(is_instance_valid(instance_from_id(id)),"ordinary home identity retained")
 var district:Node3D=districts.get_node("SunsetSpecialty47_20261022")
 check(manager.entries.size()==47 and district.get_meta("reserved_rests")==59 and district.get_meta("new_capacity")==0,"47 specialty allocations and59 rests;zero new capacity")
 var after:Dictionary=adapter.parts(house,plan)
 for key in floors:
  var row:Dictionary=floors[key];var n:MeshInstance3D=after[key]
  check(n.get_instance_id()==row.id and n.mesh==row.mesh and n.transform==row.transform,"original floor/stair intact "+key)
 for key in preserved:
  var row:Dictionary=preserved[key];var n:MeshInstance3D=after[key]
  check(n.get_instance_id()==row.id and n.mesh==row.mesh and n.transform==row.transform,"original enclosure mesh/contact owner retained "+key)
 check(house.get_node("RetainedLandscapeAndSeating").get_child_count()==133,"133 original landscape placements retained")
 check(result.find_children("*","StaticBody3D",true,false).size()==16,"16 source-wall contact groups")
 check(result.find_children("*","SpotLight3D",true,false).size()==plan.lights.size(),"Authored mounted sources in existing selector")
 check(adapter.build(host)==result,"idempotent main installation")
 var probe:MeshInstance3D=after[plan.surface_assignments[0].node];var prior:=probe.transform;probe.position.x+=.1
 check(not adapter.receiving_error(host,plan).is_empty(),"negative changed-source-pose guard rejects")
 probe.transform=prior
 check(adapter.receiving_error(host,plan).is_empty(),"original pose restored after negative guard")
 for frame in range(8):await physics_frame
 # Public routes and source floors remain actual collision owners. New work
 # projects at most36cm from a pinned opaque wall, never over open routes.
 for y in [84.0,88.5,93.0,97.5,102.0]:
  for x in [-92.0,-80.0,-65.0]:
   var query:=PhysicsRayQueryParameters3D.create(Vector3(x,y+.5,370),Vector3(x,y-.6,370));query.exclude=[actor.get_rid()]
   var hit:=host.get_world_3d().direct_space_state.intersect_ray(query)
   check(not hit.is_empty() and absf(hit.position.y-y)<.02,"retained public crosslink floor D%d x%d"%[13+int((y-84)/4.5),int(x)])
 var environment:=Environment.new();environment.background_mode=Environment.BG_COLOR;environment.background_color=Color(.025,.034,.046);environment.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;environment.ambient_light_color=Color(.75,.81,.86);environment.ambient_light_energy=.2;environment.reflected_light_source=Environment.REFLECTION_SOURCE_DISABLED
 var world:=WorldEnvironment.new();world.environment=environment;host.add_child(world)
 if capture:
  var package:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://sunset_specialty_bank_20261022/PACKAGE_R002.json"))
  var room:Dictionary=package.rooms.filter(func(r):return int(r.allocation.source_envelope_index)==402)[0]
  var entry:Dictionary=manager.entries.filter(func(e):return str(e.record.model_file)==str(room.model_file))[0];manager._load_entry(entry)
  check(is_instance_valid(entry.detail),"resident402 actual detail present")
  for home in ordinary.get_children():load("res://scripts/deferred_home_visual.gd").ensure(home)
 var budget:Node=load("res://night_garden_court_completion_20261022/lighting_budget.gd").new();systems.add_child(budget);await physics_frame;budget.configure(host,actor);budget.set_process(false)
 check(budget.previously_active.size()<=8,"existing eight-source cap preserved")
 for light in budget.sources:light.set_meta("fixture_powered",false)
 budget.refresh();check(budget.previously_active.is_empty(),"real fixture-power-off gate")
 for light in budget.sources:light.remove_meta("fixture_powered")
 budget.refresh()
 var image_path:="";var camera_position:=Vector3(-57,94.65,328);var target:=Vector3(-85,95.0,344)
 if capture and checks.all(func(c):return c.pass):
  root.size=Vector2i(1400,900)
  var camera:=Camera3D.new();host.add_child(camera);camera.position=camera_position;camera.look_at(target);camera.fov=82;camera.far=900;camera.current=true
  var layer:=CanvasLayer.new();root.add_child(layer);var label:=Label.new();layer.add_child(label);label.position=Vector2(22,18);label.add_theme_color_override("font_shadow_color",Color.BLACK);label.add_theme_constant_override("shadow_offset_x",2);label.add_theme_constant_override("shadow_offset_y",2);label.text="SUNSET CONSERVATORY / FIVE-LEVEL ENCLOSURE / RESIDENT402 OUTLOOK\nActual main-hook bounded assembly — UNFINISHED / NOT WHOLE-SHIP ACCEPTANCE"
  for frame in range(12):await process_frame
  await RenderingServer.frame_post_draw
  image_path=P+"evidence_r002/SUNSET_ENCLOSURE_CONTEXT_UNFINISHED.png"
  check(not FileAccess.file_exists(image_path),"new immutable capture destination")
  if checks.all(func(c):return c.pass):
   var saved:=root.get_texture().get_image().save_png(image_path);check(saved==OK,"actual pixel capture saved")
 var report:={"status":"PASS_FOCUSED" if checks.all(func(c):return c.pass)else"HOLD","checks":checks,"created_utc":Time.get_datetime_string_from_system(true),"actual_main_hook":true,"source_parts":plan.parts.size(),"original_material_assignments":40,"ordinary_homes":83,"specialty_allocations":47,"rest_ids":59,"retained_landscape":133,"active_lights":budget.previously_active.map(func(l):return str(l.name)),"global_light_budget":8,"image":image_path,"image_sha256":FileAccess.get_sha256(image_path)if not image_path.is_empty()else"","camera":str(camera_position),"target":str(target),"ambient_energy":.2,"exposure_changed":false,"scope":"Actual Sunset adoption/lift/receiving/Vesper,83 homes,47 specialty shells,original court/landscape plus new enclosure;capture includes402 details. Other districts/private details omitted.","whole_ship_startup":false,"visual_accepted":false}
 var f:=FileAccess.open(P+"evidence_r002/"+("CAPTURE.json"if capture else"CHECK.json"),FileAccess.WRITE);f.store_string(JSON.stringify(report,"  ")+"\n");f.close();print("SUNSET_CONTEXT ",report.status," checks=",checks.size()," active=",budget.previously_active.size());var ok:bool=report.status=="PASS_FOCUSED";host.free();await process_frame;quit(0 if ok else 1)
