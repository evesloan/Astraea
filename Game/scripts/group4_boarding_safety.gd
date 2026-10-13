extends Node3D
# Local mechanical adapter only. Existing input and the shared single tram remain the owners.
const DATA := "res://data/architecture/GROUP4_BOARDING_SAFETY_CANDIDATE.json"
const MODELS := "res://source_derivatives/group4_boarding_safety_20261011/"
var plan:Dictionary
var base:Node3D
var vehicle:AnimatableBody3D
var station_gates:Dictionary={}
var car_gates:Dictionary={}
var bridges:Dictionary={}
var phase:="secured"
var selected_station:=""
var stationary_frames:=0
var previous_vehicle_pose:=Transform3D.IDENTITY
var clamp_bodies:Array[AnimatableBody3D]=[]
var clamp_translations:Array[Vector3]=[]
var clamp_fraction:=0.0
var source_clamp_target:=false
static func data()->Dictionary:return JSON.parse_string(FileAccess.get_file_as_string(DATA))
static func model(role:String,p:Dictionary)->Dictionary:
 for item in p.models:
  if item.role==role:return item
 assert(false,"Missing Group4 model role");return {}
static func static_visual(parent:Node3D,item:Dictionary)->Node3D:
 assert(FileAccess.get_sha256(MODELS+item.file)==item.sha256)
 var n:Node3D=(load(MODELS+item.file) as PackedScene).instantiate();parent.add_child(n)
 var policies:Dictionary={};var meshes:Array[Node]=[];var count:=0
 for key:String in item.policies:policies[key.validate_node_name()]=item.policies[key]
 for mesh:MeshInstance3D in n.find_children("*","MeshInstance3D",true,false):
  count+=1;assert(policies.has(str(mesh.name)))
  if policies[str(mesh.name)]!="no_collision_detail":meshes.append(mesh)
 assert(count==policies.size());load("res://scripts/static_contact_cache.gd").attach_group(n,meshes)
 n.set_meta("verified_source_members",count);return n
static func build_terminals(parent:Node3D,candidate_only:bool=false)->Node3D:
 var p:Dictionary=data()
 if not p.get("terminal_active",false) and not candidate_only:return null
 assert(not parent.has_node("Group4TerminalBranches"))
 var n:=Node3D.new();n.name="Group4TerminalBranches";parent.add_child(n)
 static_visual(n,model("terminals",p))
 for item in p.terminal_interface.fixture_instances:
  var light:=OmniLight3D.new();light.name=item.name+"_Light";n.add_child(light)
  light.position=Vector3(item.emitter[0],item.emitter[1],item.emitter[2]);light.omni_range=item.range;light.light_energy=item.energy
  light.light_color=Color(item.color[0],item.color[1],item.color[2]);light.visible=false;light.shadow_enabled=true
  light.omni_shadow_mode=OmniLight3D.SHADOW_CUBE;light.set_meta("source_fixture",item.name);light.set_meta("fixture_powered",true)
 return n
static func register_lights_with_budget(n:Node3D,budget:Node)->void:
 for light:Light3D in n.find_children("*","Light3D",true,false):
  assert(not budget.requested_shadow.has(light.get_instance_id()))
  budget.sources.append(light);budget.requested_shadow[light.get_instance_id()]=true
 budget.refresh()
static func create_candidate_vehicle(parent:Node3D,at:Vector3)->AnimatableBody3D:
 # Construction test factory. No cart/products, motor, save identity or transport controller is created.
 var p:Dictionary=data();var item:Dictionary=model("vehicle",p)
 assert(FileAccess.get_sha256(MODELS+item.file)==item.sha256)
 var body:=AnimatableBody3D.new();body.name="Group4VehicleConstructionCandidate";body.sync_to_physics=false
 parent.add_child(body);body.position=at;body.set_meta("source_vehicle_model",item.file)
 var visual:Node3D=(load(MODELS+item.file) as PackedScene).instantiate();body.add_child(visual)
 var c:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(MODELS+"VEHICLE_COLLISION_PROPOSAL.json"))
 var modified:Dictionary={}
 for key:String in c.modified_members:modified[key.validate_node_name()]=c.modified_members[key]
 var policies:Dictionary={}
 for key:String in item.policies:
  var name:String=key.validate_node_name();assert(not policies.has(name));policies[name]=item.policies[key]
 for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
  assert(policies.has(str(mesh.name)),"Every source vehicle member requires its exact contact policy")
  if policies[str(mesh.name)]=="no_collision_detail":continue
  if modified.has(str(mesh.name)):
   for cell in modified[str(mesh.name)]:
    var shape:=ConvexPolygonShape3D.new();var points:=PackedVector3Array()
    for y in cell.y:
     for point in cell.triangle_xz:points.append(Vector3(point[0],y,point[1]))
    shape.points=points;shape.margin=.001;var col:=CollisionShape3D.new();col.shape=shape;body.add_child(col)
  else:
   var col:=CollisionShape3D.new();col.shape=mesh.mesh.create_convex_shape(false,false);col.shape.margin=.001
   col.transform=body.global_transform.affine_inverse()*mesh.global_transform;body.add_child(col)
 body.sync_to_physics=true;return body
static func build(parent:Node3D,existing_base:Node3D,existing_vehicle:AnimatableBody3D,candidate_only:bool=false)->Node3D:
 var p:Dictionary=data()
 if not p.active and not candidate_only:return null
 assert(not parent.has_node("Group4BoardingSafety"))
 var n:Node3D=load("res://scripts/group4_boarding_safety.gd").new()
 n.name="Group4BoardingSafety";n.plan=p;n.base=existing_base;n.vehicle=existing_vehicle;parent.add_child(n);return n
func _ready()->void:
 assert(FileAccess.get_sha256("res://assets/models/AST-DOR-003.glb")==plan.existing_gate_model_sha256)
 assert(vehicle.get_meta("source_vehicle_model","")==model("vehicle",plan).file,"Use the exact separate slotted successor; never overwrite original011")
 previous_vehicle_pose=vehicle.global_transform;process_physics_priority=-25
 static_visual(self,model("barrier_receivers",plan))
 for st in plan.station_mounts:
  var bridge:Node3D=base.get_node("Group4Bridge_"+st.station);bridges[st.station]=bridge
  var gate:Node3D=load("res://scripts/lift_gate.gd").new();gate.name="BoardingBarrier_"+st.station
  gate.persistent_id=StringName("group4_"+st.station.to_lower()+"_boarding_barrier_proposal")
  var pose:Transform3D=bridge.global_transform*Transform3D(Basis.IDENTITY,Vector3(-.32,0,0))
  gate.transform=global_transform.affine_inverse()*pose;gate.rotate_y(PI/2)
  gate.scale=Vector3(st.gate_scale[0],st.gate_scale[1],st.gate_scale[2]);add_child(gate);station_gates[st.station]=gate
 for item in plan.vehicle_gate_placements:
  var gate:Node3D=load("res://scripts/lift_gate.gd").new();gate.name="PoweredCarPortal_"+item.side
  gate.persistent_id=StringName("group4_vehicle_"+item.side.to_lower()+"_portal_proposal")
  gate.position=Vector3(item.origin[0],item.origin[1],item.origin[2]);gate.rotation.y=item.yaw;gate.scale=Vector3(item.scale[0],item.scale[1],item.scale[2]);vehicle.add_child(gate)
  # Fixed frame triangles move with the same car body; no hollow source is filled with a box.
  for mesh:MeshInstance3D in gate.find_children("LIFT_fixed_*","MeshInstance3D",true,false):
   var faces:=PackedVector3Array();var pose:Transform3D=vehicle.global_transform.affine_inverse()*mesh.global_transform
   for vertex in mesh.mesh.get_faces():faces.append(pose*vertex)
   var col:=CollisionShape3D.new();var shape:=ConcavePolygonShape3D.new();shape.set_faces(faces);col.shape=shape;vehicle.add_child(col)
  for node in gate.find_children("StaticContact","StaticBody3D",true,false):node.queue_free()
  car_gates[item.side]=gate
 _build_restraint_hardware()
func _build_restraint_hardware()->void:
 var item:Dictionary=model("restraint",plan);assert(FileAccess.get_sha256(MODELS+item.file)==item.sha256)
 var source:Node3D=(load(MODELS+item.file) as PackedScene).instantiate();vehicle.add_child(source)
 var fixed:Node3D=source.find_child("RESTRAINT_FIXED_ROOT",true,false);assert(fixed!=null)
 for mesh:MeshInstance3D in fixed.find_children("*","MeshInstance3D",true,false):
  var col:=CollisionShape3D.new();col.shape=mesh.mesh.create_convex_shape(false,false);col.shape.margin=.001
  col.transform=vehicle.global_transform.affine_inverse()*mesh.global_transform;vehicle.add_child(col)
 for marker:Node3D in source.find_children("CLAMP_MOVING_*","Node3D",true,false):
  var body:=AnimatableBody3D.new();body.name=marker.name;body.sync_to_physics=false;vehicle.add_child(body)
  for mesh:MeshInstance3D in marker.find_children("*","MeshInstance3D",true,false):
   var pose:Transform3D=body.global_transform.affine_inverse()*mesh.global_transform
   mesh.reparent(body,true);mesh.transform=pose;var col:=CollisionShape3D.new();col.shape=mesh.mesh.create_convex_shape(false,false);col.shape.margin=.001;col.transform=pose;body.add_child(col)
  clamp_bodies.append(body);clamp_translations.append(Vector3(.139 if "PORT_" in str(body.name) and not "STARBOARD" in str(body.name) else -.139,0,0));body.sync_to_physics=true
 assert(clamp_bodies.size()==4)
func _physical_dock_matches(station:String)->bool:
 if stationary_frames<15:return false
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/GROUP4_COMPLETION_CANDIDATE.json"))
 for st in p.stations:
  if st.label==station:
   return vehicle.global_position.distance_to(Vector3(st.track_x,56.1,st.physical_docking_z))<.005 and abs(vehicle.global_rotation.y)<.001
 return false
func request_boarding(station:String)->bool:
 if not bool(get_meta("integration_boarding_admitted",true)):return false
 if phase!="secured" or not station_gates.has(station) or not _physical_dock_matches(station):return false
 selected_station=station;phase="deploying";var bridge:Node3D=bridges[station]
 bridge.dock_authorized=true;return bridge.request_deploy()
func request_secure()->bool:
 if phase!="boarding":return false
 # The original actor/cart must be allowed to finish crossing the physical bridge.
 # Departure remains forbidden by phase; defer both portal commands until it clears.
 phase="closing"
 return true
func unloaded_clear_to_depart()->bool:
 if phase!="secured":return false
 for gate in station_gates.values():
  if not gate.is_closed_and_clear():return false
 for gate in car_gates.values():
  if not gate.is_closed_and_clear():return false
 for bridge in bridges.values():
  if not bridge.safe_to_depart():return false
 return true
func _physics_process(delta:float)->void:
 if vehicle.global_transform.is_equal_approx(previous_vehicle_pose):stationary_frames+=1
 else:stationary_frames=0
 previous_vehicle_pose=vehicle.global_transform
 if phase=="deploying" and bridges[selected_station].fraction>.999:
  station_gates[selected_station].cabin_present_and_stopped=true;station_gates[selected_station].request_open()
  var st:Dictionary={}
  for row in plan.station_mounts:
   if row.station==selected_station:st=row
  var side:="PORT" if st.yaw==0.0 else "STARBOARD"
  car_gates[side].cabin_present_and_stopped=true;car_gates[side].request_open();phase="boarding"
 elif phase=="closing":
  if bridges[selected_station].threshold_occupied():return
  station_gates[selected_station].request_close()
  for gate in car_gates.values():gate.request_close()
  if not station_gates[selected_station].is_closed_and_clear():return
  for gate in car_gates.values():
   if not gate.is_closed_and_clear():return
  station_gates[selected_station].cabin_present_and_stopped=false
  for gate in car_gates.values():gate.cabin_present_and_stopped=false
  bridges[selected_station].request_stow();phase="stowing"
 elif phase=="stowing" and bridges[selected_station].safe_to_depart():
  bridges[selected_station].dock_authorized=false;phase="secured";selected_station=""
 # Actuator source check only: no cart body/state/joint is forced, snapped, cloned or reparented.
 clamp_fraction=move_toward(clamp_fraction,1.0 if source_clamp_target else 0.0,delta*.75)
 for i in range(clamp_bodies.size()):clamp_bodies[i].position=clamp_translations[i]*clamp_fraction
