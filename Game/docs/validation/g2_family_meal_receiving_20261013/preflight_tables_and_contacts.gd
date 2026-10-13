extends SceneTree
func _initialize()->void:
 assert(ProjectSettings.load_resource_pack("/workspace/astraea-integration-cutoff-20261013/g2_family_meal_receiving/CANDIDATE_OVERLAY.zip",true))
 call_deferred("run")
func run()->void:
 var ship:=Node3D.new();root.add_child(ship);var space:=Node3D.new();space.name="ShipSpace";ship.add_child(space);var districts:=Node3D.new();districts.name="Districts";space.add_child(districts);var house:=Node3D.new();house.name="FamilyTerraceReceivingCandidate";districts.add_child(house)
 house.add_child((load("res://assets/models/FAMILY_TERRACE_ARCHITECTURE_lift_r003.glb")as PackedScene).instantiate())
 var added:Node3D=load("res://scripts/group2_family_meal/package.gd").build_on_current_receiver(ship);var kit:Node3D=added.get_child(0);var expected:Array[Vector3]=[]
 for mesh:MeshInstance3D in kit.find_children("*","MeshInstance3D",true,false):
  var shape:CollisionShape3D=mesh.get_node_or_null("StaticContact/SharedShape")
  if shape!=null:assert(not shape.disabled and shape.shape.get_faces()==mesh.mesh.get_faces())
  else:
   var pose:Transform3D=kit.global_transform.affine_inverse()*mesh.global_transform
   for vertex in mesh.mesh.get_faces():expected.append(pose*vertex)
  assert(mesh.mesh.surface_get_material(0)!=null)
 var combined:CollisionShape3D=kit.get_node("RoomStaticContacts/SharedRoomTriangles")
 assert(not combined.disabled and combined.shape.get_faces()==PackedVector3Array(expected))
 print("FAMILY_MEAL_TABLE_HASHES_AND_EXACT_CONTACTS_PREFLIGHT_PASS")
 quit(0)
