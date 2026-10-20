extends RefCounted
# Existing deferred_home_visual.ensure already supports a source path. Retain that
# path instead of a strong PackedScene while keeping room/door/occluder state.
static func release_unused_scene_owners(ship: Node3D) -> Dictionary:
 var hashes: Dictionary={}
 var changed:=0
 for label in ["TidalRoomCandidates","QuietGroveRoomCandidates","FamilyTerraceRoomCandidates","SunsetRoomCandidates","StarAtlasRoomCandidates","NightGardenRoomCandidates"]:
  var group:=ship.get_node_or_null("ShipSpace/Districts/"+label)
  if group==null:continue
  for room in group.get_children():
   if not room.has_meta("deferred_visual_scene"):continue
   var scene:PackedScene=room.get_meta("deferred_visual_scene")
   assert(scene!=null)
   var path:=scene.resource_path
   assert(path.begins_with("res://assets/models/") and path.ends_with(".glb"),"Only exact retained imported scenes may demote to paths")
   if not hashes.has(path):hashes[path]=FileAccess.get_sha256(path)
   assert(not str(hashes[path]).is_empty())
   room.set_meta("deferred_visual_path",path)
   room.set_meta("deferred_visual_source_sha256",hashes[path])
   room.remove_meta("deferred_visual_scene")
   changed+=1
 return {"demoted_room_scene_owners":changed,"distinct_source_paths":hashes.size()}
