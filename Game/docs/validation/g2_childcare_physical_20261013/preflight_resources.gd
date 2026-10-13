extends SceneTree
func _initialize()->void:
 assert(ProjectSettings.load_resource_pack("/workspace/astraea-integration-cutoff-20261013/g2_childcare_physical_receiving/CANDIDATE_OVERLAY.zip",true));call_deferred("run")
func run()->void:
 var script:Script=load("res://scripts/group2_family_childcare/package.gd");assert(script!=null and script.can_instantiate())
 var world:=Node3D.new();root.add_child(world)
 for path in ["res://assets/group2_family_childcare/FAMILY_CHILDCARE_r001.glb","res://assets/models/AST-DOR-002_wide.glb"]:
  var visual:Node3D=(load(path)as PackedScene).instantiate();world.add_child(visual);load("res://scripts/static_contact_cache.gd").attach_group(visual,visual.find_children("*","MeshInstance3D",true,false));var expected:Array[Vector3]=[]
  for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
   var contact:CollisionShape3D=mesh.get_node_or_null("StaticContact/SharedShape")
   if contact!=null:assert(not contact.disabled and contact.shape.get_faces()==mesh.mesh.get_faces())
   else:
    var pose:Transform3D=visual.global_transform.affine_inverse()*mesh.global_transform
    for vertex in mesh.mesh.get_faces():expected.append(pose*vertex)
  var combined:CollisionShape3D=visual.get_node("RoomStaticContacts/SharedRoomTriangles");assert(not combined.disabled and combined.shape.get_faces()==PackedVector3Array(expected))
  if path.ends_with("AST-DOR-002_wide.glb"):assert(visual.find_child("LEAF_LEFT",true,false).position.is_equal_approx(Vector3(-.6,0,0))and visual.find_child("LEAF_RIGHT",true,false).position.is_equal_approx(Vector3(.6,0,0)))
 print("CHILDCARE_PHYSICAL_RESOURCE_PREFLIGHT_PASS");quit(0)
