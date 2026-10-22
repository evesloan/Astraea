extends RefCounted
static func build(ship:Node3D)->void:
 var house:Node3D=ship.get_node("ShipSpace/Districts/QuietGroveReceivingCandidate")
 assert(house.has_meta("court_illumination_20261022") and not house.has_meta("court_balance_20261022"))
 var source:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/QUIET_GROVE_RECEIVING.json"))
 var counts:Dictionary={"canopy":0,"gallery":0,"lobby":0}
 for row:Dictionary in source.lights:
  var p:=Vector3(row.world_xyz[0],row.world_xyz[1],row.world_xyz[2])
  var matches:Array=house.get_children().filter(func(n):return n is OmniLight3D and n.position.distance_to(p)<.001)
  assert(matches.size()==1)
  var light:OmniLight3D=matches[0]
  assert(light.shadow_enabled and not light.visible)
  var role:String="canopy" if str(row.name).begins_with("CourtCanopy") else ("gallery" if str(row.name).begins_with("Gallery") else "lobby")
  counts[role]+=1
  # Preserve authored emitter/target locations; recover source-role hierarchy.
  light.light_energy=2.0 if role=="canopy" else (1.1 if role=="gallery" else 1.25)
  light.omni_range=34.0 if role=="canopy" else 18.0
  light.omni_attenuation=.65 if role=="canopy" else .85
  light.light_color=Color(1,.94,.84) if role=="canopy" else Color(1,.90,.77)
 var materials:Dictionary={};var affected:=0
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://quiet_court_finish_20261022/PLAN_R003.json"))
 for mesh:MeshInstance3D in house.find_children("*","MeshInstance3D",true,false):
  var e:Dictionary=mesh.get_meta("extras",{})
  if str(e.get("source_plan_sha256",""))!=str(plan.source_plan_sha256):continue
  var role:String=str(e.get("role",""))
  if role not in ["warm_stone","warm_walnut","oatmeal_weave"]:continue
  if not materials.has(role):
   var m:StandardMaterial3D=mesh.material_override.duplicate()
   var noise:=FastNoiseLite.new();noise.seed=421;noise.frequency=.075
   var gradient:=Gradient.new();gradient.set_color(0,Color(.80,.80,.80));gradient.set_color(1,Color(1,1,1))
   var texture:=NoiseTexture2D.new();texture.width=128;texture.height=128;texture.seamless=true;texture.noise=noise;texture.color_ramp=gradient
   m.albedo_texture=texture;m.uv1_triplanar=true;m.uv1_world_triplanar=true
   m.uv1_scale=Vector3(.16,2.0,.16) if role=="warm_walnut" else Vector3(.65,.65,.65)
   m.resource_name="QuietCourtSurface_r003_"+role;materials[role]=m
  mesh.material_override=materials[role];affected+=1
 assert(counts.canopy>0 and counts.gallery>0 and counts.canopy+counts.gallery+counts.lobby==79)
 house.set_meta("court_balance_20261022",{"roles":counts,"textured_meshes":affected,"shared_textures":materials.size(),"budget":8,"geometry_changed":false,"visual_accepted":false})
