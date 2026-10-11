extends RefCounted
# One rigid original chair revision, independently retained before activation.
static func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D)->void:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_COMMONS_TRANSPORT_ROUTE.json"))
 if not p.chair_revision.active:return
 var parent:Node3D=ship.get_node("ShipSpace/Districts")
 if parent.has_node("D04CommonsTransportRouting"):return
 assert(FileAccess.get_sha256("res://artifacts/d04_commons_transport_chair_sealed_r002.json")==p.sealed_static_receipt_sha256)
 assert(JSON.parse_string(FileAccess.get_file_as_string("res://artifacts/d04_commons_transport_chair_sealed_r002.json")).status=="PASS")
 assert(FileAccess.get_sha256("res://assets/models/D04_PORT_FORWARD_HOMES_RECEIVING_r001.glb")==p.original_homes_model_sha256)
 assert(FileAccess.get_sha256("res://assets/models/"+p.revised_chair_model_file)==p.revised_chair_model_sha256)
 var c:Dictionary=p.chair_revision;var chair:Node3D=ship.find_child(c.node,true,false)
 assert(chair!=null and chair.global_position.distance_to(vec(c.preimage_position))<.00005 and absf(wrapf(chair.global_rotation.y-c.preimage_yaw,-PI,PI))<.00005 and chair.scale.is_equal_approx(Vector3.ONE))
 var meshes:Array=chair.find_children("*","MeshInstance3D",true,false)
 assert(meshes.size()==p.original_chair_mesh_count)
 for mesh:MeshInstance3D in meshes:assert(mesh.get_meta("extras",{}).get("source_catalogue_id","")=="AST-FUR-002")
 chair.global_position=vec(c.position);chair.rotation.y=c.yaw
 var root:=Node3D.new();root.name="D04CommonsTransportRouting";parent.add_child(root)
 root.set_meta("rigid_original_chair_revision",p.native_sealed_commit);root.set_meta("original_mesh_objects_preserved",true);root.set_meta("new_floor_m2",0);root.set_meta("new_homes_rest_places",0);root.set_meta("dedicated_clean_used_segregation_accepted",false)
