extends Node3D
# One source information case per existing station gate. Fixed construction; no input/controller/global system.
const DATA:="res://data/architecture/GROUP4_STATION_INFORMATION_SOURCE_CANDIDATE.json"
var plan:Dictionary
var safety:Node3D
var models:Array[Node3D]=[]
var gates:Array[Node3D]=[]
static func xyz(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(parent:Node3D,existing_safety:Node3D,candidate_only:bool=false)->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(DATA))
 if not p.active and not candidate_only:return null
 assert(FileAccess.get_sha256("res://assets/models/AST-DOR-003.glb")==p.original_gate_sha256)
 for gate:Node3D in existing_safety.station_gates.values():assert(not gate.has_meta("group4_station_information"),"One fixed source information case per original gate")
 var n:Node3D=load("res://scripts/group4_station_information.gd").new();n.name="Group4SourceStationInformation";n.plan=p;n.safety=existing_safety;parent.add_child(n);return n
func paint(model:Node3D,text:String,at:Vector3,size:float,current:bool=false)->void:
 var label:=Label3D.new();label.name="StationInfoLegend_"+text.validate_node_name();label.text=text;label.font_size=64;label.pixel_size=size;label.outline_size=0;label.modulate=Color(.12,.095,.065) if current else Color(.22,.18,.12);label.position=at;label.basis=Basis.looking_at(Vector3.BACK,Vector3.UP);label.no_depth_test=false;label.billboard=BaseMaterial3D.BILLBOARD_DISABLED;model.add_child(label)
func _ready()->void:
 var file:String=plan.model_root+plan.file;assert(FileAccess.get_sha256(file)==plan.sha256);var policies:Dictionary={}
 for name:String in plan.policies:policies[name.validate_node_name()]=plan.policies[name]
 for station:String in plan.station_order:
  var gate:Node3D=safety.station_gates[station];var node:Node3D=(load(file)as PackedScene).instantiate();gate.add_child(node);models.append(node);gates.append(gate);gate.set_meta("group4_station_information",get_instance_id());var members:Array[Node]=[];var count:=0
  for mesh:MeshInstance3D in node.find_children("*","MeshInstance3D",true,false):
   count+=1;assert(policies.has(str(mesh.name)))
   if policies[str(mesh.name)]!="no_collision_detail":members.append(mesh)
  assert(count==18);load("res://scripts/static_contact_cache.gd").attach_group(node,members)
  for row in plan.nodes:paint(node,("› " if row.station==station else "")+str(row.station).replace("_"," "),xyz(row.face_label_position_xyz),.00050,row.station==station)
  var title:Dictionary=plan.fixed_legends.title;paint(node,title.text,xyz(title.position),title.pixel_size)
  var current:Dictionary=plan.fixed_legends.current_station;paint(node,station.replace("_"," "),xyz(current.position),current.pixel_size,true)
  var footer:Dictionary=plan.fixed_legends.footer;paint(node,footer.text,xyz(footer.position),footer.pixel_size)
func _exit_tree()->void:
 for gate in gates:
  if is_instance_valid(gate) and gate.get_meta("group4_station_information",0)==get_instance_id():gate.remove_meta("group4_station_information")
 for model in models:
  if is_instance_valid(model):model.queue_free()
