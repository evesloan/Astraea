extends RefCounted
const P := "res://tidal_court_finish_20261023/"
const PLAN_SHA := "4899b37fa73be0e8eec4017918f31ad9fba2ca09720876c22feb42c1efc03be7"

static func receiving_error(ship:Node3D, plan:Dictionary)->String:
 var house:=ship.get_node_or_null("ShipSpace/Districts/TidalGardenReceivingCandidate")
 if house==null:return "Tidal receiving owner absent"
 if house.get_meta("persistent_id","")!="tidal_garden_house_001" or house.get_meta("installed_guest_units",0)!=131:return "Tidal allocation/identity differs"
 var parts:=source_parts(house,plan)
 if parts.size()!=334:return "Retained Tidal architecture identity set differs"
 for row in plan.surface_assignments:
  var m:MeshInstance3D=parts.get(row.node)
  if m==null or m.mesh==null or str(m.get_meta("extras",{}).get("role",""))!=row.role:return "Tidal surface owner differs: "+str(row.node)
  if m.mesh.get_surface_count()!=1 or not m.get_active_material(0) is StandardMaterial3D:return "Tidal surface material interface differs: "+str(row.node)
 for row in plan.lights:
  var m:MeshInstance3D=parts.get(row.mesh)
  if m==null or m.mesh==null:return "Tidal emitter owner absent"
  # Import compression/reindexing can change the decoded vertex stream.
  # Validate the immutable source owner's exact stored AABB and node pose;
  # the emitter is located from the hash-pinned raw source part bounds.
  var expected:=AABB(v(row.source_mesh_min),v(row.source_mesh_max)-v(row.source_mesh_min))
  var actual: AABB=m.transform*m.get_aabb()
  if actual.position.distance_to(expected.position)>.0001 or actual.end.distance_to(expected.end)>.0001:return "Tidal emitter owner pose differs: "+str(row.name)
 return ""

static func source_parts(house:Node,plan:Dictionary)->Dictionary:
 var result:={}
 for m:MeshInstance3D in house.find_children("*","MeshInstance3D",true,false):
  if str(m.get_meta("extras",{}).get("source_plan_sha256",""))==str(plan.source_plan_sha256):result[str(m.name)]=m
 return result

static func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])

static func build(ship:Node3D)->Node3D:
 if OS.get_environment("ASTRAEA_TIDAL_CANDIDATE_ISOLATION")=="1":return null
 if FileAccess.get_sha256(P+"PLAN.json")!=PLAN_SHA:push_error("Tidal court finish plan differs");return null
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PLAN.json"))
 if FileAccess.get_sha256(plan.model)!=plan.model_sha256 or FileAccess.get_sha256(plan.definition)!=plan.definition_sha256:push_error("Retained Tidal court source differs");return null
 var problem:=receiving_error(ship,plan)
 if not problem.is_empty():push_error(problem);return null
 var house:Node3D=ship.get_node("ShipSpace/Districts/TidalGardenReceivingCandidate")
 var old:=house.get_node_or_null("TidalCourtFinish_r001") as Node3D
 if old!=null:return old
 var parts:=source_parts(house,plan);var materials:={}
 # Original immutable texture, UV, transparency and culling settings survive.
 # Only the five declared opaque surface families receive shared successors.
 for row in plan.surface_assignments:
  var mesh:MeshInstance3D=parts[row.node]
  if not materials.has(row.role):
   var material:StandardMaterial3D=mesh.get_active_material(0).duplicate()
   var spec:Dictionary=plan.materials[row.role]
   material.resource_name="TidalCourtSurface_r001_"+str(row.role)
   material.albedo_color=Color(spec.tint[0],spec.tint[1],spec.tint[2],spec.tint[3])
   material.roughness=spec.roughness;material.metallic=spec.metallic
   materials[row.role]=material
  mesh.material_override=materials[row.role]
 var result:=Node3D.new();result.name="TidalCourtFinish_r001";house.add_child(result)
 for row in plan.lights:
  var light:=OmniLight3D.new();light.name=row.name;light.position=v(row.position)
  light.light_color=Color(row.color[0],row.color[1],row.color[2]);light.light_energy=row.energy
  light.omni_range=row.range;light.omni_attenuation=row.attenuation
  light.shadow_enabled=true;light.visible=false;light.set_meta("fixture_powered",true)
  light.set_meta("retained_fixture_source",row.source_part_id);result.add_child(light)
 result.set_meta("acceptance","source_candidate_not_final_visual_accepted")
 result.set_meta("surface_assignments",267);result.set_meta("shared_materials",materials.size())
 result.set_meta("new_geometry",0);result.set_meta("new_contacts",0)
 return result
