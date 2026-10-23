extends SceneTree
var failures:=0
var options:Dictionary={}
func _initialize()->void:call_deferred("run")
func check(ok:bool,message:String="focused chain invariant")->bool:
 if not ok:failures+=1;push_error("RELEASE_FIXTURE_FAILED: "+message)
 return ok
func run()->void:
 for item in OS.get_cmdline_user_args():
  var pair:String=item.trim_prefix("--");var split:int=pair.find("=")
  if split>=0:options[pair.left(split)]=pair.substr(split+1)
 if not check(not OS.is_debug_build() or options.get("allow-editor","")=="1","Actual release binary required"):quit(3);return
 if not check(ProjectSettings.load_resource_pack(str(options.get("baseline",""))),"Baseline pack mount"):quit(3);return
 if FileAccess.file_exists("res://runtime_source_contracts.pck"):
  if not check(ProjectSettings.load_resource_pack("res://runtime_source_contracts.pck"),"Embedded exact-source contract pack"):quit(3);return
 if not check(ProjectSettings.load_resource_pack(str(options.get("overlay",""))),"Repair overlay mount"):quit(3);return
 print("RELEASE_FIXTURE_BUILD debug=",OS.is_debug_build()," mode=",options.get("mode","operations"))
 var mode:String=options.get("mode","operations")
 var guard:Script=load("res://scripts/release_operations_20261023/guard.gd")
 if mode=="negative-glb":guard.load_gltf("res://deliberately_missing_release_probe.glb");return
 if mode=="negative-config":guard.load_config("res://deliberately_missing_release_probe.import",ConfigFile.new());return
 if mode=="chain":chain();return
 if mode in ["d17","d17-raw"]:d17(mode=="d17-raw");return
 if not check(guard.sha256_bytes("abc".to_utf8_buffer())=="ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad","Unconditional SHA256 operation"):quit(1);return
 var value:Variant={"probe":"release operations","value":17}
 var expected:String=guard.sha256_bytes(var_to_bytes(value))
 check(load("res://scripts/star_atlas_fitted_receiving.gd").digest(value)==expected,"Actual StarAtlas digest")
 for name:String in ["MOVEMENT_STUDIO","SPORTS_CARE"]:
  var prefix:String="movement_studio"if name=="MOVEMENT_STUDIO"else "sports_care"
  var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D07_"+name+"_RECEIVING.json"))
  if not check(not d.is_empty(),"Import-policy contract "+name):quit(1);return
  var script:Script=load("res://scripts/"+prefix+"_receiving.gd")
  check(script.model_ready(str(d.model_file),str(d.model_sha256)),"Model precision "+name)
  check(script.model_ready(str(d.guard_file),str(d.guard_sha256)),"Guard precision "+name)
 var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/night_garden_specialty_d15_20261020/PACKAGE_R003.json"))
 var holder:=Node3D.new();root.add_child(holder)
 var receiving:Node3D=load("res://scripts/night_garden_residency_20261022/source_visual.gd").contact_visual(holder,str(data.receiving.model_file))
 if not check(receiving!=null,"NightGarden actual raw receiving"):quit(1);return
 check(receiving.name=="NightGardenD15ConnectedReceiving_r003","NightGarden receiving identity")
 print("NIGHT_GARDEN_RAW meshes=",receiving.find_children("*","MeshInstance3D",true,false).size()," contacts=",receiving.find_children("*","CollisionShape3D",true,false).size());holder.free()
 var standard:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D17_STARBOARD_STANDARD_CANDIDATE_20261019.json"))
 var raw:Node3D=load("res://royalty790_integration_20261022/package.gd").raw("res://assets/models/"+str(standard.structure_file))
 if not check(raw!=null,"Royalty actual raw standard"):quit(1);return
 for row in standard.walls:check(raw.find_child(str(row.replacement_name).replace(".","_"),true,false)!=null,"D17 raw replacement "+str(row.name))
 raw.free()
 print("RELEASE_OPERATIONS_RESULT failures=",failures," debug=",OS.is_debug_build());quit(1 if failures else 0)
func chain()->void:
 var host:Node3D=load("res://quiet_grove_specialty_20261022/fixture_host.gd").new();root.add_child(host)
 var space:=Node3D.new();space.name="ShipSpace";host.add_child(space);var districts:=Node3D.new();districts.name="Districts";space.add_child(districts)
 var systems:=Node.new();systems.name="ShipSystems";host.add_child(systems);var budget:Node=load("res://scripts/lighting_budget.gd").new();budget.name="LocalShadowSourceBudget";systems.add_child(budget);budget.set_process(false)
 var house:Node3D=load("res://scripts/quiet_grove_receiving.gd").build(host)
 var manager:Node=load("res://scripts/night_garden_residency_20261022/manager.gd").new();host.add_child(manager);manager.setup(host);manager.set_physics_process(false);host.private_detail_residency=manager
 var specialty:Node3D=load("res://quiet_grove_specialty_20261022/adapter_r002.gd").build(host);check(specialty!=null)
 var bank:Node3D=load("res://quiet_grove_bank_20261022/adapter_r002.gd").build(host);check(bank!=null)
 var clinical:=Node3D.new();clinical.name="Group3ForeStarboardClinical";space.add_child(clinical)
 var visual:Node3D=load("res://assets/models/group3_fore_starboard_clinical_20261011/AST-STF-G3-037.glb").instantiate();clinical.add_child(visual)
 for m:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):load("res://scripts/static_contact_cache.gd").attach(m)
 var d15:Node3D=load("res://scripts/quiet_d15_receiving_20261016/package.gd").build(host);check(d15!=null)
 var d14:Node3D=load("res://scripts/quiet_d14_receiving_20261016/package.gd").build(host);check(d14!=null and d14.has_meta("physical_receiving_only"))
 var family:Node3D=load("res://scripts/family_terrace_adoption.gd").build(host);check(family!=null)
 var meal:Node3D=load("res://scripts/group2_family_meal/package.gd").build_on_current_receiver(host);check(meal!=null,"Actual FamilyMeal receiving")
 var chain_steps:Array=[]
 for label:String in ["quiet_d13","quiet_d16","family_d13","family_d14","family_d15","family_d16"]:
  var group:Node3D=load("res://scripts/"+label+"_receiving_20261016/package.gd").build(host)
  check(group!=null and group.get_meta("physical_receiving_only",false))
  chain_steps.append(label);print("CHAIN_STEP_PASS ",label)
 var family_bank:Node3D=load("res://family_specialty_bank_20261022/adapter_r002.gd").build(host);check(family_bank!=null)
 check(family_bank.get_meta("reserved_rests")==59)
 check(districts.get_node("FamilyTerraceRoomCandidates").get_child_count()==82)
 var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://scripts/delivery_quiet_d14_20261023/COMPOSITION.json"));var results:Array=[]
 for row:Dictionary in data.rows:
  var m:MeshInstance3D=specialty.get_node("QuietGrove17Receiving_r001/"+str(row.name));check(m.mesh.get_faces().size()==int(row.result_triangles)*3)
  var contacts:Array=m.find_children("*","CollisionShape3D",true,false);check(contacts.size()==1)
  check(contacts[0].shape.get_faces()==m.mesh.get_faces())
  results.append({"name":row.name,"triangles":m.mesh.get_faces().size()/3,"owner":str(m.get_path()),"bounds":str(m.get_aabb()),"contact_matches_mesh":true})
 check(manager.entries.size()==94 and specialty.get_meta("reserved_rests")==19 and bank.get_meta("view_bank_reserved_rests")==59)
 var result:={"status":"PASS","actual_adapters":["QuietGrove17 adapter_r002","QuietGrove30 adapter_r002","QuietD15 original package","QuietD14 patched package"],"clinical_context":"Exact AST-STF-G3-037 imported owner with original static contacts; unrelated clinical models omitted","rows":results,"quiet_rooms":47,"family_specialty_rooms":47,"family_ordinary_rooms":82,"downstream_chain":chain_steps,"family_successor_guard":true,"reserved_rests":59,"full_ship":false,"guard_tolerance":.0002}
 print("RELEASE_CHAIN_RESULT failures=",failures," debug=",OS.is_debug_build()," result=",JSON.stringify(result));host.free();quit(1 if failures else 0)

func d17(raw_branch:bool)->void:
 var host:Node3D=load("res://royalty790_integration_20261022/fixture_host.gd").new();root.add_child(host)
 var space:=Node3D.new();space.name="ShipSpace";host.add_child(space)
 var districts:=Node3D.new();districts.name="Districts";space.add_child(districts)
 var systems:=Node.new();systems.name="ShipSystems";host.add_child(systems)
 var budget:Node=load("res://scripts/lighting_budget.gd").new();budget.name="LocalShadowSourceBudget";systems.add_child(budget);budget.set_process(false)
 var floors:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
 var regions:Array=floors.regions.filter(func(r):return r.id in ["D17_connected_house_floor_00","D17_starboard_house_extension"])
 load("res://scripts/structural_floor_builder.gd").build_regions(space,StandardMaterial3D.new(),StandardMaterial3D.new(),regions)
 host.model(districts,"AST-COM-003.glb","ExistingUpperCommons",Vector3(63,84,0))
 load("res://scripts/d17_connected_house.gd").build(districts,host)
 # Exact installed fore receiving frame; unrelated care rooms/fixtures omitted.
 var fore:=Node3D.new();fore.name="Group2CentralSupportedAdjunct";space.add_child(fore)
 var frame:Node3D=load("res://assets/group2_central_receiving_20261013/CENTRAL_ADJUNCT_RECEIVING_FRAME_r004.glb").instantiate();frame.name="ReceivingFrame";fore.add_child(frame)
 load("res://scripts/static_contact_cache.gd").attach_group(frame,frame.find_children("*","MeshInstance3D",true,false))
 var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D17_STARBOARD_STANDARD_CANDIDATE_20261019.json"))
 var path:String="res://assets/models/"+str(data.structure_file)if raw_branch else ""
 var receiving:Node3D=load("res://scripts/d17_starboard_standard_20261019/package.gd").build(host,path)
 if not check(receiving!=null,"Actual D17 receiving build"):host.free();quit(1);return
 check(receiving.get_meta("retained_standard_reservations")==18,"D17 unchanged reservations")
 var upper:Node3D=load("res://royalty790_integration_20261022/package.gd").build(host)
 check(upper!=null,"Actual Royalty successor after D17")
 print("RELEASE_D17_CHAIN_RESULT failures=",failures," debug=",OS.is_debug_build()," raw_branch=",raw_branch)
 host.free();quit(1 if failures else 0)
