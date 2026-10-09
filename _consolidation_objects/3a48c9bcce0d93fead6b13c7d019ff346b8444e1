extends SceneTree
class InteractionProbe extends StaticBody3D:
	var activations:=0
	func interact(_actor):activations+=1
	func get_interaction_label():return "Probe"
var player: CharacterBody3D
var checks: Array=[]
func _initialize():call_deferred("run")
func key(code:Key, down:bool, echo:bool=false):
	var e=InputEventKey.new();e.keycode=code;e.physical_keycode=code;e.pressed=down;e.echo=echo
	Input.parse_input_event(e);Input.flush_buffered_events()
func focus(down:bool):
	var e=InputEventMouseButton.new();e.button_index=MOUSE_BUTTON_RIGHT;e.pressed=down
	Input.parse_input_event(e);Input.flush_buffered_events()
func frames(n:int):
	for i in range(n):await physics_frame
func check(ok:bool,label:String):
	checks.append({"check":label,"passed":ok})
	if not ok:push_error(label)
func run():
	var world=Node3D.new();root.add_child(world)
	var floor=StaticBody3D.new();var shape=CollisionShape3D.new();var box=BoxShape3D.new();box.size=Vector3(30,1,30);shape.shape=box;floor.add_child(shape);floor.position.y=-.5;world.add_child(floor)
	player=load("res://scripts/player.gd").new();world.add_child(player)
	await frames(30);check(player.is_on_floor(),"grounded start")
	key(KEY_SPACE,true);await frames(1);key(KEY_SPACE,false);await frames(5)
	check(player.position.y>.1 and player.velocity.y>0,"Space initiates grounded jump")
	var before=player.velocity.y;key(KEY_SPACE,true);await frames(2);key(KEY_SPACE,false)
	check(player.velocity.y<before,"airborne Space does not double jump")
	await frames(90);check(player.is_on_floor() and abs(player.position.y)<.02,"jump lands without recovery")
	key(KEY_SPACE,true,true);await frames(5);key(KEY_SPACE,false);check(player.is_on_floor(),"key repeat does not trigger jump")
	player.set_controls_enabled(false);key(KEY_SPACE,true);await frames(5);key(KEY_SPACE,false);check(player.is_on_floor(),"disabled controls reject jump")
	player.set_controls_enabled(true)
	for code in [KEY_W,KEY_A,KEY_S,KEY_D]:
		var start=player.position;key(code,true);await frames(20);key(code,false);await frames(12);check(player.position.distance_to(start)>.4,"walk key "+str(code))
	var target=InteractionProbe.new();var target_shape=CollisionShape3D.new();var target_box=BoxShape3D.new();target_box.size=Vector3(.5,.5,.2);target_shape.shape=target_box;target.add_child(target_shape);world.add_child(target);target.global_position=player.camera.global_position+Vector3(0,0,-1)
	focus(true);await frames(30);check(player.camera.fov<59,"RMB focuses camera")
	key(KEY_E,true);await frames(2);key(KEY_E,false);check(target.activations==1,"RMB plus E activates aimed interaction after jumping")
	focus(false);await frames(30);check(player.camera.fov>71,"release restores camera")
	var ok=true
	for c in checks:ok=ok and c.passed
	var f=FileAccess.open("res://artifacts/player_delivery_controls.json",FileAccess.WRITE);f.store_string(JSON.stringify({"status":"PASS" if ok else "FAIL","checks":checks,"player_sha256":FileAccess.get_sha256("res://scripts/player.gd"),"scope":"Actual production controller in bounded physics fixture; does not certify whole ship traversal, carts, elevator interactions or Windows hardware."},"  "));f.close()
	print("PLAYER DELIVERY CONTROLS ","PASS" if ok else "FAIL");quit(0 if ok else 1)
