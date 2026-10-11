extends Node
# Bound active shadow sources while retaining visible fixture geometry/emission.
# This is an initial cloud-tested budget, not target-GPU performance acceptance.
@export var shadow_source_budget := 8
const MAX_VISIBILITY_CANDIDATES := 32
var actor: Node3D
var sources: Array[Light3D] = []
var requested_shadow: Dictionary = {}
var elapsed := 0.0
var previously_active: Array[Light3D] = []
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
		if not is_instance_valid(light) or not light.is_inside_tree(): continue
		if not light.get_meta("fixture_powered",true):
			if light.visible: light.visible = false
			if light.shadow_enabled: light.shadow_enabled = false
			continue
		if not requested_shadow[light.get_instance_id()]: continue
		var reach: float = light.spot_range if light is SpotLight3D else (light.omni_range if light is OmniLight3D else 120.0)
		var distance := actor.global_position.distance_to(light.global_position)
		# Normalize for source reach; retain a small preference to avoid boundary flicker.
		var score := distance/maxf(reach,1.0)-(0.08 if light.visible else 0.0)
		# Keep only the nearest visibility candidates; avoid sorting every ship light.
		if ranked.size() == MAX_VISIBILITY_CANDIDATES and score >= float(ranked[-1].score): continue
		var insert_at := ranked.size()
		while insert_at > 0 and score < float(ranked[insert_at-1].score): insert_at -= 1
		ranked.insert(insert_at,{"light":light,"score":score})
		if ranked.size() > MAX_VISIBILITY_CANDIDATES: ranked.pop_back()
	for old in previously_active:
		if not is_instance_valid(old): continue
		var retained := false
		for row in ranked:
			if row.light == old:
				retained = true
				break
		if not retained:
			old.visible = false
			old.shadow_enabled = false
	previously_active.clear()
	# Visibility is required, not a penalty: hidden/untested sources cannot fill slots.
	# Eight extra candidates avoid newly fitted decks starving nearby room fixtures.
	# Stop once the budget is full; visibility work stays independent of ship size.
	var active_sources := 0
	for i in range(ranked.size()):
		var light: Light3D = ranked[i].light
		# A shadowed fixture is never silently converted to a wall-leaking unshadowed lamp.
		var active := i < MAX_VISIBILITY_CANDIDATES and active_sources < shadow_source_budget and _has_visible_sample(light)
		if active:
			active_sources += 1
			previously_active.append(light)
		if light.visible != active: light.visible = active
		if light.shadow_enabled != active: light.shadow_enabled = active

func _has_visible_sample(light:Light3D) -> bool:
	var origins:Array[Vector3]=[light.global_position]
	# A wallwasher may face away from the viewer while its illuminated relief is
	# plainly visible. Admit one authored receiver only when the real cone reaches
	# it unobstructed; this does not enlarge the eight-shadow-source budget.
	var receiver=light.get_meta("illumination_anchor") if light.has_meta("illumination_anchor") else null
	if receiver is Vector3 and light is SpotLight3D:
		var delta:Vector3=receiver-light.global_position
		if delta.length()<light.spot_range and delta.normalized().dot(-light.global_basis.z)>=cos(deg_to_rad(light.spot_angle)):
			if _clear_sample(light.global_position,receiver):origins.append(receiver)
	for origin in origins:
		for offset in [Vector3(0,1.5,0),Vector3(0,.4,0),Vector3(.65,1.0,0),Vector3(-.65,1.0,0)]:
			if _clear_sample(origin,actor.global_position+offset):return true
	return false

func _clear_sample(start:Vector3,end:Vector3) -> bool:
	var query:=PhysicsRayQueryParameters3D.create(start,end)
	if actor is CollisionObject3D:query.exclude=[actor.get_rid()]
	for crossing in range(6):
		var hit:=actor.get_world_3d().direct_space_state.intersect_ray(query)
		if hit.is_empty():return true
		var body=hit.collider
		var transparent:bool=body is RigidBody3D or body is CharacterBody3D
		var owner_mesh:=body.get_parent()as MeshInstance3D
		if owner_mesh!=null:
			var material:Material=owner_mesh.get_active_material(0)
			if material is ShaderMaterial and material.shader!=null and "glass" in material.shader.resource_path:transparent=true
			elif material is StandardMaterial3D and material.transparency!=BaseMaterial3D.TRANSPARENCY_DISABLED:transparent=true
		if not transparent:return false
		var excluded:=query.exclude
		excluded.append(body.get_rid())
		query.exclude=excluded
	return false
