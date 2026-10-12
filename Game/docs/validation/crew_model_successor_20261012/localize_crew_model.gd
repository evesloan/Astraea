extends SceneTree

func _initialize() -> void:
    call_deferred("inspect_live")

func inspect_live() -> void:
    var main=(load("res://scenes/main.tscn") as PackedScene).instantiate()
    root.add_child(main)
    for frame in range(150): await physics_frame
    var ship=main.get_node("World360/Astraea")
    var data=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/crew_batch/runtime_manifest.json"))
    var crew=ship.get_node("ShipSpace/"+str(data.root_name))
    var targets:Array=[]
    for section in data.sections:
        targets.append({"wrapper":crew.get_node(str(section.root_name)+"/Source"),"file":str(section.model_file)})
    targets.append({"wrapper":ship.get_node("ShipSpace/Districts/AftPublicCore_WIP/PrimaryCoreEnclosure"),"file":"AST-CIR-005_aft_uniforms_d03.glb"})
    var rows:Array=[]
    for target in targets:
        var wrapper:Node3D=target.wrapper
        var original=(load("res://assets/models/"+target.file) as PackedScene).instantiate()
        var visual:Node3D=wrapper.get_child(0)
        var failures:Array=[]
        var checked:=0
        for mesh in original.find_children("*","MeshInstance3D",true,false):
            var node_path=original.get_path_to(mesh)
            var actual=visual.get_node_or_null(node_path)
            checked+=1
            if actual==null:
                failures.append({"mesh":str(node_path),"missing":true})
                continue
            if actual.transform!=mesh.transform or actual.mesh!=mesh.mesh or actual.material_override!=null:
                failures.append({"mesh":str(node_path),"actual_node":str(actual.get_path()),"transform_equal":actual.transform==mesh.transform,"mesh_resource_equal":actual.mesh==mesh.mesh,"material_override_null":actual.material_override==null,"actual_transform":str(actual.transform),"original_transform":str(mesh.transform),"actual_mesh_resource":actual.mesh.resource_path,"original_mesh_resource":mesh.mesh.resource_path,"actual_material_override":str(actual.material_override),"actual_aabb":str(actual.mesh.get_aabb()),"original_aabb":str(mesh.mesh.get_aabb())})
        rows.append({"wrapper":str(wrapper.get_path()),"expected_file":target.file,"wrapper_child_count":wrapper.get_child_count(),"visual_transform_equal":visual.transform==original.transform,"meshes_checked":checked,"failed_exact_mesh_checks":failures})
        original.free()
    var report={"status":"DIAGNOSTIC_ONLY_NO_CRITERIA_CHANGED","rows":rows,"original_assertion":"transform equality AND mesh Resource equality AND null override","scene_frames_before_inspection":150}
    var file=FileAccess.open("/workspace/astraea-protected-integration-evidence-20261012/CREW_INSTANCE_DIAGNOSTIC.json",FileAccess.WRITE)
    file.store_string(JSON.stringify(report,"  ")+"\n")
    for row in rows: print("CREW_DIAGNOSTIC ",row.expected_file," failed=",row.failed_exact_mesh_checks.size())
    print("PASS: diagnostic completed; no receiving or route acceptance")
    quit(0)
