extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://../BlenderCatalogue/assets/group3_crew_service_20261009/extensions/clinical_streets_batch002/source/CLINICAL_STREETS.json"))
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(60):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var state:=ship.get_world_3d().direct_space_state;var rows:Array=[];var count:=0
 var shape:=CapsuleShape3D.new();shape.radius=.31;shape.height=1.82;shape.margin=.001
 for route in p.routes:
  var blockers:Dictionary={};var samples:=0;var supported:=0
  var path:Array=route.proposed_centerline_xz
  for j in range(path.size()-1):
   var a:=Vector3(path[j][0],21,path[j][1]);var b:=Vector3(path[j+1][0],21,path[j+1][1]);var n:=int(ceil(a.distance_to(b)/1.0))
   for i in range(n+1):
    var at:=a.lerp(b,float(i)/n);var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform=Transform3D(Basis.IDENTITY,at+Vector3.UP*.925);q.margin=.001
    var hits:=state.intersect_shape(q,128)
    for h in hits:
     if not h.collider is StaticBody3D or h.collider is AnimatableBody3D:continue
     var key:=str(h.collider.get_path())
     if not blockers.has(key):blockers[key]={"existing_static_contact":key,"first_witness":[at.x,at.y,at.z],"sample_count":0}
     blockers[key].sample_count+=1
    if hits.size()==128:blockers["SATURATED_QUERY"]={"first_witness":[at.x,at.y,at.z]}
    var f:=state.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.1,at-Vector3.UP*.4));if not f.is_empty()and absf(f.position.y-21)<.002:supported+=1
    samples+=1;count+=1
  rows.append({"route_id":route.id,"worker_samples":samples,"floor_supported_samples":supported,"existing_static_blockers":blockers.values()})
 var terminals:Array=[]
 for t in p.retained_terminal_interfaces:
  var at:=Vector3(t.source_origin[0],21,t.source_origin[2]);var sign:float=-1 if at.x<0 else 1
  var h:=state.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3(sign*1,1,0),at-Vector3(sign*1, -1,0)))
  terminals.append({"programme_key":t.programme_key,"role":t.role,"source_origin":t.source_origin,"existing_receiver_contact":str(h.collider.get_path())if not h.is_empty()else null,"receiver_or_original_room_modified":false})
 var result={"status":"READ_ONLY_ACTUAL_MAIN_CLINICAL_SCREEN","rows":rows,"terminal_receivers":terminals,"worker_samples":count,"sample_spacing_m":1.0,"body_volume_radius_m":.31,"loaded_cart_species_or_continuous_route_acceptance":false,"main_or_original_source_or_receiver_modified":false,"new_controller_or_ID_created":false}
 FileAccess.open("res://artifacts/group3_clinical_full_20261011/existing_survey.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
 for r in rows:print(JSON.stringify({"route":r.route_id,"worker_samples":r.worker_samples,"existing_blockers":r.existing_static_blockers.size(),"floor_supported":r.floor_supported_samples}))
 quit()
