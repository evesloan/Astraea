extends RefCounted
const P := "res://tidal_d14_landing_20261023/"
const PLAN_SHA := "d689b52b41225cc4be42e0f92f21ec4d0b62d043a9c65149ecc97792b648e3bf"
const RUNTIME_SHA := "147b39abd668440376d64ba0b55f95ad3e4ece56358bda5443d3b79422f98a7d"
static func receiving_error(ship:Node3D)->String:
 var house:=ship.get_node_or_null("ShipSpace/Districts/TidalGardenReceivingCandidate")
 if house==null:return "Retained Tidal receiving owner is absent"
 if house.get_meta("persistent_id","")!="tidal_garden_house_001":return "Tidal identity differs"
 if int(house.get_meta("installed_guest_units",-1))!=131:return "Tidal installed allocation contract differs"
 var seats:=house.get_node_or_null("RetainedLandscapeAndSeating")
 if seats==null:return "Retained furniture owner absent"
 var def:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/TIDAL_LIFT_RECEIVING_CANDIDATE.json"))
 for row in def.retained_asset_instances:
  if not str(row.name) in ["D14_LandingSeat_-89","D14_LandingSeat_-85","D14_LandingTable"]:continue
  var node:=seats.get_node_or_null(NodePath(str(row.name))) as Node3D
  if node==null:return "Retained landing furniture absent: "+str(row.name)
  var p:Array=row.world_xyz
  if node.position.distance_to(Vector3(p[0],p[1],p[2]))>.00001:return "Retained furniture position changed"
 return ""
static func build(ship:Node3D)->Node3D:
 if OS.get_environment("ASTRAEA_TIDAL_CANDIDATE_ISOLATION")=="1":return null
 if FileAccess.get_sha256(P+"PLAN.json")!=PLAN_SHA or FileAccess.get_sha256(P+"runtime/TidalD14Landing_r001.scn")!=RUNTIME_SHA:
  push_error("Tidal D14 landing exact source package differs");return null
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PLAN.json"))
 if FileAccess.get_sha256("res://data/architecture/TIDAL_LIFT_RECEIVING_CANDIDATE.json")!=plan.original_definition_sha256 or FileAccess.get_sha256("res://assets/models/AST-RES-TIDAL_lift_fit_r003.glb")!=plan.source_model_sha256:
  push_error("Retained Tidal floor/architecture bytes changed");return null
 var reason:=receiving_error(ship)
 if not reason.is_empty():push_error(reason);return null
 var house:Node3D=ship.get_node("ShipSpace/Districts/TidalGardenReceivingCandidate")
 var existing:=house.get_node_or_null("TidalD14Landing_r001") as Node3D
 if existing!=null:return existing
 var packed:=load(P+"runtime/TidalD14Landing_r001.scn") as PackedScene
 if packed==null:push_error("Tidal landing runtime unavailable");return null
 var addition:=packed.instantiate() as Node3D;house.add_child(addition)
 addition.set_meta("acceptance","integrated_construction_wip_not_visual_accepted")
 addition.set_meta("new_floors",0);addition.set_meta("new_guest_units",0);addition.set_meta("new_reserved_rests",0)
 return addition

static func after_step(ship:Node3D,label:String)->Node3D:
 if label!="tidal_garden_adoption.gd":return null
 return build(ship)
