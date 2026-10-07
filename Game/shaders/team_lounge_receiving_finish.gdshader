shader_type spatial;
render_mode diffuse_burley, specular_schlick_ggx;
// Material-only adaptation on the existing 52 authenticated top chunks.
uniform sampler2D warm_stone : source_color, filter_nearest_mipmap, repeat_enable;
uniform sampler2D teal_weave : source_color, filter_nearest_mipmap, repeat_enable;
uniform sampler2D clay_weave : source_color, filter_nearest_mipmap, repeat_enable;
uniform sampler2D staff_floor : source_color, filter_nearest_mipmap, repeat_enable;
varying vec2 ship_xz;
void vertex() { ship_xz = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xz; }
bool lobe(vec2 p, float center_z) {
	vec2 q = (p - vec2(31.0, center_z)) / vec2(22.0, 15.0);
	float step_angle = 6.283185307179586 / 192.0;
	float angle = atan(q.y, q.x);
	float sector_offset = mod(angle, step_angle) - step_angle * 0.5;
	return length(q) * cos(sector_offset) <= cos(step_angle * 0.5);
}
void fragment() {
	vec2 p = ship_xz;
	vec2 uv = vec2(p.x - 31.0, 216.0 - p.y);
	bool annex = p.x >= 47.0 && p.x <= 53.0 && p.y >= 208.0 && p.y <= 224.0;
	bool neck = p.x >= 8.0 && p.x <= 48.0 && p.y >= 211.0 && p.y <= 221.0;
	bool nominal = annex || neck || lobe(p, 198.5) || lobe(p, 233.5);
	vec3 color = texture(warm_stone, uv).rgb;
	float rough = 0.78;
	if (nominal) {
		if (annex) { color = texture(staff_floor, uv / 0.8).rgb; rough = 0.87; }
		else if (p.y < 211.0) { color = texture(teal_weave, uv / 0.8).rgb; rough = 0.91; }
		else if (p.y > 221.0) { color = texture(clay_weave, uv / 0.8).rgb; rough = 0.91; }
	}
	ALBEDO = color;
	ROUGHNESS = rough;
	METALLIC = 0.0;
}
