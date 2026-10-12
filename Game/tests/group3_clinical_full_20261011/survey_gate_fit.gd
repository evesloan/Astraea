extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_clinical_full_20261011/CLINICAL.json"));var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(60):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea")
 var stream:Node3D=ship.get_node("ShipSystems/RemainingBatchStreaming");stream.set_physics_process(false)
 var loaded:Array=[]
 for item in stream.entries:
  if not str(item.key).begins_with("D05_directory_"):continue
  var room:Node3D=stream.rooms[str(item.key)]
  if not room.get_meta("stream_loaded",false):load("res://scripts/remaining_batch_receiving.gd").install(ship,item,room)
  loaded.append(str(item.key))
 for i in range(5):await physics_frame
 var state:=ship.get_world_3d().direct_space_state;var rows:Array=[]
 for name in ["D05_directory_01_crossing_0","D05_directory_01_crossing_3","D05_directory_02_crossing_0"]:
  var s:Dictionary=p.door_bindings.filter(func(d):return d.name==name)[0]
  for delta in [0.0,.2,.4,.6,.8,1.0,1.2]:
   var at:=Vector3(s.position[0],21,s.position[2]);if name.ends_with("_3"):at.x+=delta
   else:at.z+=delta
   var bad:Array=[];var saturated:=false
   var pieces:Array=[]
   var template:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://../BlenderCatalogue/assets/group3_crew_service_20261009/extensions/clinical_full_transfer_batch020/qa/SLIDING_NATIVE_ASSEMBLY.json"))
   for part in template.template_new_parts:
    if not str(part.name).begins_with("LEFT_")and not str(part.name).begins_with("RIGHT_"):pieces.append(part.aabb)
   for step in range(41):
    var f:float=step/40.0
    for side in range(2):
     var d:float=(-1.9 if side==0 else 1.9)*(clampf(f/.85,0,1)if side==0 else clampf((f-.15)/.85,0,1))
     pieces.append([(-1.799 if side==0 else .001)+d,(-.001 if side==0 else 1.799)+d,.001,2.399,-.0265,.0265])
   for a in pieces:
    a=a.duplicate()
    if float(a[2])<.001:a[2]=.001
    var shape:=BoxShape3D.new();shape.size=Vector3(a[1]-a[0],a[3]-a[2],a[5]-a[4]);shape.margin=.0001
    var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform=Transform3D(Basis(Vector3.UP,s.yaw),at)*Transform3D(Basis.IDENTITY,Vector3((a[0]+a[1])/2,(a[2]+a[3])/2,(a[4]+a[5])/2));q.margin=.0001
    var hits:=state.intersect_shape(q,128);saturated=saturated or hits.size()==128
    for h in hits:
     if h.collider is StaticBody3D and not h.collider is AnimatableBody3D:
      var key:=str(h.collider.get_path())
      if not key in bad:bad.append(key)
   rows.append({"gate":name,"inward_delta_m":delta,"position":[at.x,21,at.z],"full_fitting_and_leaf_travel_box_static_contacts":bad,"saturated":saturated})
 var result={"status":"READ_ONLY_ALL_ORIGINAL_D05_RECEIVERS_PARTS_AND_41_POSE_SCREEN","loaded_original_programmes":loaded,"temporary_stream_residency_frozen_for_complete_source_screen":true,"fixed_feet_support_contacts_excluded_by_1mm_start":true,"rows":rows,"main_or_original_room_or_support_modified":false,"existing_main_commit":"affc5c807087ff87da29f3642c2d6e418241b896","query_limit":128}
 FileAccess.open("res://artifacts/group3_clinical_full_20261011/gate_fit_survey.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
 for r in rows:print(JSON.stringify({"gate":r.gate,"delta":r.inward_delta_m,"contacts":r.full_fitting_and_leaf_travel_box_static_contacts.size(),"saturated":r.saturated}))
 quit()
