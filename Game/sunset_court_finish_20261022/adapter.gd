extends RefCounted
const P:="res://sunset_court_finish_20261022/"
static func build(ship:Node3D)->void:
 var house:Node3D=ship.get_node("ShipSpace/Districts/SunsetReceivingCandidate")
 assert(ship.has_node("ShipSpace/Districts/SunsetSpecialty47_20261022"))
 assert(not house.has_meta("sunset_court_finish_20261022"))
 assert(FileAccess.get_sha256(P+"PLAN_R003.json")=="c88cbf3d4e9419b9f671f6ac10458508ad2e459c51fb796b815f2ca82c78f0e7")
 assert(FileAccess.get_sha256(P+"runtime/SunsetCourtFinish_r003.scn")=="6e3f05fe9c0f83bbf7fb7235950c9948e1e2e232310b8288181d989fcfbb2009")
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PLAN_R003.json"))
 var mats:={}
 for role:String in plan.materials:
  var row:Dictionary=plan.materials[role];var c:Array=row.color;var m:=StandardMaterial3D.new();m.resource_name="SunsetCourt_"+role;m.albedo_color=Color(c[0],c[1],c[2],c[3]);m.roughness=row.roughness;m.metallic=row.metallic
  mats[role]=m
 var changed:=0;var preserved_glass:=0
 for mesh:MeshInstance3D in house.find_children("*","MeshInstance3D",true,false):
  var e:Dictionary=mesh.get_meta("extras",{})
  if str(e.get("source_plan_sha256",""))!=str(plan.source_plan_sha256):continue
  var role:String=str(e.get("role",""))
  if role=="glass":preserved_glass+=1;continue
  if mats.has(role):mesh.material_override=mats[role];changed+=1
 assert(changed>0 and preserved_glass>0)
 var additive:Node3D=load(P+"runtime/SunsetCourtFinish_r003.scn").instantiate();house.add_child(additive)
 assert(additive.find_children("*","OmniLight3D",true,false).size()==8)
 assert(house.get_node("RetainedLandscapeAndSeating").get_child_count()==133)
 house.set_meta("sunset_court_finish_20261022",{"material_meshes":changed,"preserved_glass":preserved_glass,"coping_bands":22,"soil_finish":22,"roof_profiles":8,"added_understory":99,"added_fixtures":8,"global_light_budget":8,"visual_accepted":false})
