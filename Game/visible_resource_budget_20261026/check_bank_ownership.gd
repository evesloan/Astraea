extends SceneTree
var output:String
func _initialize()->void:
 for arg:String in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.substr(9)
 call_deferred("run")
func run()->void:
 var host:Node3D=load("res://visible_resource_budget_20261026/bank_fixture_host.gd").new();root.add_child(host)
 var space:=Node3D.new();space.name="ShipSpace";host.add_child(space)
 var systems:=Node.new();systems.name="ShipSystems";host.add_child(systems)
 var budget:Node=load("res://scripts/lighting_budget.gd").new();budget.name="LocalShadowSourceBudget";systems.add_child(budget)
 var before:=OS.get_static_memory_usage()
 var bank:Node3D=load("res://scripts/group3_remaining_crew_20261019/package.gd").build(host)
 await process_frame
 var counts:Dictionary={};var examples:Dictionary={};var meshes:Dictionary={};var materials:Dictionary={};var rows:Array=[]
 for mesh:MeshInstance3D in bank.find_children("*","MeshInstance3D",true,false):
  var reason:="eligible"
  var material:Material=mesh.get_active_material(0)
  if not mesh.mesh is ArrayMesh:reason="not_array_mesh"
  elif mesh.mesh.get_surface_count()!=1:reason="multiple_surfaces"
  elif not material is StandardMaterial3D:reason="nonstandard_material"
  elif material.transparency!=BaseMaterial3D.TRANSPARENCY_DISABLED or material.albedo_color.a<.999:reason="transparent"
  elif mesh.skeleton!=NodePath(""):reason="skeleton_path"
  elif mesh.get_script()!=null:reason="script"
  elif not load("res://spatial_instance_cells_20261026/rules.gd").eligible(mesh,bank):reason="other_rule"
  counts[reason]=int(counts.get(reason,0))+1
  if not examples.has(reason):examples[reason]={"path":str(bank.get_path_to(mesh)),"mesh":mesh.mesh.get_class(),"material":material.get_class() if material!=null else "null","skeleton":str(mesh.skeleton),"scale":str(mesh.global_basis.get_scale())}
  meshes[mesh.mesh.get_instance_id()]=true
  if material!=null:materials[material.get_instance_id()]=true
 var loaded:=OS.get_static_memory_usage();var nodes:=Performance.get_monitor(Performance.OBJECT_NODE_COUNT)
 var bodies:=bank.find_children("*","StaticBody3D",true,false)
 var freed:=0
 for body:StaticBody3D in bodies:
  if body.name=="StaticContact" and body.get_script()==null and body.get_parent() is MeshInstance3D:body.free();freed+=1
 await process_frame
 var contacts_removed:=OS.get_static_memory_usage()
 for mesh:MeshInstance3D in bank.find_children("*","MeshInstance3D",true,false):
  if mesh.get_script()==null and mesh.get_child_count()==0:mesh.free()
 await process_frame
 var visual_removed:=OS.get_static_memory_usage()
 var result:={"fixture_only_destructive_accounting":true,"counts":counts,"examples":examples,"unique_meshes":meshes.size(),"unique_materials":materials.size(),"before_static":before,"loaded_static":loaded,"loaded_nodes":nodes,"freed_static_contacts":freed,"after_contacts_removed_static":contacts_removed,"after_visual_nodes_removed_static":visual_removed,"remaining_nodes":Performance.get_monitor(Performance.OBJECT_NODE_COUNT)}
 var file:=FileAccess.open(output,FileAccess.WRITE);file.store_string(JSON.stringify(result,"\t"));file.close();host.free();quit()
