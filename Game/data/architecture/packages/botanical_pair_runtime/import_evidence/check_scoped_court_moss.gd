extends SceneTree
func _initialize()->void:
 call_deferred("_run")
func _run()->void:
 var medical=load("res://tests/medical_triage_successor_guard.gd")
 medical._ensure()
 var host:Node3D=load("res://scripts/ship.gd").new()
 # Host never enters the tree, so its entire-world _ready does not run.
 var space:=Node3D.new();space.name="ScopedActualCourtAndCompiledFloors";root.add_child(space)
 var material:=StandardMaterial3D.new()
 var floors:Node3D=load("res://scripts/structural_floor_builder.gd").build(space,material,material)
 assert(floors.get_child_count()==303)
 assert(load("res://tests/botanical_pair_successor_guard.gd").floor_children(floors).size()==300)
 var court:Node3D=host.model(space,"AST-ATR-001_botanical_nursery_open001.glb","BotanicalCourtReceivingClosedInterim",Vector3.ZERO)
 var moss_data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/moss_sanctuary/runtime_manifest.json"))
 load("res://scripts/moss_sanctuary_receiving.gd")._open_supported_portal(space,moss_data)
 var helper=load("res://tests/botanical_pair_court_guard.gd")
 helper.validate_moss_roster(court,14,106,moss_data.opened_guard_names)
 helper.validate(floors,medical.botanical_proof)
 assert(helper.physical_validation_succeeded())
 print("PASS: actual scoped court120 mesh/contact/hierarchy fidelity; unchanged production Moss portal function opens14 and retains106; actual303 compiled slab geometry validates. No complete main-scene/Moss-room/route acceptance.")
 host.free();space.queue_free();await process_frame;quit(0)
