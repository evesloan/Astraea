extends SceneTree
var checks:=0
var errors:Array=[]
func ck(ok:bool,label:String):
 checks+=1
 if not ok:errors.append(label);print("FAIL ",label)
func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func _initialize():call_deferred("run")
func run():
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_COMMONS_CEILING_JUNCTIONS.json"));var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var d:Node3D=ship.get_node("ShipSpace/Districts");var space:=ship.get_world_3d().direct_space_state;var old:Dictionary={}
 for root_name in ["D04PortCentralHabitatNeighborhood","D04PortCentralCommonsRearRoute","D04StarboardCentralCourtRoutes","D04StarboardAftCourtRoutes"]:
  for mesh:MeshInstance3D in d.get_node(root_name).find_children("*","MeshInstance3D",true,false):old[str(mesh.get_path())]={"mesh":mesh,"faces":mesh.mesh.get_faces(),"pose":mesh.global_transform}
 var n:Node3D=load("res://scripts/d04_commons_ceiling_junctions.gd").build(ship,true)
 for i in range(30):await physics_frame
 for key in old:
  var q:Dictionary=old[key];ck(is_instance_valid(q.mesh)and q.mesh.mesh.get_faces()==q.faces and q.mesh.global_transform==q.pose,"source mesh and pose exact "+key)
 var cap_rids:Array[RID]=[]
 for body:StaticBody3D in n.find_children("*","StaticBody3D",true,false):cap_rids.append(body.get_rid())
 var joints:Array=[]
 for part in p.parts:
  var mesh:MeshInstance3D=n.find_child(part.name,true,false);ck(mesh!=null,"new source-native cap "+part.name)
  var a:AABB=mesh.global_transform*mesh.get_aabb();ck(a.position.distance_to(v(part.expected_bounds[0]))<.001 and a.end.distance_to(v(part.expected_bounds[1]))<.001,"cap exact authored bounds "+part.name)
  var original:MeshInstance3D=d.get_node(part.source_root).find_child(part.source_name,true,false);ck(original!=null,"named original wall owner "+part.source_name);var oa:AABB=original.global_transform*original.get_aabb();ck(abs(oa.end.y-part.bottom)<.001,"closure starts at exact wall top "+part.source_name)
  var x:float=(a.position.x+a.end.x)/2;var z:float=(a.position.z+a.end.z)/2
  # Use an interior point of the wall footprint, avoiding boundary-edge ray ambiguity.
  var ray:=PhysicsRayQueryParameters3D.create(Vector3(x,part.top+.025,z),Vector3(x,part.top-.025,z));ray.hit_back_faces=true;ray.exclude=cap_rids;var h:=space.intersect_ray(ray);ck(not h.is_empty(),"cap reaches retained ceiling "+part.name)
  if not h.is_empty():ck(abs(h.position.y-part.top)<.001,"exact ceiling underside datum "+part.name);joints.append({"part":part.name,"ceiling_owner":str(h.collider.get_path()),"y":h.position.y})
  var box:=BoxShape3D.new();box.size=Vector3(max(.002,a.size.x-.004),max(.002,a.size.y-.01),max(.002,a.size.z-.004));var q:=PhysicsShapeQueryParameters3D.new();q.shape=box;q.transform=Transform3D(Basis.IDENTITY,a.get_center());q.exclude=cap_rids;var hits:=space.intersect_shape(q,64);ck(hits.is_empty(),"closure adds no unexplained occupied-geometry overlap "+part.name)
  if not hits.is_empty():print("CAP_CONTACT ",part.name," ",hits.map(func(row):return str(row.collider.get_path())))
 var court:Node3D=d.get_node("D04StarboardCentralHabitatNeighborhood");var screen:MeshInstance3D=d.get_node("D04StarboardCentralCourtRoutes").find_child("SCK_D04HC3_east_PrivacyScreen",true,false);var upper:MeshInstance3D=d.get_node("D04StarboardCentralCourtRoutes").find_child("SCK_D04HC3_east_GlassUpper",true,false);var roof:MeshInstance3D=court.find_child("SCK_D04HC3_east_Roof",true,false);ck(screen!=null and upper!=null and roof!=null,"court screen upper glass and roof retained");var ua:AABB=upper.global_transform*upper.get_aabb();var ra:AABB=roof.global_transform*roof.get_aabb();ck(abs(ua.end.y-ra.position.y)<.001,"court upper glass already reaches original roof")
 var commons:Node3D=d.get_node("D04PortCentralCommonsRearRoute")
 for g in JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PORT_CENTRAL_COMMONS_RECOMPOSITION.json")).gates:
  var gate:Node3D=commons.get_node(g.name);ck(gate.open_fraction==0 and not gate.desired_open and String(gate.persistent_id)==g.id,"original staff gate default and identity intact "+g.name)
 var result={"status":"PASS"if errors.is_empty()else"HOLD","checks":checks,"errors":errors,"model_pins":p.model_pins,"original_meshes_exact":old.size(),"wall_ceiling_joints":joints,"new_floor_m2":0,"new_capacity":0,"court_glazing_retained_to_roof":true};FileAccess.open("res://artifacts/d04_commons_ceiling_junctions_geometry.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":checks,"errors":errors}));quit(0 if errors.is_empty()else 1)
