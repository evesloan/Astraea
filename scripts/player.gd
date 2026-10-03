extends CharacterBody3D
@export var spawn_position := Vector3(63.0,52.6,-20.5)
var camera: Camera3D
var pitch := 0.0
var interaction_target: Node
var interaction_requested := false

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
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_E:
		interaction_requested = true
	if event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	if event is InputEventMouseButton and event.pressed and event.button_index in [MOUSE_BUTTON_LEFT,MOUSE_BUTTON_RIGHT]:
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		rotate_y(-event.relative.x * 0.002)
		pitch = clampf(pitch - event.relative.y * 0.002, -1.35, 1.35)
		camera.rotation.x = pitch

func _physics_process(delta: float) -> void:
	var wish := Vector3.ZERO
	if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		wish.x = float(Input.is_physical_key_pressed(KEY_D)) - float(Input.is_physical_key_pressed(KEY_A))
		wish.z = float(Input.is_physical_key_pressed(KEY_S)) - float(Input.is_physical_key_pressed(KEY_W))
	wish = (basis * wish).normalized() * 3.1
	velocity.x = move_toward(velocity.x, wish.x, delta * 16.0)
	velocity.z = move_toward(velocity.z, wish.z, delta * 16.0)
	if not is_on_floor(): velocity.y -= 9.8 * delta
	else: velocity.y = 0.0
	move_and_slide()
	interaction_target = target_from_view() if Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT) else null
	if interaction_requested:
		if is_instance_valid(interaction_target): interaction_target.interact(self)
		interaction_requested = false
	camera.fov = lerpf(camera.fov, 58.0 if Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT) else 72.0, 1.0 - exp(-delta*10.0))
	if position.y < spawn_position.y - 7.0:
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
