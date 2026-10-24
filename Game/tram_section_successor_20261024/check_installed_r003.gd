extends SceneTree
# Explicit opt-in root-owned selected-world check. No default scene fallback,
# second ship in an existing world, actor movement or production admission.
const P := "res://tram_section_successor_20261024/"
var checks := 0
var failures := 0
var ship: Node3D

func _initialize() -> void:
	call_deferred("run")

func require(value: bool, message: String) -> void:
	checks += 1
	if not value:
		failures += 1
		push_error("TRAM_INSTALLED_R003_FAIL: " + message)

func argument(key: String) -> String:
	for arg: String in OS.get_cmdline_user_args():
		if arg.begins_with(key + "="):
			return arg.substr(key.length() + 1)
	return ""

func run() -> void:
	if "--negative-control" in OS.get_cmdline_user_args():
		require(false, "intentional fail-latch control; no ship constructed")
		finish({})
		return
	var scene_path := argument("--ship-scene")
	var scene_sha := argument("--ship-sha256")
	var script_sha := argument("--script-sha256")
	require(scene_path.begins_with("res://") and scene_sha.length() == 64 and script_sha.length() == 64, "explicit candidate scene, scene digest and main-script digest required")
	if failures > 0:
		finish({})
		return
	require(FileAccess.get_sha256(scene_path) == scene_sha, "exact root-owned candidate scene bytes")
	if failures > 0:
		finish({})
		return
	var packed: PackedScene = load(scene_path)
	require(packed != null, "candidate scene resolves")
	if packed == null:
		finish({})
		return
	ship = packed.instantiate()
	require(ship != null and ship.has_signal("runtime_ready") and ship.has_signal("construction_finished"), "complete inherited constructor interface")
	if ship == null:
		finish({})
		return
	var script: Script = ship.get_script()
	require(script != null and FileAccess.get_sha256(script.resource_path) == script_sha, "exact root-owned most-derived constructor bytes")
	if failures > 0:
		finish({})
		return
	var verify_ok: bool = load(P + "integration_r003.gd").verify(ship)
	require(verify_ok, "retained assembly, predecessor and integration contracts before construction")
	if failures > 0:
		finish({})
		return
	# No scene is ever loaded implicitly. The supplied experimental scene retains
	# every actual district hook and ReceivedSectionInstallation/deferred phase.
	root.add_child(ship)
	var started := Time.get_ticks_msec()
	var limit := 300.0
	if not argument("--startup-limit").is_empty():
		limit = clampf(float(argument("--startup-limit")), 30.0, 900.0)
	while not bool(ship.get_meta("runtime_ready", false)):
		if ship.has_meta("tram_section_adapter_error"):
			require(false, str(ship.get_meta("tram_section_adapter_error")))
			finish({"stage":str(ship.get_meta("startup_stage", ""))})
			return
		if Time.get_ticks_msec() - started > int(limit * 1000.0):
			require(false, "bounded startup limit; no readiness inferred")
			finish({"stage":str(ship.get_meta("startup_stage", "")), "startup_limit_seconds":limit})
			return
		await process_frame
	require(not ship.has_meta("tram_section_adapter_error"), "no failed adapter hidden by readiness")
	var installation: Node = ship.get_node_or_null("ReceivedSectionInstallation")
	require(installation != null and bool(installation.get_meta("installation_ready", false)), "actual received-section installation completed")
	require(ship.startup_deferred_builders.is_empty(), "all actual deferred receiving hooks completed")
	if failures > 0:
		finish({})
		return
	# Allow actual physics to establish stationary docking. The synchronous
	# read-only sweep changes no actor physics, world pause or body transform.
	for i in range(20):
		await physics_frame
	var assembly: Node3D = ship.get_node_or_null("ShipSpace/Districts/Group4Completion")
	require(assembly != null, "canonical single Group4 owner")
	if assembly == null:
		finish({})
		return
	require(not ship.has_node("ShipSpace/Districts/Group4SectionSuccessor20261024"), "no second temporary-named owner survived")
	require(assembly.get_meta("tram_section_source_revision", "") == "20261024/r003", "named normal-constructor successor is installed")
	require(bool(assembly.get_meta("tram_section_before_complete", false)) and bool(assembly.get_meta("tram_section_after_complete", false)), "both integration phases completed")
	var actor: CharacterBody3D = ship.get_node("ShipSpace/PersistentActors/Player")
	var cart: RigidBody3D = ship.get_node("ShipSpace/PersistentActors/CustodialCart")
	var body: AnimatableBody3D = assembly.get_node("Group4OwnedTram_Source024")
	var safety: Node3D = assembly.get_node("Group4BoardingSafety")
	var restraint: Node3D = assembly.get_node("Group4OriginalCartRestraint")
	var motor: Node3D = assembly.get_node("Group4LoadedSourceTravelActuator")
	var controls: Node3D = assembly.get_node("Group4SourceOperatingControls")
	var information: Node3D = assembly.get_node("Group4SourceStationInformation")
	var budget: Node = ship.get_node("ShipSystems/LocalShadowSourceBudget")
	var identity: Dictionary = assembly.get_meta("tram_section_original_identity")
	var products: Array[int] = []
	for product: RigidBody3D in cart.products:
		products.append(product.get_instance_id())
	require(actor.get_instance_id() == identity.actor and cart.get_instance_id() == identity.cart and products == identity.products, "original player/cart/four stock identities preserved")
	require(cart.interaction_owner.get_instance_id() == identity.handle and controls.original_handle_script == identity.handle_script, "same original handle and restoration script")
	require(restraint.cart == cart and motor.restraint == restraint and controls.restraint == restraint and controls.player == actor, "actual motor/restraint/controls bind original actors")
	require(controls.motor == motor and controls.vehicle == body and safety.vehicle == body and motor.vehicle == body, "one exact vehicle owner throughout")
	require(controls.light_budget == budget and budget.sources.count(controls.light) == 1, "existing light budget owns exactly one retained car light")
	require(information.safety == safety and information.gates.size() == 5 and controls.controls.size() == 13, "all five station cases/calls and eight car controls retained")
	require(not assembly.get_meta("tram_operations_admitted") and not safety.get_meta("integration_boarding_admitted") and not restraint.get_meta("integration_joint_admitted") and not motor.get_meta("integration_motion_admitted"), "all production admission remains false")
	require(not motor.moving and not motor.motion_fault and not restraint.motion_fault and restraint.phase == "unlocked", "unloaded startup retains no new motion/restraint fault")
	require(motor.bogies.size() == 2 and motor.wheel_pivots.size() == 4 and body.get_meta("exact_original_portal_contact_components", 0) == 18, "actual articulated source bogies/wheels and exact portal components installed")
	require(safety.stationary_frames >= 15 and safety._physical_dock_matches("CENTRAL") and safety.door_side("CENTRAL") == "PORT", "actual stationary curved CENTRAL docking and explicit PORT identity")
	require(not safety.request_boarding("CENTRAL") and not motor.request_stop("AFT") and not restraint.request_lock(), "normal requests cannot bypass admission holds")
	if failures > 0:
		finish({"startup_seconds":float(Time.get_ticks_msec() - started) / 1000.0})
		return
	var result: Dictionary = load(P + "installed_gate.gd").audit(assembly, ship)
	require(result.status == "PASS_SAMPLED_INSTALLED_CONTACTS", "actual installed-world contact sweep: " + str(result.status))
	result.startup_seconds = float(Time.get_ticks_msec() - started) / 1000.0
	result.scene = scene_path
	result.scene_sha256 = scene_sha
	result.main_script_sha256 = script_sha
	finish(result)

func finish(sweep: Dictionary) -> void:
	var result := {"status":"PASS_INSTALLED_SOURCE_CONNECTION" if failures == 0 else "FAIL_INSTALLED_SOURCE_CONNECTION", "checks":checks, "failures":failures, "production_admission":false, "contact_sweep":sweep, "not_accepted":["moving passenger/scenic experience", "original loaded cart/caster/joint", "structural capacity", "full visual geometry coverage", "whole-ship gameplay/performance"]}
	print("TRAM_INSTALLED_R003_RESULT " + JSON.stringify(result))
	var report_path := argument("--report")
	if not report_path.is_empty():
		var output := FileAccess.open(report_path, FileAccess.WRITE)
		if output != null:
			output.store_string(JSON.stringify(result, "  ") + "\n")
	if is_instance_valid(ship):
		ship.free()
	quit(1 if failures > 0 else 0)
