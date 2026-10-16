extends "res://tests/validate_d04_port_forward_commons_service.gd"
func _initialize()->void:call_deferred("run")
func raw(file:String)->Node3D:
 var doc:=GLTFDocument.new();var state:=GLTFState.new();assert(doc.append_from_file(file,state,64)==OK);return doc.generate_scene(state)
func frames(n:int)->void:
 for i in range(n):await physics_frame
func run()->void:
 var revision:=OS.get_cmdline_user_args()[0];var base:="/workspace/Astraea/BlenderCatalogue/assets/quiet_d14_staff_receiving_20261016/";var d:=base+("r002/"if revision=="r002"else "");var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(d+"RECEIPT.json"));var world:=Node3D.new();root.add_child(world)
 var floors:=raw("res://assets/models/group3_fore_starboard_clinical_20261011/AST-STF-G3-041.glb");world.add_child(floors)
 for name in ["floor_staff_floor_D14","floor_staff_floor_D15"]:load("res://scripts/static_contact_cache.gd").attach(floors.find_child(name,true,false))
 var model:=raw(d+str(p.file));world.add_child(model);var contacts:Array[Node]=[]
 for row in p.parts:
  if row.collide:contacts.append(model.find_child(str(row.name).replace(".","_"),true,false))
 load("res://scripts/static_contact_cache.gd").attach_group(model,contacts)
 for row in p.walls:
  if row.owner=="lobby":load("res://scripts/static_contact_cache.gd").attach(model.find_child(str(row.replacement_name).replace(".","_"),true,false))
 var prior:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/quiet_d15_receiving_20261016/RECEIPT.json"));var upper:Node3D=load("res://assets/quiet_d15_receiving_20261016/"+str(prior.file)).instantiate();world.add_child(upper);contacts=[]
 for row in prior.parts:
  if row.collide:contacts.append(upper.find_child(str(row.name).replace(".","_"),true,false))
 load("res://scripts/static_contact_cache.gd").attach_group(upper,contacts)
 var actor:CharacterBody3D=load("res://scripts/player.gd").new();actor.position=Vector3(21,88.53,-485.5);world.add_child(actor);var legs:Array=[]
 for y in [88.5,93.0]:
  actor.set_physics_process(false);actor.position=Vector3(21,y+.03,-485.5);actor.velocity=Vector3.ZERO;actor.set_physics_process(true);await frames(20)
  for z in [-483.5,-485.5]:legs.append(await walk_to(actor,Vector3(21,y,z)))
 var result={"revision":revision,"legs":legs,"raw_import_flags":64,"scope":"Isolated exact lobby floors, receiver contacts and original player controller; no main-scene acceptance"};FileAccess.open("/workspace/quiet-d14-integration/THRESHOLD_"+revision+".json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(result);quit()
