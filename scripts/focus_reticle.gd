extends Node2D
func _draw() -> void:
	var centre := Vector2(get_viewport_rect().size*0.5).floor()
	var unit := maxf(1.0,roundf(get_viewport_rect().size.x/640.0))
	var offsets := [Vector2.ZERO,Vector2(-2,0),Vector2(2,0),Vector2(0,-2),Vector2(0,2)]
	for offset in offsets:
		draw_rect(Rect2(centre+(offset-Vector2.ONE)*unit,Vector2(3,3)*unit),Color(0.04,0.06,0.07,0.85))
	for offset in offsets:
		draw_rect(Rect2(centre+offset*unit,Vector2.ONE*unit),Color(0.88,0.95,0.93))
