extends SceneTree
func _initialize()->void:
 var semantic_scripts:Array=["tests/botanical_pair_successor_guard.gd","tests/d12_pair_successor_guard.gd","tests/medical_triage_successor_guard.gd","tests/botanical_pair_court_guard.gd","tests/validate_botanical_pair_geometry.gd","tests/botanical_pair_live_contact_guard.gd","tests/validate_botanical_nursery_access.gd","tests/validate_botanical_cloud_access.gd","tests/validate_botanical_pair_cart.gd","tests/validate_botanical_receiving_access.gd","scripts/botanical_pair_receiving.gd"]
 for path in semantic_scripts:
  var script:Script=load("res://"+str(path)) as Script
  assert(script!=null and script.can_instantiate(),"Semantic GDScript load failed: "+str(path))
 var outer=load("res://tests/botanical_pair_successor_guard.gd")
 outer.ensure()
 assert(outer.checked)
 var current:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
 var projected:Dictionary=outer.project_compiled(current)
 assert(current.regions.size()==303 and projected.regions.size()==300)
 var d12=load("res://tests/d12_pair_successor_guard.gd")
 d12.ensure()
 assert(d12.checked)
 var twice:Dictionary=d12.project_compiled(current)
 assert(twice.regions.size()==296)
 var old_path:String="res://data/architecture/packages/d12_pair_runtime/predecessors/data/generated/structural_meshes.json"
 # D12's own proof determines its retained path; don't assume the filesystem layout.
 var proof:Dictionary=JSON.parse_string(outer.current_text(d12.PROOF))
 old_path="res://"+str(proof.predecessors["data/generated/structural_meshes.json"].retained_path)
 assert(twice==JSON.parse_string(FileAccess.get_file_as_string(old_path)))
 var text:String=outer.current_text("res://scripts/ship.gd")
 assert(text.sha256_text()==outer.current_sha256("res://scripts/ship.gd"))
 var medical=load("res://tests/medical_triage_successor_guard.gd")
 medical._ensure()
 assert(medical.checked)
 var court=load("res://tests/botanical_pair_court_guard.gd")
 court.ensure()
 assert(court.checked and court.expected.objects.size()==120 and court.import_to_source.size()==120)
 var receipt={"status":"PASS_SOURCE_PROJECTION_ONLY","stages":[303,300,296],"actual_guard_code_executed":true,"semantic_script_load_count":semantic_scripts.size(),"actual_floor_children_executed":false,"court_source_delta_136_to_120_verified":true,"court_import_identity_verified":false,"medical_historical_source_chain_executed":true,"fullworld_or_assets_instantiated":false,"activation_ready":false,"runtime_acceptance":false}
 print("BOTANICAL_PROJECTION002 PASS: "+JSON.stringify(receipt))
 quit(0)
