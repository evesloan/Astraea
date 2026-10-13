extends SceneTree
func _initialize()->void:
 assert(ProjectSettings.load_resource_pack("/workspace/astraea-integration-cutoff-20261013/g3_full_clinical_receiving/CANDIDATE_OVERLAY.zip",true));call_deferred("run")
func run()->void:
 var world:=Node3D.new();root.add_child(world)
 for file in ["AST-MED-G3-007.glb","AST-MED-G3-008.glb","AST-MED-G3-010.glb"]:
  var visual:Node3D=(load("res://assets/models/group3_clinical_full_20261011/"+file)as PackedScene).instantiate();visual.name=file.trim_suffix(".glb");world.add_child(visual)
  for mesh in visual.find_children("*","MeshInstance3D",true,false):load("res://scripts/static_contact_cache.gd").attach(mesh)
 for i in range(5):await physics_frame
 var at:=Vector3(-98.872,21,34.141333333333);var state:PhysicsDirectSpaceState3D=world.get_world_3d().direct_space_state;var rows:Array=[]
 for extent in [.02,.1,.4]:
  var q:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*extent,at-Vector3.UP*extent);var h:Dictionary=state.intersect_ray(q);rows.append({"extent":extent,"empty":h.is_empty(),"collider":str(h.collider.get_path())if not h.is_empty()else null,"position":str(h.position)if not h.is_empty()else null,"normal":str(h.normal)if not h.is_empty()else null})
 var floor:Node3D=world.get_node("AST-MED-G3-008");var meshes:Array=[]
 for mesh:MeshInstance3D in floor.find_children("*","MeshInstance3D",true,false):
  meshes.append({"name":mesh.name,"bounds":str(mesh.global_transform*mesh.get_aabb()),"format":mesh.mesh.surface_get_format(0)})
 FileAccess.open("/workspace/astraea-integration-cutoff-20261013/g3_full_clinical_receiving/FLOOR_WITNESS_PROBE.json",FileAccess.WRITE).store_string(JSON.stringify({"point":str(at),"rays":rows,"floor_meshes":meshes},"  "));print("CLINICAL_FLOOR_WITNESS_PROBE_PASS");quit(0)
