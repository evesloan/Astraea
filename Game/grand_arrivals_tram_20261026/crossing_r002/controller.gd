extends Node3D
# Local physical crossing only. Never owns the tram, player, cart or input.
const MODEL:="res://grand_arrivals_tram_20261026/crossing_r002/ForwardCrossing.glb"
const SHA:="e5d429a969888cfe85bb3390c6286e5b15043d379b07a943604461a6f89e21f3"
var panels:Array[AnimatableBody3D]=[]
var fraction:=1.0
var reserved:=false
var obstructed:=false
var sensor_saturated:=false
var payload_exclusions:Array[RID]=[]
func _ready()->void:
	assert(FileAccess.get_sha256(MODEL)==SHA)
	process_physics_priority=-40
	var document:=GLTFDocument.new();var state:=GLTFState.new()
	assert(document.append_from_file(ProjectSettings.globalize_path(MODEL),state)==OK)
	var visual:Node3D=document.generate_scene(state);add_child(visual)
	for side:String in ["West","East"]:
		var panel:=AnimatableBody3D.new();panel.name="CrossingPanel_"+side;panel.sync_to_physics=false;add_child(panel)
		for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
			if str(mesh.name).begins_with("Crossing_"+side+"_Moving"):mesh.reparent(panel,true)
		var shape:=BoxShape3D.new();shape.size=Vector3(.08,2.60,4.0);shape.margin=.001
		var col:=CollisionShape3D.new();col.shape=shape;col.position=Vector3(3.56 if side=="West" else 7.5,1.32,-432);panel.add_child(col)
		panel.position.y=2.98;panel.sync_to_physics=true;panels.append(panel)
	for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):mesh.create_trimesh_collision()
	set_meta("persistent_id","forward_arrivals_public_crossing_001")
	set_meta("production_admitted",false)
func occupied()->bool:
	var shape:=BoxShape3D.new();shape.size=Vector3(5.0,5.70,4.4)
	var query:=PhysicsShapeQueryParameters3D.new();query.shape=shape;query.transform=global_transform*Transform3D(Basis.IDENTITY,Vector3(5.65,2.85,-432));query.exclude=payload_exclusions
	var hits:=get_world_3d().direct_space_state.intersect_shape(query,256)
	sensor_saturated=hits.size()>=256
	if sensor_saturated:return true # Never interpret truncated occupancy as clear.
	for hit:Dictionary in hits:
		if hit.collider is CharacterBody3D or hit.collider is RigidBody3D:return true
	return false
func request_lock()->bool:
	reserved=true
	return closed_and_clear()
func closed_and_clear()->bool:
	return panels.size()==2 and fraction<=.0001 and not occupied()
func request_release(vehicle_clear:bool)->bool:
	if not vehicle_clear:return false
	reserved=false;return true
func _physics_process(delta:float)->void:
	var target:=0.0 if reserved else 1.0
	if is_equal_approx(target,fraction):return
	obstructed=occupied()
	if obstructed:return
	fraction=move_toward(fraction,target,delta*.6)
	for panel:AnimatableBody3D in panels:panel.position.y=fraction*2.98
