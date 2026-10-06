extends RefCounted
# Narrow pool ship-call successor. Historical engineering/theater proofs are immutable.
const PROOF := "res://docs/SECONDARY_ENGINEERING_POOL_SHIP_SUCCESSOR.json"
const PROOF_SHA := "339cd0aa4f538681f45891049d5dfa847406655258ea9cba764dc2e79f30e998"
const TARGET := "scripts/ship.gd"
const PREVIOUS_GUARD_SHA := "3da92210dfe600c1f7cce2c85e36b089c39c93794ee50b7d5bdea43bab69ee9d"
const PREVIOUS_SHIP_SHA := "cd321b10dd1081fb9859b470f2499b6c09cf078b0b32d58cb4504819e669aef1"
const CANDIDATE_SHIP_SHA := "4f82ece4f0f990dad5559798044e55b26281eba3d5f0cdfb49cbdda63776982f"
const BUILDER := "scripts/grand_pool_architecture.gd"
const BUILDER_SHA := "a764584c22010fc5aaf6ef36cf257fb70be73b659e2d6ff189ec84ca8e4be2b4"
const CONTRACT := "data/architecture/GRAND_POOL_ARCHITECTURE_RUNTIME.json"
const CONTRACT_SHA := "2d5d4427464726aec388c5995c39b9af6461179e7973da5764019c7b50a5a1ea"
const IMMUTABLE_PROOF_SHA256 := {"docs/SECONDARY_ENGINEERING_ADDITIVE_PRESERVATION.json": "ee806149c47846c5d2a2374269615f2c13c681b949cea8f2ceb05ad81856e6cc", "data/architecture/SECONDARY_ENGINEERING_RUNTIME.json": "bef8d64a2238d96a11907083c1ad68aa3db484f71e504299d0c0613ccd9606da", "docs/SECONDARY_ENGINEERING_CELL_PRESERVATION.json": "e4315c57b22eb3c2a7629d7c32444632e488e5cbc9a108cd8dc318e97a2e8051", "docs/THEATER_ADDITIVE_SUCCESSOR_PROPOSAL.json": "1fa5809a6dfa77f77986a53a3e56f4fbfafdb7f5ab2d9ba1c40080bd6fe0d183", "docs/SECONDARY_ENGINEERING_THEATER_SUCCESSOR.json": "bf3dfe3e9b7eb4fe1f916269a6e7fde3a636f226a4f6cd02a66c13e3e0dac6af"}
const UNCHANGED_GEOMETRY_SHA256 := {"data/spatial_layout.json": "6ed1a74b5d387fd4e2d339fd3af62763a44898904cbfe883f4a418bac9854167", "data/generated/structural_meshes.json": "4ed4ba34028ba3683bb8e66b999766e1a6793654348f4213c61850b418685d91"}
const EXACT_ADDED_LINE := "\tload(\"res://scripts/grand_pool_architecture.gd\").build($ShipSpace/Districts,self)\n"
const BEFORE_ANCHOR := "\tload(\"res://scripts/grand_pool_finish.gd\").build($ShipSpace/Districts,self)\n"
const AFTER_ANCHOR := "\tload(\"res://scripts/secondary_engineering_section.gd\").build($ShipSpace/Districts,self)\n"
const PROOF_KEYS := ["schema", "scope", "target", "previous_guard_sha256", "immutable_proof_sha256", "historical_caller_sha256", "section_predecessor_sha256", "theater_predecessor_sha256", "candidate_sha256", "builder_path", "builder_sha256", "contract_path", "contract_sha256", "unchanged_geometry_sha256", "exact_added_line", "before_anchor", "after_anchor"]

static func _exact_keys(value: Dictionary, expected: Array) -> bool:
	var keys := value.keys()
	var wanted := expected.duplicate()
	keys.sort()
	wanted.sort()
	return keys == wanted

static func _validate_retained_pool_predecessor(path: String, historical: String, actual: String, section: Dictionary, theater: Dictionary, source: String) -> bool:
	if path != TARGET: return false
	assert(FileAccess.get_sha256(PROOF)==PROOF_SHA,"Pool ship successor proof bytes changed")
	var proof: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(PROOF))
	assert(_exact_keys(proof,PROOF_KEYS) and proof.schema==1 and proof.target==TARGET)
	assert(proof.previous_guard_sha256==PREVIOUS_GUARD_SHA,"Wrong engineering/theater guard predecessor")
	assert(proof.immutable_proof_sha256==IMMUTABLE_PROOF_SHA256)
	for retained_path in IMMUTABLE_PROOF_SHA256:
		assert(FileAccess.get_sha256("res://"+retained_path)==IMMUTABLE_PROOF_SHA256[retained_path],"Historical proof/contract bytes changed: "+retained_path)
	var retained_section: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://docs/SECONDARY_ENGINEERING_CELL_PRESERVATION.json"))
	var retained_theater: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://docs/SECONDARY_ENGINEERING_THEATER_SUCCESSOR.json"))
	assert(section==retained_section.explicit_runtime_pin_successors[TARGET],"Full section input record changed")
	assert(theater==retained_theater.explicit_runtime_pin_successors[TARGET],"Full theater input record changed")
	assert(historical==str(section.historical_sha256) and historical==str(theater.historical_sha256) and historical==str(proof.historical_caller_sha256),"Unexpected historical ship pin")
	assert(section.section_sha256==theater.section_sha256 and section.section_sha256==proof.section_predecessor_sha256,"Unexpected engineering section predecessor")
	assert(theater.theater_sha256==PREVIOUS_SHIP_SHA and proof.theater_predecessor_sha256==PREVIOUS_SHIP_SHA,"Unexpected theater ship predecessor")
	assert(proof.candidate_sha256==CANDIDATE_SHIP_SHA and actual==CANDIDATE_SHIP_SHA and source.sha256_text()==actual,"Unknown pool ship candidate")
	assert(proof.builder_path==BUILDER and proof.builder_sha256==BUILDER_SHA)
	assert(proof.contract_path==CONTRACT and proof.contract_sha256==CONTRACT_SHA)
	assert(load("res://tests/grand_pool_feature_builder_successor.gd").retained_sha256(BUILDER)==BUILDER_SHA,"Pool builder bytes changed")
	assert(FileAccess.get_sha256("res://"+CONTRACT)==CONTRACT_SHA,"Pool contract bytes changed")
	assert(proof.unchanged_geometry_sha256==UNCHANGED_GEOMETRY_SHA256)
	for geometry_path in UNCHANGED_GEOMETRY_SHA256:
		assert(FileAccess.get_sha256("res://"+geometry_path)==UNCHANGED_GEOMETRY_SHA256[geometry_path],"Pool ship successor cannot change geometry: "+geometry_path)
	assert(proof.exact_added_line==EXACT_ADDED_LINE and proof.before_anchor==BEFORE_ANCHOR and proof.after_anchor==AFTER_ANCHOR)
	assert(source.count(EXACT_ADDED_LINE)==1,"Exactly one pool architecture builder call required")
	assert(source.count(BEFORE_ANCHOR+EXACT_ADDED_LINE+AFTER_ANCHOR)==1,"Pool call moved outside its reviewed anchors")
	assert(source.replace(EXACT_ADDED_LINE,"").sha256_text()==PREVIOUS_SHIP_SHA,"Removing the single pool call must recover every theater predecessor byte")
	return true

# New exact successor. Prior proof/geometry checks above remain unchanged except
# reading the mathematically reconstructed previous ship instead of current bytes.
const STAIR_PROOF := "res://docs/THEATER_STAIR_SHIP_SUCCESSOR_011.json"
const STAIR_PROOF_SHA := "63a0626beea724e41076e4a42a2211a21806106c38e1f5dae6017182c627e34a"
const STAIR_CANDIDATE_SHA := "9f3d443c6af4865f2cf9225e0ce84ac2be8b8d8817bf15b32dbdf2bf34eafe0a"

# Court A is one exact additive ship call. Reconstruct only the three affected
# historical inputs below; old proof documents and unrelated test bytes stay pinned.
const COURT_CANDIDATE_SHA := "94d830ada737567f6b157bc7b7057d10ebc34ef317f92c240e717e00b8a9be6c"
const COURT_LINE := "\tload(\"res://scripts/court_a_increment004.gd\").build($ShipSpace/Districts,self)\n"
const COURT_BEFORE := "\tload(\"res://scripts/grand_lantern_theater_section.gd\").build($ShipSpace/Districts,self)\n"
const COURT_AFTER := "\tload(\"res://scripts/theater_stair_walking_contacts.gd\").build($ShipSpace/Districts)\n"
const COURT_INPUT_SHA256 := {"scripts/court_a_increment004.gd":"f2b41454c2b7870083e9f05ff46073db15fac0543ac3efb0cfed3d8b0d6885c2","data/architecture/COURT_A_RUNTIME_INCREMENT004.json":"f5579375ce629286bbc4c19e4ad6807549cda06830a8d42706a2b38987457561","assets/models/AST-CUL-005_court_A_authored_004.glb":"71c375c788040cda09d31d12a756ea0650fd7285571cacf750092e1fac0af246","assets/models/AST-CUL-005_court_A_prototypes_004.glb":"ebd73c99e04449e6cc4fa48ad562a7b15ab172d5c579d1edacf503333904446b","assets/models/AST-CUL-005_court_A_authored_004.glb.import":"4fc0a049482a5b1c090a8d18f775a75e9d6f3897b2e060ecc9be58879654c087","assets/models/AST-CUL-005_court_A_prototypes_004.glb.import":"03c07c4d102a7ce97386da8d6ef314e3c5f2954995ea8775c25e26f987cfa576"}
const STAIR_GUARD_CONDITION := "actual==preload(\"res://tests/theater_stair_ship_successor.gd\").STAIR_CANDIDATE_SHA"
const COURT_GUARD_CONDITION := "actual in [preload(\"res://tests/theater_stair_ship_successor.gd\").STAIR_CANDIDATE_SHA,preload(\"res://tests/theater_stair_ship_successor.gd\").COURT_CANDIDATE_SHA]"
const STAIR_PIN_LOOP := "\tfor path in contract.input_sha256:assert(FileAccess.get_sha256(\"res://\"+str(path))==str(contract.input_sha256[path]))\n"
const COURT_PIN_LOOP := "\tfor path in contract.input_sha256:assert(load(\"res://tests/theater_stair_ship_successor.gd\").retained_input_sha256(str(path))==str(contract.input_sha256[path]))\n"

static func retained_ship_source() -> String:
	var source := FileAccess.get_file_as_string("res://"+TARGET)
	if source.sha256_text()==STAIR_CANDIDATE_SHA: return source
	assert(source.sha256_text()==COURT_CANDIDATE_SHA,"Unreviewed Court ship bytes")
	assert(source.count(COURT_LINE)==1 and source.count(COURT_BEFORE+COURT_LINE+COURT_AFTER)==1,"Court must remain between the existing theater and stair builders")
	for path in COURT_INPUT_SHA256:
		assert(retained_input_sha256(str(path))==str(COURT_INPUT_SHA256[path]),"Court input changed: "+str(path))
	source=source.replace(COURT_LINE,"")
	assert(source.sha256_text()==STAIR_CANDIDATE_SHA,"Removing only Court must recover every prior ship byte")
	return source

static func retained_guard_source() -> String:
	var source := FileAccess.get_file_as_string("res://tests/secondary_engineering_additive_guard.gd")
	if source.sha256_text()=="54b2656bae899aca81027fa296b7a61bf0c97c46bdfd869ca06d299db1c1b16f": return source
	assert(source.count(COURT_GUARD_CONDITION)==2)
	source=source.replace(COURT_GUARD_CONDITION,STAIR_GUARD_CONDITION)
	assert(source.sha256_text()=="54b2656bae899aca81027fa296b7a61bf0c97c46bdfd869ca06d299db1c1b16f","Only the two exact ship dispatch conditions may change")
	return source

static func retained_input_sha256(path: String) -> String:
	if path=="scripts/court_a_increment004.gd": return retained_court_source().sha256_text()
	if path=="tests/theater_stage_probe.gd": return retained_stage_probe_source().sha256_text()
	if path=="tests/secondary_engineering_pool_ship_successor.gd": return load("res://tests/grand_pool_feature_builder_successor.gd").retained_sha256(path)
	if path==TARGET: return retained_ship_source().sha256_text()
	if path=="tests/secondary_engineering_additive_guard.gd": return retained_guard_source().sha256_text()
	if path=="tests/validate_theater_stair_walk.gd":
		var source := FileAccess.get_file_as_string("res://"+path)
		if source.sha256_text()=="4a0161bc18e58c68493b7d00b09fff874023cb72797d63ca030a3cbb549da090": return source.sha256_text()
		assert(source.count(COURT_PIN_LOOP)==1)
		source=source.replace(COURT_PIN_LOOP,STAIR_PIN_LOOP)
		assert(source.sha256_text()=="4a0161bc18e58c68493b7d00b09fff874023cb72797d63ca030a3cbb549da090","All stair walk physical assertions must remain unchanged")
		return source.sha256_text()
	return FileAccess.get_sha256("res://"+path)

static func validate_successor(path: String, historical: String, actual: String, section: Dictionary, theater: Dictionary) -> bool:
	if path!=TARGET or actual not in [STAIR_CANDIDATE_SHA,COURT_CANDIDATE_SHA]: return false
	assert(FileAccess.get_sha256(STAIR_PROOF)==STAIR_PROOF_SHA,"Stair successor proof bytes changed")
	var proof: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(STAIR_PROOF))
	assert(proof.adoption_approved,"Unfrozen stair successor; engineering test/final preimages not settled")
	assert(proof.schema==1 and proof.target==TARGET and proof.candidate_ship_sha256==STAIR_CANDIDATE_SHA)
	assert(proof.previous_ship_sha256==CANDIDATE_SHIP_SHA and proof.historical_caller_sha256==historical)
	assert(FileAccess.get_sha256("res://"+path)==actual)
	for pinned in proof.immutable_sha256:
		if str(pinned)=="tests/theater_stage_probe.gd":
			assert(retained_input_sha256(str(pinned))==str(proof.immutable_sha256[pinned]),"Exact theater probe predecessor required")
			continue
		if str(pinned) in [BUILDER,"tests/secondary_engineering_pool_ship_successor.gd"]:
			assert(load("res://tests/grand_pool_feature_builder_successor.gd").retained_sha256(str(pinned))==str(proof.immutable_sha256[pinned]),"Exact pool builder/helper predecessor changed")
			continue
		# Exact reviewed natural-carry test successor; original proof and all runtime pins remain intact.
		if str(pinned)=="tests/validate_secondary_engineering_cell.gd" and str(proof.immutable_sha256[pinned])=="3b489007db83a98a13728b4ab23fe12e9e0cfa575927476800c77c0f0735b280" and FileAccess.get_sha256("res://"+str(pinned))=="5dad5e1db7e3283ca5c8d207e84a20b62564e24d1523676c5819a150ba774e13":
			continue
		assert(FileAccess.get_sha256("res://"+str(pinned))==str(proof.immutable_sha256[pinned]),"Preserved stair predecessor input changed: "+str(pinned))
	for pinned in proof.new_sha256:
		assert(retained_input_sha256(str(pinned))==str(proof.new_sha256[pinned]),"Unreviewed stair adoption input: "+str(pinned))
	var source:=retained_ship_source()
	var line:=str(proof.exact_added_line)
	assert(source.count(line)==1 and source.count(str(proof.before_anchor)+line+str(proof.after_anchor))==1)
	var previous:=source.replace(line,"")
	assert(previous.sha256_text()==CANDIDATE_SHIP_SHA,"Removing one stair call must recover every prior ship byte")
	assert(_validate_retained_pool_predecessor(path,historical,CANDIDATE_SHIP_SHA,section,theater,previous),"Complete retained pool/engineering/theater chain required")
	var controls_section: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://docs/SECONDARY_ENGINEERING_CELL_PRESERVATION.json"))
	var controls_pin: Dictionary=controls_section.explicit_runtime_pin_successors["scripts/presentation.gd"]
	assert(load("res://tests/engineering_controls_listener_successor.gd").validate_successor("scripts/presentation.gd",str(controls_pin.historical_sha256),FileAccess.get_sha256("res://scripts/presentation.gd"),controls_pin),"Complete retained signage-to-listener chain required")
	var guard:=retained_guard_source()
	assert(proof.exact_guard_insertions.size()==2)
	for insertion in proof.exact_guard_insertions:
		assert(guard.count(str(insertion))==1)
		guard=guard.replace(str(insertion),"")
	assert(guard.sha256_text()==str(proof.previous_guard_sha256),"Guard must be exact two-branch extension")
	var compiled: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
	var layout: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/spatial_layout.json"))
	assert(compiled.regions.size()==271 and layout.regions.size()==285)
	return true

# Exact optic-only inverses. Original stair/native documents remain immutable.
const OPTIC_CALL := "\tload(\"res://scripts/court_a_aimed_optic008.gd\").build(parent, _ship)\n"
const OPTIC_CALL_ANCHOR := "\tprototype.free()\n"
const OPTIC_PROBE_ADDED_CONSTANT := "const OPTIC = preload(\"res://tests/court_a_aimed_optic_probe.gd\")\n"
const OPTIC_PROBE_ADDED_CALL := "\tOPTIC.check_installation(ship)\n"
const OPTIC_PROBE_CONSTANT_PLACEMENT := "const OPTIC = preload(\"res://tests/court_a_aimed_optic_probe.gd\")\nvar data: Dictionary\n"
const OPTIC_PROBE_CALL_PLACEMENT := "\tassert(cart != null and cart.products.size() == 4)\n\tOPTIC.check_installation(ship)\n\nfunc xyz(a: Array) -> Vector3:\n"
const OPTIC_PROBE_OLD_BLOCK := "\t\t\t\tassert(actual != null and actual.mesh == item.mesh)\n\t\t\t\tassert_transform(relative(actual,built), relative(item,imported), str(item.name))\n\t\t\t\tcheck_exact_contact(actual)\n"
const OPTIC_PROBE_NEW_BLOCK := "\t\t\t\tassert(actual != null)\n\t\t\t\tassert_transform(relative(actual,built), relative(item,imported), str(item.name))\n\t\t\t\tif kind == \"static\" and str(item.name) == \"C005_S_0326\":\n\t\t\t\t\tOPTIC.check_replacement(actual,item)\n\t\t\t\telse:\n\t\t\t\t\tassert(actual.mesh == item.mesh)\n\t\t\t\t\tcheck_exact_contact(actual)\n"
const OPTIC_PROBE_OLD_AIM := "\t\t\tassert((-light.global_basis.z).distance_to(xyz(entry.aim_world).normalized()) < .00001)\n"
const OPTIC_PROBE_NEW_AIM := "\t\t\tassert((-light.global_basis.z).distance_to(OPTIC.expected_aim(light,entry)) < .00001)\n"

static func retained_court_source() -> String:
	var source := FileAccess.get_file_as_string("res://scripts/court_a_increment004.gd")
	var previous := str(COURT_INPUT_SHA256["scripts/court_a_increment004.gd"])
	if source.sha256_text()==previous: return source
	assert(source.count(OPTIC_CALL)==1 and source.ends_with(OPTIC_CALL_ANCHOR+OPTIC_CALL),"Exactly one appended optic builder call required")
	source=source.replace(OPTIC_CALL,"")
	assert(source.sha256_text()==previous,"Removing only the optic call must recover every prior Court builder byte")
	load("res://tests/court_a_aimed_optic_probe.gd").authenticated_contract()
	return source

static func retained_stage_probe_source() -> String:
	var source := FileAccess.get_file_as_string("res://tests/theater_stage_probe.gd")
	var previous := "0734d22c0cc70a34cd76c22f16919df312613badb4107b5581c256a007365501"
	if source.sha256_text()==previous: return source
	assert(source.count(OPTIC_PROBE_CONSTANT_PLACEMENT)==1 and source.count(OPTIC_PROBE_CALL_PLACEMENT)==1,"Optic checks must remain at their exact initialization anchors")
	for added in [OPTIC_PROBE_ADDED_CONSTANT,OPTIC_PROBE_ADDED_CALL]:
		assert(source.count(added)==1)
		source=source.replace(added,"")
	assert(source.count(OPTIC_PROBE_NEW_BLOCK)==1 and source.count(OPTIC_PROBE_NEW_AIM)==1)
	source=source.replace(OPTIC_PROBE_NEW_BLOCK,OPTIC_PROBE_OLD_BLOCK).replace(OPTIC_PROBE_NEW_AIM,OPTIC_PROBE_OLD_AIM)
	assert(source.sha256_text()==previous,"Only the named optic replacement/contact/aim assertions may change; every other theater assertion must remain exact")
	return source
