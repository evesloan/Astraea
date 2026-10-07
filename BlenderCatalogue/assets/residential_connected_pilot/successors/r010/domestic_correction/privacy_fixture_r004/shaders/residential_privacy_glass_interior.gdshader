shader_type spatial;
render_mode blend_mix, depth_prepass_alpha, cull_disabled;

uniform vec3 aperture_plane_origin = vec3(0.0);
uniform vec3 room_inside_normal = vec3(1.0, 0.0, 0.0);
uniform float interior_threshold_m = 0.015;
uniform vec3 interior_tint : source_color = vec3(0.56, 0.70, 0.67);

void fragment() {
    float inside_distance = dot(CAMERA_POSITION_WORLD - aperture_plane_origin,
                                normalize(room_inside_normal));
    if (inside_distance <= interior_threshold_m) {
        discard;
    }
    float facing = clamp(abs(dot(normalize(NORMAL), normalize(VIEW))), 0.0, 1.0);
    float edge = pow(1.0 - facing, 4.0);
    ALBEDO = interior_tint;
    ROUGHNESS = 0.08;
    SPECULAR = 0.55;
    ALPHA = 0.035 + edge * 0.12;
}
