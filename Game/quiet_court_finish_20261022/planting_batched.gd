extends RefCounted
const P:="res://quiet_court_finish_20261022/"
static func build()->Node3D:
	var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PLAN_R003.json"))
	var templates:={}
	for source in plan.sources:
		var path:String="res://assets/models/"+str(source.catalogue_id)+".glb"
		assert(FileAccess.get_sha256(path)==source.export_sha256)
		templates[source.catalogue_id]=load(path) as PackedScene
	var root:=Node3D.new();root.name="QuietCourtPlantedBeds20261022"
	for row in plan.placements:
		var instance:=Node3D.new();instance.name=row.name;root.add_child(instance)
		instance.position=Vector3(row.position[0],row.position[1],row.position[2]);instance.rotation.y=row.yaw;instance.scale=Vector3.ONE*float(row.scale)
		instance.set_meta("retained_catalogue_id",row.catalogue_id);instance.set_meta("receiving_bed",row.receiving_bed)
		var visual:Node3D=templates[row.catalogue_id].instantiate();instance.add_child(visual)
		assert(visual.find_children("*","CollisionObject3D",true,false).is_empty())
		assert(visual.find_children("*","MeshInstance3D",true,false).size()==(4 if row.catalogue_id=="AST-BOT-008" else 5))
	return root
