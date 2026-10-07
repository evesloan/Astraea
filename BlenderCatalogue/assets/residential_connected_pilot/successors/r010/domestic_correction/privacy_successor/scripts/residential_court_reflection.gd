extends Node3D
## Bounded native trial: capture only public court geometry and opaque residential
## coatings; apply reflections only to those exterior coatings. No ambient fill.
const CAPTURE_LAYER := 1 << 18
const EXTERIOR_RECEIVER_LAYER := 1 << 19
const PROBE_CENTER := Vector3(18.8, 88.35, -320.5)
const PROBE_SIZE := Vector3(23.4, 9.4, 26.0)
const APPROACH_REGION := AABB(Vector3(3.0, 82.5, -341.0), Vector3(44.0, 11.0, 39.0))
var pilot: Node3D
var ship: Node3D
var probe: ReflectionProbe
var busy := false
var configured := false
var elapsed := 0.0
var nearby_seconds := 0.0
var tagged_public_meshes := 0
var tagged_private_exteriors := 0

func configure(pilot_root: Node3D, ship_root: Node3D) -> void:
    assert(not configured)
    pilot = pilot_root
    ship = ship_root
    set_meta("scope", "One local once-updated residential exterior reflection trial")
    set_meta("native_appearance_verified", false)
    configured = true
    set_process(true)

func _process(delta: float) -> void:
    if not configured or busy or is_instance_valid(probe):
        return
    elapsed += delta
    if elapsed < .25:
        return
    var step := elapsed
    elapsed = 0
    var actor := ship.get_node_or_null("ShipSpace/PersistentActors/Player") as Node3D
    var budget := ship.get_node_or_null("ShipSystems/LocalShadowSourceBudget")
    if actor == null or budget == null or not APPROACH_REGION.has_point(actor.global_position):
        nearby_seconds = 0
        return
    nearby_seconds += step
    if nearby_seconds >= .5:
        capture_for_review()

func _tag_exact_capture_scope() -> void:
    var court := pilot.get_node("ActualConnectedCourt_WIP") as Node3D
    assert(court != null)
    # Check the two visual bits before first use. Physics masks are unrelated.
    if tagged_public_meshes == 0:
        for mesh: MeshInstance3D in ship.find_children("*", "MeshInstance3D", true, false):
            assert((mesh.layers & (CAPTURE_LAYER | EXTERIOR_RECEIVER_LAYER)) == 0,
                "Reserved local reflection layer already has another owner")
        for mesh: MeshInstance3D in court.find_children("*", "MeshInstance3D", true, false):
            mesh.layers |= CAPTURE_LAYER
            mesh.set_meta("residential_court_capture_public", true)
            tagged_public_meshes += 1
        for mesh: MeshInstance3D in pilot.find_children("*", "MeshInstance3D", true, false):
            if bool(mesh.get_meta("residential_privacy_exterior", false)):
                mesh.layers |= CAPTURE_LAYER | EXTERIOR_RECEIVER_LAYER
                tagged_private_exteriors += 1
    assert(tagged_public_meshes > 0 and tagged_private_exteriors == 3)
    # Private room shells, furnishings, emitters and test targets are never
    # captured, even while an optical positive control temporarily hides glass.
    for mesh: MeshInstance3D in ship.find_children("*", "MeshInstance3D", true, false):
        if (mesh.layers & CAPTURE_LAYER) != 0:
            assert(court.is_ancestor_of(mesh) or bool(mesh.get_meta("residential_privacy_exterior", false)))
        if (mesh.layers & EXTERIOR_RECEIVER_LAYER) != 0:
            assert(bool(mesh.get_meta("residential_privacy_exterior", false)))

func capture_for_review() -> void:
    if not configured or busy:
        return
    busy = true
    var budget := ship.get_node_or_null("ShipSystems/LocalShadowSourceBudget")
    assert(budget != null)
    budget.refresh()  # Same existing eight-source policy; no power/budget override.
    for step in range(3):
        await get_tree().process_frame
    _tag_exact_capture_scope()
    if is_instance_valid(probe):
        probe.queue_free()
        await get_tree().process_frame
    probe = ReflectionProbe.new()
    probe.name = "ActualCourt_Once_ExteriorOnly"
    probe.size = PROBE_SIZE
    probe.max_distance = 22.0
    probe.interior = true
    probe.ambient_mode = ReflectionProbe.AMBIENT_DISABLED
    probe.box_projection = true
    probe.update_mode = ReflectionProbe.UPDATE_ONCE
    probe.cull_mask = CAPTURE_LAYER
    probe.reflection_mask = EXTERIOR_RECEIVER_LAYER
    probe.enable_shadows = true
    probe.intensity = .85
    add_child(probe)
    probe.global_position = PROBE_CENTER
    # Official once-update capture spans the following six frames. Appearance
    # still requires a native image; this wait is not a fabricated bake result.
    for step in range(9):
        await get_tree().process_frame
    set_meta("capture_request_completed", true)
    set_meta("public_capture_meshes", tagged_public_meshes)
    set_meta("private_exterior_receivers", tagged_private_exteriors)
    set_meta("probe_ambient_disabled", true)
    set_meta("private_room_interiors_excluded_from_capture", true)
    busy = false
    set_process(false)
