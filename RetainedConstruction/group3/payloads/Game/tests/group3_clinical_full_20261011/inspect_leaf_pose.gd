extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(60):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var state:=ship.get_world_3d().direct_space_state;var rows:Array=[]
 var owner:=Node3D.new();owner.name="ReadOnlyPoseDiagnosticFixture";ship.get_node("ShipSpace").add_child(owner)
 for at in [Vector3(57,21,-406),Vector3(-57,21,-406),Vector3(-61,21,-402)]:
  var gate:Node3D=load("res://scripts/group3_clinical_full_20261011/sliding_gate.gd").new();gate.name="ProbeGate"+str(rows.size());gate.position=at;gate.rotation.y=PI/2 if at.x==-61 else 0;gate.persistent_id=StringName("__validation_only_pose_"+str(rows.size()));owner.add_child(gate)
  for i in range(20):await physics_frame
  gate.desired_open=true
  for frame in range(280):
   await physics_frame
   if frame%20!=0:continue
   for leaf in gate.leaves:
    var c:CollisionShape3D=leaf.get_node("DimensionedLeafContact");var q:=PhysicsShapeQueryParameters3D.new();q.shape=c.shape;q.transform=c.global_transform;q.exclude=[leaf.get_rid()];q.margin=.0001;var bad:Array=[]
    for h in state.intersect_shape(q,128):
     if h.collider is StaticBody3D and not h.collider is AnimatableBody3D:bad.append(str(h.collider.get_path()))
    rows.append({"gate_position":[at.x,at.y,at.z],"fraction":gate.open_fraction,"leaf":str(leaf.name),"leaf_gate_local_pose":str(leaf.transform),"contact_global_pose":str(c.global_transform),"contact_size":str(c.shape.size),"static_contacts":bad})
  gate.free()
 var result={"status":"READ_ONLY_MAIN_WITH_TEMPORARY_FITTING_POSE_WITNESSES","rows":rows,"existing_sources_or_root_or_IDs_changed":false}
 FileAccess.open("res://artifacts/group3_clinical_full_20261011/leaf_pose.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"samples":rows.size(),"bad":rows.filter(func(r):return not r.static_contacts.is_empty()).size()}));quit()
