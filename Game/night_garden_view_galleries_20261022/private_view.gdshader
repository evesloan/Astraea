shader_type spatial;
render_mode blend_mix, depth_prepass_alpha, cull_disabled;
uniform float plane_x = 0.0;
uniform float interior_sign = -1.0;
void fragment() {
 bool inside = (CAMERA_POSITION_WORLD.x - plane_x) * interior_sign > 0.0;
 ALBEDO = inside ? vec3(0.24,0.38,0.33) : vec3(0.055,0.09,0.08);
 ROUGHNESS = inside ? 0.16 : 0.42;
 ALPHA = inside ? 0.12 : 1.0;
}
