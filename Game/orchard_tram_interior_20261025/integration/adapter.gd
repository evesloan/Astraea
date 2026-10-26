extends RefCounted
# Named normal-construction adapter. Never swaps a live owner or admits motion.
const P := "res://tram_section_successor_20261024/"
const NORMAL_PATH := "ShipSpace/Districts/Group4Completion"
const ORIGINAL_ADAPTER := "res://scripts/group4_integrated_receiving.gd"

static func reject(ship: Node3D, reason: String) -> bool:
	ship.set_meta("tram_section_adapter_error", reason)
	push_error("TRAM_SECTION_INTEGRATION_HELD: " + reason)
	return false

static func verify(ship: Node3D) -> bool:
	var record = JSON.parse_string(FileAccess.get_file_as_string(P + "INTEGRATION_CONTRACTS_r003.json"))
	if not record is Dictionary:
		return reject(ship, "Missing exact integration source contracts")
	for bucket: Dictionary in [record.prerequisites, record.owned]:
		for path: String in bucket:
			if FileAccess.get_sha256(path) != str(bucket[path]):
				return reject(ship, "Integration source differs: " + path)
	if not load("res://orchard_tram_interior_20261025/integration/assembly.gd").verify():
		return reject(ship, "Retained r002 assembly contracts differ")
	var initial:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://tram_passenger_successor_20261024/CONTRACTS_r002.json"))
	for bucket:Dictionary in [initial.prerequisites,initial.owned]:
		for path:String in bucket:
			if FileAccess.get_sha256(path)!=str(bucket[path]):return reject(ship,"Initial-pose source differs: "+path)
	return true

static func before_budget(ship: Node3D) -> Node3D:
	# Caller must stop its _ready if null is returned; see the exact hook recipe.
	if not verify(ship):
		return null
	# Preserve the actual retained three-owner pit proof and all original active,
	# north-stop/shared-pit/terminal predicates. No structural acceptance shortcut.
	load("res://tests/group4_exact_pit_successor_guard.gd").ensure()
	var original = load(ORIGINAL_ADAPTER)
	var plans := {}
	for key: String in original.CONFIGS:
		plans[key] = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/" + str(original.CONFIGS[key])))
		if not bool(plans[key].get("active", false)):
			reject(ship, "Retained source component inactive: " + key)
			return null
	for key: String in ["travel", "loaded"]:
		if not bool(plans[key].get("north_stop_adopted", false)) or not bool(plans[key].get("shared_pits_adopted", false)):
			reject(ship, "Retained north-stop/pit prerequisite held: " + key)
			return null
	if not bool(plans.boarding.get("terminal_active", false)):
		reject(ship, "Retained terminal branches must remain installed")
		return null
	var districts: Node3D = ship.get_node_or_null("ShipSpace/Districts")
	var actor: CharacterBody3D = ship.get_node_or_null("ShipSpace/PersistentActors/Player")
	var cart: RigidBody3D = ship.get_node_or_null("ShipSpace/PersistentActors/CustodialCart")
	if districts == null or actor == null or cart == null:
		reject(ship, "Actual districts and original persistent player/cart must preexist")
		return null
	if districts.has_node("Group4Completion") or districts.has_node("Group4SectionSuccessor20261024"):
		reject(ship, "A surviving Group4 owner exists; never overwrite or create a competing assembly")
		return null
	if not districts.global_transform.is_equal_approx(Transform3D.IDENTITY):
		reject(ship, "Authored world-coordinate section requires the retained identity district frame")
		return null
	if cart.has_meta("group4_restraint_owner") or is_instance_valid(cart.driver):
		reject(ship, "Original cart is already owned or actively driven")
		return null
	var products: Array[int] = []
	for product: RigidBody3D in cart.products:
		products.append(product.get_instance_id())
	var original_identity := {"actor":actor.get_instance_id(), "cart":cart.get_instance_id(), "products":products, "actor_pose":actor.global_transform, "cart_pose":cart.global_transform, "handle":cart.interaction_owner.get_instance_id(), "handle_script":cart.interaction_owner.get_script()}
	if not load("res://orchard_tram_interior_20261025/integration/floor.gd").apply(ship):
		reject(ship,"Orchard exact floor receiving failed");return null
	if not load("res://orchard_tram_interior_20261025/integration/rooms.gd").apply(ship):
		reject(ship,"Orchard exact room/light receiving failed");return null
	var assembly: Node3D = load("res://orchard_tram_interior_20261025/integration/assembly.gd").create(districts,"FORE_MIDSHIP" if "--orchard-review-spawn" in OS.get_cmdline_user_args() else "CENTRAL")
	if assembly == null:
		reject(ship, "Named assembly construction failed")
		return null
	# Canonical node identity is restored before binding original actors/controls.
	# This is the one normal constructor, never a late replacement operation.
	assembly.name = "Group4Completion"
	assembly.set_meta("tram_section_source_revision", "20261024/r003")
	assembly.set_meta("tram_initial_pose_revision", "20261024/r002")
	assembly.set_meta("tram_section_original_identity", original_identity)
	assembly.set_meta("tram_section_before_complete", false)
	assembly.set_meta("tram_section_after_complete", false)
	var motor: Node3D = load("res://orchard_tram_interior_20261025/integration/assembly.gd").attach_original_cart(assembly, cart)
	var safety: Node3D = assembly.get_node("Group4BoardingSafety")
	var restraint: Node3D = assembly.get_node("Group4OriginalCartRestraint")
	if motor == null or motor.moving or safety.phase != "secured" or restraint.phase != "unlocked":
		reject(ship, "Original loaded motor/restraint failed its initial secured state")
		return null
	if not actor.global_transform.is_equal_approx(original_identity.actor_pose) or not cart.global_transform.is_equal_approx(original_identity.cart_pose):
		reject(ship, "Original actor/cart pose changed during construction")
		return null
	assembly.set_meta("tram_operations_admitted", false)
	safety.set_meta("integration_boarding_admitted", false)
	restraint.set_meta("integration_joint_admitted", false)
	motor.set_meta("integration_motion_admitted", false)
	assembly.set_meta("tram_operation_hold", "Named section/controller source integrated; installed-world contacts, structural capacity, original caster/joint and moving-passenger acceptance remain held")
	assembly.set_meta("receiving_north_physical_dock", Vector3(17.3, 56.1, -236.1))
	assembly.set_meta("directory_fore_midship_catchment_z", -216)
	assembly.set_meta("integrated_empty_startup_station", "CENTRAL")
	assembly.set_meta("source_scope", "One retained five-station assembly, X47.5 section, curved CENTRAL body, original actors and loaded guards; admission false")
	assembly.set_meta("tram_section_before_complete", true)
	return assembly

static func after_budget(ship: Node3D) -> bool:
	# Must be called AFTER the unchanged first construction-step label and budget
	# configure; the court successor owns that hook and must not be bypassed.
	var assembly: Node3D = ship.get_node_or_null(NORMAL_PATH)
	if assembly == null or not bool(assembly.get_meta("tram_section_before_complete", false)):
		return reject(ship, "Named before-budget phase is incomplete")
	if assembly.has_node("Group4SourceOperatingControls") or assembly.has_node("Group4SourceStationInformation"):
		return reject(ship, "Operating controls or information already exist; build exactly once")
	var budget: Node = ship.get_node_or_null("ShipSystems/LocalShadowSourceBudget")
	var actor: CharacterBody3D = ship.get_node("ShipSpace/PersistentActors/Player")
	var cart: RigidBody3D = ship.get_node("ShipSpace/PersistentActors/CustodialCart")
	if budget == null or budget.actor != actor or budget.sources.is_empty():
		return reject(ship, "Original light-budget configure phase has not completed")
	if budget.get_script() != load("res://night_garden_court_completion_20261022/lighting_budget.gd"):
		return reject(ship, "Current inherited court light-budget owner was not preserved")
	var body: AnimatableBody3D = assembly.get_node("Group4OwnedTram_Source024")
	var safety: Node3D = assembly.get_node("Group4BoardingSafety")
	var restraint: Node3D = assembly.get_node("Group4OriginalCartRestraint")
	var motor: Node3D = assembly.get_node("Group4LoadedSourceTravelActuator")
	var identity: Dictionary = assembly.get_meta("tram_section_original_identity")
	if actor.get_instance_id() != identity.actor or cart.get_instance_id() != identity.cart or restraint.cart != cart or motor.restraint != restraint:
		return reject(ship, "Persistent actor/cart/restraint/motor ownership differs")
	var products: Array[int] = []
	for product: RigidBody3D in cart.products:
		products.append(product.get_instance_id())
	if products != identity.products or cart.interaction_owner.get_instance_id() != identity.handle:
		return reject(ship, "Original product identities/order or handle changed across construction phases")
	# The intervening retained construction-step yield may legitimately advance
	# physics. Compare poses within this synchronous call, not across that yield.
	var actor_before := actor.global_transform
	var cart_before := cart.global_transform
	var previous_lights: int = budget.sources.size()
	var controls: Node3D = load("res://scripts/group4_tram_operating_controls.gd").build(assembly, body, safety, restraint, motor, actor, budget)
	var information: Node3D = load("res://scripts/group4_station_information.gd").build(assembly, safety)
	if controls == null or information == null:
		return reject(ship, "Retained controls/information construction failed")
	if budget.sources.size() != previous_lights + 1 or budget.sources.count(controls.light) != 1:
		return reject(ship, "Exactly one retained car light must join the existing budget")
	if controls.original_handle.get_instance_id() != identity.handle or controls.original_handle_script != identity.handle_script:
		return reject(ship, "Retained original handle owner or restoration script differs")
	if not actor.global_transform.is_equal_approx(actor_before) or not cart.global_transform.is_equal_approx(cart_before):
		return reject(ship, "Original actor/cart was moved by the integration")
	assembly.set_meta("tram_section_after_complete", true)
	return true
