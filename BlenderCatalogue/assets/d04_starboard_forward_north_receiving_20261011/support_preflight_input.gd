extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var space:=ship.get_world_3d().direct_space_state;var feet:Array=[];var results:Array=[];var bad:Array=[]
 for x in [8.5,20.0,32.0,43.7]:
  for z in [-290.65,-286.75]:feet.append(Vector3(x,-3.2,z))
 for x in [26.5,61.4]:
  for z in [-333.7,-324.3,-316.9,-309.5,-302.1,-294.6]:feet.append(Vector3(x,-3.2,z))
 for x in [47.3,58.6]:
  for z in [-294.4,-286.8]:feet.append(Vector3(x,-3.2,z))
 for foot:Vector3 in feet:
  var h:=space.intersect_ray(PhysicsRayQueryParameters3D.create(foot+Vector3.UP*.03,foot-Vector3.UP*.03));var owner:=str(h.collider.get_path())if not h.is_empty()else "NO_FLOOR";var ok:=not h.is_empty()and absf(h.position.y+3.2)<.002 and "HUL_KeelPan"in owner
  var q:=PhysicsShapeQueryParameters3D.new();var sh:=BoxShape3D.new();sh.size=Vector3(.24,19.435,.24);sh.margin=.001;q.shape=sh;q.transform=Transform3D(Basis.IDENTITY,Vector3(foot.x,6.5275,foot.z));var hits:=space.intersect_shape(q,32);var blockers:Array=[]
  for hit in hits:blockers.append(str(hit.collider.get_path()))
  if not ok or not blockers.is_empty():bad.append(str(foot))
  results.append({"foot":[foot.x,foot.y,foot.z],"bearing_owner":owner,"original_keel_bearing":ok,"new_column_volume_blockers":blockers})
 var result={"status":"PASS"if bad.is_empty()else"FAIL","foot_count":feet.size(),"errors":bad,"results":results,"new_geometry_installed":false,"primary_load_accepted":false};FileAccess.open("/tmp/starboard_receiving_support001.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"foot_count":feet.size(),"errors":bad}));quit()
