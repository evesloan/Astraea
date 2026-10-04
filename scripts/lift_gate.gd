extends Node3D
# A controller-owned landing gate. It intentionally exposes no interact() method:
# only the lift interlock can authorize opening at a present, stationary cabin.
var persistent_id:StringName
var leaves:Array[AnimatableBody3D]=[]
var origins:Array[Vector3]=[]
var travels:Array[float]=[]
var open_fraction:=0.0
var requested_open:=false
var cabin_present_and_stopped:=false
var obstructed:=false

func _ready() -> void:
	set_meta("catalogue_file","AST-DOR-003.glb")
	var visual:Node3D=(load("res://assets/models/AST-DOR-003.glb")as PackedScene).instantiate()
	add_child(visual)
	var glass:=ShaderMaterial.new()
	glass.shader=load("res://shaders/hospitality_glass.gdshader")
	for side in ["LEFT","RIGHT"]:
		for rank in ["INNER","OUTER"]:
			var source:=visual.find_child("LEAF_"+side+"_"+rank,true,false)as Node3D
			assert(source!=null)
			var body:=AnimatableBody3D.new()
			body.name="GateLeaf_"+side+"_"+rank
			body.sync_to_physics=false
			body.transform=global_transform.affine_inverse()*source.global_transform
			add_child(body)
			source.reparent(body,true)
			source.transform=Transform3D.IDENTITY
			var contact:=CollisionShape3D.new()
			var shape:=BoxShape3D.new()
			shape.size=Vector3(.595 if rank=="INNER" else .615,2.60,.016)
			shape.margin=.001
			contact.shape=shape
			contact.position=Vector3(0,1.33,0)
			body.add_child(contact)
			leaves.append(body)
			origins.append(body.position)
			travels.append((-1.0 if side=="LEFT" else 1.0)*(1.21 if rank=="INNER" else .61))
			for mesh in source.find_children("*","MeshInstance3D",true,false):
				if "glass" in mesh.name:mesh.material_override=glass
			body.sync_to_physics=true
	for mesh in visual.find_children("*","MeshInstance3D",true,false):
		load("res://scripts/static_contact_cache.gd").attach(mesh)

func request_open() -> bool:
	if not cabin_present_and_stopped:return false
	requested_open=true
	return true

func request_close() -> void:
	requested_open=false

func is_closed_and_clear() -> bool:
	return open_fraction<=.0001 and not threshold_occupied()

func threshold_occupied() -> bool:
	var shape:=BoxShape3D.new()
	shape.size=Vector3(3.82,2.67,.40)
	var query:=PhysicsShapeQueryParameters3D.new()
	query.shape=shape
	query.transform=global_transform*Transform3D(Basis.IDENTITY,Vector3(0,1.335,0))
	for hit in get_world_3d().direct_space_state.intersect_shape(query,64):
		if hit.collider is CharacterBody3D or hit.collider is RigidBody3D:return true
	return false

func _physics_process(delta:float) -> void:
	var target:=1.0 if requested_open and cabin_present_and_stopped else 0.0
	if is_equal_approx(open_fraction,target):return
	obstructed=threshold_occupied()
	if obstructed:return
	open_fraction=move_toward(open_fraction,target,delta*.75)
	for i in range(leaves.size()):
		leaves[i].position=origins[i]+Vector3(travels[i]*open_fraction,0,0)
