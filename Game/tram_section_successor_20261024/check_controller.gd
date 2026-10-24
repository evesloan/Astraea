extends SceneTree
# Isolated, fail-latched physical fixture. Never attach to a live ship.
# Root alone runs this. A local test instance briefly authorizes BOARDING ONLY
# to exercise the original phase machine; motion/joint authority stays false.
const P := "res://tram_section_successor_20261024/"
var checks := 0
var failures := 0
var world: Node3D

func _initialize() -> void:
	call_deferred("run")

func require(value: bool, message: String) -> void:
	checks += 1
	if not value:
		failures += 1
		push_error("TRAM_SECTION_CONTROLLER_FAIL: " + message)

func frames(count: int) -> void:
	for i in range(count):
		await physics_frame

func run() -> void:
	if "--negative-control" in OS.get_cmdline_user_args():
		require(false, "intentional failure latch")
		finish()
		return
	var factory = load(P + "assembly.gd")
	require(factory.verify(), "exact selected source contracts")
	if failures > 0:
		finish()
		return
	world = Node3D.new()
	world.name = "IsolatedSectionControllerFixture_UNADOPTED"
	root.add_child(world)
	var assembly: Node3D = factory.create(world)
	require(assembly != null, "one named candidate assembly")
	if assembly == null:
		finish()
		return
	var safety: Node3D = assembly.get_node("Group4BoardingSafety")
	var body: AnimatableBody3D = assembly.get_node("Group4OwnedTram_Source024")
	var bridge: Node3D = assembly.get_node("Group4Bridge_CENTRAL")
	# Same retained empty/stowed initialization as the original motor. No motor,
	# cart, passenger or persistent state is fabricated for this controller gate.
	load("res://scripts/group4_tram_source_actuator.gd").initialize_bridge_physics(safety)
	await frames(2)
	require(not assembly.get_meta("tram_operations_admitted"), "assembly admission stays false")
	require(not safety.get_meta("integration_boarding_admitted"), "default boarding stays false")
	require(not assembly.has_node("Group4LoadedSourceTravelActuator"), "no motor or moving-passenger claim")
	require(safety.door_side("CENTRAL") == "PORT", "curved CENTRAL uses explicit PORT identity")
	var expected: Transform3D = safety.expected_dock("CENTRAL")
	require(body.global_transform.origin.distance_to(expected.origin) < .000001, "actual body/chord position equals authored docking position")
	require(safety.pose_matches(expected, expected, 15), "15 stationary frames at exact body pose")
	require(not safety.pose_matches(expected, expected, 14), "14 stationary frames rejected")
	var displaced := expected
	displaced.origin += Vector3(.006, 0, 0)
	require(not safety.pose_matches(displaced, expected, 15), "6 mm body mismatch rejected by unchanged 5 mm criterion")
	var turned := Transform3D(Basis(Vector3.UP, .0012) * expected.basis, expected.origin)
	require(not safety.pose_matches(turned, expected, 15), "1.2 mrad mismatch rejected by unchanged 1 mrad criterion")
	var seam := Transform3D(Basis(Vector3.UP, TAU) * expected.basis, expected.origin)
	require(safety.pose_matches(seam, expected, 15), "equivalent yaw winding accepted")
	await frames(16)
	require(safety._physical_dock_matches("CENTRAL"), "actual stationary controller reaches physical docking gate")
	require(not safety.request_boarding("CENTRAL"), "physical docking does not bypass default admission")
	require(absf(bridge.threshold_shape.size.x - 1.532626557256718) < .000001, "expanded longer-panel occupancy length")
	var witness := RigidBody3D.new()
	witness.name = "ThresholdOccupancyWitness_NOT_A_PASSENGER"
	witness.freeze = true
	var col := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(.04, .1, .04)
	col.shape = box
	witness.add_child(col)
	world.add_child(witness)
	witness.global_transform = bridge.global_transform * Transform3D(Basis.IDENTITY, Vector3(1.30, 1, 0))
	await frames(2)
	require(bridge.threshold_occupied(), "occupant at extended x=1.30 m detected; original 1.17 m end would miss it")
	require(not bridge.safe_to_depart(), "occupied extension forbids departure even when stowed")
	bridge.dock_authorized = true
	var request_ok: bool = bridge.request_deploy()
	require(request_ok, "fixture-only bridge request accepted with physical docking authority")
	await frames(5)
	require(bridge.obstructed and bridge.fraction < .0001, "extended occupancy prevents panel movement")
	bridge.request_stow()
	bridge.dock_authorized = false
	witness.free()
	await frames(2)
	require(not bridge.threshold_occupied(), "occupancy clears on actual collider removal")
	if failures > 0:
		finish()
		return
	# This isolated fixture is not an integration receipt. Permit one physical
	# boarding cycle here to test actual PORT/STARBOARD phase dispatch.
	safety.set_meta("integration_boarding_admitted", true)
	var board_ok: bool = safety.request_boarding("CENTRAL")
	require(board_ok, "isolated 15-frame exact curved docking begins deployment")
	for i in range(220):
		await physics_frame
		if safety.phase == "boarding" and safety.car_gates.PORT.open_fraction > .999:
			break
	require(safety.phase == "boarding", "deployment reaches retained boarding phase")
	require(safety.car_gates.PORT.requested_open and safety.car_gates.PORT.open_fraction > .999, "actual PORT gate opens")
	require(not safety.car_gates.STARBOARD.requested_open and safety.car_gates.STARBOARD.open_fraction < .0001, "opposite car gate remains shut")
	require(safety.station_gates.CENTRAL.requested_open, "CENTRAL platform barrier opens")
	require(not safety.unloaded_clear_to_depart(), "boarding forbids departure")
	var secure_ok: bool = safety.request_secure()
	require(secure_ok, "secure request accepted by existing phase machine")
	for i in range(240):
		await physics_frame
		if safety.phase == "secured":
			break
	require(safety.phase == "secured" and bridge.safe_to_depart(), "PORT closes, panel stows, and closed safety is restored")
	safety.set_meta("integration_boarding_admitted", false)
	require(not safety.request_boarding("CENTRAL"), "fixture authority removed and default hold restored")
	finish()

func finish() -> void:
	print(JSON.stringify({"status":"PASS_ISOLATED_CURVED_BOARDING" if failures == 0 else "FAIL_ISOLATED_CURVED_BOARDING", "checks":checks, "failures":failures, "production_admission":false, "not_tested":["full selected ship contacts", "moving passenger", "loaded original cart/caster/joint", "structural capacity", "scenic/visual/performance acceptance"]}))
	if is_instance_valid(world):
		world.free()
	quit(1 if failures > 0 else 0)
