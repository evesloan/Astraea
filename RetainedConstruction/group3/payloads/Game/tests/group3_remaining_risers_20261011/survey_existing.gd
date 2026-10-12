extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/whole_ship_layout.json"))
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(60):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var state:=ship.get_world_3d().direct_space_state
 var skip:Array=["port_service_riser_1","port_service_riser_2","port_service_riser_3","starboard_service_riser_1"]
 var rows:Array=[]
 for r in p.staff_riser_reservations:
  if r.id in skip:continue
  var x:float=r.center_xz[0];var z:float=r.center_xz[1]
  var b:=BoxShape3D.new();b.size=Vector3(3.6,105.18,4.0)
  var q:=PhysicsShapeQueryParameters3D.new();q.shape=b;q.transform=Transform3D(Basis.IDENTITY,Vector3(x,52.41,z));q.margin=.0001
  var blockers:Array=[]
  for h in state.intersect_shape(q,512):
   if h.collider is StaticBody3D and not h.collider is AnimatableBody3D:blockers.append(str(h.collider.get_path()))
  var floors:Array=[]
  for y in [0.0,6.0,12.0,16.5,21.0,27.0,35.5,44.0,52.5,61.0,69.5,78.0,84.0,88.5,93.0,97.5,102.0]:
   var shape:=BoxShape3D.new();shape.size=Vector3(4.38,.239,12)
   var f:=PhysicsShapeQueryParameters3D.new();f.shape=shape;f.transform=Transform3D(Basis.IDENTITY,Vector3(-20.99 if x<0 else 20.99,y-.1205,z));f.margin=.0001
   var contacts:Array=[]
   for h in state.intersect_shape(f,512):
    if h.collider is StaticBody3D and not h.collider is AnimatableBody3D:contacts.append(str(h.collider.get_path()))
   if not contacts.is_empty():floors.append({"floor_y":y,"existing_contacts":contacts})
  rows.append({"reservation_id":r.id,"center_xz":r.center_xz,"existing_shaft_blockers":blockers,"landing_slab_existing_contacts":floors,"query_limit":512})
 var result={"status":"READ_ONLY_ACTUAL_MAIN_SURVEY","source_layout_sha256":FileAccess.get_sha256("res://data/whole_ship_layout.json"),"rows":rows,
 "main_or_registry_modified":false,"new_lift_or_door_or_persistent_id_created":false,"scope":"Conservative actual static-contact survey; no engineering or occupancy acceptance."}
 FileAccess.open("res://artifacts/group3_remaining_risers_20261011/existing_survey.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
 for r in rows:print(JSON.stringify({"reservation":r.reservation_id,"shaft_blockers":r.existing_shaft_blockers.size(),"landing_contact_levels":r.landing_slab_existing_contacts.size()}))
 quit()
