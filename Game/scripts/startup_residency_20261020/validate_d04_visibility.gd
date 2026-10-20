extends SceneTree
class ResidencyHost extends Node3D:
 var streamed_models:Dictionary
 var exact_contact_residency:Node
func _initialize():call_deferred("run")
func frames(count:int):
 for i in range(count):await process_frame
 await RenderingServer.frame_post_draw
func capture(label:String):
 await RenderingServer.frame_post_draw
 assert(root.get_texture().get_image().save_png("/workspace/shared/astraea_runtime_open/d04_visibility_"+label+".png")==OK)
func run():
 assert(DisplayServer.get_name()!="headless")
 root.use_occlusion_culling=true
 var host:=ResidencyHost.new();root.add_child(host)
 host.streamed_models=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/startup_residency_20261020/index.json")).models
 host.exact_contact_residency=load("res://scripts/startup_residency_20261020/exact_contact_residency.gd").new();host.add_child(host.exact_contact_residency);host.exact_contact_residency.setup(host);host.exact_contact_residency.set_physics_process(false)
 var space:=Node3D.new();space.name="ShipSpace";host.add_child(space)
 var actors:=Node3D.new();actors.name="PersistentActors";space.add_child(actors)
 var actor:=Node3D.new();actor.name="Player";actors.add_child(actor)
 actor.position=Vector3(13.775,18.1,328)
 var camera:=Camera3D.new();host.add_child(camera);camera.position=actor.position;camera.look_at(Vector3(-52,18.1,328));camera.fov=12;camera.current=true
 var environment:=WorldEnvironment.new();host.add_child(environment)
 environment.environment=Environment.new();environment.environment.background_mode=Environment.BG_COLOR;environment.environment.background_color=Color(.08,.09,.11);environment.environment.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;environment.environment.ambient_light_color=Color.WHITE;environment.environment.ambient_light_energy=.7
 var file:="D04_PORT_AFT_HOME_882_r001.glb"
 var manifest:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(str(host.streamed_models[file].manifest_path)))
 var original:Node3D=load("res://scripts/startup_residency_20261020/original_visual_contacts.gd").instantiate_visual(file,manifest);host.add_child(original)
 load("res://scripts/static_room_occlusion.gd").install(original)
 await frames(8);await capture("source_far_entry")
 original.free();await frames(4)
 var manager=load("res://scripts/startup_residency_20261020/d04_detail_residency.gd").new();host.add_child(manager);manager.setup(host);manager.set_physics_process(false)
 var home:=Node3D.new();home.name=manager.index[file].room_id;host.add_child(home)
 manager.register_room(home,file)
 await frames(15)
 var entry:Dictionary=manager.entries[0]
 assert(not manager._near(actor.position,entry.bounds,manager.KEEP),"Test must be outside proximity retention")
 assert(is_instance_valid(entry.detail),"Visible distant doorway details must load independently of proximity")
 await capture("streamed_far_entry")
 camera.look_at(camera.position+Vector3.RIGHT)
 await frames(15);manager.refresh(9.0);await frames(3)
 assert(entry.detail==null,"Offscreen distant private details must genuinely release")
 camera.look_at(Vector3(-52,18.1,328));await frames(15)
 assert(is_instance_valid(entry.detail),"Distant details must reload on visible return")
 await capture("streamed_return")
 print("D04_DISTANT_VISIBILITY_PASS ",JSON.stringify(manager.statistics()))
 host.free();quit()
