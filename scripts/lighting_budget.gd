extends Node
# Bound active shadow sources while retaining visible fixture geometry/emission.
# This is an initial cloud-tested budget, not target-GPU performance acceptance.
@export var shadow_source_budget := 8
var actor: Node3D
var sources: Array[Light3D] = []
var requested_shadow: Dictionary = {}
var elapsed := 0.0
func configure(ship: Node3D, player: Node3D) -> void:
	actor = player
	for light in ship.find_children("*","Light3D",true,false):
		sources.append(light)
		requested_shadow[light.get_instance_id()] = light.shadow_enabled
		if light.shadow_enabled: light.shadow_enabled = false
	refresh()
func _process(delta: float) -> void:
	elapsed += delta
	if elapsed >= 0.2:
		elapsed = 0
		refresh()
func refresh() -> void:
	if not is_instance_valid(actor): return
	var ranked: Array = []
	for light in sources:
		if not is_instance_valid(light): continue
		if not light.get_meta("fixture_powered",true):
			if light.visible: light.visible = false
			if light.shadow_enabled: light.shadow_enabled = false
			continue
		if not requested_shadow[light.get_instance_id()]: continue
		var reach: float = light.spot_range if light is SpotLight3D else (light.omni_range if light is OmniLight3D else 120.0)
		var distance := actor.global_position.distance_to(light.global_position)
		# Normalize for source reach; retain a small preference to avoid boundary flicker.
		var score := distance/maxf(reach,1.0)-(0.08 if light.visible else 0.0)
		ranked.append({"light":light,"score":score})
	ranked.sort_custom(func(a,b): return a.score < b.score)
	# Do not spend scarce shadow slots on fixtures behind occupied decks or walls.
	# Bounded candidate count keeps this visibility preference independent of ship size.
	for i in range(mini(24,ranked.size())):
		if not _has_visible_sample(ranked[i].light):ranked[i].score+=4.0
	for i in range(24,ranked.size()):ranked[i].score+=4.0
	ranked.sort_custom(func(a,b): return a.score < b.score)
	for i in range(ranked.size()):
		var light: Light3D = ranked[i].light
		# A shadowed fixture is never silently converted to a wall-leaking unshadowed lamp.
		var active := i < shadow_source_budget
		if light.visible != active: light.visible = active
		if light.shadow_enabled != active: light.shadow_enabled = active

func _has_visible_sample(light:Light3D) -> bool:
	for offset in [Vector3(0,1.5,0),Vector3(0,.4,0),Vector3(.65,1.0,0),Vector3(-.65,1.0,0)]:
		var query:=PhysicsRayQueryParameters3D.create(light.global_position,actor.global_position+offset)
		if actor is CollisionObject3D:query.exclude=[actor.get_rid()]
		var clear:=false
		for crossing in range(6):
			var hit:=light.get_world_3d().direct_space_state.intersect_ray(query)
			if hit.is_empty():
				clear=true
				break
			var body=hit.collider
			var transparent:bool=body is RigidBody3D or body is CharacterBody3D
			var owner_mesh:=body.get_parent()as MeshInstance3D
			if owner_mesh!=null:
				var material:Material=owner_mesh.get_active_material(0)
				if material is ShaderMaterial and material.shader!=null and "glass" in material.shader.resource_path:transparent=true
				elif material is StandardMaterial3D and material.transparency!=BaseMaterial3D.TRANSPARENCY_DISABLED:transparent=true
			if not transparent:break
			var excluded:=query.exclude
			excluded.append(body.get_rid())
			query.exclude=excluded
		if clear:return true
	return false
