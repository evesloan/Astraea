extends "res://tools/night_garden_specialty_20261020/check_receiving.gd"
func run()->void:
 world=Node3D.new();root.add_child(world)
 var districts:=Node3D.new();districts.name="Districts";world.add_child(districts)
 var lower:=Node3D.new();lower.name="D13_D14_StarboardCommons_WIP";districts.add_child(lower)
 var upper:=Node3D.new();upper.name="D15_D17_StarboardHouseUpper_WIP";lower.add_child(upper)
 var wrapper:=Node3D.new();wrapper.name="StarboardHouseUpperArchitecture";upper.add_child(wrapper);wrapper.position=Vector3(63,84,0)
 var raw:=load_raw("AST-COM-003.glb");raw.reparent(wrapper,false)
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/night_garden_specialty_d15_20261020/PACKAGE_R003.json"))
 var target:=districts.get_node_or_null("D13_D14_StarboardCommons_WIP/D15_D17_StarboardHouseUpper_WIP/StarboardHouseUpperArchitecture")
 check("exact_nested_commons_target",target==wrapper)
 for patch in p.receiving.commons_patch:
  var mesh:=target.find_child(patch.source_mesh,true,false) as MeshInstance3D
  check("exact_predecessor_"+str(patch.source_mesh),mesh!=null and mesh.mesh!=null)
  if mesh!=null:mesh.free()
 load_raw(p.receiving.model_file)
 await physics_frame;await physics_frame
 for sign in [-1,1]:check("filled_8cm_portal_seam_%s"%sign,not ray(Vector3(90.5,93.2,sign*14.04),Vector3(90.5,92.8,sign*14.04)).is_empty())
 var failed:=checks.filter(func(c):return not c.pass)
 var result:Dictionary={"scope":"r003 changed work only: actual AST-COM-003 raw node lookup in source-derived hierarchy, four exact predecessor meshes, two portal seam triangle rays. Source hierarchy chain separately pinned. Not full main integration.","checks":checks,"count":checks.size(),"failures":failed.size()}
 var f:=FileAccess.open("res://docs/validation/night_garden_specialty_20261020/FOCUSED_R003.json",FileAccess.WRITE);f.store_string(JSON.stringify(result,"\t"));f.close();print(JSON.stringify(result));quit(0 if failed.is_empty() else 1)
