extends Node3D
var controller:Node
var floor_index:=0
var persistent_id:StringName
func _ready() -> void:
	var area:=Area3D.new()
	area.collision_layer=2
	area.collision_mask=0
	area.monitoring=false
	area.monitorable=false
	var contact:=CollisionShape3D.new()
	var shape:=SphereShape3D.new()
	shape.radius=.065
	contact.shape=shape
	area.add_child(contact)
	add_child(area)
	var visual:=MeshInstance3D.new()
	var sphere:=SphereMesh.new()
	sphere.radius=.045
	sphere.height=.09
	sphere.radial_segments=8
	sphere.rings=4
	visual.mesh=sphere
	var mat:=StandardMaterial3D.new()
	mat.albedo_color=Color(.8,.68,.38)
	mat.emission_enabled=true
	mat.emission=Color(.25,.19,.08)
	visual.material_override=mat
	add_child(visual)
	var label:=Label3D.new()
	label.text=str(13+floor_index)
	label.font_size=32
	label.pixel_size=.003
	label.position=Vector3(0,.12,.015)
	label.modulate=Color(.94,.92,.85)
	add_child(label)
func get_interaction_label() -> String:
	return "E · Commons deck "+str(13+floor_index)
func interact(_actor:CharacterBody3D) -> void:
	controller.request_floor(floor_index)
