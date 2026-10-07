extends SceneTree
func arr(v: Vector3) -> Array:return [v.x,v.y,v.z]
func basis_array(b: Basis) -> Array:return [arr(b.x),arr(b.y),arr(b.z)]
func _initialize() -> void:call_deferred("run")
func run() -> void:
	var out:=OS.get_environment("ASTRAEA_STOCK_SCALE_OBSERVATION")
	assert(not out.is_empty() and not FileAccess.file_exists(out))
	var data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/GRAND_POOL_EAST_GALLERY_RUNTIME.json"))
	# Unparented ship instance supplies the exact existing model() method without _ready.
	var ship: Node3D=load("res://scripts/ship.gd").new()
	var parent:=Node3D.new();parent.name="ReadOnlyStockObservation";root.add_child(parent)
	var rows: Array=[]
	for entry in data.receiving_stock:
		var spec: Dictionary=data.models[str(entry.asset)];var p: Array=entry.position_xyz
		assert(FileAccess.get_sha256("res://assets/models/"+str(spec.file))==str(spec.sha256))
		var item: Node3D=ship.model(parent,str(spec.file),str(entry.name),Vector3(p[0],p[1],p[2]),float(entry.yaw_radians))
		var expected_basis:=Basis.from_euler(Vector3(0,float(entry.yaw_radians),0))
		var expected_transform:=Transform3D(expected_basis,Vector3(p[0],p[1],p[2]))
		var visual:=item.get_child(0) as Node3D
		var row: Dictionary={"name":entry.name,"asset":entry.asset,"file_sha256":spec.sha256,"source_declared_scale":entry.scale_xyz,"scale_component_types":[typeof(entry.scale_xyz[0]),typeof(entry.scale_xyz[1]),typeof(entry.scale_xyz[2])],"literal_integer_component_type":typeof(1),"array_equal_to_integer_literals":entry.scale_xyz==[1,1,1],"numeric_components_equal_one":float(entry.scale_xyz[0])==1.0 and float(entry.scale_xyz[1])==1.0 and float(entry.scale_xyz[2])==1.0,"actual_wrapper_scale":arr(item.scale),"wrapper_scale_exact_one":item.scale==Vector3.ONE,"actual_wrapper_basis":basis_array(item.basis),"expected_same_euler_basis":basis_array(expected_basis),"exact_expected_rigid_transform":item.transform==expected_transform,"actual_wrapper_rotation":arr(item.rotation),"authored_yaw":entry.yaw_radians,"native_visual_root_scale":arr(visual.scale),"native_visual_root_transform":{"basis":basis_array(visual.basis),"origin":arr(visual.position)},"mesh_count":visual.find_children("*","MeshInstance3D",true,false).size(),"no_scale_assignment_performed":true}
		rows.append(row);print("STOCK_SCALE_OBSERVATION ",JSON.stringify(row))
	var report: Dictionary={"status":"OBSERVATION_ONLY_NO_GAME_WRITES","contract_sha256":FileAccess.get_sha256("res://data/architecture/GRAND_POOL_EAST_GALLERY_RUNTIME.json"),"same_existing_model_path":true,"full_ship_instantiated":false,"rows":rows}
	var file:=FileAccess.open(out,FileAccess.WRITE);assert(file!=null);file.store_string(JSON.stringify(report,"  ",true,true));file.close()
	parent.queue_free();ship.free();await process_frame;quit(0)
