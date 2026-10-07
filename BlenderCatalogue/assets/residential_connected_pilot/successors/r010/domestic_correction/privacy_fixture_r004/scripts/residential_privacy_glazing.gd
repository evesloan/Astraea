extends RefCounted
## Local residential optical privacy. Court/rail/shower glass is never matched.
## Explicit game material behavior, not a claim about ordinary one-way mirrors.

const INSIDE_SHADER := "res://shaders/residential_privacy_glass_interior.gdshader"
const OUTSIDE_SHADER := "res://shaders/residential_privacy_exterior.gdshader"
const THRESHOLD_M := 0.015

static func apply_to_pane(pane: MeshInstance3D, plane_origin: Vector3,
        inside_normal: Vector3, suite_identity: String) -> Dictionary:
    assert(pane != null and pane.mesh != null)
    assert(inside_normal.length() > 0.999 and inside_normal.length() < 1.001)
    assert(not pane.has_meta("residential_privacy_profile"), "Do not apply twice")
    assert(not suite_identity.is_empty())
    var normal := inside_normal.normalized()
    var interior := ShaderMaterial.new()
    interior.shader = load(INSIDE_SHADER) as Shader
    var exterior := ShaderMaterial.new()
    exterior.shader = load(OUTSIDE_SHADER) as Shader
    assert(interior.shader != null and exterior.shader != null)
    for material: ShaderMaterial in [interior, exterior]:
        material.set_shader_parameter("aperture_plane_origin", plane_origin)
        material.set_shader_parameter("room_inside_normal", normal)
        material.set_shader_parameter("interior_threshold_m", THRESHOLD_M)
    pane.material_override = interior
    pane.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
    var opaque_face := MeshInstance3D.new()
    opaque_face.name = "ResidentialExteriorPrivacyFace"
    opaque_face.mesh = pane.mesh
    opaque_face.material_override = exterior
    opaque_face.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
    pane.add_child(opaque_face)
    opaque_face.transform = Transform3D.IDENTITY
    var contract := {
        "version": "residential_privacy_v001",
        "suite_identity": suite_identity,
        "plane_origin_world": plane_origin,
        "room_inside_normal_world": normal,
        "interior_threshold_m": THRESHOLD_M,
        "exterior_pipeline": "opaque; no ALPHA; independent of room brightness",
        "interior_pipeline": "low-opacity clear view, finite existing aperture",
        "source_requirement": "Sentinel_1367a9f10c748191835bf2083b1308da",
        "native_verified": false,
    }
    pane.set_meta("residential_privacy_profile", contract)
    opaque_face.set_meta("suite_identity", suite_identity)
    opaque_face.set_meta("residential_privacy_exterior", true)
    return {"interior": pane, "exterior": opaque_face, "contract": contract}

static func camera_is_inside(camera_position: Vector3, plane_origin: Vector3,
        inside_normal: Vector3) -> bool:
    return (camera_position - plane_origin).dot(inside_normal.normalized()) > THRESHOLD_M
