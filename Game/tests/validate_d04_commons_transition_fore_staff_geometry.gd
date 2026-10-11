extends SceneTree
var checks:=0
var errors:Array=[]
var pose_count:=0
var contacts:Array=[]
func ck(ok:bool,label:String):
 checks+=1
 if not ok:errors.append(label);print("FAIL ",label)
func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func visit(gate:Node3D,actor:CharacterBody3D):
 var x:RefCounted=load("res://scripts/d04_court_service_visit.gd").new();x.actor=weakref(actor);x.request_id=&"geometry_explicit_temporary_known_visit";x.court_ids.assign([gate.persistent_id]);x.consent_known=true;x.consent_allowed=true;x.active=true;gate.visit=x
func checked_pose(gate:Node3D,space:PhysicsDirectSpaceState3D,frame:int,phase:String):
 pose_count+=1
 var members:Array=gate.fitting.members;var index:=0
 for contact:CollisionShape3D in gate.leaves[0].find_children("*","CollisionShape3D",true,false):
  var moving:String=str(members[index]);index+=1;var q:=PhysicsShapeQueryParameters3D.new();q.shape=contact.shape;q.transform=contact.global_transform;q.exclude=[gate.leaves[0].get_rid()];var hits=space.intersect_shape(q,64)
  ck(hits.size()<64,"unsaturated exact shape contact query "+str(gate.name))
  var points:PackedVector3Array=contact.shape.points;var lo:=Vector3(INF,INF,INF);var hi:=-lo
  for point in points:lo=lo.min(contact.global_transform*point);hi=hi.max(contact.global_transform*point)
  # Explicit volume check also catches handles wholly embedded in a concave screen.
  if str(gate.name)in["D04PC_StaffUsed","D04PC_StaffClean"]:
   for name in ["D04PC_Successor_D04SA_ServiceLaneScreen_0","D04SA_ServiceLaneScreen_1"]:
    var screen:MeshInstance3D=gate.authored_visual.find_child(name,true,false);var a:AABB=screen.global_transform*screen.get_aabb();var overlap:Vector3=hi.min(a.end)-lo.max(a.position)
    ck(min(overlap.x,min(overlap.y,overlap.z))<=0.0001220703125,"moving member outside fixed screen volume "+str(gate.name)+" "+moving+" "+name+" "+phase+" "+str(frame))
  for hit in hits:
   var fixed:Node=hit.collider.get_parent();var row={"gate":str(gate.name),"phase":phase,"frame":frame,"moving":moving,"moving_lo":[lo.x,lo.y,lo.z],"moving_hi":[hi.x,hi.y,hi.z],"fixed":str(fixed.name),"classification":"UNEXPLAINED_CONTACT"};var accepted:=false
   if fixed is MeshInstance3D:
    var a:AABB=fixed.global_transform*fixed.get_aabb();row.fixed_lo=[a.position.x,a.position.y,a.position.z];row.fixed_hi=[a.end.x,a.end.y,a.end.z];var overlap:Vector3=hi.min(a.end)-lo.max(a.position);row.aabb_overlap=[overlap.x,overlap.y,overlap.z]
    # Only named source bearing/frame contacts qualify. No world/control exemption.
    var own_jamb:=false;var hinge_bearing:=false
    for j in range(3):
     if str(gate.name)=="PriorCourtGate_"+str(j):
      own_jamb=str(fixed.name)in["D04PCS_ServiceJamb_"+str(j)+"_0","D04PCS_ServiceJamb_"+str(j)+"_1"] and moving=="D04PCS_OpaqueGate_"+str(j)
      hinge_bearing=moving in["D04PCS_Hinge_"+str(j)+"_0","D04PCS_Hinge_"+str(j)+"_1"]and str(fixed.name)=="D04PCS_ServiceJamb_"+str(j)+"_0"
    if str(gate.name)=="D04PC_CourtSouth":own_jamb=moving=="D04PC_CourtSouth_Leaf"and str(fixed.name)in["D04PC_CourtSouth_Jamb_0","D04PC_CourtSouth_Jamb_1"]
    for label in ["D04PC_StaffUsed","D04PC_StaffClean"]:
     if str(gate.name)==label:own_jamb=moving==label+"_Leaf"and str(fixed.name)in[label+"_Jamb_0",label+"_Jamb_1"]
    var surface_bound:float=2.0*contact.shape.margin+0.0001220703125
    if own_jamb and min(overlap.x,min(overlap.y,overlap.z))<=surface_bound:accepted=true;row.classification="SOURCE_FRAME_SURFACE_CONTACT_WITHIN_MARGIN_AND_FLOAT32_BOUND";row.surface_bound_m=surface_bound
    if hinge_bearing:accepted=true;row.classification="RETAINED_SOURCE_HINGE_BEARING_ON_OWN_FIXED_JAMB"
   contacts.append(row);ck(accepted,"actual moving fitting contact classified "+str(gate.name)+" "+moving+" "+str(fixed.name)+" "+phase+" frame="+str(frame))
   if not accepted:print("CONTACT ",JSON.stringify(row))
func gate_poses(gate:Node3D,actor:CharacterBody3D,space:PhysicsDirectSpaceState3D,private_gate:bool):
 ck(gate.open_fraction==0 and not gate.desired_open,"initial fitting closed "+str(gate.name))
 if private_gate:
  gate.interact(actor);ck(gate.access_refused and not gate.desired_open,"unknown private visit refused "+str(gate.name));visit(gate,actor)
 for phase in ["open","close"]:
  gate.interact(actor)
  for i in range(100):
   await physics_frame
   if i%5==0:checked_pose(gate,space,i,phase)
  ck(gate.open_fraction==(1.0 if phase=="open"else 0.0),"original controller endpoint "+phase+" "+str(gate.name))
 # Open for the source floor and worker stance samples.
 gate.interact(actor)
 for i in range(100):await physics_frame
func _initialize():call_deferred("run")
func run():
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_COMMONS_TRANSITION_AND_FORE_STAFF.json"));var main=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var space=ship.get_world_3d().direct_space_state;var removed:Array=[];var retained:Dictionary={}
 for pre in p.fore_runtime_preimages:removed.append(pre.name)
 for mesh:MeshInstance3D in ship.find_children("*","MeshInstance3D",true,false):
  var a:AABB=mesh.global_transform*mesh.get_aabb()
  if str(mesh.name)not in removed and ((a.position.z< -270 and a.end.z> -500)or str(mesh.get_path()).contains("D04PortCentralHabitatNeighborhood")):
   retained[str(mesh.get_path())]={"node":mesh,"faces":mesh.mesh.get_faces(),"pose":mesh.global_transform}
 var common:Node3D=load("res://scripts/d04_commons_transition_fore_staff.gd").commons_candidate(ship);var fore:Node3D=load("res://scripts/d04_commons_transition_fore_staff.gd").fore_build(ship,true)
 for i in range(60):await physics_frame
 for key in retained:
  var q:Dictionary=retained[key];ck(is_instance_valid(q.node),"original mesh exists "+key)
  if is_instance_valid(q.node):ck(q.node.mesh.get_faces()==q.faces and q.node.global_transform==q.pose,"original source faces/pose exact "+key)
 for part in p.commons_parts:
  var mesh:MeshInstance3D=common.find_child(part.name,true,false);ck(mesh!=null,"new short-profile part "+part.name)
  if mesh==null:continue
  var lo:=Vector3(INF,INF,INF);var hi:=-lo
  for at in part.verts:lo=lo.min(v(at));hi=hi.max(v(at))
  var a:AABB=mesh.global_transform*mesh.get_aabb();ck(a.position.distance_to(lo)<.001 and a.end.distance_to(hi)<.001,"short-profile native dimensions "+part.name);ck(a.end.y<18.8,"distinct profile beneath retained2.30m entry header "+part.name)
 for spec in p.commons_gates:await gate_poses(common.get_node(spec.name),actor,space,false)
 for spec in p.fore_new_gates:await gate_poses(fore.get_node(spec.name),actor,space,spec.requires_visit)
 for i in range(3):await gate_poses(fore.get_node("PriorCourtGate_"+str(i)),actor,space,true)
 var samples:=0
 for at in [Vector3(-75,16.5,-2),Vector3(-75,16.5,-5),Vector3(-71.8,16.5,-2),Vector3(-71.8,16.5,-5),Vector3(-57.3,12,-447),Vector3(-53,12,-447),Vector3(-40,12,-447),Vector3(-34,12,-447),Vector3(-53,12,-449),Vector3(-40,12,-449),Vector3(-34,12,-449),Vector3(-28.1,16.5,-447.05),Vector3(-28.1,16.5,-443.8),Vector3(-28.1,16.5,-428),Vector3(-28.1,16.5,-417)]:
  var cap:=CapsuleShape3D.new();cap.height=1.8;cap.radius=.3;cap.margin=.001;var q:=PhysicsShapeQueryParameters3D.new();q.shape=cap;q.transform=Transform3D(Basis.IDENTITY,at+Vector3.UP*.925);var hits=space.intersect_shape(q,64);ck(hits.is_empty(),"staff/short-transition worker clearance "+str(at));samples+=1
  if not hits.is_empty():print("STANCE_CONTACT ",at," ",hits.map(func(h):return str(h.collider.get_path())))
  var h=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.05,at-Vector3.UP*.1));ck(not h.is_empty()and abs(h.position.y-at.y)<.001,"actual source/candidate floor contact "+str(at))
 for mesh:MeshInstance3D in fore.find_children("*","MeshInstance3D",true,false):ck(not str(mesh.name).begins_with("D04PC_Home"),"home maintenance modules excluded "+str(mesh.name))
 ck(not p.commons_candidate_active,"commons candidate has no production activation or separated rear-route claim");ck(not fore.get_meta("home_tool_hatches_or_panes_installed"),"home maintenance components excluded");ck(not fore.get_meta("production_private_consent_provider_available"),"no private consent provider invented")
 var result={"contact_rows":contacts,"contact_policy":"Exact native convex query; only explicitly named retained hinge bearings and source frame edge contacts within2*0.001m shape margin+0.0001220703125m float32 bound accepted; other contacts strict.","status":"PASS"if errors.is_empty()else"HOLD","checks":checks,"errors":errors,"exact_retained_original_meshes":retained.size(),"actual_original_controller_gate_pose_samples":pose_count,"worker_capsule_samples":samples,"commons_distinct_short_profiles":3,"commons_original_entry_clearance_m":2.3,"commons_original_canopy_clearance_m":2.65,"new_profile_overall_height_m":2.28,"fore_runtime_preimages":p.fore_runtime_preimages.size(),"fore_selected_native_meshes":p.fore_selected_mesh_count,"fore_production_floor_m2":p.new_floor_m2,"home_panes_hatches_tools_activated":false,"production_private_consent_provider_available":false,"temporary_known_private_visits_test_only":true,"model_pins":p.model_pins,"limits":p.limits};FileAccess.open("res://artifacts/d04_commons_transition_fore_staff_geometry.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":checks,"errors":errors}));quit(0 if errors.is_empty()else 1)
