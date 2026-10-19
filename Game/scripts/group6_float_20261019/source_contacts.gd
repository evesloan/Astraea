extends RefCounted
const SOURCE="res://data/architecture/group6_float_20261019/SOURCE_COLLISIONS.json"
static func v(q:Array)->Vector3:return Vector3(q[0],q[2],-q[1])
static func convex(body:RigidBody3D,points:PackedVector3Array)->void:
 var contact:=CollisionShape3D.new();var shape:=ConvexPolygonShape3D.new();shape.points=points;shape.margin=.001;contact.shape=shape;body.add_child(contact)
static func build(body:RigidBody3D)->Vector3:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(SOURCE))
 assert(FileAccess.get_sha256("res://assets/models/Group6LeisureFloat_r001.glb")==str(p.source_visual_sha256))
 for wedge in p.body_proposal.wedges:
  var points:=PackedVector3Array()
  for q in wedge.convex_hull_input_points_m:points.append(v(q))
  convex(body,points)
 var surface:Dictionary=p.seat_proposal.sampled_surface
 for triangle in surface.top_triangles:
  var points:=PackedVector3Array()
  for index in triangle:
   var point:=v(surface.vertices_m[int(index)]);points.append(point);points.append(point-Vector3.UP*float(surface.thickness_m))
  convex(body,points)
 for chain in p.grip_proposal.capsule_chains:
  for segment in chain.capsules:
   var a:=v(segment.a_m);var b:=v(segment.b_m);var contact:=CollisionShape3D.new();var cap:=CapsuleShape3D.new();cap.radius=float(segment.radius_m);cap.height=a.distance_to(b)+2*cap.radius;cap.margin=.001;contact.shape=cap;contact.position=(a+b)*.5;contact.basis=Basis(Quaternion(Vector3.UP,(b-a).normalized()));body.add_child(contact)
 var visual:Node3D=load("res://assets/models/Group6LeisureFloat_r001.glb").instantiate();body.add_child(visual)
 # Midpoint of two measured membrane contacts; not the central drain as support.
 return (v(p.seat_proposal.actor_contact_points_m[0])+v(p.seat_proposal.actor_contact_points_m[1]))*.5
