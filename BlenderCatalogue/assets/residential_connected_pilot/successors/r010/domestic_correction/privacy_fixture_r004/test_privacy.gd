extends SceneTree
var world: Node3D
var camera: Camera3D
var report: Dictionary = {"status":"RUNNING", "scope":"Isolated exact-source optical-material fixture, not connected Game acceptance", "rows":[]}
var all_pass := true

func _initialize() -> void:
    call_deferred("run")

func write_report() -> void:
    var file := FileAccess.open("res://results/PRIVACY_PIXEL_RESULT.json", FileAccess.WRITE)
    file.store_string(JSON.stringify(report, "  "))

func fail(message: String) -> void:
    all_pass = false
    report["error"] = message
    write_report()
    push_error(message)
    quit(1)

func target_at(position: Vector3) -> MeshInstance3D:
    var target := MeshInstance3D.new()
    target.name = "TEMPORARY_LABELLED_PRIVACY_TEST_TARGET"
    var box := BoxMesh.new()
    box.size = Vector3(.02, 1.6, 1.8)
    target.mesh = box
    target.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
    var material := StandardMaterial3D.new()
    material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
    target.material_override = material
    world.add_child(target)
    target.position = position
    return target

func image_for(target: MeshInstance3D, color: Color) -> Image:
    (target.material_override as StandardMaterial3D).albedo_color = color
    for step in range(3):
        await process_frame
    await RenderingServer.frame_post_draw
    return root.get_texture().get_image()

func difference(a: Image, b: Image) -> int:
    var changed := 0
    for y in range(a.get_height()):
        for x in range(a.get_width()):
            var p := a.get_pixel(x,y)
            var q := b.get_pixel(x,y)
            if maxf(absf(p.r-q.r),maxf(absf(p.g-q.g),absf(p.b-q.b))) > 3.0/255.0:
                changed += 1
    return changed


func aperture_trial(pane: MeshInstance3D, exterior: MeshInstance3D, target: MeshInstance3D, identity: String, label: String, expect_leak: bool) -> Dictionary:
    var optical: Material = pane.material_override
    var control := StandardMaterial3D.new()
    control.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
    control.albedo_color = Color(.56,.70,.67,.035)
    control.cull_mode = BaseMaterial3D.CULL_DISABLED
    pane.material_override = control
    exterior.visible = false
    var ca := await image_for(target,Color(1,0,1))
    var cb := await image_for(target,Color(0,1,1))
    var positive := difference(ca,cb)
    pane.material_override = optical
    exterior.visible = true
    var a := await image_for(target,Color(1,0,1))
    var b := await image_for(target,Color(0,1,1))
    var leak := difference(a,b)
    var passed := positive >= 8 and (leak >= 8 if expect_leak else leak == 0)
    if label == "full_perimeter_0_light10" or label.begins_with("r009_known_"):
        a.save_png("res://results/"+identity+"_"+label+".png")
        ca.save_png("res://results/"+identity+"_"+label+"_unshielded.png")
    return {"unit":identity,"phase":label,"camera_world":[camera.position.x,camera.position.y,camera.position.z],"actual_image_size":[a.get_width(),a.get_height()],"positive_control_pixels":positive,"target_dependent_pixels":leak,"expected_old_source_leak":expect_leak,"pass":passed}

func run() -> void:
    if DisplayServer.get_name() == "headless":
        fail("Graphical Compatibility renderer required for pixel evidence")
        return
    world = Node3D.new()
    root.add_child(world)
    var environment := WorldEnvironment.new()
    var settings := Environment.new()
    settings.background_mode = Environment.BG_COLOR
    settings.background_color = Color(.12,.15,.16)
    settings.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    settings.ambient_light_color = Color(.85,.88,.92)
    settings.ambient_light_energy = .5
    environment.environment = settings
    world.add_child(environment)
    camera = Camera3D.new()
    world.add_child(camera)
    camera.current = true
    camera.fov = 72
    var definitions: Array = JSON.parse_string(FileAccess.get_file_as_string("res://rooms.json"))
    for definition in definitions:
        var packed := load("res://assets/suite_"+str(int(definition.index))+".glb") as PackedScene
        if packed == null:
            fail("Exact source shell failed to load")
            return
        var shell := packed.instantiate() as Node3D
        world.add_child(shell)
        shell.position = Vector3(float(definition.origin[0]),float(definition.origin[1]),float(definition.origin[2]))
        shell.rotation.y = float(definition.yaw)
        var pane := shell.find_child("SUI_Runtime_SuiteHospitalityGlass".validate_node_name(),true,false) as MeshInstance3D
        if pane == null:
            fail("Exact source pane not found")
            return
        var z := float(definition.origin[2])
        load("res://scripts/residential_privacy_glazing.gd").apply_to_pane(pane,Vector3(29.17,90.54,z),Vector3.RIGHT,str(definition.id))
        var exterior := pane.get_node("ResidentialExteriorPrivacyFace") as MeshInstance3D
        var optical: Material = pane.material_override
        var light := OmniLight3D.new()
        world.add_child(light)
        light.position = Vector3(30.3,90.8,z)
        light.omni_range = 8
        light.light_color = Color(1,.93,.82)
        var target := target_at(Vector3(29.26,90.54,z))
        var eyes: Array[Vector3] = [Vector3(27.4,90.54,z),Vector3(20,90.54,z),Vector3(10,90.54,z),Vector3(27.1,90.54,z-3),Vector3(27.1,90.54,z+3),Vector3(28.7,90.54,z-8),Vector3(28.7,90.54,z+8),Vector3(29.165,90.54,z-1.65),Vector3(29.175,90.54,z-1.65)]
        for energy in [0.0,1.0,10.0]:
            light.light_energy = energy
            for index in range(eyes.size()):
                target.position = Vector3(29.26,90.54,z-1.65 if index >= 7 else z)
                camera.position = eyes[index]
                camera.near = .001 if index >= 7 else .05
                camera.look_at(target.position,Vector3.UP)
                var control := StandardMaterial3D.new()
                control.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
                control.albedo_color = Color(.56,.70,.67,.035)
                control.cull_mode = BaseMaterial3D.CULL_DISABLED
                pane.material_override = control
                exterior.visible = false
                var ca := await image_for(target,Color(1,0,1))
                var cb := await image_for(target,Color(0,1,1))
                var positive := difference(ca,cb)
                pane.material_override = optical
                exterior.visible = true
                var a := await image_for(target,Color(1,0,1))
                var b := await image_for(target,Color(0,1,1))
                var leak := difference(a,b)
                var passed := positive >= 8 and leak == 0
                all_pass = all_pass and passed
                report.rows.append({"unit":definition.id,"camera_index":index,"camera_world":[eyes[index].x,eyes[index].y,eyes[index].z],"near_clip_m":camera.near,"room_light_energy":energy,"actual_image_size":[a.get_width(),a.get_height()],"positive_control_pixels":positive,"exterior_target_dependent_pixels":leak,"pass":passed})
                if index == 0 and energy == 10.0:
                    ca.save_png("res://results/unit_"+str(int(definition.index))+"_positive_control.png")
                    a.save_png("res://results/unit_"+str(int(definition.index))+"_private_exterior.png")
                write_report()
        var reverse_z := z if int(definition.index) == 205 else z-1.65
        target.position = Vector3(27.8,90.54,reverse_z)
        camera.position = Vector3(31.2,90.54,reverse_z)
        camera.near = .05
        camera.look_at(target.position,Vector3.UP)
        var ia := await image_for(target,Color(1,0,1))
        var ib := await image_for(target,Color(0,1,1))
        var visible := difference(ia,ib)
        all_pass = all_pass and visible >= 8
        report.rows.append({"unit":definition.id,"direction":"inside_out","actual_image_size":[ia.get_width(),ia.get_height()],"target_dependent_pixels":visible,"pass":visible>=8})
        ia.save_png("res://results/unit_"+str(int(definition.index))+"_clear_interior.png")
        # Full aperture target remains within the outer source enclosure. It
        # reaches all frame joints, including the seams the small target missed.
        var full_shape := BoxMesh.new()
        full_shape.size = Vector3(.02,3.74,7.10)
        target.mesh = full_shape
        target.position = Vector3(29.22,90.54,z)
        var perimeter_eyes: Array[Vector3] = [Vector3(25.5,90.54,z),Vector3(20,90.54,z),Vector3(10,90.54,z),Vector3(25.5,88.985,z),Vector3(25.5,92.095,z),Vector3(25.5,90.54,z-4),Vector3(25.5,90.54,z+4)]
        for energy in [0.0,10.0]:
            light.light_energy = energy
            for index in range(perimeter_eyes.size()):
                camera.position = perimeter_eyes[index]
                camera.near = .05
                camera.look_at(target.position,Vector3.UP)
                var result := await aperture_trial(pane,exterior,target,str(int(definition.index)),"full_perimeter_"+str(index)+"_light"+str(int(energy)),false)
                all_pass = all_pass and bool(result.pass)
                report.rows.append(result)
                write_report()
        target.queue_free()
        shell.queue_free()
        light.queue_free()
        await process_frame
    # Known-unsealed source must fail the larger target test. This proves the
    # new coverage reaches the original header/sill holes rather than hiding them.
    var old_shell := (load("res://assets/suite_205_r009_negative_control.glb") as PackedScene).instantiate() as Node3D
    world.add_child(old_shell)
    old_shell.position = Vector3(41.95,88.5,-320.6)
    old_shell.rotation.y = PI/2
    var old_pane := old_shell.find_child("SUI_Runtime_SuiteHospitalityGlass".validate_node_name(),true,false) as MeshInstance3D
    load("res://scripts/residential_privacy_glazing.gd").apply_to_pane(old_pane,Vector3(29.17,90.54,-320.6),Vector3.RIGHT,"known_unsealed_source_control")
    var old_exterior := old_pane.get_node("ResidentialExteriorPrivacyFace") as MeshInstance3D
    var old_target := target_at(Vector3(29.22,90.54,-320.6))
    var old_shape := BoxMesh.new()
    old_shape.size = Vector3(.02,3.74,7.10)
    old_target.mesh = old_shape
    var old_light := OmniLight3D.new()
    world.add_child(old_light)
    old_light.position = Vector3(30.3,90.8,-320.6)
    old_light.light_energy = 10
    old_light.omni_range = 8
    for edge in [{"y":88.985,"name":"sill"},{"y":92.095,"name":"header"}]:
        camera.position = Vector3(25.5,float(edge.y),-320.6)
        camera.near = .05
        camera.look_at(old_target.position,Vector3.UP)
        var negative_control := await aperture_trial(old_pane,old_exterior,old_target,"205","r009_known_"+str(edge.name)+"_seam_failure",true)
        all_pass = all_pass and bool(negative_control.pass)
        report.rows.append(negative_control)
    old_target.queue_free()
    old_shell.queue_free()
    old_light.queue_free()
    await process_frame
    report.status = "PASS" if all_pass else "FAIL"
    report.renderer = RenderingServer.get_current_rendering_method()
    report.rendering_driver = RenderingServer.get_current_rendering_driver_name()
    report.targets_removed = true
    report.limits = ["Isolated optical test; no actual court, LightingBudget, player collision or connected-pilot adoption acceptance", "Near-plane cameras use a labelled1mm clip; ordinary cameras use50mm", "Natural polished-material appearance and actual court lighting remain separate native gates"]
    write_report()
    print("RESIDENTIAL_ISOLATED_PRIVACY_",report.status," cases=",report.rows.size())
    quit(0 if all_pass else 1)
