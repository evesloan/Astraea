extends SceneTree
const OUT:="res://../BlenderCatalogue/assets/group4_completion_20261011/theater_upper_approaches_016/"
func _initialize()->void:call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func picture(camera:Camera3D,selector:Node,at:Vector3,focus:Vector3,name:String)->void:
 camera.position=at;camera.look_at(focus,Vector3.UP);selector.refresh();await frames(20);await RenderingServer.frame_post_draw
 var pic:=root.get_texture().get_image();assert(pic.get_width()==1920 and pic.get_height()==1080);assert(pic.save_png(OUT+name)==OK);print("G4_THEATER_SOURCE_PHOTO_SAVED ",name)
func run()->void:
 root.size=Vector2i(1920,1080);var world:=Node3D.new();world.name="OriginalTheaterAndGroup4ExteriorSourceReview";root.add_child(world)
 var env:=WorldEnvironment.new();var settings:=Environment.new();settings.background_mode=Environment.BG_COLOR;settings.background_color=Color(.58,.65,.71);settings.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;settings.ambient_light_color=Color(.96,.95,.91);settings.ambient_light_energy=.30;env.environment=settings;world.add_child(env)
 var sun:=DirectionalLight3D.new();sun.rotation_degrees=Vector3(-42,-35,0);sun.light_energy=.40;sun.shadow_enabled=true;world.add_child(sun)
 var space:=Node3D.new();space.name="ShipSpace";world.add_child(space);var districts:=Node3D.new();districts.name="Districts";space.add_child(districts)
 var definition:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"));var floors:Array=[]
 for r in definition.regions:
  if r.deck in ["D11","D12","D13","D14"]:floors.append(r)
 var top:=StandardMaterial3D.new();top.albedo_color=Color(.65,.61,.51);var side:=StandardMaterial3D.new();side.albedo_color=Color(.53,.48,.39);load("res://scripts/structural_floor_builder.gd").build_regions(space,top,side,floors)
 load("res://scripts/grand_lantern_theater_section.gd").build(districts,world);load("res://scripts/group4_theater_upper_approaches.gd").build(districts,true)
 var camera:=Camera3D.new();camera.fov=65;camera.far=1400;world.add_child(camera);camera.current=true
 var selector:Node=load("res://scripts/lighting_budget.gd").new();selector.name="ExistingLightingSelectorForReviewFixture";world.add_child(selector);selector.configure(world,camera);await frames(30)
 await picture(camera,selector,Vector3(-9,81.5,-93),Vector3(-19,77.5,-126),"SOURCE_GAME_G4_THEATER_STACKED_APPROACHES_WIDE004.png")
 if not FileAccess.file_exists(OUT+"SOURCE_GAME_G4_D12_THEATER_RECEIVING_EYE001.png"):
  await picture(camera,selector,Vector3(-4.2,79.65,-126),Vector3(-33,79.8,-126),"SOURCE_GAME_G4_D12_THEATER_RECEIVING_EYE001.png")
 FileAccess.open(OUT+"SOURCE_GAME_PHOTO_RECEIPT.json",FileAccess.WRITE).store_string(JSON.stringify({"resolution":[1920,1080],"source_fixture_only":true,"retained_source_context":"Actual original GrandLantern builder,2200 chairs and original D11 portico/compiled floor plus D11-D14 original floor context; new Group4 D12/D13 exterior assembly","original_geometry_hidden_or_cut":false,"upper_doors_closed":true,"lights":"Six copied original physical coffer fixtures under canonical8-source selector; separate review sun/ambient. No ordinary-main CRT, calibration, target-hardware or final-art acceptance.","ordinary_player_evidence":"Separate ACTUAL_PLAYER_RECEIVING.json and original-main test log","new_beam_loads_adopted":false,"whole_group_complete":false}," "));quit()
