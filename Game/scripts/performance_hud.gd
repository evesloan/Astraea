extends Label
# F9 toggles live measurements. Headless/fixed-step results are not GPU FPS.
var elapsed:=0.0
var samples:Array[float]=[]
var enabled:=false
func _ready()->void:
	position=Vector2(18,150)
	add_theme_font_size_override("font_size",16)
	mouse_filter=Control.MOUSE_FILTER_IGNORE
	visible=false
func _unhandled_input(event:InputEvent)->void:
	if event is InputEventKey and event.pressed and not event.echo and event.keycode==KEY_F9:
		enabled=not enabled
		visible=enabled
func _process(delta:float)->void:
	if not enabled:return
	elapsed+=delta
	samples.append(delta*1000.0)
	if elapsed<.5:return
	elapsed=0.0
	var ordered:=samples.duplicate()
	ordered.sort()
	var p95:float=ordered[mini(ordered.size()-1,int(ordered.size()*.95))]
	text="PERFORMANCE · F9 hide\n%d FPS · frame p95 %.1f ms\nProcess %.1f ms · physics %.1f ms\nDraw calls %d · primitives %d\nResident nodes %d · objects %d\nStatic memory %.0f MB"%[Engine.get_frames_per_second(),p95,Performance.get_monitor(Performance.TIME_PROCESS)*1000.0,Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS)*1000.0,Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME),Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME),get_tree().get_node_count(),Performance.get_monitor(Performance.OBJECT_COUNT),Performance.get_monitor(Performance.MEMORY_STATIC)/1048576.0]
	samples.clear()
