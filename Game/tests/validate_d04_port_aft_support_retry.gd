extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var space:=ship.get_world_3d().direct_space_state
 var input:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/d04_port_aft_neighborhood_20261011/SUPPORT_RETRY_CANDIDATES.json"));var results:Array=[];var bad:Array=[]
 for f in input.feet:
  var alternatives:Array=[];var chosen:Dictionary={}
  for y in [12.0,-3.2]:
   if y>=f.top_y:continue
   var foot:=Vector3(f.x,y,f.z);var q:=PhysicsRayQueryParameters3D.create(foot+Vector3.UP*.03,foot-Vector3.UP*.03);var h:=space.intersect_ray(q);var owner:=str(h.collider.get_path())if not h.is_empty()else"NO_FLOOR"
   var floor_ok:bool=not h.is_empty()and absf(h.position.y-y)<.002 and ((y==12 and ("D03"in owner or "Crew"in owner))or(y<0 and "HUL_KeelPan"in owner))
   var shape:=BoxShape3D.new();shape.size=Vector3(f.width_x,f.top_y-y-.01,f.width_z);shape.margin=.001;var query:=PhysicsShapeQueryParameters3D.new();query.shape=shape;query.transform=Transform3D(Basis.IDENTITY,Vector3(f.x,(f.top_y+y+.01)/2,f.z));var blockers:Array=[]
   for hit in space.intersect_shape(query,32):blockers.append(str(hit.collider.get_path()))
   var corners:Array=[]
   for dx in [-f.width_x/2+.005,f.width_x/2-.005]:
    for dz in [-f.width_z/2+.005,f.width_z/2-.005]:
     var at:=foot+Vector3(dx,0,dz);var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.03,at-Vector3.UP*.03));var ok:bool=not hit.is_empty()and absf(hit.position.y-y)<.002 and not h.is_empty()and hit.collider==h.collider;corners.append(ok)
     if not ok:floor_ok=false
   var item={"foot":[f.x,y,f.z],"bearing_owner":owner,"bearing_source_node":str(h.collider.get_parent().get_path())if not h.is_empty()else"NO_FLOOR","four_shoe_corners":corners,"bearing_accepted":floor_ok,"column_volume_blockers":blockers};alternatives.append(item)
   if floor_ok and blockers.is_empty():chosen=item;break
  if chosen.is_empty():
   var point:=Vector3(f.x,f.top_y-.002,f.z);var h:=space.intersect_ray(PhysicsRayQueryParameters3D.create(point,Vector3(f.x,-4.0,f.z)));var name:=str(h.collider.get_path())if not h.is_empty()else "NO_FLOOR"
   var structural:bool=not h.is_empty()and h.normal.y>.15 and ("HUL_LowerBand"in name or "HUL_KeelPan"in name or "ReceivedSectionStructuralFloors"in name or "CompiledStructuralFloors"in name)
   alternatives.append({"fallback_surface_probe":true,"bearing_owner":name,"hit_y":h.position.y if not h.is_empty()else -INF,"normal":str(h.normal)if not h.is_empty()else "none","structural_surface_accepted":structural})
   var patches:Array=[];var max_y:float=-INF
   if structural:
    for dx in [-f.width_x/2,f.width_x/2]:
     for dz in [-f.width_z/2,f.width_z/2]:
      var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(f.x+dx,f.top_y-.002,f.z+dz),Vector3(f.x+dx,-4.0,f.z+dz)))
      if hit.is_empty()or hit.collider!=h.collider or hit.normal.y<.15:structural=false
      else:patches.append([hit.position.x,hit.position.y,hit.position.z]);max_y=maxf(max_y,hit.position.y)
   if structural:
    var base_y:float=max_y+.08;var sh:=BoxShape3D.new();sh.size=Vector3(f.width_x,f.top_y-base_y-.004,f.width_z);sh.margin=.001;var q:=PhysicsShapeQueryParameters3D.new();q.shape=sh;q.transform=Transform3D(Basis.IDENTITY,Vector3(f.x,(f.top_y+base_y+.004)/2,f.z));var blockers:Array=[]
    for hit in space.intersect_shape(q,32):blockers.append(str(hit.collider.get_path()))
    var item={"foot":[f.x,h.position.y,f.z],"bearing_owner":name,"bearing_source_node":str(h.collider.get_parent().get_path()),"four_shoe_corners":[true,true,true,true],"corner_contact_world":patches,"pier_bottom_y":base_y,"bearing_accepted":blockers.is_empty(),"column_volume_blockers":blockers,"actual_retained_structural_surface_fallback":true,"source_surface_normal":[h.normal.x,h.normal.y,h.normal.z]};alternatives.append(item)
    if blockers.is_empty():chosen=item
  if chosen.is_empty():bad.append({"candidate":f,"alternatives":alternatives})
  results.append({"candidate":f,"chosen":chosen,"alternatives":alternatives})
 var route:Array=[];var blockers:Array=[]
 var result={"status":"PASS"if bad.is_empty()else"FAIL","input_sha256":FileAccess.get_sha256("/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/d04_port_aft_neighborhood_20261011/SUPPORT_RETRY_CANDIDATES.json"),"candidate_count":results.size(),"results":results,"errors":bad,"actual_D03_floor_route_samples":route,"staff_bridge_headspace_blockers":blockers,"new_geometry_installed":false,"primary_engineering_accepted":false};FileAccess.open("/tmp/port_aft_support006_retry.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"count":results.size(),"failed":bad.size()}));quit()
