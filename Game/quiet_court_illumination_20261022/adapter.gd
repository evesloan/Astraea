extends RefCounted
const P:="res://quiet_court_illumination_20261022/"
static func build(ship:Node3D)->void:
 var house:Node3D=ship.get_node("ShipSpace/Districts/QuietGroveReceivingCandidate")
 assert(house.has_meta("court_finish_20261022") and not house.has_meta("court_illumination_20261022"))
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://quiet_court_finish_20261022/PLAN_R003.json"))
 var surfaces:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"SURFACES.json"))
 var materials:Dictionary={}
 for role:String in surfaces:
  var row:Dictionary=surfaces[role];var c:Array=row.color
  var m:=StandardMaterial3D.new();m.resource_name="QuietCourtSurface_r002_"+role
  m.albedo_color=Color(c[0],c[1],c[2],c[3]);m.roughness=row.roughness;m.metallic=row.metallic
  materials[role]=m
 var original_meshes:=0;var changed:=0
 for mesh:MeshInstance3D in house.find_children("*","MeshInstance3D",true,false):
  var e:Dictionary=mesh.get_meta("extras",{})
  if str(e.get("source_plan_sha256",""))!=str(plan.source_plan_sha256):continue
  original_meshes+=1
  var role:String=str(e.get("role",""))
  if materials.has(role):mesh.material_override=materials[role];changed+=1
 assert(original_meshes==580)
 var receiving:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/QUIET_GROVE_RECEIVING.json"))
 var fixtures:=0
 for row:Dictionary in receiving.lights:
  var xyz:=Vector3(row.world_xyz[0],row.world_xyz[1],row.world_xyz[2])
  var matches:Array=house.get_children().filter(func(n):return n is OmniLight3D and n.position.distance_to(xyz)<.001)
  assert(matches.size()==1)
  var light:OmniLight3D=matches[0]
  assert(not light.visible and not light.shadow_enabled,"Must run before budget.configure, once")
  # Opt the retained fixture into the existing guarded eight-source selector.
  # configure disables it until its power, proximity and visibility tests pass.
  light.shadow_enabled=true
  light.set_meta("quiet_court_budget_eligible",true)
  fixtures+=1
 assert(fixtures==79)
 house.set_meta("court_illumination_20261022",{"fixtures":fixtures,"material_meshes":changed,"original_meshes":original_meshes,"visual_accepted":false})
