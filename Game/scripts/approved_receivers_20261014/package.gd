extends RefCounted
static func build(ship:Node3D)->Node3D:
 var group:=Node3D.new()
 group.name="ApprovedSixHouseReceiving"
 ship.get_node("ShipSpace").add_child(group)
 group.set_meta("default_main_adoption",true)
 group.set_meta("capacity_or_operational_admission",false)
 group.set_meta("structural_capacity_accepted",false)
 var source:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/approved_receivers_20261014/REGIONS.json"))
 var manifest:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/approved_receivers_20261014/NATIVE_EXPORT_VERIFICATION.json"))
 for row in manifest.models:
  var path:String="res://assets/approved_receivers_20261014/"+str(row.file)
  assert(FileAccess.get_sha256(path)==str(row.sha256))
  var original:Node3D=(load(path)as PackedScene).instantiate()
  var tool:=SurfaceTool.new();tool.begin(Mesh.PRIMITIVE_TRIANGLES)
  var material:Material
  var meshes:Array[Node]=original.find_children("*","MeshInstance3D",true,false)
  assert(meshes.size()==int(row.meshes))
  for mesh:MeshInstance3D in meshes:
   var pose:Transform3D=mesh.transform
   var parent:Node3D=mesh.get_parent()
   while parent!=original:
    pose=parent.transform*pose;parent=parent.get_parent()
   for surface in range(mesh.mesh.get_surface_count()):
    if material==null:material=mesh.mesh.surface_get_material(surface)
    tool.append_from(mesh.mesh,surface,pose)
  tool.set_material(material)
  var combined:ArrayMesh=tool.commit()
  var visual:=MeshInstance3D.new();visual.name=str(row.house);visual.mesh=combined
  group.add_child(visual)
  load("res://scripts/static_contact_cache.gd").attach(visual)
  visual.set_meta("exact_native_source_meshes",meshes.size())
  original.free()
 load("res://scripts/structural_floor_builder.gd").build_regions(group,ship.stone,ship.ivory,source.regions,{},"ExactRetainedMissingFloors")
 return group
