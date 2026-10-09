extends SceneTree
var host: Node3D
var meshes := 0
var bodies := 0
var policy: Dictionary
var policies := []
var unknown := []
func _initialize() -> void:
 call_deferred("check")
func collisions(node: Node) -> void:
 if node is MeshInstance3D:
  meshes += 1
  var kind = str(policy.get(str(node.name), policy.get(str(node.get_parent().name), "")))
  policies.append({"node":str(node.name),"kind":kind,"collision":not kind in ["water_visual", "tube_static_visual", "fixture_lens", "plant_static"]})
  if kind.is_empty():unknown.append(str(node.name))
  if not kind in ["water_visual", "tube_static_visual", "fixture_lens", "plant_static"]:
   var shape = node.mesh.create_trimesh_shape()
   var body = StaticBody3D.new()
   var child = CollisionShape3D.new()
   child.shape = shape
   body.add_child(child)
   node.add_child(body)
   bodies += 1
 for c in node.get_children():
  if not c is StaticBody3D: collisions(c)
func check() -> void:
 policy = JSON.parse_string(FileAccess.get_file_as_string("res://collision_policy.json"))
 host = Node3D.new()
 root.add_child(host)
 for path in ["res://models/AQD_architecture.glb", "res://models/AQD_floor_proposals.glb"]:
  var scene = load(path)
  if scene == null:
   push_error("Broken imported scene: " + path)
   quit(2)
   return
  host.add_child(scene.instantiate())
 collisions(host)
 await physics_frame
 await physics_frame
 var space = host.get_world_3d().direct_space_state
 var pins = [
  ["dry_arrival",58.0,240.0,44.0], ["connection_tongue",55.0,240.0,44.0],
  ["arrival_ramp",68.0,245.9,44.583333], ["wet_west",58.0,220.0,45.45],
  ["wet_south",89.0,244.0,45.45], ["island",80.0,217.5,45.45],
  ["crossing",66.9,202.0,47.7], ["west_bridge_ramp",60.5,215.5,46.575],
  ["island_bridge_ramp",73.4,215.5,46.575],
  ["launch_lower_flight",92.4,232.3,46.425], ["launch_upper_flight",95.2,232.3,48.375],
  ["launch_top_landing",95.2,243.6,49.35], ["launch_gallery",98.2,225.0,49.35],
  ["north_queue",80.0,196.2,49.35], ["service_portal",99.2,210.0,45.45], ["north_recovery_approach",75.8,192.9,45.45]]
 var results = []
 var failures = unknown.duplicate()
 for p in pins:
  var floor_y = float(p[3])
  var from = Vector3(p[1],floor_y+.16,p[2])
  var ray = PhysicsRayQueryParameters3D.create(from,from-Vector3(0,.6,0))
  ray.hit_back_faces = false
  var hit = space.intersect_ray(ray)
  var ok = not hit.is_empty() and abs(hit.position.y-floor_y)<.06
  var capsule = CapsuleShape3D.new()
  capsule.radius = .30
  capsule.height = 2.20
  var query = PhysicsShapeQueryParameters3D.new()
  query.shape = capsule
  query.transform = Transform3D(Basis.IDENTITY,Vector3(p[1],floor_y+1.15,p[2]))
  query.margin = .001
  var obstruction = space.intersect_shape(query,8)
  var row = {"id":p[0],"xyz": [p[1],floor_y,p[2]],"floor_contact_pass":ok,"actual_floor_y":hit.position.y if not hit.is_empty() else null,"major_stationary_obstructions":obstruction.size()}
  results.append(row)
  if not ok or not obstruction.is_empty():failures.append(p[0])
 var report = {"passed":failures.is_empty(),"godot_version":Engine.get_version_info().string,"mesh_nodes":meshes,"collision_policy":policies,"unknown_kinds":unknown,"collision_nodes_for_review":bodies,"floor_contact_points":results,"failures":failures,"capsule_reference":{"radius_m":.3,"height_m":2.2,"scope":"Stationary construction obstruction probes only. Species fit, movement, routes, carts and operational physics deferred."},"scope":"Isolated actual GLB imports with temporary compiler floor proposals; host Game untouched."}
 var file = FileAccess.open(ProjectSettings.globalize_path("res://").path_join("../qa/godot_quick_checks.json"),FileAccess.WRITE)
 file.store_string(JSON.stringify(report,"  "))
 print(JSON.stringify(report))
 quit(0 if failures.is_empty() else 2)
