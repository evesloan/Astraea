extends SceneTree
const P := "res://tidal_court_finish_20261023/"
var checks:=0
var failures:Array[String]=[]
func _initialize()->void:call_deferred("run")
func test(ok:bool,message:String)->void:
 checks+=1
 if not ok:failures.append(message);push_error(message)
func raw(path:String)->Node3D:
 var document:=GLTFDocument.new();var state:=GLTFState.new()
 state.handle_binary_image=GLTFState.HANDLE_BINARY_EMBED_AS_UNCOMPRESSED
 var error:=document.append_from_buffer(FileAccess.get_file_as_bytes(path),path.get_base_dir(),state)
 test(error==OK,"raw source parse");return document.generate_scene(state)
func run()->void:
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PLAN.json"))
 var adapter=load(P+"adapter_r002.gd")
 var ship:=Node3D.new();root.add_child(ship)
 test(not adapter.receiving_error(ship,plan).is_empty(),"missing owner rejected")
 var space:=Node3D.new();space.name="ShipSpace";ship.add_child(space)
 var districts:=Node3D.new();districts.name="Districts";space.add_child(districts)
 var connected:=OS.get_cmdline_user_args().has("--connected")
 var house:Node3D
 if connected:
  house=load("res://scripts/tidal_garden_receiving.gd").build(ship,plan.definition)
 else:
  house=Node3D.new();house.name="TidalGardenReceivingCandidate";districts.add_child(house)
 house.set_meta("persistent_id","tidal_garden_house_001");house.set_meta("installed_guest_units",131)
 if not connected:
  var visual:=raw(plan.model);house.add_child(visual)
 else:
  test(load("res://tidal_d14_landing_20261023/adapter.gd").build(ship)!=null,"retained D14 package attaches to actual receiving builder")
 var parts:Dictionary=adapter.source_parts(house,plan)
 var original:={};var faces:=PackedVector3Array()
 for key in parts:
  var mesh:MeshInstance3D=parts[key]
  original[key]={"mesh":mesh.mesh,"pose":mesh.global_transform,"children":mesh.get_child_count(),"material":mesh.get_active_material(0),"color":mesh.get_active_material(0).albedo_color,"roughness":mesh.get_active_material(0).roughness}
  if mesh.get_meta("extras",{}).get("runtime_collision",false):
   for point in mesh.mesh.get_faces():faces.append(mesh.global_transform*point)
 var body:=StaticBody3D.new()
 var shape:=ConcavePolygonShape3D.new();shape.set_faces(faces)
 if not connected:
  ship.add_child(body);var contact:=CollisionShape3D.new();contact.shape=shape;body.add_child(contact)
 else:body.free()
 test(adapter.receiving_error(ship,plan).is_empty(),"exact retained receiver accepted")
 var changed:Node3D=adapter.build(ship)
 test(changed!=null,"finish package installs")
 if changed==null:ship.free();quit(1);return
 test(adapter.build(ship)==changed,"repeat installation is idempotent")
 var shared:={};var retained_other:=0;var textured:=0;var original_groups:={}
 for key in parts:
  var mesh:MeshInstance3D=parts[key];var old:Dictionary=original[key]
  test(mesh.mesh==old.mesh and mesh.global_transform==old.pose and mesh.get_child_count()==old.children,"original geometry/contact identity "+key)
  var role:String=mesh.get_meta("extras",{}).get("role","")
  var material:StandardMaterial3D=mesh.get_active_material(0)
  if plan.materials.has(role):
   test(material!=old.material and material.albedo_texture==old.material.albedo_texture,"retained exact texture, named material successor "+key)
   test(old.material.albedo_color==old.color and old.material.roughness==old.roughness,"original material immutable "+key)
   test(material.transparency==old.material.transparency and material.cull_mode==old.material.cull_mode and material.uv1_scale==old.material.uv1_scale,"material coverage/UV/privacy "+key)
   var material_key:=str(role)+":"+str(old.material.get_instance_id())
   original_groups[material_key]=true
   if shared.has(material_key):test(shared[material_key]==material,"shared original material owner "+key)
   else:shared[material_key]=material
   textured+=1
  else:
   test(material==old.material,"glass/water/lens/soil unchanged "+key);retained_other+=1
 test(textured==267 and retained_other==67 and shared.size()==original_groups.size() and shared.size()>=5,"bounded material coverage")
 test(changed.find_children("*","MeshInstance3D",true,false).is_empty() and changed.find_children("*","CollisionShape3D",true,false).is_empty(),"no duplicate architecture or contacts")
 test(shape.get_faces()==faces,"contact triangle bytes preserved")
 var lights:=changed.find_children("*","Light3D",true,false)
 test(lights.size()==16,"sixteen exact physical emitters")
 for row in plan.lights:
  var light:OmniLight3D=changed.get_node(NodePath(row.name))
  test(light.position.distance_to(adapter.v(row.position))<.00001 and light.shadow_enabled and not light.visible,"emitter source pose and selector enrollment "+str(row.name))
 var actor:=Node3D.new();ship.add_child(actor)
 var budget:Node=load("res://scripts/lighting_budget.gd").new();ship.add_child(budget)
 actor.position=Vector3(-69,84,-379.2);await physics_frame;await physics_frame
 budget.configure(ship,actor)
 var per_floor:=[]
 for floor_y in [84.0,88.5,93.0,97.5,102.0]:
  actor.position=Vector3(-69,floor_y,-379.2);await physics_frame;budget.refresh()
  var active:int=budget.previously_active.size()
  var deck:int=13+roundi((floor_y-84.0)/4.5)
  var local:OmniLight3D=changed.get_node("D%d_CoveLight_0"%deck)
  test(active>0 and active<=8 and budget.shadow_source_budget==8,"existing light budget on D"+str(deck))
  test(local.visible and local.shadow_enabled,"local visible physical fixture on D"+str(deck))
  per_floor.append({"deck":deck,"active_sources":active,"local_fixture_selected":local.visible})
 for light in lights:light.set_meta("fixture_powered",false)
 budget.refresh();test(lights.all(func(x):return not x.visible and not x.shadow_enabled),"power-off suppression retained")
 for light in lights:light.set_meta("fixture_powered",true)
 house.set_meta("installed_guest_units",132);test(not adapter.receiving_error(ship,plan).is_empty(),"allocation mismatch rejected");house.set_meta("installed_guest_units",131)
 var lens:MeshInstance3D=parts[plan.lights[0].mesh];lens.position.x+=.1
 test(not adapter.receiving_error(ship,plan).is_empty(),"shifted source emitter rejected");lens.position.x-=.1
 var report:={"status":"PASS" if failures.is_empty() else "FAIL","checks":checks,"failures":failures,"geometry_parts_unchanged":334,"opaque_material_assignments":267,"unchanged_glass_water_lens_soil":67,"shared_materials":shared.size(),"material_families":5,"added_light_nodes":16,"new_geometry_contacts_rooms_rests":0,"per_floor":per_floor,"full_ship_test":false,"visual_accepted":false,"fixture":"Actual retained receiving builder/frontage successors/81 furnishings/transfer plus priorD14 addition; private131-home and later service/neighbor systems omitted" if connected else "Complete raw retained court geometry/contact coverage; furnishings/private rooms and unrelated neighbors omitted"}
 var f:=FileAccess.open(P+"evidence/"+("CONNECTED" if connected else "CHECK")+".json",FileAccess.WRITE);f.store_string(JSON.stringify(report,"  ")+"\n");f.close()
 print("TIDAL_COURT_FINISH_CHECK ",JSON.stringify(report));ship.free();quit(0 if failures.is_empty() else 1)
