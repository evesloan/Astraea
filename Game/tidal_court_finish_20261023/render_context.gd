extends SceneTree
const P := "res://tidal_court_finish_20261023/"
var failed:=false
func _initialize()->void:call_deferred("run")
func raw(path:String)->Node3D:
 var document:=GLTFDocument.new();var state:=GLTFState.new();state.handle_binary_image=GLTFState.HANDLE_BINARY_EMBED_AS_UNCOMPRESSED
 var error:=document.append_from_buffer(FileAccess.get_file_as_bytes(path),path.get_base_dir(),state)
 if error!=OK:failed=true;push_error("context source unavailable "+path);return null
 return document.generate_scene(state)
func run()->void:
 root.size=Vector2i(1280,800)
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PLAN.json"))
 var definition:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(plan.definition))
 var ship:=Node3D.new();root.add_child(ship)
 var space:=Node3D.new();space.name="ShipSpace";ship.add_child(space)
 var districts:=Node3D.new();districts.name="Districts";space.add_child(districts)
 var house:=Node3D.new();house.name="TidalGardenReceivingCandidate";districts.add_child(house)
 house.set_meta("persistent_id","tidal_garden_house_001");house.set_meta("installed_guest_units",131)
 var visual:=raw(plan.model);house.add_child(visual)
 var faces:=PackedVector3Array()
 for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
  if mesh.get_meta("extras",{}).get("runtime_collision",false):
   for point in mesh.mesh.get_faces():faces.append(mesh.global_transform*point)
 # Every retained furnishing/planting placement is present, not just the landing crop.
 var furnishings:=Node3D.new();furnishings.name="RetainedLandscapeAndSeating";house.add_child(furnishings)
 var templates:={}
 for row in definition.retained_asset_instances:
  var id:String=row.catalogue_id
  if not templates.has(id):
   var path:String="res://assets/models/"+str(definition.retained_asset_definitions[id].model_file)
   if FileAccess.get_sha256(path)!=str(definition.retained_asset_definitions[id].sha256):push_error("context asset hash differs");quit(1);return
   templates[id]=raw(path)
  var placement:=Node3D.new();placement.name=row.name;placement.position=Vector3(row.world_xyz[0],row.world_xyz[1],row.world_xyz[2]);placement.rotation.y=deg_to_rad(row.yaw);placement.scale=Vector3.ONE*float(row.scale);furnishings.add_child(placement)
  var asset:Node3D=templates[id].duplicate();placement.add_child(asset)
  if not id.begins_with("AST-BOT"):
   for mesh:MeshInstance3D in asset.find_children("*","MeshInstance3D",true,false):
    for point in mesh.mesh.get_faces():faces.append(mesh.global_transform*point)
 for template in templates.values():template.free()
 var body:=StaticBody3D.new();ship.add_child(body);var contact:=CollisionShape3D.new();var shape:=ConcavePolygonShape3D.new();shape.set_faces(faces);contact.shape=shape;body.add_child(contact)
 var landing:Node3D=load("res://tidal_d14_landing_20261023/adapter.gd").build(ship)
 var finish:Node3D=load(P+"adapter.gd").build(ship)
 if landing==null or finish==null or failed:quit(1);return
 var environment:=WorldEnvironment.new();var settings:=Environment.new();settings.background_mode=Environment.BG_COLOR;settings.background_color=Color(.015,.02,.026)
 settings.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;settings.ambient_light_color=Color(.30,.34,.39);settings.ambient_light_energy=.22;settings.tonemap_mode=Environment.TONE_MAPPER_FILMIC;environment.environment=settings;ship.add_child(environment)
 var camera:=Camera3D.new();ship.add_child(camera);camera.position=Vector3(-75,94.65,-370);camera.look_at(Vector3(-87,93.5,-402));camera.fov=80;camera.near=.08;camera.far=500;camera.current=true
 var actor:=Node3D.new();actor.position=camera.position-Vector3(0,1.65,0);ship.add_child(actor)
 await physics_frame;await physics_frame
 var budget:Node=load("res://scripts/lighting_budget.gd").new();ship.add_child(budget);budget.configure(ship,actor)
 for i in 5:await process_frame
 await RenderingServer.frame_post_draw
 var picture:=root.get_texture().get_image()
 var error:=picture.save_png(P+"evidence/TIDAL_COURT_CONTEXT_UNFINISHED.png")
 if error!=OK:push_error("Cannot save context picture");quit(1);return
 var receipt:={"status":"bounded_actual_Godot_context_unfinished","camera":var_to_str(camera.position),"target":"D15 supported cross-ship arrival looking fore across court","original_architecture_meshes":334,"retained_furnishing_plant_placements":furnishings.get_child_count(),"new_geometry":0,"prior_Tidal_D14_landing_present":true,"active_shadow_sources":budget.previously_active.size(),"selector_budget":budget.shadow_source_budget,"ambient_energy":.22,"render_adapter":RenderingServer.get_video_adapter_name(),"image_sha256":FileAccess.get_sha256(P+"evidence/TIDAL_COURT_CONTEXT_UNFINISHED.png"),"omitted_context":"Private131-unit interiors and later service/adjacent-hull receivers outside this bounded court fixture. This image cannot establish whole-ship context or missing production owners.","main_integrated":false,"visual_accepted":false,"target_hardware_performance":false}
 var f:=FileAccess.open(P+"evidence/CONTEXT_VIEW.json",FileAccess.WRITE);f.store_string(JSON.stringify(receipt,"  ")+"\n");f.close();print("TIDAL_COURT_CONTEXT ",JSON.stringify(receipt));ship.free();quit()
