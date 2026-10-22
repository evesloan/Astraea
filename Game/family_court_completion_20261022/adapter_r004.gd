extends RefCounted
const P:="res://family_court_completion_20261022/"
static func build(ship:Node3D)->void:
 var house:Node3D=ship.get_node("ShipSpace/Districts/FamilyTerraceReceivingCandidate")
 assert(ship.has_node("ShipSpace/Districts/FamilySpecialty47_20261022"))
 assert(not house.has_meta("family_court_completion_20261022"))
 assert(FileAccess.get_sha256(P+"PLAN_R004.json")=="e57e882be9525871e9ad715bf963ea07a2b099dca02c3d68f4ca5c3e04e13b7a")
 assert(FileAccess.get_sha256(P+"runtime/FamilyForwardCourt_r004.scn")=="03ba136ae0549f41e224c67025f8630de1bb88f9e582f4eb85b101fe673e93b9")
 assert(FileAccess.get_sha256("res://data/architecture/FAMILY_TERRACE_RECEIVING.json")=="36ff6a961dcb5d84f7d5c387bd72b11a347ea1eb727bc0b2750a580a1cbb64fe")
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PLAN_R004.json"))
 var mats:={}
 for role:String in plan.materials:
  var row:Dictionary=plan.materials[role];var c:Array=row.color;var m:=StandardMaterial3D.new();m.resource_name="FamilyCourt_"+role;m.albedo_color=Color(c[0],c[1],c[2],c[3]);m.roughness=row.roughness;m.metallic=row.metallic
  mats[role]=m
 var changed:=0;var preserved_glass:=0
 for mesh:MeshInstance3D in house.find_children("*","MeshInstance3D",true,false):
  var e:Dictionary=mesh.get_meta("extras",{})
  if str(e.get("source_plan_sha256",""))!="bd0ecf9d52e8f445c31c7b4222aa664a75fc8a1ff9553d01fecd27ad9ceddf2c":continue
  var role:String=str(e.get("role",""))
  if role=="glass":preserved_glass+=1;continue
  if mats.has(role):mesh.material_override=mats[role];changed+=1
 assert(changed>0 and preserved_glass>0)
 var additive:Node3D=load(P+"runtime/FamilyForwardCourt_r004.scn").instantiate();house.add_child(additive)
 assert(additive.find_children("*","OmniLight3D",true,false).size()==3)
 assert(house.get_node("RetainedLandscapeAndSeating").get_child_count()==157)
 house.set_meta("family_court_completion_20261022",{"material_meshes":changed,"preserved_glass":preserved_glass,"coping_bands":2,"soil_finish":2,"roof_profiles":3,"added_understory":36,"added_fixtures":3,"global_light_budget":8,"visual_accepted":false})
