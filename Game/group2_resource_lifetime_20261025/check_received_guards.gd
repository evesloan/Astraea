extends SceneTree
const LEASE=preload("res://group2_resource_lifetime_20261025/mesh_lease.gd")
const DISPATCH=preload("res://scripts/received_homes_20261015/source_dispatch.gd")
func _initialize()->void:call_deferred("run")
func run()->void:
	var host:=Node3D.new();root.add_child(host)
	var room:=Node3D.new();host.add_child(room)
	var path:="res://assets/models/SOL_D02_directory_09_source001.glb"
	var packed:PackedScene=load(path);var visual:Node3D=packed.instantiate();room.add_child(visual)
	assert(LEASE.bind(room,visual,packed,path,true));packed=null
	room.set_meta("source_mesh_lease_host",weakref(host))
	var lease:Dictionary=room.get_meta("group2_mesh_lease")
	var first:MeshInstance3D=lease.rows[0].node.get_ref()
	var second:MeshInstance3D=lease.rows[1].node.get_ref()
	var third:MeshInstance3D=lease.rows[2].node.get_ref()
	var first_id:int=first.mesh.get_instance_id()
	var live_rejected:bool=LEASE.suspend(room)==0 and first.mesh.get_instance_id()==first_id
	var changed_bounds:AABB=first.mesh.get_aabb().grow(.125)
	first.mesh.custom_aabb=changed_bounds
	var box:=BoxMesh.new();second.mesh=box
	var material:Material=third.mesh.surface_get_material(0)
	host.remove_child(room)
	DISPATCH.release(room)
	var construction_held:bool=third.mesh!=null
	host.set_meta("runtime_ready",true);DISPATCH.release(room)
	var dirty_preserved:bool=first.mesh!=null and first.mesh.get_instance_id()==first_id and first.mesh.custom_aabb==changed_bounds
	var replacement_preserved:bool=second.mesh==box
	var unchanged_released:bool=third.mesh==null
	var sha:String=lease.sha256;lease.sha256="negative-control"
	var mismatch_rejected:bool=not LEASE.resume(room) and third.mesh==null
	lease.sha256=sha
	var restored:bool=LEASE.resume(room) and third.mesh!=null and third.mesh.surface_get_material(0)==material and first.mesh.get_instance_id()==first_id and second.mesh==box
	var result:={"live_release_rejected":live_rejected,"construction_held":construction_held,"in_place_changed_mesh_preserved":dirty_preserved,"replacement_preserved":replacement_preserved,"unchanged_released":unchanged_released,"source_mismatch_rejected_before_writes":mismatch_rejected,"restored_same_material_and_edited_meshes":restored,"expected_error_messages":2}
	print("RECEIVED_GUARDS ",JSON.stringify(result));room.free();host.free()
	quit(0 if live_rejected and construction_held and dirty_preserved and replacement_preserved and unchanged_released and mismatch_rejected and restored else 1)
