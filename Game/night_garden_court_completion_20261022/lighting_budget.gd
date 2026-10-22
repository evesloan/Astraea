extends "res://scripts/lighting_budget.gd"
const PRIVATE_PANE:="res://night_garden_view_galleries_20261022/private_view.gdshader"
func configure(ship:Node3D,player:Node3D)->void:
	assert(FileAccess.get_sha256(PRIVATE_PANE)=="667540952dbd7be555c1f63aca3009f3db2ef2f599b80bc52dfc4aa5924c5923")
	super.configure(ship,player)
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
			if material is ShaderMaterial and material.shader!=null:
				if "glass" in material.shader.resource_path:transparent=true
				elif material.shader.resource_path==PRIVATE_PANE:
					transparent=(actor.global_position.x-float(material.get_shader_parameter("plane_x")))*float(material.get_shader_parameter("interior_sign"))>0.0
			elif material is StandardMaterial3D and material.transparency!=BaseMaterial3D.TRANSPARENCY_DISABLED:transparent=true
		if not transparent:return false
		var excluded:=query.exclude
		excluded.append(body.get_rid())
		query.exclude=excluded
	return false
