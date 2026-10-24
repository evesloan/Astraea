extends RefCounted
const P:="res://sunset_enclosure_finish_20261024/"
const PLAN_SHA:="2a5081884350fdcf8d46c91eb23305d4edfc0fabea6163ddec3258ebdd93ae51"
const RUNTIME_SHA:="0b51dbab8eb017d77d7927bb6ff5b80e418d7bbcd881ffee060876d071683a5d"
static func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func parts(house:Node,plan:Dictionary)->Dictionary:
 var found:={}
 for mesh:MeshInstance3D in house.find_children("*","MeshInstance3D",true,false):
  if str(mesh.get_meta("extras",{}).get("source_plan_sha256",""))==plan.source_extras_plan_sha256:found[str(mesh.name)]=mesh
 return found
static func receiving_error(ship:Node3D,plan:Dictionary)->String:
 var house:=ship.get_node_or_null("ShipSpace/Districts/SunsetReceivingCandidate")
 var district:=ship.get_node_or_null("ShipSpace/Districts/SunsetSpecialty47_20261022")
 if house==null or house.get_meta("persistent_id","")!="sunset_house_001" or house.get_meta("installed_guest_units",0)!=83:return "Sunset original house/83-home identity differs"
 if district==null or district.get_meta("reserved_rests",0)!=59 or district.get_meta("new_capacity",-1)!=0:return "Sunset specialty/rest identity differs"
 if not house.has_meta("sunset_court_finish_20261022") or house.get_node_or_null("SunsetCourtFinish20261022")==null:return "Retained court finish missing"
 if house.get_node("RetainedLandscapeAndSeating").get_child_count()!=133:return "Retained landscape identity set differs"
 var found:=parts(house,plan)
 for row in plan.surface_assignments:
  var mesh:MeshInstance3D=found.get(row.node)
  if mesh==null or mesh.mesh==null:return "Sunset solid surface owner absent: "+str(row.node)
  var extras:Dictionary=mesh.get_meta("extras",{})
  if str(extras.role)!=row.role or str(extras.category)!=row.category:return "Sunset source role/category differs"
  var a:AABB=mesh.transform*mesh.get_aabb()
  if a.position.distance_to(v(row.min))>.0001 or a.end.distance_to(v(row.max))>.0001:return "Sunset receiving source bounds differ: "+str(row.node)
 return ""
static func build(ship:Node3D)->Node3D:
 if FileAccess.get_sha256(P+"PLAN.json")!=PLAN_SHA or FileAccess.get_sha256(P+"runtime/SunsetEnclosure_r001.scn")!=RUNTIME_SHA:push_error("Sunset enclosure package bytes differ");return null
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PLAN.json"))
 if FileAccess.get_sha256(plan.model)!=plan.model_sha256:push_error("Sunset original architecture bytes differ");return null
 var problem:=receiving_error(ship,plan)
 if not problem.is_empty():push_error(problem);return null
 var house:Node3D=ship.get_node("ShipSpace/Districts/SunsetReceivingCandidate")
 var old:=house.get_node_or_null("SunsetEnclosure_r001")as Node3D
 if old!=null:return old
 var found:=parts(house,plan);var materials:={}
 for row in plan.surface_assignments:
  if not materials.has(row.role):
   var source:=load(P+"runtime/"+str(row.role)+".tres")as StandardMaterial3D
   if source==null:push_error("Sunset enclosure native material unavailable");return null
   var material:=source.duplicate()as StandardMaterial3D
   # Retained geometry/UVs remain immutable. World-metre projection makes the
   # native texture legible on existing source surfaces without rebuilding them.
   material.uv1_triplanar=true;material.uv1_world_triplanar=true;material.uv1_scale=Vector3.ONE
   materials[row.role]=material
 var packed:=load(P+"runtime/SunsetEnclosure_r001.scn")as PackedScene
 if packed==null:push_error("Sunset enclosure runtime absent");return null
 var result:=packed.instantiate()as Node3D
 for row in plan.surface_assignments:found[row.node].material_override=materials[row.role]
 house.add_child(result);result.set_meta("changed_original_materials",plan.surface_assignments.size())
 return result
