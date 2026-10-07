shader_type spatial;
render_mode blend_mix, depth_draw_opaque, cull_back, diffuse_burley, specular_schlick_ggx;
// The retained surface is sampled exactly outside this material-only district.
uniform sampler2D retained_stone : source_color, filter_nearest_mipmap, repeat_enable;
uniform sampler2D finish_mineral : source_color, filter_nearest_mipmap, repeat_enable;
uniform vec4 finish_bounds = vec4(-17.8, -8.15, -461.1, -435.4);
uniform bool finish_enabled = true;
varying vec2 floor_world_xz;
void vertex() {
	floor_world_xz = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xz;
}
void fragment() {
	vec3 retained = texture(retained_stone, UV).rgb;
	vec3 result = retained;
	vec2 p = floor_world_xz;
	bool inside = finish_enabled && p.x >= finish_bounds.x && p.x <= finish_bounds.y && p.y >= finish_bounds.z && p.y <= finish_bounds.w;
	if (inside) {
		// Broad mineral field and readable inset edge, no tiny grid or emissive wash.
		vec3 mineral = texture(finish_mineral, (p - finish_bounds.xz) / 2.0).rgb;
		float edge = min(min(p.x-finish_bounds.x, finish_bounds.y-p.x), min(p.y-finish_bounds.z, finish_bounds.w-p.y));
		vec3 warm_field = mineral * vec3(0.90, 0.73, 0.54);
		vec3 teal_border = mineral * vec3(0.12, 0.23, 0.21);
		vec3 warm_reveal = mineral * vec3(0.58, 0.39, 0.18);
		result = edge < 0.22 ? teal_border : (edge < 0.36 ? warm_reveal : warm_field);
	}
	ALBEDO = result;
	METALLIC = 0.0;
	SPECULAR = 0.5;
	ROUGHNESS = 0.83;
}
