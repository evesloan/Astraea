extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/whole_ship_layout.json"))
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(60):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var state:=ship.get_world_3d().direct_space_state
 var rows:Array=[]
 for key in ["starboard_service_riser_1","starboard_service_riser_3"]:
  var r:Dictionary=p.staff_riser_reservations.filter(func(q):return q.id==key)[0];var z:float=r.center_xz[1]
  var b:=BoxShape3D.new();b.size=Vector3(3.6,105.18,4.0);var q:=PhysicsShapeQueryParameters3D.new();q.shape=b;q.transform=Transform3D(Basis.IDENTITY,Vector3(25,52.41,z));q.margin=.0001
  var shaft:Array=[]
  for hit in state.intersect_shape(q,512):
   if hit.collider is StaticBody3D and not hit.collider is AnimatableBody3D:shaft.append(str(hit.collider.get_path()))
  var lobby:Array=[]
  for y in [0.0,6.0,12.0,16.5,21.0,27.0,35.5,44.0,52.5,61.0,69.5,78.0,84.0,88.5,93.0,97.5,102.0]:
   var box:=BoxShape3D.new();box.size=Vector3(4.18,3.16,r.lobby_z[1]-r.lobby_z[0]-.04);var probe:=PhysicsShapeQueryParameters3D.new();probe.shape=box;probe.transform=Transform3D(Basis.IDENTITY,Vector3(20.99,y+1.6,z));probe.margin=.0001
   var hits:Array=[]
   for hit in state.intersect_shape(probe,512):
    if hit.collider is StaticBody3D and not hit.collider is AnimatableBody3D:hits.append(str(hit.collider.get_path()))
   if not hits.is_empty():lobby.append({"floor_y":y,"existing_contacts":hits})
  rows.append({"reservation_id":key,"source_reservation":r,"shaft_blockers":shaft,"above_floor_lobby_contacts":lobby,"query_limit":512})
 var result={"status":"READ_ONLY_ACTUAL_MAIN_SURVEY","rows":rows,"originals_or_registry_or_main_modified":false,"new_controller_or_identity_created":false}
 FileAccess.open("res://artifacts/group3_fore_starboard_clinical_20261011/existing_survey.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
 for r in rows:print(JSON.stringify({"reservation_id":r.reservation_id,"shaft_blockers":r.shaft_blockers.size(),"lobby_contact_levels":r.above_floor_lobby_contacts.size()}))
 quit()
