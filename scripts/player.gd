extends CharacterBody3D
@export var spawn_position := Vector3(63.0,52.6,-20.5)
var camera: Camera3D
var pitch := 0.0

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
	if event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
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
	camera.fov = lerpf(camera.fov, 58.0 if Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT) else 72.0, 1.0 - exp(-delta*10.0))
	if position.y < spawn_position.y - 7.0:
		position = spawn_position
		velocity = Vector3.ZERO
