extends SceneTree
const HERE="res://docs/manual_editor_handoff_20261020/"
func _initialize()->void:call_deferred("run")
func record_nodes(node:Node,scene:Node)->Dictionary:
	var result:Dictionary={}
	for child in node.find_children("*","",true,false):
		assert(child.owner==scene,"Every authored child must be saved")
		result[str(scene.get_path_to(child))]=child.get_class()
	return result
func run()->void:
	var packed:PackedScene=load(HERE+"ParcelRoom_R064_Authored.tscn")
	var scene:Node3D=packed.instantiate();root.add_child(scene)
	var before:Dictionary=record_nodes(scene,scene)
	assert(scene.get_meta("stable_room_id")=="R064")
	assert(scene.find_children("*","Light3D",true,false).size()==3)
	var ids:Array=[]
	for label in ["PublicDoors","WorkBayDoors","StockStreetDoors"]:
		var door:Node3D=scene.get_node(label)
		assert(door.panels.size()==4)
		assert(door.persistent_id==StringName("SHOP_D09_S72_A080__"+label))
		ids.append(str(door.persistent_id))
		assert(door.find_children("MovingPanel_*","AnimatableBody3D",true,false).size()==4)
	# Save an actual added mesh to a separate test-only scene and reopen it;
	# never mutate the final authored entry to conduct this check.
	var addition:=MeshInstance3D.new();addition.name="ManualPersistenceProbe"
	addition.mesh=BoxMesh.new();addition.position=Vector3(1.25,2.5,3.75)
	scene.get_node("ManualAdditions").add_child(addition);addition.owner=scene
	var test:=PackedScene.new();assert(test.pack(scene)==OK)
	assert(ResourceSaver.save(test,HERE+"persistence_probe_test_only.tscn",ResourceSaver.FLAG_BUNDLE_RESOURCES)==OK)
	var reopened:Node3D=load(HERE+"persistence_probe_test_only.tscn").instantiate();root.add_child(reopened)
	var probe:MeshInstance3D=reopened.get_node("ManualAdditions/ManualPersistenceProbe")
	assert(probe.position==Vector3(1.25,2.5,3.75) and probe.mesh is BoxMesh)
	assert(reopened.get_node("PublicDoors").panels.size()==4)
	var after:Dictionary=record_nodes(reopened,reopened)
	assert(after.size()==before.size()+1,"Reload must not regenerate duplicate door geometry")
	for path in before:assert(after.has(path) and after[path]==before[path])
	var report={"saved_node_count":before.size(),"door_physical_ids":ids,"source_lights":3,"added_mesh_save_reopen":true,"reopen_preserves_node_paths_and_types":true,"duplicate_geometry_on_ready":false,"whole_ship_run":false,"visual_acceptance":false,"operational_acceptance":false}
	var f:=FileAccess.open(HERE+"ASSEMBLED_SCENE_CHECKS.json",FileAccess.WRITE);f.store_string(JSON.stringify(report,"\t")+"\n");f.close()
	print("PARCEL_AUTHORED_CHECKS ",JSON.stringify(report))
	reopened.free();scene.free();quit()
