extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 assert(ProjectSettings.load_resource_pack("/tmp/astraea-laptop-contract-1bc13d51/Astraea-1bc13d51.pck"))
 var pack:=PCKPacker.new();assert(pack.pck_start("/tmp/quiet-chain-test.pck")==OK)
 var payload:="/workspace/Astraea-recovered-e6274e77-20261021/recovery/quiet_d14_chain_fix/payload/Game/"
 for path:String in ["data/family_d13_receiving_20261016/RECEIPT.json", "data/family_d14_receiving_20261016/RECEIPT.json", "data/family_d15_receiving_20261016/RECEIPT.json", "data/family_d16_receiving_20261016/RECEIPT.json", "data/quiet_d13_receiving_20261016/RECEIPT.json", "data/quiet_d16_receiving_20261016/RECEIPT.json", "family_specialty_bank_20261022/evidence/GUARD_PLAN.json", "scripts/delivery_quiet_d14_20261023/COMPOSITION.json", "scripts/delivery_quiet_d14_20261023/composition.gd", "scripts/quiet_d14_receiving_20261016/package.gd", "scripts/runtime_contracts_20261022/SOURCE_CONTRACTS.json"]:assert(pack.add_file("res://"+path,payload+path)==OK)
 assert(pack.flush()==OK);assert(ProjectSettings.load_resource_pack("/tmp/quiet-chain-test.pck"))
 var host:Node3D=load("res://quiet_grove_specialty_20261022/fixture_host.gd").new();root.add_child(host)
 var space:=Node3D.new();space.name="ShipSpace";host.add_child(space);var districts:=Node3D.new();districts.name="Districts";space.add_child(districts)
 var systems:=Node.new();systems.name="ShipSystems";host.add_child(systems);var budget:Node=load("res://scripts/lighting_budget.gd").new();budget.name="LocalShadowSourceBudget";systems.add_child(budget);budget.set_process(false)
 var house:Node3D=load("res://scripts/quiet_grove_receiving.gd").build(host)
 var manager:Node=load("res://scripts/night_garden_residency_20261022/manager.gd").new();host.add_child(manager);manager.setup(host);manager.set_physics_process(false);host.private_detail_residency=manager
 var specialty:Node3D=load("res://quiet_grove_specialty_20261022/adapter_r002.gd").build(host);assert(specialty!=null)
 var bank:Node3D=load("res://quiet_grove_bank_20261022/adapter_r002.gd").build(host);assert(bank!=null)
 var clinical:=Node3D.new();clinical.name="Group3ForeStarboardClinical";space.add_child(clinical)
 var visual:Node3D=load("res://assets/models/group3_fore_starboard_clinical_20261011/AST-STF-G3-037.glb").instantiate();clinical.add_child(visual)
 for m:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):load("res://scripts/static_contact_cache.gd").attach(m)
 var d15:Node3D=load("res://scripts/quiet_d15_receiving_20261016/package.gd").build(host);assert(d15!=null)
 var d14:Node3D=load("res://scripts/quiet_d14_receiving_20261016/package.gd").build(host);assert(d14!=null and d14.has_meta("physical_receiving_only"))
 var family:Node3D=load("res://scripts/family_terrace_adoption.gd").build(host);assert(family!=null)
 var chain:Array=[]
 for label:String in ["quiet_d13","quiet_d16","family_d13","family_d14","family_d15","family_d16"]:
  var group:Node3D=load("res://scripts/"+label+"_receiving_20261016/package.gd").build(host)
  assert(group!=null and group.get_meta("physical_receiving_only",false))
  chain.append(label);print("CHAIN_STEP_PASS ",label)
 var family_bank:Node3D=load("res://family_specialty_bank_20261022/adapter_r002.gd").build(host);assert(family_bank!=null)
 assert(family_bank.get_meta("reserved_rests")==59)
 assert(districts.get_node("FamilyTerraceRoomCandidates").get_child_count()==82)
 var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://scripts/delivery_quiet_d14_20261023/COMPOSITION.json"));var results:Array=[]
 for row:Dictionary in data.rows:
  var m:MeshInstance3D=specialty.get_node("QuietGrove17Receiving_r001/"+str(row.name));assert(m.mesh.get_faces().size()==int(row.result_triangles)*3)
  var contacts:Array=m.find_children("*","CollisionShape3D",true,false);assert(contacts.size()==1)
  assert(contacts[0].shape.get_faces()==m.mesh.get_faces())
  results.append({"name":row.name,"triangles":m.mesh.get_faces().size()/3,"owner":str(m.get_path()),"bounds":str(m.get_aabb()),"contact_matches_mesh":true})
 assert(manager.entries.size()==94 and specialty.get_meta("reserved_rests")==19 and bank.get_meta("view_bank_reserved_rests")==59)
 var result:={"status":"PASS","actual_adapters":["QuietGrove17 adapter_r002","QuietGrove30 adapter_r002","QuietD15 original package","QuietD14 patched package"],"clinical_context":"Exact AST-STF-G3-037 imported owner with original static contacts; unrelated clinical models omitted","rows":results,"quiet_rooms":47,"family_specialty_rooms":47,"family_ordinary_rooms":82,"downstream_chain":chain,"family_successor_guard":true,"reserved_rests":59,"full_ship":false,"guard_tolerance":.0002}
 var f:=FileAccess.open("/tmp/quiet_chain_validation.json",FileAccess.WRITE);f.store_string(JSON.stringify(result,"  "));f.close();print("QUIET_CHAIN_PASS ",JSON.stringify(result));host.free();quit()
