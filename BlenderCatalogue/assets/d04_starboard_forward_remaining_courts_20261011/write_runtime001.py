from pathlib import Path
R=Path('/workspace/astraea-recovered-532087b9-20261010T083844Z');W=R/'BlenderCatalogue/assets/d04_starboard_forward_remaining_courts_20261011';s=(R/'Game/scripts/d04_starboard_forward_work_branches.gd').read_text().replace('D04_STARBOARD_FORWARD_WORK_BRANCHES','D04_STARBOARD_FORWARD_REMAINING_COURTS').replace('D04StarboardForwardWorkBranches','D04StarboardForwardRemainingCourts').replace('d04_starboard_forward_work_branches','d04_starboard_forward_remaining_courts');(R/'Game/scripts/d04_starboard_forward_remaining_courts.gd').write_text(s)
s=(R/'Game/tests/validate_d04_starboard_forward_work_branches_geometry.gd').read_text().replace('D04_STARBOARD_FORWARD_WORK_BRANCHES','D04_STARBOARD_FORWARD_REMAINING_COURTS').replace('d04_starboard_forward_work_branches','d04_starboard_forward_remaining_courts').replace('p.gates.slice(0,4)','p.gates.slice(0,5)');a=s.index(' for spec in p.gates:await gate_poses');s=s[:a]+''' var ledger_count:=0
 for row in p.ledger_preimages:
  for c in row.corners:
   var at:=v(c.point);var ray:=PhysicsRayQueryParameters3D.create(at-Vector3.RIGHT*.1,at+Vector3.RIGHT*.1);ray.exclude=exclude;ray.hit_back_faces=true;var h=space.intersect_ray(ray);ck(not h.is_empty(),"unchanged source floor-edge ledger joint exists")
   if not h.is_empty():ck(h.position.distance_to(at)<.001 and str(h.collider.get_path())==c.owner and str(h.collider.get_parent().name)==row.site.source_mesh,"exact named floor-edge joint identity/pose");ledger_count+=1
 # Outside the new floor polygons these are retained approach samples, not missing-floor claims.
 for at_array in p.route_samples:
  if at_array[0]>64:continue
  var at:=v(at_array);var ray:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.05,at-Vector3.UP*.1);ray.exclude=exclude;ck(space.intersect_ray(ray).is_empty(),"new missing floor does not duplicate original walking surface")
 for g in JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_STARBOARD_FORWARD_WORK_BRANCHES.json")).gates:
  var old_gate:Node3D=districts.get_node("D04StarboardForwardWorkBranches").get_node(g.name);ck(String(old_gate.persistent_id)==g.id and old_gate.open_fraction==0 and old_gate.visit==null,"retained east/staff fitting ID/default closed/visit preserved "+g.name)
''' +s[a:];s=s.replace('"source_hull_bearing_corners":bearing_count','"source_hull_bearing_corners":bearing_count,"source_floor_edge_joint_corners":ledger_count,"narrow_court_exterior_stance_only":true');(R/'Game/tests/validate_d04_starboard_forward_remaining_courts_geometry.gd').write_text(s);(W/'write_runtime001.py').write_bytes(Path(__file__).read_bytes())
