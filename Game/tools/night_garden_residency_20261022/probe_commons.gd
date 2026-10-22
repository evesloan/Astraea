extends SceneTree
func _initialize():call_deferred('run')
func run():
 var root3=Node3D.new();root.add_child(root3)
 var n=load('res://scripts/night_garden_residency_20261022/source_visual.gd').contact_visual(root3,'NightGardenD15ConnectedReceiving_r003.glb')
 var d=GLTFDocument.new();var st=GLTFState.new();d.append_from_file('res://assets/models/AST-COM-003.glb',st);var c=d.generate_scene(st);root3.add_child(c);c.position=Vector3(63,84,0)
 for m in c.find_children('*','MeshInstance3D',true,false):load('res://scripts/static_contact_cache.gd').attach(m)
 await physics_frame;await physics_frame
 for z in [-12.5,-14.04,-15,-19,-25]:
  var hit=root3.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(90.5,94,z),Vector3(90.5,92,z)))
  print(z,' hit=',hit)
 print('contacts=',n.find_children('*','StaticBody3D',true,false).size());quit()
