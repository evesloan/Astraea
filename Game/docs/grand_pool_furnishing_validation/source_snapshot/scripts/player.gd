extends CharacterBody3D
@export var spawn_position := Vector3(63.0,52.6,-20.5)
# Recovery is below the lowest ship deck (D01 = 0), independent of the selected spawn deck.
@export var fall_recovery_y := -7.0
var camera: Camera3D
var pitch := 0.0
var interaction_target: Node
var interaction_requested := false
var held_interaction:Node
var gameplay_input_enabled:=true

func _ready() -> void:
	name = "Player"
	var shape := CapsuleShape3D.new()
	shape.radius = 0.3
	shape.height = 1.8
	var collider := CollisionShape3D.new()
	collider.shape = shape
	collider.position.y = 0.9
	add_child(collider)
	camera = Camera3D.new()
	camera.position.y = 1.65
	camera.fov = 72.0
	camera.far = 1600.0
	add_child(camera)
	camera.current = true
	set_controls_enabled(true)

func set_controls_enabled(enabled:bool) -> void:
	gameplay_input_enabled=enabled
	Input.mouse_mode=Input.MOUSE_MODE_CAPTURED if enabled else Input.MOUSE_MODE_VISIBLE
	if not enabled:
		interaction_requested=false
		if is_instance_valid(held_interaction):held_interaction.interact(self)

func _unhandled_input(event: InputEvent) -> void:
	if gameplay_input_enabled and event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_E:
		interaction_requested = true
	if event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
		set_controls_enabled(false)
	if event is InputEventMouseButton and event.pressed and event.button_index in [MOUSE_BUTTON_LEFT,MOUSE_BUTTON_RIGHT]:
		set_controls_enabled(true)
	if event is InputEventMouseMotion and gameplay_input_enabled:
		rotate_y(-event.relative.x * 0.002)
		pitch = clampf(pitch - event.relative.y * 0.002, -1.35, 1.35)
		camera.rotation.x = pitch

func _physics_process(delta: float) -> void:
	var wish := Vector3.ZERO
	if gameplay_input_enabled:
		wish.x = float(Input.is_physical_key_pressed(KEY_D)) - float(Input.is_physical_key_pressed(KEY_A))
		wish.z = float(Input.is_physical_key_pressed(KEY_S)) - float(Input.is_physical_key_pressed(KEY_W))
	var speed:=2.0 if is_instance_valid(held_interaction) and held_interaction.is_in_group("cart_handles") else 3.1
	wish = (basis * wish).normalized() * speed
	velocity.x = move_toward(velocity.x, wish.x, delta * 16.0)
	velocity.z = move_toward(velocity.z, wish.z, delta * 16.0)
	if not is_on_floor(): velocity.y -= 9.8 * delta
	else: velocity.y = 0.0
	move_and_slide()
	interaction_target = (held_interaction if is_instance_valid(held_interaction) else target_from_view()) if gameplay_input_enabled and Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT) else null
	if interaction_requested:
		if Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT) and is_instance_valid(held_interaction): held_interaction.interact(self)
		elif is_instance_valid(interaction_target): interaction_target.interact(self)
		interaction_requested = false
	camera.fov = lerpf(camera.fov, 58.0 if Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT) else 72.0, 1.0 - exp(-delta*10.0))
	if position.y < fall_recovery_y:
		position = spawn_position
		velocity = Vector3.ZERO

func target_from_view() -> Node:
	var start := camera.global_position
	var query := PhysicsRayQueryParameters3D.create(start,start-camera.global_basis.z*2.5)
	query.exclude = [get_rid()]
	query.collide_with_areas = true
	var hit := get_world_3d().direct_space_state.intersect_ray(query)
	if hit.is_empty(): return null
	var candidate: Node = hit.collider
	while candidate != null:
		if candidate.has_method("interact") and candidate.has_method("get_interaction_label"): return candidate
		candidate = candidate.get_parent()
	return null
