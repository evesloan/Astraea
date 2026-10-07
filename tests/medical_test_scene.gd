extends SceneTree
const CONTRACT: String="res://data/architecture/D05_MEDICAL_WELCOME_RUNTIME.json"
var test_name: String="medical"
var main: Node
var ship: Node3D
var actor: CharacterBody3D
var cart: RigidBody3D
var floors: Node3D
var built: Node3D
var space: PhysicsDirectSpaceState3D
var data: Dictionary
var triage_evidence: Dictionary
var triage_proof: Dictionary
var failed: bool=false
var frames: int=0
var support_samples: int=0
var started: int=0
var keys: Dictionary={}
var metrics: Dictionary={}
var receipt_path: String

func _process(_delta: float) -> bool:
	if started>0 and Time.get_ticks_msec()-started>480000 and not failed: require(false,"480-second bounded watchdog")
	return false

func require(ok: bool,message: String) -> bool:
	if ok: return true
	if failed: return false
	failed=true
	release_inputs()
	write_receipt("FAIL",message)
	push_error(test_name+": "+message)
	quit(1)
	return false

func xyz(v: Array) -> Vector3: return Vector3(float(v[0]),float(v[1]),float(v[2]))

func key(code: Key,pressed: bool) -> void:
	if keys.get(code,false)==pressed: return
	keys[code]=pressed
	var event: InputEventKey=InputEventKey.new()
	event.keycode=code;event.physical_keycode=code;event.pressed=pressed
	Input.parse_input_event(event);Input.flush_buffered_events()

func focus(pressed: bool) -> void:
	var event: InputEventMouseButton=InputEventMouseButton.new()
	event.button_index=MOUSE_BUTTON_RIGHT;event.pressed=pressed
	Input.parse_input_event(event);Input.flush_buffered_events()

func release_inputs() -> void:
	for code in [KEY_W,KEY_A,KEY_S,KEY_D,KEY_E]: key(code,false)
	focus(false)

func ray(a: Vector3,b: Vector3,excluded: Array[RID]=[]) -> Dictionary:
	var q: PhysicsRayQueryParameters3D=PhysicsRayQueryParameters3D.create(a,b,1)
	q.exclude=excluded;q.hit_back_faces=true
	return space.intersect_ray(q)

func exclusions() -> Array[RID]:
	var result: Array[RID]=[actor.get_rid(),cart.get_rid()]
	for product in cart.products: result.append(product.get_rid())
	return result

func support_at(point: Vector3,owner: String="") -> bool:
	var hit: Dictionary=ray(point+Vector3.UP*.14,point-Vector3.UP*.16,exclusions())
	if not require(not hit.is_empty() and floors.is_ancestor_of(hit.collider),"Missing compiler-owned support at "+str(point)): return false
	if not require(absf(float(hit.position.y)-point.y)<.015 and float(hit.normal.y)>.95,"Wrong support level/normal at "+str(point)): return false
	if not owner.is_empty() and not require(str(hit.collider.get_parent().name)==owner,"Wrong floor owner at "+str(point)): return false
	support_samples+=1
	return true

func advance(count: int,check_d05_support: bool=false) -> bool:
	for frame in range(count):
		await physics_frame
		frames+=1
		if failed: return false
		if not require(frames<30000,"Bounded30000-frame allowance exceeded"): return false
		if check_d05_support:
			if not require(absf(actor.global_position.y-21.0)<.08,"Original capsule left D05 datum"): return false
			if not support_at(Vector3(actor.global_position.x,21,actor.global_position.z)): return false
	return true

func pin_imports() -> bool:
	for filename in data.model_pins:
		var path: String="res://assets/models/"+str(filename)
		if not require(FileAccess.get_sha256(path)==str(data.model_pins[filename]),"Changed source model "+path): return false
		var config: ConfigFile=ConfigFile.new()
		if not require(config.load(path+".import")==OK,"Missing import settings "+path): return false
		var imported: String=str(config.get_value("remap","path",""))
		if not require(not imported.is_empty() and FileAccess.file_exists(imported),"Missing imported scene "+path): return false
		var cached: ConfigFile=ConfigFile.new()
		if not require(cached.load(imported.get_basename()+".md5")==OK,"Missing cache digest "+path): return false
		if not require(str(cached.get_value("","source_md5",""))==FileAccess.get_md5(path),"Stale actual import "+path): return false
	return true

func exact_node(parent: Node,original: String) -> Node:
	var node: Node=parent.find_child(original,true,false)
	if node==null: node=parent.find_child(original.validate_node_name(),true,false)
	return node

func write_receipt(status: String,detail: String="") -> void:
	if receipt_path.is_empty(): return
	var out: Dictionary={"test":test_name,"status":status,"detail":detail,"physics_frames":frames,"support_samples":support_samples,"metrics":metrics,"runtime_contract_sha256":FileAccess.get_sha256(CONTRACT),"scope":"Focused actual-world construction test only; no completed clinical department, species/robot fit, freehand comfort or target-GPU claim."}
	var f: FileAccess=FileAccess.open(receipt_path,FileAccess.WRITE)
	if f!=null: f.store_string(JSON.stringify(out,"  ")+"\n")

func run() -> void:
	started=Time.get_ticks_msec()
	receipt_path="res://artifacts/"+test_name+"_attempt_"+str(Time.get_unix_time_from_system()).replace(".","_")+"_"+str(started)+".json"
	data=JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	if not require(data.has("source_evidence_file") and data.has("source_evidence_sha256"),"Pinned source010 test evidence required"): return
	if not require(FileAccess.get_sha256(str(data.source_evidence_file))==str(data.source_evidence_sha256),"Source010 expectations changed"): return
	triage_evidence=JSON.parse_string(FileAccess.get_file_as_string(str(data.source_evidence_file)))
	main=(load("res://scenes/main.tscn") as PackedScene).instantiate();root.add_child(main)
	for frame in range(150): await physics_frame
	ship=main.get_node("World360/Astraea") as Node3D
	actor=ship.get_node("ShipSpace/PersistentActors/Player") as CharacterBody3D
	cart=ship.find_child("CustodialCart",true,false) as RigidBody3D
	floors=ship.find_child("CompiledStructuralFloors_NotFinishedRooms",true,false) as Node3D
	built=ship.find_child(str(data.root_name),true,false) as Node3D
	space=ship.get_world_3d().direct_space_state
	if not require(built!=null and floors!=null and cart!=null,"Installed medical root/floors/original cart required"): return
	if not pin_imports(): return
	triage_proof=load("res://tests/medical_triage_successor_guard.gd").validate_current(floors)
	if not require(bool(triage_proof.get("validation_completed",false)),"Authenticated complete triage successor proof did not complete"): return
	var proof: Dictionary=load("res://tests/medical_successor_guard.gd").validate_current(floors)
	if not require(bool(proof.get("validation_completed",false)),"Authenticated medical predecessor/current-world proof did not complete"): return
	if not await exercise(): return
	if failed: return
	release_inputs();write_receipt("PASS")
	print(test_name.to_upper()," PASS: ",JSON.stringify(metrics)," support:",support_samples," frames:",frames)
	main.queue_free();await process_frame;quit(0)

func exercise() -> bool: return false
