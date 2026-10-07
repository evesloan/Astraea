extends RefCounted
# Source-preserved whole receiving candidate. No new capacity or gameplay authority.
const MANIFEST := "res://data/architecture/moss_sanctuary/runtime_manifest.json"
static func build(ship: Node3D) -> Node3D:
 var data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(MANIFEST))
 assert(FileAccess.get_sha256(data.derivative_file)==data.derivative_sha256)
 var space: Node3D=ship.get_node("ShipSpace")
 assert(not space.has_node("D06_MossSanctuary_Receiving_WIP"))
 var root: Node3D=(load(data.derivative_file) as PackedScene).instantiate()
 root.name="D06_MossSanctuary_Receiving_WIP"
 assert(root.find_children("*","Light3D",true,false).is_empty())
 var nodes: Dictionary={}
 _index(root,nodes)
 var mesh_count:=0
 for row in data.meshes:
  assert(nodes.has(row.runtime_name))
  var mesh: MeshInstance3D=nodes[row.runtime_name]
  assert(mesh.mesh!=null)
  mesh_count+=1
  if row.decorative_water: continue
  var body:=StaticBody3D.new()
  body.name="SourceContact"
  var collider:=CollisionShape3D.new()
  collider.name="ExactMeshLocalFaces"
  collider.shape=mesh.mesh.create_trimesh_shape()
  assert(collider.shape!=null)
  body.add_child(collider)
  mesh.add_child(body)
 assert(mesh_count==976)
 for row in data.lights:
  var parent: Node3D=nodes[row.runtime_name]
  var light:=SpotLight3D.new()
  light.name="PhysicalSource"
  light.visible=false
  light.shadow_enabled=true
  light.light_color=Color(row.color[0],row.color[1],row.color[2])
  light.light_energy=float(row.energy)
  light.spot_range=float(row.range_m)
  light.spot_angle=float(row.outer_angle_degrees)
  light.spot_attenuation=1.0
  light.set_meta("fixture_powered",true)
  light.set_meta("source_fixture",row.source_name)
  light.set_meta("receiving_calibration_pending",true)
  parent.add_child(light)
 var water: MeshInstance3D=nodes[data.water_node]
 var material:=ShaderMaterial.new()
 assert(FileAccess.get_sha256("res://shaders/flowing_water.gdshader")==data.water_shader_sha256)
 material.shader=load("res://shaders/flowing_water.gdshader")
 material.set_shader_parameter("flow_speed",.12)
 water.material_override=material
 water.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
 root.set_meta("programme_key","D06_directory_03")
 root.set_meta("source_sha256",data.source_sha256)
 root.set_meta("status","receiving_candidate_runtime_visual_route_gates_pending")
 space.add_child(root)
 var info: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/moss_sanctuary/information_targets.json"))
 var bound: Dictionary=load("res://scripts/moss_sanctuary/bind_information.gd").bind(root,info)
 assert(bound.rejected.is_empty() and bound.bound.size()==2)
 _finish_floor(space,data)
 _open_supported_portal(space,data)
 return root
static func _index(node: Node,out: Dictionary) -> void:
 assert(not out.has(str(node.name)))
 out[str(node.name)]=node
 for child in node.get_children(): _index(child,out)

static func _finish_floor(space: Node3D, data: Dictionary) -> void:
 var floor: Node3D=space.get_node("CompiledStructuralFloors_NotFinishedRooms/"+str(data.floor_owner))
 assert(floor.get_meta("floor_y",27.0)==27.0)
 var material:=ShaderMaterial.new()
 material.shader=load(str(data.floor_shader))
 for record in data.finish_textures:
  assert(FileAccess.get_sha256(str(record.file))==str(record.sha256))
  material.set_shader_parameter(str(record.role),load(str(record.file)))
 var count:=0
 for child in floor.get_children():
  if child is MeshInstance3D and str(child.name).begins_with("cell_"):
   assert(child.mesh.get_surface_count()==1)
   child.set_surface_override_material(0,material)
   count+=1
 assert(count==data.finish_top_chunks.size())

static func _open_supported_portal(space: Node3D, data: Dictionary) -> void:
 # Authenticate a connected floor owner before changing only the named portal.
 var floors: Node3D=space.get_node("CompiledStructuralFloors_NotFinishedRooms")
 var compiled: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
 var matches:=0
 for row in compiled.regions:
  if str(row.id)!=str(data.floor_owner): continue
  assert(row.deck=="D06" and row.floor_y==27 and row.thickness==.24 and row.structural_area_m2==3128)
  assert(row==data.floor_record)
  matches+=1
 assert(matches==1 and floors.has_node(NodePath(str(data.floor_owner))))
 var guard: Node3D=space.get_node("BotanicalCourtReceivingClosedInterim")
 var changed:=0
 for mesh in guard.find_children("*","MeshInstance3D",true,false):
  if str(mesh.name) not in data.opened_guard_names: continue
  assert(mesh.visible)
  var shapes: Array=mesh.find_children("*","CollisionShape3D",true,false)
  assert(shapes.size()==1 and not shapes[0].disabled)
  mesh.visible=false
  shapes[0].disabled=true
  mesh.set_meta("moss_supported_portal_open",true)
  changed+=1
 assert(changed==14)
