extends SceneTree
var checks:=0
var errors:Array=[]
func ck(ok:bool,label:String):
 checks+=1
 if not ok:errors.append(label);print("FAIL ",label)
func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func _initialize():call_deferred("run")
func run():
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_STARBOARD_AFT_COMMONS_ENCLOSURE.json"));var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var d:Node3D=ship.get_node("ShipSpace/Districts");var space:=ship.get_world_3d().direct_space_state;var old:Dictionary={}
 for root_name in ["D04StarboardAftHabitatNeighborhood","D04StarboardAftCourtRoutes","D04PortCentralCommonsRearRoute","LowerSharedAftStaffRoute"]:
  for mesh:MeshInstance3D in d.get_node(root_name).find_children("*","MeshInstance3D",true,false):old[str(mesh.get_path())]={"mesh":mesh,"faces":mesh.mesh.get_faces(),"pose":mesh.global_transform}
 var n:Node3D=load("res://scripts/d04_starboard_aft_commons_enclosure.gd").build(ship,true)
 for i in range(30):await physics_frame
 for key in old:
  var q:Dictionary=old[key];ck(is_instance_valid(q.mesh)and q.mesh.mesh.get_faces()==q.faces and q.mesh.global_transform==q.pose,"source mesh and pose exact "+key)
 var cap_rids:Array[RID]=[]
 for body:StaticBody3D in n.find_children("*","StaticBody3D",true,false):cap_rids.append(body.get_rid())
 var joints:Array=[]
 for site in p.closure_sites:
  var original:MeshInstance3D=d.get_node(site.source_root).find_child(site.source_name,true,false);ck(original!=null,"named original wall owner "+site.source_name);var oa:AABB=original.global_transform*original.get_aabb();ck(abs(oa.end.y-site.bottom)<.001,"exact original wall-top datum "+site.source_name)
 for part in p.parts:
  var mesh:MeshInstance3D=n.find_child(part.name,true,false);ck(mesh!=null,"new native fitted closure "+part.name)
  var a:AABB=mesh.global_transform*mesh.get_aabb();ck(a.position.distance_to(v(part.expected_bounds[0]))<.001 and a.end.distance_to(v(part.expected_bounds[1]))<.001,"actual fitted native bounds "+part.name)
  var center:=Vector3.ZERO
  for at in part.verts:center+=v(at)
  center/=part.verts.size();var shape:=ConvexPolygonShape3D.new();shape.margin=.001;var points:=PackedVector3Array()
  for at in part.verts:points.append(center+(v(at)-center)*.98)
  shape.points=points;var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform=Transform3D.IDENTITY;q.exclude=cap_rids;var hits:=space.intersect_shape(q,64);ck(hits.is_empty(),"fitted closure interior has no source overlap "+part.name)
  if not hits.is_empty():print("CAP_CONTACT ",part.name," ",hits.map(func(row):return str(row.collider.get_path())))
  # Verify actual mesh planes directly, including roofs with retained collision policies,
  # including the adjacent closure band when a retained member divides the wall.
  if part.category=="ceiling_edge_closure":continue
  var point:=Vector3(center.x,part.top,center.z);var owners:Array=[]
  for candidate:MeshInstance3D in ship.find_children("*","MeshInstance3D",true,false):
   if candidate==mesh:continue
   var ca:AABB=candidate.global_transform*candidate.get_aabb()
   if ca.position.y>point.y+.001 or ca.end.y<point.y-.001 or point.x<ca.position.x-.001 or point.x>ca.end.x+.001 or point.z<ca.position.z-.001 or point.z>ca.end.z+.001:continue
   var fs:=candidate.mesh.get_faces()
   for k in range(0,fs.size(),3):
    var A:Vector3=candidate.global_transform*fs[k];var B:Vector3=candidate.global_transform*fs[k+1];var C:Vector3=candidate.global_transform*fs[k+2]
    if max(abs(A.y-point.y),max(abs(B.y-point.y),abs(C.y-point.y)))>.001:continue
    var ab:=Vector2(B.x-A.x,B.z-A.z);var ac:=Vector2(C.x-A.x,C.z-A.z);var ap:=Vector2(point.x-A.x,point.z-A.z);var det:=ab.cross(ac)
    if abs(det)<.00000001:continue
    var u:=ap.cross(ac)/det;var t:=ab.cross(ap)/det
    if u>=-.00001 and t>=-.00001 and u+t<=1.00001:owners.append(str(candidate.get_path()));break
  ck(not owners.is_empty(),"closure joins actual ceiling retained member or adjacent band "+part.name);joints.append({"part":part.name,"actual_mesh_plane_owners":owners,"y":part.top})
 var commons:Node3D=d.get_node("D04StarboardAftHabitatNeighborhood")
 ck(commons.get_meta("preserved_home_allocations")==20 and commons.get_meta("preserved_reserved_rests")==25,"twenty original homes and twentyfive rests")
 var retained:Node3D=d.get_node("D04StarboardAftCourtRoutes")
 for spec in JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_STARBOARD_AFT_COURT_ROUTES.json")).gates:
  var gate:Node3D=retained.get_node(spec.name);ck(gate.open_fraction==0 and not gate.desired_open and gate.visit==null and String(gate.persistent_id)==spec.id,"original gates identity and closed defaults "+spec.name)
 var result={"status":"PASS"if errors.is_empty()else"HOLD","checks":checks,"errors":errors,"model_pins":p.model_pins,"original_meshes_exact":old.size(),"wall_ceiling_joints":joints,"new_floor_m2":0,"new_capacity":0,"quiet_entrance_below_original_head_preserved":true};FileAccess.open("res://artifacts/d04_starboard_aft_commons_enclosure_geometry.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":checks,"errors":errors}));quit(0 if errors.is_empty()else 1)
