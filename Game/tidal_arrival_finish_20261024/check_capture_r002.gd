extends SceneTree
const P := "res://tidal_arrival_finish_20261024/"
var failures:Array[String]=[]
var checks:=0
func _initialize()->void:call_deferred("run")
func test(value:bool,message:String)->void:
 checks+=1
 if not value:failures.append(message);push_error(message)
func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func run()->void:
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PLAN_r002.json"))
 var adapter=load(P+"adapter_r002.gd")
 var ship:=Node3D.new();root.add_child(ship)
 test(not adapter.receiving_error(ship,plan).is_empty(),"absent owner rejected")
 var space:=Node3D.new();space.name="ShipSpace";ship.add_child(space)
 var districts:=Node3D.new();districts.name="Districts";space.add_child(districts)
 var lift:Node3D=load("res://scripts/tidal_lift_candidate.gd").build(ship)
 var house:Node3D=lift.get_parent()
 test(lift.landing_gates.size()==5,"all five actual retained landing gates included")
 test(lift.persistent_id==&"tidal_garden_lift_001","actual lift identity retained")
 # Bounded fixture declares the unchanged adoption interface, as in the prior
 # connected check. Private-room instantiation/capacity acceptance is omitted.
 house.set_meta("persistent_id","tidal_garden_house_001");house.set_meta("installed_guest_units",131)
 test(load("res://tidal_d14_landing_20261023/adapter.gd").build(ship)!=null,"prior D14 retained")
 test(load("res://tidal_court_finish_20261023/adapter_r002.gd").build(ship)!=null,"prior court finish retained")
 var old_plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(plan.source_plan))
 var parts:Dictionary=load("res://tidal_court_finish_20261023/adapter_r002.gd").source_parts(house,old_plan)
 var before:={}
 for name in parts:
  var m:MeshInstance3D=parts[name];before[name]=[m.mesh,m.global_transform,m.get_active_material(0),m.get_child_count()]
 test(adapter.receiving_error(ship,plan).is_empty(),"all five exact header supports")
 var added:Node3D=adapter.build(ship)
 test(added!=null,"new package attaches")
 if added==null:ship.free();quit(1);return
 test(adapter.build(ship)==added,"idempotent installation")
 for name in parts:
  var m:MeshInstance3D=parts[name];var b:Array=before[name]
  test(m.mesh==b[0] and m.global_transform==b[1] and m.get_active_material(0)==b[2] and m.get_child_count()==b[3],"original geometry/contact/material unchanged "+str(name))
 var new_meshes:=added.find_children("*","MeshInstance3D",true,false)
 test(new_meshes.size()==20,"four shared material batches on each of five decks")
 for m:MeshInstance3D in new_meshes:
  var y:=84.0+(int(m.get_meta("deck"))-13)*4.5
  var bounds:AABB=m.global_transform*m.get_aabb()
  test(bounds.position.y>=y+2.899 and bounds.end.y<=y+3.811,"new solids stay above retained clear opening "+str(m.name))
  test(bounds.position.x>=-76.441 and bounds.end.x<=-72.559,"new crown within retained header width "+str(m.name))
 test(added.find_children("*","CollisionShape3D",true,false).size()==5,"one bounded fixed-contact group per deck")
 var lights:=added.find_children("*","Light3D",true,false)
 test(lights.size()==10,"ten physical fixture sources")
 var actor:=Node3D.new();ship.add_child(actor)
 actor.position=Vector3(-75,93,-370);await physics_frame;await physics_frame
 var budget:Node=load("res://scripts/lighting_budget.gd").new();ship.add_child(budget);budget.configure(ship,actor)
 var per_deck:=[]
 for deck in range(13,18):
  actor.position=Vector3(-75,84+(deck-13)*4.5,-370);await physics_frame;budget.refresh()
  var local_active:=0
  for light in lights:
   if int(light.get_meta("deck"))==deck and light.visible:local_active+=1
  test(budget.previously_active.size()<=8 and budget.shadow_source_budget==8,"unchanged budget D"+str(deck))
  test(local_active>0,"local physical arrival source visible D"+str(deck))
  per_deck.append({"deck":deck,"total_active":budget.previously_active.size(),"new_local_active":local_active})
 for light in lights:light.set_meta("fixture_powered",false)
 budget.refresh();test(lights.all(func(x):return not x.visible and not x.shadow_enabled),"power-off guard")
 for light in lights:light.set_meta("fixture_powered",true)
 var header:MeshInstance3D=parts["TG_Batch_331"];header.position.z+=.01
 test(not adapter.receiving_error(ship,plan).is_empty(),"shifted header rejected");header.position.z-=.01
 house.set_meta("installed_guest_units",132);test(not adapter.receiving_error(ship,plan).is_empty(),"capacity mismatch rejected");house.set_meta("installed_guest_units",131)
 var report:={"status":"PASS" if failures.is_empty()else"FAIL","checks":checks,"failures":failures,"retained_architecture":334,"native_new_parts":80,"new_spatial_batches":20,"new_contact_groups":5,"new_lights":10,"per_deck":per_deck,"rooms_capacity_changed":false,"new_floor_or_cut":false,"full_ship":false,"final_visual_accepted":false}
 var f:=FileAccess.open(P+"evidence_r002/CHECK.json",FileAccess.WRITE);f.store_string(JSON.stringify(report,"  ")+"\n");f.close();print(JSON.stringify(report))
 if not failures.is_empty():ship.free();quit(1);return
 if "--capture" in OS.get_cmdline_user_args():
  root.size=Vector2i(1280,800)
  var environment:=WorldEnvironment.new();var settings:=Environment.new();settings.background_mode=Environment.BG_COLOR;settings.background_color=Color(.015,.02,.026)
  settings.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;settings.ambient_light_color=Color(.30,.34,.39);settings.ambient_light_energy=.22;settings.tonemap_mode=Environment.TONE_MAPPER_FILMIC;environment.environment=settings;ship.add_child(environment)
  var camera:=Camera3D.new();ship.add_child(camera);camera.position=Vector3(-75,94.65,-370);camera.look_at(Vector3(-87,93.5,-402));camera.fov=80;camera.near=.08;camera.far=500;camera.current=true
  actor.position=Vector3(-75,93,-370);await physics_frame;budget.refresh()
  for i in 8:await process_frame
  await RenderingServer.frame_post_draw
  var out:=P+"evidence_r002/TIDAL_ARRIVAL_CONTEXT_UNFINISHED.png"
  if FileAccess.file_exists(out):push_error("Refuse duplicate capture output");ship.free();quit(1);return
  var error:=root.get_texture().get_image().save_png(out)
  if error!=OK:push_error("Capture failed");ship.free();quit(1);return
  var capture:={"status":"UNFINISHED_CONNECTED_CONTEXT","sha256":FileAccess.get_sha256(out),"same_camera_and_exposure_as_prior":true,"context_difference":"Retained five-stop lift included; prior r001 omitted it","ambient_energy":.22,"camera":[-75,94.65,-370],"fixture":"Actual receiving builder/frontage,81 source placements,transfer,priorD14,court finish and retained five-stop cabin/landing gates","omitted":"Private131 interiors and later service/neighbor receivers","active_sources":budget.previously_active.size(),"render_adapter":RenderingServer.get_video_adapter_name(),"production_integrated":false,"final_visual_accepted":false}
  f=FileAccess.open(P+"evidence_r002/CAPTURE.json",FileAccess.WRITE);f.store_string(JSON.stringify(capture,"  ")+"\n");f.close();print(JSON.stringify(capture))
 ship.free();quit(0)
