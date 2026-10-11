extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var space:=ship.get_world_3d().direct_space_state
 var input:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/d04_starboard_full_commons_20261011/SUPPORT_CANDIDATES.json"));var results:Array=[];var bad:Array=[]
 for f in input.feet:
  var alternatives:Array=[];var chosen:Dictionary={}
  for y in [-3.2]:
   var foot:=Vector3(f.x,y,f.z);var q:=PhysicsRayQueryParameters3D.create(foot+Vector3.UP*.03,foot-Vector3.UP*.03);var h:=space.intersect_ray(q);var owner:=str(h.collider.get_path())if not h.is_empty()else"NO_FLOOR"
   var floor_ok:bool=not h.is_empty()and absf(h.position.y-y)<.002 and ((y==12 and ("D03"in owner or "Crew"in owner))or(y<0 and "HUL_KeelPan"in owner))
   var shape:=BoxShape3D.new();shape.size=Vector3(.28,f.top_y-y-.01,.28);shape.margin=.001;var query:=PhysicsShapeQueryParameters3D.new();query.shape=shape;query.transform=Transform3D(Basis.IDENTITY,Vector3(f.x,(f.top_y+y+.01)/2,f.z));var blockers:Array=[]
   for hit in space.intersect_shape(query,32):blockers.append(str(hit.collider.get_path()))
   var corners:Array=[]
   for dx in [-.135,.135]:
    for dz in [-.135,.135]:
     var at:=foot+Vector3(dx,0,dz);var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.03,at-Vector3.UP*.03));var ok:bool=not hit.is_empty()and absf(hit.position.y-y)<.002 and not h.is_empty()and hit.collider==h.collider;corners.append(ok)
     if not ok:floor_ok=false
   var item={"foot":[f.x,y,f.z],"bearing_owner":owner,"bearing_source_node":str(h.collider.get_parent().get_path())if not h.is_empty()else"NO_FLOOR","four_shoe_corners":corners,"bearing_accepted":floor_ok,"column_volume_blockers":blockers};alternatives.append(item)
   if floor_ok and blockers.is_empty():chosen=item;break
  if chosen.is_empty():bad.append({"candidate":f,"alternatives":alternatives})
  results.append({"candidate":f,"chosen":chosen,"alternatives":alternatives})
 var route:Array=[]
 for point in [Vector3(3,12,-369.9),Vector3(4.2,12,-369.9),Vector3(20,12,-369.9),Vector3(40,12,-369.9),Vector3(60,12,-369.9),Vector3(67.5,12,-369.9)]:
  var h:=space.intersect_ray(PhysicsRayQueryParameters3D.create(point+Vector3.UP*.04,point-Vector3.UP*.04));route.append({"at":[point.x,point.y,point.z],"floor_owner":str(h.collider.get_parent().get_path())if not h.is_empty()else"NO_FLOOR"})
 var blockers:Array=[]
 for spec in [{"size":Vector3(59.18,1.79,4.38),"center":Vector3(33.6,12.905,-381.2)},{"size":Vector3(9.28,1.79,15.58),"center":Vector3(64.65,12.905,-375.6)}]:
  var headspace:=BoxShape3D.new();headspace.size=spec.size;headspace.margin=.001;var query:=PhysicsShapeQueryParameters3D.new();query.shape=headspace;query.transform=Transform3D(Basis.IDENTITY,spec.center)
  for h in space.intersect_shape(query,64):blockers.append(str(h.collider.get_path()))
 if not blockers.is_empty():bad.append({"staff_bridge_headspace_blockers":blockers})
 var result={"status":"PASS"if bad.is_empty()else"FAIL","candidate_count":results.size(),"results":results,"errors":bad,"actual_D03_floor_route_samples":route,"staff_bridge_headspace_blockers":blockers,"new_geometry_installed":false,"primary_engineering_accepted":false};FileAccess.open("/tmp/starboard_commons_support001.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"count":results.size(),"failed":bad.size()}));quit()
