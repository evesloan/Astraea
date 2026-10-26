extends SceneTree
const POOL=preload("res://visible_resource_budget_20261026/exact_contact_pool.gd")
func _initialize()->void:call_deferred("run")
func run()->void:
 var mesh:=BoxMesh.new()
 var shape:=POOL.intern(mesh.get_faces())
 print("after_intern ",POOL.entries.size()," margin ",shape.margin)
 shape.changed.connect(func()->void:print("changed shape margin ",shape.margin," faces ",shape.get_faces().size()))
 var body:=StaticBody3D.new();root.add_child(body)
 var col:=CollisionShape3D.new();col.shape=shape
 print("after_assignment ",POOL.entries.size()," margin ",shape.margin)
 body.add_child(col)
 print("after_child ",POOL.entries.size()," margin ",shape.margin)
 await process_frame
 print("after_frame ",POOL.entries.size()," margin ",shape.margin)
 body.free();quit()
