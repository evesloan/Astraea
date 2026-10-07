extends RefCounted
# Eight existing stock models, physically supported by the retained furniture.
static func build(parent: Node3D, ship: Node3D, data: Dictionary) -> void:
	assert(data.receiving_stock.size() == 8 and parent.get_child_count() == 2)
	var root := Node3D.new()
	root.name = "ReceivingStock"
	parent.add_child(root)
	for entry in data.receiving_stock:
		var spec: Dictionary = data.models[str(entry.asset)]
		assert(spec.existing_retained_runtime_model and spec.original_scale)
		assert(FileAccess.get_sha256("res://assets/models/"+str(spec.file)) == str(spec.sha256))
		var p: Array = entry.position_xyz
		var item: Node3D = ship.model(root,str(spec.file),str(entry.name),Vector3(p[0],p[1],p[2]),float(entry.yaw_radians))
		assert(item.scale == Vector3.ONE and entry.scale_xyz == [1.0,1.0,1.0])
		assert(item.transform == Transform3D(Basis.from_euler(Vector3(0,float(entry.yaw_radians),0)),Vector3(p[0],p[1],p[2])), "Stock must retain its exact source-authored rigid transform")
		item.set_meta("placement_support",entry.support_instance)
		item.set_meta("parent_design_id",entry.asset)
		item.set_meta("source_assembly_sha256",data.source_sha256)
		item.set_meta("static_display_only",true)
	assert(root.get_child_count() == 8)
