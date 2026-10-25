extends RefCounted
# Additive D18 gallery envelope. No floor, room, transit or actor owner replacement.
const PACKAGE := "res://group7_terminal_roof_links_20261025/"

static func build(ship:Node3D)->Node3D:
 var space:Node3D=ship.get_node("ShipSpace")
 if space.has_node("Group7TerminalRoofLinks20261025"):
  push_error("Refusing duplicate Group7 terminal roof links")
  return null
 var receipt:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(PACKAGE+"RUNTIME.json"))
 for path:String in receipt.source_pins:
  if FileAccess.get_sha256(path)!=str(receipt.source_pins[path]):
   push_error("Group7 roof receiver differs: "+path)
   return null
 if FileAccess.get_sha256(PACKAGE+"G7_TerminalRoofLinks_r011.glb")!=str(receipt.model_sha256):
  push_error("Group7 roof model differs")
  return null
 var packed:PackedScene=load(PACKAGE+"G7_TerminalRoofLinks_r011.glb")
 if packed==null:return null
 var root:=Node3D.new()
 root.name="Group7TerminalRoofLinks20261025"
 root.set_meta("capacity_delta",0)
 root.set_meta("primary_capacity_accepted",false)
 root.set_meta("source_revision","r011")
 space.add_child(root)
 var visual:Node3D=packed.instantiate();root.add_child(visual)
 var glass:=ShaderMaterial.new()
 glass.shader=load("res://shaders/hospitality_glass.gdshader")
 var meshes:Array=visual.find_children("*","MeshInstance3D",true,false)
 if meshes.size()!=int(receipt.mesh_batches):
  push_error("Group7 roof spatial batch count differs")
  root.queue_free();return null
 for mesh:MeshInstance3D in meshes:
  var extras:Dictionary=mesh.get_meta("extras",{})
  var role:String=str(extras.get("role",""))
  if role.is_empty():role=str(mesh.name).get_slice("_",str(mesh.name).get_slice_count("_")-1)
  if role not in ["glass","lens","metal","enamel"]:
   push_error("Unknown Group7 roof material role: "+str(mesh.name))
   root.queue_free();return null
  mesh.set_meta("roof_link_cell",str(extras.get("cell","")))
  if role=="glass":
   mesh.material_override=glass
   mesh.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
  if role=="lens":
   mesh.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
  else:
   load("res://scripts/static_contact_cache.gd").attach(mesh)
  # Only the actual opaque ceiling spine can occlude. No glazing hull proxy.
  if role=="enamel":
   load("res://scripts/architectural_occlusion.gd").from_mesh(mesh,mesh.mesh,"ActualRoofSpineOccluder")
 for row:Dictionary in receipt.lights:
  if visual.find_child(str(row.housing_mesh),true,false)==null or visual.find_child(str(row.lens_mesh),true,false)==null:
   push_error("Missing physical Group7 roof fixture: "+str(row.id))
   root.queue_free();return null
  var light:=SpotLight3D.new()
  light.name=str(row.id)
  root.add_child(light)
  light.position=Vector3(row.position[0],row.position[1],row.position[2])
  light.rotation.x=-PI/2
  light.spot_angle=78
  light.spot_range=15
  light.light_energy=1.1
  light.light_color=Color(1,.84,.63)
  light.shadow_enabled=true
  light.visible=false
  light.set_meta("source_fixture",str(row.housing_mesh))
  light.set_meta("source_fixture_part",str(row.housing))
  load("res://scripts/group7_completion.gd").register_new_light(ship,light)
 root.set_meta("authored_parts",int(receipt.authored_parts))
 root.set_meta("mesh_batches",meshes.size())
 return root
