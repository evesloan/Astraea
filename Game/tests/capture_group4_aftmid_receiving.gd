extends SceneTree
const OUT:="res://../BlenderCatalogue/assets/group4_completion_20261011/aftmid_upper_receiving_015/"
func _initialize()->void:call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func run()->void:
 root.size=Vector2i(1920,1080);var world:=Node3D.new();root.add_child(world)
 var env:=WorldEnvironment.new();var setting:=Environment.new();setting.background_mode=Environment.BG_COLOR;setting.background_color=Color(.66,.73,.78);setting.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;setting.ambient_light_color=Color(.96,.95,.91);setting.ambient_light_energy=.4;env.environment=setting;world.add_child(env)
 var sun:=DirectionalLight3D.new();sun.rotation_degrees=Vector3(-42,-35,0);sun.light_energy=.6;sun.shadow_enabled=true;world.add_child(sun)
 var camera:=Camera3D.new();camera.fov=57;camera.far=1400;world.add_child(camera);camera.current=true
 var definition:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"));var floors:Array=[]
 for region in definition.regions:
  if region.deck=="D09":floors.append(region)
 var top:=StandardMaterial3D.new();top.albedo_color=Color(.65,.61,.51);var side:=StandardMaterial3D.new();side.albedo_color=Color(.53,.48,.39);load("res://scripts/structural_floor_builder.gd").build_regions(world,top,side,floors,{},"OriginalD09FloorContext")
 var transfers:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://../BlenderCatalogue/assets/group4_completion_20261011/DESTINATION_CONNECTION_CONTRACT.json"))
 for core in transfers.five_core_transfers:
  var scene:Node3D=(load("res://assets/models/"+core.core_model) as PackedScene).instantiate();scene.position=Vector3(core.core_origin[0],core.core_origin[1],core.core_origin[2]);world.add_child(scene)
 var base:Node3D=load("res://scripts/group4_completion.gd").build(world,true,true);load("res://scripts/group4_aftmid_upper_successor.gd").build(base,true)
 camera.position=Vector3(-8,60.8,233);camera.look_at(Vector3(3,56.65,225),Vector3.UP);await frames(35);await RenderingServer.frame_post_draw
 var picture:=root.get_texture().get_image();assert(picture.get_width()==1920 and picture.get_height()==1080);assert(picture.save_png(OUT+"SOURCE_GAME_G4_AFTMID_RECEIVING_WIDE002.png")==OK)
 FileAccess.open(OUT+"SOURCE_GAME_PHOTO_RECEIPT.json",FileAccess.WRITE).store_string(JSON.stringify({"source_fixture_only":true,"resolution":[1920,1080],"view":"Wide Aft Midship original station012 successor030/r002, retained D09 compiled floors and public-core source enclosure","camera_xyz":[-8,60.8,233],"focus_xyz":[3,56.65,225],"source_hidden_or_cut":false,"original_pier_and_floor_preserved":true,"new_missing_only_return_floor_m2":2.7,"review_lighting":"Bright separate review ambient/sun; Compatibility llvmpipe. Not calibrated project lighting, normal-main CRT or target-hardware acceptance.","ordinary_player_evidence":"Separate retained run002 four circuits plus focused Aft Midship run004 original W/E/RMB circuit","production_or_whole_group_accepted":false}," "))
 print("SOURCE_GAME_AFTMID_RECEIVING_PHOTO_SAVED");quit()
