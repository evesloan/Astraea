extends RefCounted
# Isolated receiving candidate. No controller, root-light-budget or source-room edits.
# Source/import fidelity, complete runtime routes and final design review remain gates.
const MANIFEST := "res://data/architecture/botanical_pair/runtime_manifest.json"

static func _v(value: Array) -> Vector3:
 return Vector3(float(value[0]),float(value[1]),float(value[2]))

static func _file_matches(file: String, expected: String) -> bool:
 return expected.length()==64 and FileAccess.file_exists(file) and FileAccess.get_sha256(file)==expected

static func validate_inputs() -> bool:
 var parsed=JSON.parse_string(FileAccess.get_file_as_string(MANIFEST))
 if not parsed is Dictionary: return false
 var data:Dictionary=parsed
 # Explicit return gate still operates when debug assertions are disabled.
 if not bool(data.get("activation_ready",false)): return false
 if data.sections.size()!=2 or data.required_floor_records.size()!=3: return false
 for asset in [data.court_successor,data.cloud_link_guard]:
  if not _file_matches("res://assets/models/"+str(asset.model_file),str(asset.runtime_sha256)): return false
 if str(data.court_successor.existing_node_name)!="BotanicalCourtReceivingClosedInterim": return false
 if not _file_matches(str(data.lighting_budget.script),str(data.lighting_budget.sha256)): return false
 if not _file_matches(str(data.lighting_budget.profile_file),str(data.lighting_budget.profile_sha256)): return false
 if int(data.lighting_budget.shadow_source_budget)!=8 or int(data.lighting_budget.visibility_candidates)!=32: return false
 if not _file_matches(str(data.nursery_fixture_lighting_proposal.file),str(data.nursery_fixture_lighting_proposal.sha256)): return false
 if not _file_matches(str(data.nursery_fixture_position_proof.file),str(data.nursery_fixture_position_proof.sha256)): return false
 var proposal:Array=JSON.parse_string(FileAccess.get_file_as_string(str(data.nursery_fixture_lighting_proposal.file)))
 if proposal.size()!=30: return false
 for section in data.sections:
  if not _file_matches("res://assets/models/"+str(section.model_file),str(section.runtime_sha256)): return false
  if section.rotation!=[0.0,0.0,0.0] or section.scale!=[1.0,1.0,1.0]: return false
  if str(section.programme)=="D06_directory_04":
   if section.position!=[8.0,27.0,-216.0] or int(section.source_punctual_light_count)!=0: return false
   if section.mounted_receiving_lights.size()!=30: return false
   var used:Dictionary={}
   for spec in section.mounted_receiving_lights:
    var i:=int(spec.proposal_index)
    if i<0 or i>=proposal.size() or used.has(i): return false
    used[i]=true
    if str(spec.fixture_source_name)!=str(proposal[i].fixture): return false
    var original:Array=proposal[i].source_position
    var source_world:=Vector3(8+float(original[0]),27+float(original[2]),-216-float(original[1]))
    if _v(spec.world_position).distance_to(source_world)>.0001: return false
    if _v(spec.proposal_world_emitter).distance_to(_v(proposal[i].world_emitter))>.0001: return false
    if str(spec.profile)!="guest_lounge" or float(spec.source_energy_watts)!=float(proposal[i].energy_watts): return false
    if _v(spec.world_direction).length()<.99: return false
    if float(spec.energy)<=0 or float(spec.range_m)<=0 or float(spec.angle_degrees)<=0 or float(spec.angle_degrees)>=90: return false
  elif str(section.programme)=="D06_directory_02":
   if section.position!=[0.0,0.0,0.0] or int(section.source_punctual_light_count)!=36: return false
  else: return false
 var compiled:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
 if compiled.regions.size()!=303: return false
 var found:=0
 for expected in data.required_floor_records:
  for actual in compiled.regions:
   if str(actual.id)==str(expected.id):
    if actual!=expected: return false
    found+=1
 return found==3

static func build(ship: Node3D) -> Node3D:
 if not validate_inputs():
  push_error("Botanical pair candidate inputs or required receiving gates are not finalized")
  return null
 var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(MANIFEST))
 var space:Node3D=ship.get_node("ShipSpace")
 assert(space.get_node_or_null(str(data.root_name))==null)
 var court:Node3D=space.get_node(str(data.court_successor.existing_node_name))
 assert(court.get_meta("catalogue_file","")==str(data.court_successor.model_file))
 var floors:Node3D=space.get_node("CompiledStructuralFloors_NotFinishedRooms")
 for record in data.required_floor_records: assert(floors.has_node(NodePath(str(record.id))))
 var root:=Node3D.new();root.name=str(data.root_name);space.add_child(root)
 root.set_meta("operational_acceptance",false)
 root.set_meta("design_acceptance",false)
 root.set_meta("receiving_runtime_validation_pending",true)
 for section in data.sections:
  var room:=Node3D.new();room.name=str(section.root_name);root.add_child(room)
  room.set_meta("programme_key",str(section.programme))
  room.set_meta("source_sha256",str(section.runtime_sha256))
  var source:Node3D=ship.model(room,str(section.model_file),"Source",_v(section.position))
  var retained:Array=source.find_children("*","Light3D",true,false)
  assert(retained.size()==int(section.source_punctual_light_count))
  for light in retained:
   assert(light is SpotLight3D or light is OmniLight3D)
   # Register all punctual fixtures with the existing eight-source selector.
   light.visible=false;light.shadow_enabled=true
   light.set_meta("fixture_powered",true)
   light.set_meta("receiving_calibration_pending",true)
  for spec in section.mounted_receiving_lights:
   var lamp:=SpotLight3D.new();lamp.name="MountedSourceFixture_%02d"%int(spec.proposal_index)
   room.add_child(lamp);lamp.global_position=_v(spec.world_position)
   var direction:Vector3=_v(spec.world_direction).normalized()
   var up:Vector3=Vector3.FORWARD if absf(direction.dot(Vector3.UP))>.99 else Vector3.UP
   lamp.look_at(lamp.global_position+direction,up)
   ship.apply_light_profile(lamp,"guest_lounge")
   lamp.spot_angle=float(spec.angle_degrees)
   lamp.visible=false;lamp.shadow_enabled=true
   lamp.set_meta("fixture_powered",true)
   lamp.set_meta("source_fixture",str(spec.fixture_source_name))
   lamp.set_meta("source_energy_watts",float(spec.source_energy_watts))
   lamp.set_meta("source_type","AREA")
   lamp.set_meta("proposal_world_emitter",_v(spec.proposal_world_emitter))
   lamp.set_meta("actual_source_world_position",_v(spec.world_position))
   lamp.set_meta("proposal_minus_actual_world_m",_v(spec.proposal_minus_actual_world_m))
   lamp.set_meta("area_light_proxy",true)
   lamp.set_meta("receiving_calibration_pending",true)
 ship.model(root,str(data.cloud_link_guard.model_file),"CloudLinkAuthoredReceivingGuards",Vector3.ZERO)
 # Ship calls its existing LocalShadowSourceBudget.configure exactly once after build.
 return root
