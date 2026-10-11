from pathlib import Path
R=Path('/workspace/astraea-recovered-532087b9-20261010T083844Z');W=R/'BlenderCatalogue/assets/d04_starboard_forward_work_branches_20261011'
s=(R/'Game/scripts/d04_port_central_west_staff_circuit.gd').read_text().replace('D04_PORT_CENTRAL_WEST_STAFF_CIRCUIT','D04_STARBOARD_FORWARD_WORK_BRANCHES').replace('D04PortCentralWestStaffCircuit','D04StarboardForwardWorkBranches').replace('d04_port_central_west_staff_circuit','d04_starboard_forward_work_branches');(R/'Game/scripts/d04_starboard_forward_work_branches.gd').write_text(s)
s=(R/'Game/tests/validate_d04_commons_transition_fore_staff_geometry.gd').read_text();s=s[:s.index('func _initialize()')]
a=s.index('  # Explicit volume check');b=s.index('  for hit in hits:',a);s=s[:a]+s[b:]
a=s.index('    var own_jamb:=false');b=s.index('    var surface_bound:',a)
s=s[:a]+'''    var own_jamb:=moving.ends_with("D04PC_CourtSouth_Leaf")and str(fixed.name)in gate.fitting.control_members and str(fixed.name).ends_with("D04PC_CourtSouth_Jamb_1")
    var hinge_bearing:=false
'''+s[b:]
s+='''func rids(n:Node)->Array[RID]:
 var out:Array[RID]=[]
 if n is CollisionObject3D:out.append(n.get_rid())
 for c in n.get_children():out.append_array(rids(c))
 return out
func _initialize():call_deferred("run")
func run():
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_STARBOARD_FORWARD_WORK_BRANCHES.json"));var main=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var districts:Node3D=ship.get_node("ShipSpace/Districts");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var space=ship.get_world_3d().direct_space_state;var removed:Array=[];var retained:Dictionary={}
 for pre in p.runtime_preimages:removed.append(pre.name)
 for mesh:MeshInstance3D in ship.find_children("*","MeshInstance3D",true,false):
  var a:AABB=mesh.global_transform*mesh.get_aabb()
  if str(mesh.name)not in removed and ((a.position.z< -270 and a.end.z> -500)or str(mesh.get_path()).contains("D04PortCentralHabitatNeighborhood")):retained[str(mesh.get_path())]={"node":mesh,"faces":mesh.mesh.get_faces(),"pose":mesh.global_transform}
 var n:Node3D=load("res://scripts/d04_starboard_forward_work_branches.gd").build(ship,true)
 for i in range(60):await physics_frame
 for key in retained:
  var q:Dictionary=retained[key];ck(is_instance_valid(q.node),"original mesh exists "+key)
  if is_instance_valid(q.node):ck(q.node.mesh.get_faces()==q.faces and q.node.global_transform==q.pose,"original geometry/pose exact "+key)
 var parts:Array=p.parts.duplicate();parts.append_array(p.copied_gate_parts);parts.append_array(p.closed_staging_parts)
 for part in parts:
  var mesh:MeshInstance3D=n.find_child(part.name,true,false);ck(mesh!=null,"native part "+part.name)
  if mesh==null:continue
  var lo:=Vector3(INF,INF,INF);var hi:=-lo
  for at in part.verts:lo=lo.min(v(at));hi=hi.max(v(at))
  var a:AABB=mesh.global_transform*mesh.get_aabb();ck(a.position.distance_to(lo)<.001 and a.end.distance_to(hi)<.001,"actual native bounds "+part.name)
 var exclude:=rids(n);var bearing_count:=0
 for s in p.support_preimages:
  for c in s.corners:
   var at:=v(c.point);var ray:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.05,at-Vector3.UP*.05);ray.exclude=exclude;ray.hit_back_faces=true;var h=space.intersect_ray(ray);ck(not h.is_empty(),"source hull bearing present")
   if not h.is_empty():ck(h.position.distance_to(at)<.001 and str(h.collider.get_path())==c.owner,"source keel bearing exact identity/datum");bearing_count+=1
  var half:float=s.half-.04;var box:=BoxShape3D.new();box.size=Vector3(half*2,16.13-s.column_bottom-.01,half*2);var q:=PhysicsShapeQueryParameters3D.new();q.shape=box;q.transform=Transform3D(Basis.IDENTITY,Vector3(s.x,(16.13+s.column_bottom+.01)/2,s.z));q.exclude=exclude;ck(space.intersect_shape(q,64).is_empty(),"column retains source occupied volumes")
 for spec in p.gates:await gate_poses(n.get_node(spec.name),actor,space,spec.requires_visit)
 var samples:Array=p.route_samples.duplicate();samples.append_array(p.source_approach_samples)
 for g in p.gates.slice(0,4):
  for x in [g.lane_x,(g.pivot[0]+g.lane_x)/2,g.pivot[0],g.wall_x,g.court_stance[0]]:samples.append([x,16.5,g.z])
 for at_array in samples:
  var at:=v(at_array);var cap:=CapsuleShape3D.new();cap.height=1.8;cap.radius=.3;cap.margin=.001;var q:=PhysicsShapeQueryParameters3D.new();q.shape=cap;q.transform=Transform3D(Basis.IDENTITY,at+Vector3.UP*.925);var hits=space.intersect_shape(q,64);ck(hits.is_empty(),"worker clearance "+str(at))
  if not hits.is_empty():print("STANCE_CONTACT ",at," ",hits.map(func(h):return str(h.collider.get_path())))
  var h=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.05,at-Vector3.UP*.1));ck(not h.is_empty()and abs(h.position.y-at.y)<.001,"actual source/candidate floor contact "+str(at))
 for g in p.gates.slice(0,4):
  var gate:Node3D=n.get_node(g.name);var stranger:=CharacterBody3D.new();n.add_child(stranger);gate.interact(stranger);ck(gate.access_refused,"foreign actor refused "+g.name);stranger.free()
 ck(not n.get_meta("production_private_consent_provider_available"),"no private consent provider invented");ck(not JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_COMMONS_TRANSITION_AND_FORE_STAFF.json")).commons_candidate_active,"pending port-central commons remains inactive")
 var result={"status":"PASS"if errors.is_empty()else"HOLD","checks":checks,"errors":errors,"contact_rows":contacts,"model_pins":p.model_pins,"exact_retained_original_meshes":retained.size(),"runtime_exact_preimages":p.runtime_preimages.size(),"source_hull_bearing_corners":bearing_count,"actual_original_controller_gate_pose_samples":pose_count,"worker_capsule_samples":samples.size(),"new_missing_floor_m2":p.new_floor_m2,"temporary_known_private_visits_test_only":true,"production_private_consent_provider_available":false,"ordinary_game_visual_acceptance":false,"limits":p.limits};FileAccess.open("res://artifacts/d04_starboard_forward_work_branches_geometry.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":checks,"errors":errors}));quit(0 if errors.is_empty()else 1)
'''
(R/'Game/tests/validate_d04_starboard_forward_work_branches_geometry.gd').write_text(s);(W/'write_runtime001.py').write_bytes(Path(__file__).read_bytes());print('Candidate helper and essential geometry test prepared')
