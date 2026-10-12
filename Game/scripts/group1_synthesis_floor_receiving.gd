extends RefCounted
# Owned missing-only counterpart;source bay,floor,IDs and compiler records stay exact.
static func build(ship:Node3D)->Node3D:
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/GROUP1_SYNTHESIS_SUPPORTING_FLOOR.json"))
 assert(FileAccess.get_sha256("res://data/generated/structural_meshes.json")==plan.current_compiled_source_sha256)
 assert(not ship.has_node("ShipSpace/Group1SynthesisSupportingFloor"))
 var original:Node3D=ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms/D01_synthesis_service_bay")
 var actual:Array=[]
 for contact:CollisionShape3D in original.find_children("*","CollisionShape3D",true,false):
  assert(contact.shape is ConcavePolygonShape3D)
  var faces:PackedVector3Array=contact.shape.get_faces()
  for i in range(0,faces.size()-2,3):
   var a:Vector3=contact.global_transform*faces[i];var b:Vector3=contact.global_transform*faces[i+1];var c:Vector3=contact.global_transform*faces[i+2]
   if absf(a.y)<.00002 and absf(b.y)<.00002 and absf(c.y)<.00002:actual.append([Vector2(a.x,a.z),Vector2(b.x,b.z),Vector2(c.x,c.z)])
 assert(actual.size()==plan.actual_original_collider_triangles.size())
 for i in range(actual.size()):
  for j in range(3):assert(actual[i][j]==Vector2(plan.actual_original_collider_triangles[i][j][0],plan.actual_original_collider_triangles[i][j][1]))
 var group:Node3D=load("res://scripts/structural_floor_builder.gd").build_regions(ship.get_node("ShipSpace"),ship.stone,ship.ivory,plan.regions,{"staff_floor":ship.surface("staff_floor",Color.WHITE)},"Group1SynthesisSupportingFloor")
 group.set_meta("shared_adoption",true);group.set_meta("adopted_missing_only_m2",plan.adopted_missing_only_m2);group.set_meta("primary_load_capacity_accepted",false);group.set_meta("new_capacity_or_room_ids",0)
 return group
