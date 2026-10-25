extends SceneTree
const LEASE=preload("res://group2_resource_lifetime_20261025/mesh_lease.gd")
func _initialize()->void:call_deferred("run")
func run()->void:
	var room:=Node3D.new();root.add_child(room)
	var source:Node3D=load("res://scripts/group2_completion/package.gd").build_section(room,"780")
	var lease:Dictionary=source.get_meta("group2_mesh_lease")
	var first:MeshInstance3D=lease.rows[0].node.get_ref()
	var original_id:=first.mesh.get_instance_id()
	var live_rejected:bool=LEASE.suspend(source)==0 and first.mesh.get_instance_id()==original_id
	root.remove_child(room)
	LEASE.suspend(source)
	var expected:String=lease.sha256
	lease.sha256="intentional-negative-control"
	var mismatch_rejected:bool=not LEASE.resume(source)
	var untouched:=true
	for row:Dictionary in lease.rows:
		var node:MeshInstance3D=row.node.get_ref()
		if node.mesh!=null:untouched=false
	lease.sha256=expected
	var restored:bool=LEASE.resume(source)
	var replacement:=BoxMesh.new()
	first.mesh=replacement
	LEASE.suspend(source)
	var replacement_preserved:bool=first.mesh==replacement
	var second_restore:bool=LEASE.resume(source)
	replacement_preserved=replacement_preserved and first.mesh==replacement
	var result:={"live_release_rejected":live_rejected,"changed_source_rejected_before_restoration":mismatch_rejected and untouched,"exact_source_restored":restored,"independent_replacement_preserved":replacement_preserved and second_restore,"expected_error_messages":2}
	print("GROUP2_GUARDS ",JSON.stringify(result))
	room.free()
	quit(0 if live_rejected and mismatch_rejected and untouched and restored and replacement_preserved and second_restore else 1)
