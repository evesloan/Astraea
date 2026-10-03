shader_type spatial;
render_mode blend_mix, cull_back, depth_prepass_alpha;
uniform vec3 water_tint : source_color = vec3(0.12,0.38,0.40);
uniform vec2 boundary[9];
varying vec2 world_xz;
void vertex() {
	world_xz = (MODEL_MATRIX * vec4(VERTEX,1.0)).xz;
	VERTEX.y += 0.012 * sin(world_xz.x*1.8+TIME*0.5) * cos(world_xz.y*1.3-TIME*0.4);
}
void fragment() {
	vec2 grid = floor(world_xz*12.0)/12.0;
	float ripples = sin(grid.x*3.0 + TIME*0.7) * cos(grid.y*2.3-TIME*0.6);
	float edge = 100.0;
	for (int i=0; i<9; i++) {
		vec2 a = boundary[i]; vec2 b = boundary[(i+1)%9];
		vec2 span = b-a;
		float t = clamp(dot(world_xz-a,span)/dot(span,span),0.0,1.0);
		edge = min(edge,length(world_xz-a-span*t));
	}
	float rim = 1.0-smoothstep(0.04,0.16,edge);
	ALBEDO = mix(water_tint*(0.95+0.05*ripples),vec3(0.55,0.72,0.68),rim*0.55);
	ROUGHNESS = 0.45;
	METALLIC = 0.0;
	SPECULAR = 0.45;
	ALPHA = 0.74;
}
