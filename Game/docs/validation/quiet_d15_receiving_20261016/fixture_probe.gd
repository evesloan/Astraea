extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 var d:=GLTFDocument.new();var s:=GLTFState.new();d.append_from_file("/workspace/Astraea/BlenderCatalogue/assets/quiet_d15_staff_receiving_20261016/r003/QUIET_D15_STAFF_RECEIVING_r003.glb",s);var n:=d.generate_scene(s);root.add_child(n);var meshes:Array[Node]=[]
 for m in n.find_children("*","MeshInstance3D",true,false):
  if not str(m.name).begins_with("PATCH_")and not str(m.name).contains("Lens"):meshes.append(m)
 load("res://scripts/static_contact_cache.gd").attach_group(n,meshes)
 for i in range(10):await physics_frame
 var space:PhysicsDirectSpaceState3D=n.get_world_3d().direct_space_state
 for x in [26.22,31.78,34.22,39.78]:
  for off in [.07,.15]:
   var q:=PhysicsRayQueryParameters3D.create(Vector3(x+off,95.78,-483.9),Vector3(x+off,95.86,-483.9));var h:=space.intersect_ray(q);print(x," ",off," ",h.get("position"))
 quit()
