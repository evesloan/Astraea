extends RefCounted
const P := "res://tidal_arrival_finish_20261024/"
const PLAN_SHA := "0500a554e932ba497dacfc3880c0f6676e0838582aab3300aa5033501d5511f1"
const RUNTIME_SHA := "0f608bb5b156f1d836d9c254c7a04d12a80b86fed819d062e2b3829ad109f71c"
static func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func receiving_error(ship:Node3D,plan:Dictionary)->String:
 var house:=ship.get_node_or_null("ShipSpace/Districts/TidalGardenReceivingCandidate")
 if house==null or house.get_meta("persistent_id","")!="tidal_garden_house_001" or house.get_meta("installed_guest_units",0)!=131:return "Tidal receiving identity/allocation differs"
 if house.get_node_or_null("TidalCourtFinish_r001")==null:return "Protected five-level finish prerequisite absent"
 var original:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(plan.source_plan))
 var previous=load("res://tidal_court_finish_20261023/adapter_r002.gd")
 var problem:String=previous.receiving_error(ship,original)
 if not problem.is_empty():return problem
 var parts:Dictionary=previous.source_parts(house,original)
 for row in plan.supports:
  var mesh:MeshInstance3D=parts.get(row.node)
  if mesh==null:return "Header support absent: "+str(row.node)
  var a:AABB=mesh.transform*mesh.get_aabb()
  if a.position.distance_to(v(row.min))>.0001 or a.end.distance_to(v(row.max))>.0001:return "Header source support pose differs: "+str(row.node)
 return ""
static func build(ship:Node3D)->Node3D:
 if FileAccess.get_sha256(P+"PLAN_r002.json")!=PLAN_SHA or FileAccess.get_sha256(P+"runtime/TidalArrivalPortals_r002.scn")!=RUNTIME_SHA:push_error("Tidal arrival package bytes differ");return null
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PLAN_r002.json"))
 if FileAccess.get_sha256(plan.model)!=plan.model_sha256 or FileAccess.get_sha256(plan.source_plan)!=plan.source_plan_sha256:push_error("Tidal arrival source prerequisites differ");return null
 var problem:=receiving_error(ship,plan)
 if not problem.is_empty():push_error(problem);return null
 var house:Node3D=ship.get_node("ShipSpace/Districts/TidalGardenReceivingCandidate")
 var old:=house.get_node_or_null("TidalArrivalPortals_r002") as Node3D
 if old!=null:return old
 var pack:=load(P+"runtime/TidalArrivalPortals_r002.scn")as PackedScene
 if pack==null:push_error("Tidal arrival packed source missing");return null
 var result:=pack.instantiate()as Node3D;house.add_child(result)
 return result
