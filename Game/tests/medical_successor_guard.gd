extends RefCounted
# Authenticated medical projection for unchanged historical assertions.
# Every projected byte/owner is checked against the full current postimage first.
const PROOF := "res://docs/MEDICAL_ADDITIVE_SUCCESSOR.json"
const PROOF_SHA := "d9a2f984fbcf831879628546a087e8fd7a790e4e313744b273d0a9bfed6d2637"
const OWNER := "D05_forward_waiting_support_floor"
const CURRENT_ONLY := ["docs/LAYOUT_COMPILE_CHECKS.json"]
static var checked := false
static var proof: Dictionary = {}
static var old_text: Dictionary = {}
static var current_compiled: Dictionary = {}

static func _relative(path: String) -> String:
	return path.trim_prefix("res://")

# This bounded successor recognizes only the reviewed D11 helper and registry.
# All unrelated medical inputs retain their direct byte hashes and assertions.
const D11_ENTRY_MEDICAL_INPUTS := {
  "tests/theater_stair_ship_successor.gd": {
    "preimage_sha256": "51aef784cfbac473a715c35188c06c17f589c5ac29ce2281e165155095e1b170",
    "candidate_sha256": "18bb798eaa160bbe3c5e91466546c0663aeee79a86a29449daa81f8d2690aacd",
    "reversals": [
      {
        "before": "\nstatic func retained_court_source() -> String:\n",
        "after": "\n# Exact D11 entry inverses run before the retained optic inverses below.\nconst ENTRY_CALL := \"\\tload(\\\"res://scripts/theater_d11_entry.gd\\\").build(parent, _ship)\\n\"\nconst ENTRY_COURT_PREVIOUS_SHA := \"753f174f327693d5d96b5e1ea8110a58e65e237625c032f04c7f011ca17b81b3\"\nconst ENTRY_COURT_CANDIDATE_SHA := \"8cbeaf8f9525f7dc8acb4b0d9326c4b09a8b2e08173863610dfe17c5f57bea00\"\nconst ENTRY_PROBE_PREVIOUS_SHA := \"6b8fa8e2e9ce5c2d44c3828aa4c3a65157d59d690a81e6dee29eefdbf1158ee0\"\nconst ENTRY_PROBE_CANDIDATE_SHA := \"9002147b4a8719e901efde10db8b3d2d925d166696cb33ad16238b45b2f68436\"\nconst ENTRY_PROBE_CHANGES := [{\"previous\": \"const OPTIC = preload(\\\"res://tests/court_a_aimed_optic_probe.gd\\\")\\n\", \"current\": \"const OPTIC = preload(\\\"res://tests/court_a_aimed_optic_probe.gd\\\")\\nconst ENTRY = preload(\\\"res://tests/theater_d11_entry_probe.gd\\\")\\n\"}, {\"previous\": \"\\tOPTIC.check_installation(ship)\\n\", \"current\": \"\\tOPTIC.check_installation(ship)\\n\\tENTRY.check_installation(ship)\\n\"}, {\"previous\": \"func check_motion_poses_and_barriers() -> void:\\n\\tassert(data.held_open_groups == [\\\"THEATER_D11_MAIN_LEAF_LEFT\\\",\\\"THEATER_D11_MAIN_LEAF_RIGHT\\\"])\\n\", \"current\": \"func check_motion_poses_and_barriers() -> void:\\n\\tassert(data.held_open_groups == [\\\"THEATER_D11_MAIN_LEAF_LEFT\\\",\\\"THEATER_D11_MAIN_LEAF_RIGHT\\\"])\\n\\tENTRY.check_installation(ship)\\n\\tassert(data.motion_groups.size() == 39)\\n\\tvar fully_open := true\\n\\tvar active_groups := 0\\n\"}, {\"previous\": \"\\t\\tif held: expected.origin += xyz(spec.axis_world) * float(spec.travel_m)\\n\", \"current\": \"\\t\\tif held:\\n\\t\\t\\t# Only the two original D11 main groups are operational. The entry\\n\\t\\t\\t# probe verifies their six retained Mesh/Shape resources and carriers.\\n\\t\\t\\tvar fraction := float(node.get_meta(\\\"current_pose_fraction\\\"))\\n\\t\\t\\tassert(is_finite(fraction) and fraction >= 0.0 and fraction <= 1.0)\\n\\t\\t\\texpected.origin += xyz(spec.axis_world) * float(spec.travel_m) * fraction\\n\\t\\t\\tassert_transform(relative(node,motion),expected,str(identity))\\n\\t\\t\\tassert(node.get_meta(\\\"operation_enabled\\\") == true and not node.has_meta(\\\"locked_pose_fraction\\\"))\\n\\t\\t\\tassert(node.find_children(\\\"*\\\",\\\"Area3D\\\",true,false).is_empty())\\n\\t\\t\\tassert(identity not in data.visual_only_motion_groups)\\n\\t\\t\\tfully_open = fully_open and fraction == 1.0\\n\\t\\t\\tactive_groups += 1\\n\\t\\t\\tcontinue\\n\"}, {\"previous\": \"\\ttemplate.free()\\n\\tassert(motion.get_meta(\\\"cabin_static_floor_credit\\\") == false)\\n\\tclear_box(Vector3(-35.0,69.51,-128.59),Vector3(-33.95,72.50,-123.41),\\\"D11 5.2m held-open aperture and 3m route headroom\\\")\\n\", \"current\": \"\\ttemplate.free()\\n\\tassert(active_groups == 2)\\n\\tassert(motion.get_meta(\\\"cabin_static_floor_credit\\\") == false)\\n\\tif fully_open:\\n\\t\\tclear_box(Vector3(-35.0,69.51,-128.59),Vector3(-33.95,72.50,-123.41),\\\"D11 5.2m held-open aperture and 3m route headroom\\\")\\n\"}]\n\nstatic func retained_court_source() -> String:\n",
        "count": 1
      },
      {
        "before": "\tif source.sha256_text()==previous: return source\n\tassert(source.count(OPTIC_CALL)==1",
        "after": "\tif source.sha256_text()==previous: return source\n\tif source.sha256_text()==ENTRY_COURT_CANDIDATE_SHA:\n\t\tassert(source.count(ENTRY_CALL)==1 and source.ends_with(OPTIC_CALL+ENTRY_CALL),\"Exactly one D11 entry call must follow the retained optic call\")\n\t\tsource=source.replace(ENTRY_CALL,\"\")\n\t\tassert(source.sha256_text()==ENTRY_COURT_PREVIOUS_SHA,\"Removing only the D11 entry call must recover every optic-era Court byte\")\n\tassert(source.count(OPTIC_CALL)==1",
        "count": 1
      },
      {
        "before": "\tif source.sha256_text()==previous: return source\n\tassert(source.count(OPTIC_PROBE_CONSTANT_PLACEMENT)==1",
        "after": "\tif source.sha256_text()==previous: return source\n\tif source.sha256_text()==ENTRY_PROBE_CANDIDATE_SHA:\n\t\tfor replacement in ENTRY_PROBE_CHANGES:\n\t\t\tassert(source.count(str(replacement.current))==1,\"Exact D11 entry assertion successor required\")\n\t\t\tsource=source.replace(str(replacement.current),str(replacement.previous))\n\t\tassert(source.sha256_text()==ENTRY_PROBE_PREVIOUS_SHA,\"Only two D11 groups may change; recover every optic-era probe byte before its inverse\")\n\tassert(source.count(OPTIC_PROBE_CONSTANT_PLACEMENT)==1",
        "count": 1
      }
    ]
  },
  "tools/validate.py": {
    "preimage_sha256": "2e277e2ccfbb94dabad7a0cccf7e5a0dc8e8ab62421b9ee2f581ab1302ad7a2c",
    "candidate_sha256": "401d94ed323d617fb81937620121bd2cd77b00d5fb8ef0bca33db23c53fa17ef",
    "reversals": [
      {
        "before": "commands.sort(key=lambda entry: entry[0] != 'import')\n",
        "after": "commands += [('theater_main_entry', ['--script', 'res://tests/validate_theater_main_entry.gd'])]\ncommands.sort(key=lambda entry: entry[0] != 'import')\n",
        "count": 1
      },
      {
        "before": "    if label == 'theater_stair_walk': frame_budget='24000'\n",
        "after": "    if label == 'theater_stair_walk': frame_budget='24000'\n    if label == 'theater_main_entry': frame_budget='12000'\n",
        "count": 1
      },
      {
        "before": "else 240 if label in ['theater_structure','theater_access'] else",
        "after": "else 240 if label in ['theater_structure','theater_access','theater_main_entry'] else",
        "count": 1
      }
    ]
  }
}

static func _d11_entry_medical_text(path: String) -> String:
	var relative := _relative(path)
	var source := FileAccess.get_file_as_string("res://"+relative)
	if not D11_ENTRY_MEDICAL_INPUTS.has(relative): return source
	var spec: Dictionary=D11_ENTRY_MEDICAL_INPUTS[relative]
	if source.sha256_text()==str(spec.preimage_sha256): return source
	assert(source.sha256_text()==str(spec.candidate_sha256),"Unreviewed D11 medical successor: "+relative)
	var reversals: Array=spec.reversals
	for i in range(reversals.size()-1,-1,-1):
		var replacement: Dictionary=reversals[i]
		assert(source.count(str(replacement.after))==int(replacement.count),"Exact D11 inverse cardinality: "+relative)
		source=source.replace(str(replacement.after),str(replacement.before))
	assert(source.sha256_text()==str(spec.preimage_sha256),"Every medical-era byte must survive D11: "+relative)
	return source

static func _d11_entry_medical_sha256(path: String) -> String:
	var relative := _relative(path)
	if D11_ENTRY_MEDICAL_INPUTS.has(relative): return _d11_entry_medical_text(relative).sha256_text()
	return FileAccess.get_sha256("res://"+relative)

static func _ensure() -> void:
	if checked: return
	assert(FileAccess.get_sha256(PROOF)==PROOF_SHA,"Medical proof bytes changed")
	proof=JSON.parse_string(FileAccess.get_file_as_string(PROOF))
	assert(proof.schema==1 and proof.owner_id==OWNER)
	for path in proof.postimage_sha256:
		assert(_d11_entry_medical_sha256(str(path))==str(proof.postimage_sha256[path]),"Unreviewed medical postimage: "+str(path))
	for path in proof.predecessors:
		var spec: Dictionary=proof.predecessors[path]
		var retained_path := "res://"+str(spec.retained_path)
		assert(FileAccess.get_sha256(retained_path)==str(spec.sha256),"Medical predecessor changed: "+str(path))
		old_text[path]=FileAccess.get_file_as_string(retained_path)
	for path in proof.exact_patch_reversals:
		var restored := _d11_entry_medical_text(str(path))
		var reversals: Array=proof.exact_patch_reversals[path]
		for i in range(reversals.size()-1,-1,-1):
			var replacement: Dictionary=reversals[i]
			assert(restored.count(str(replacement.after))==int(replacement.count),"Patch inverse cardinality: "+str(path))
			restored=restored.replace(str(replacement.after),str(replacement.before))
		assert(restored.sha256_text()==str(proof.predecessors[path].sha256),"Every historical assertion/byte must survive: "+str(path))
	var old_layout: Dictionary=JSON.parse_string(old_text["data/spatial_layout.json"])
	var old_compiled: Dictionary=JSON.parse_string(old_text["data/generated/structural_meshes.json"])
	var layout: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/spatial_layout.json"))
	current_compiled=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
	assert(old_layout.regions.size()==285 and old_compiled.regions.size()==271 and old_layout.voids.size()==28)
	assert(layout.regions.size()==286 and current_compiled.regions.size()==272 and layout.voids.size()==28)
	var summary: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://docs/LAYOUT_COMPILE_CHECKS.json"))
	assert(summary==current_compiled.source_checks,"Compile receipt must equal the current actual compiled checks")
	for pair in [[layout,old_layout,proof.new_layout_record],[current_compiled,old_compiled,proof.new_compiled_record]]:
		var retained: Array=[]
		var ids: Dictionary={}
		var found := 0
		for row in pair[0].regions:
			assert(not ids.has(str(row.id)),"Duplicate medical/current owner")
			ids[str(row.id)]=true
			if str(row.id)==OWNER:
				assert(row==pair[2],"Exact authenticated medical record required")
				found+=1
			else: retained.append(row)
		assert(found==1 and retained==pair[1].regions,"All current predecessor records and order must remain exact")
	var globals: Dictionary=layout.duplicate(true)
	var prior_globals: Dictionary=old_layout.duplicate(true)
	globals.erase("regions");prior_globals.erase("regions")
	assert(globals==prior_globals,"All old layout globals and void records must remain exact")
	var record: Dictionary=proof.new_compiled_record
	assert(record.deck=="D05" and absf(float(record.floor_y)-21.0)<.000001 and absf(float(record.thickness)-.24)<.000001)
	assert(absf(float(record.structural_area_m2)-350.72)<.000001)
	var old_core: Dictionary=JSON.parse_string(old_text["data/architecture/FORWARD_PUBLIC_CORE.json"])
	var core: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/FORWARD_PUBLIC_CORE.json"))
	assert(core.enclosure_file==proof.core_derivative_file)
	assert(not old_core.has(str(proof.core_interface_key)) and core.has(str(proof.core_interface_key)))
	core.erase(str(proof.core_interface_key));core.enclosure_file=old_core.enclosure_file
	assert(core==old_core,"Only the core filename and explicit D05 interface may change")
	checked=true

static func retained_text(path: String) -> String:
	_ensure()
	if not checked: return ""
	var relative := _relative(path)
	if old_text.has(relative) and relative not in CURRENT_ONLY: return str(old_text[relative])
	return FileAccess.get_file_as_string(path if path.begins_with("res://") else "res://"+path)

static func retained_sha256(path: String) -> String:
	_ensure()
	if not checked: return ""
	var relative := _relative(path)
	if proof.predecessors.has(relative) and relative not in CURRENT_ONLY: return str(proof.predecessors[relative].sha256)
	return FileAccess.get_sha256(path if path.begins_with("res://") else "res://"+path)

static func retained_compiled(value: Dictionary) -> Dictionary:
	_ensure()
	if not checked: return {}
	var prior: Dictionary=JSON.parse_string(old_text["data/generated/structural_meshes.json"])
	if value!=current_compiled and value!=prior:
		push_error("Caller is neither authenticated full current nor exact retained predecessor")
		return {}
	return prior

static func retained_floor_children(floors: Node) -> Array:
	_ensure()
	if not checked: return []
	if floors==null or floors.get_child_count()!=272:
		push_error("Medical successor requires all272 actual owners")
		return []
	var expected: Dictionary={}
	for record in current_compiled.regions: expected[str(record.id)]=record
	var seen: Dictionary={}
	var retained: Array=[]
	for owner in floors.get_children():
		var id := str(owner.name)
		if not expected.has(id) or seen.has(id):
			push_error("Unknown or duplicate loaded owner")
			return []
		if owner.get_meta("region_id","")!=id:
			push_error("Actual owner identity mismatch")
			return []
		seen[id]=true
		if id==OWNER:
			var contacts := owner.find_children("*","StaticBody3D",true,false)
			if contacts.size()!=1:
				push_error("Medical slab must have one compiler contact owner")
				return []
		else: retained.append(owner)
	if seen.size()!=272 or retained.size()!=271 or not seen.has(OWNER):
		push_error("Incomplete actual floor owner roster")
		return []
	return retained

static func retained_owner_count(floors: Node) -> int:
	var retained: Array=retained_floor_children(floors)
	if not checked or retained.size()!=271: return -1
	return retained.size()

static func retained_json(path: String) -> Dictionary:
	var content: String=retained_text(path)
	if not checked or content.is_empty(): return {}
	var value: Variant=JSON.parse_string(content)
	if not value is Dictionary:
		push_error("Expected an authenticated dictionary")
		return {}
	return value

static func validate_current(floors: Node = null) -> Dictionary:
	_ensure()
	if not checked: return {}
	if floors==null:
		push_error("Actual loaded floor root required for completed medical validation")
		return {}
	var retained: Array=retained_floor_children(floors)
	if retained.size()!=271: return {}
	var result: Dictionary=proof.duplicate(true)
	result["validation_completed"]=true
	return result
