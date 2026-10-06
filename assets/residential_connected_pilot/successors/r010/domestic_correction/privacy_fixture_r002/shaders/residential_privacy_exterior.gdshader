shader_type spatial;
// Dedicated opaque pipeline: never read/write ALPHA in this material.
// A dark transparent coating cannot guarantee privacy with room lights on.
render_mode depth_draw_opaque, cull_disabled;

uniform vec3 aperture_plane_origin = vec3(0.0);
uniform vec3 room_inside_normal = vec3(1.0, 0.0, 0.0);
uniform float interior_threshold_m = 0.015;
uniform vec3 exterior_tint : source_color = vec3(0.105, 0.205, 0.195);
uniform float polish_roughness : hint_range(0.03, 0.4) = 0.11;

void fragment() {
    float inside_distance = dot(CAMERA_POSITION_WORLD - aperture_plane_origin,
                                normalize(room_inside_normal));
    if (inside_distance > interior_threshold_m) {
        discard;
    }
    ALBEDO = exterior_tint;
    METALLIC = 0.68;
    ROUGHNESS = polish_roughness;
    SPECULAR = 0.65;
}
