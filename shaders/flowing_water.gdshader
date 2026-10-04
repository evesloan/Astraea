shader_type spatial;
render_mode blend_mix, cull_disabled, depth_prepass_alpha;
uniform vec3 water_tint : source_color = vec3(0.15,0.40,0.42);
uniform float flow_speed = 0.7;
void fragment() {
	vec2 grid = floor(UV*vec2(24.0,12.0))/vec2(24.0,12.0);
	float travel = grid.y-TIME*flow_speed;
	float streak = sin(travel*9.0+sin(grid.x*21.0)*1.4);
	float fine = sin(travel*17.0+grid.x*37.0);
	float foam = smoothstep(0.86,1.0,streak)*0.22+smoothstep(0.94,1.0,fine)*0.08;
	ALBEDO = mix(water_tint,vec3(0.70,0.81,0.78),foam);
	ROUGHNESS = 0.36;
	SPECULAR = 0.45;
	ALPHA = 0.72+foam*0.5;
}
