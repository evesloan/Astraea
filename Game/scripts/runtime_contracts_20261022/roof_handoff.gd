extends RefCounted
# The later fitted roof mutates this mesh. Return its original exact shape and
# relinquish only its immutable-residency entry before the original cutter runs.
static func prepare(ship:Node3D)->Dictionary:
 var config:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/fitted_wet_pavilions_20261015/FITTED_CONFIG_r010.json"))
 var manager:Node=ship.tidal_contacts
 assert(manager!=null)
 var transferred:=0
 for row:Dictionary in config.roofs:
  if str(row.receiver_root)!="TidalGardenReceivingCandidate":continue
  assert(FileAccess.get_sha256("res://assets/models/"+str(row.model))==str(row.source_sha256))
  var mesh:MeshInstance3D=ship.get_node("ShipSpace/Districts/"+str(row.receiver_root)).find_child(str(row.node),true,false)
  assert(mesh!=null and mesh.global_transform.is_equal_approx(Transform3D.IDENTITY))
  assert(manager._digest(mesh.mesh.get_faces())==str(row.faces_sha256))
  var matches:Array=[]
  for entry:Dictionary in manager.entries:
   if entry.mesh.get_ref()==mesh:matches.append(entry)
  assert(matches.size()==1,"Exactly one immutable roof owner required")
  var entry:Dictionary=matches[0]
  manager._load_entry(entry)
  var collider:CollisionShape3D=entry.collider.get_ref()
  assert(collider!=null and collider.shape is ConcavePolygonShape3D)
  assert(manager._digest(collider.shape.get_faces())==str(row.faces_sha256))
  assert(is_equal_approx(collider.shape.margin,float(entry.margin)))
  assert(collider.shape.backface_collision==bool(entry.backface))
  manager.unregister(entry)
  mesh.set_meta("fitted_roof_residency_handoff",true)
  transferred+=1
 assert(transferred==1)
 return {"transferred":transferred,"remaining_immutable_contacts":manager.entries.size()}
