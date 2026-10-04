shader_type spatial;
render_mode blend_mix, cull_back, depth_prepass_alpha;
varying vec2 world_xz;
void vertex() {
 world_xz=(MODEL_MATRIX*vec4(VERTEX,1.0)).xz;
 VERTEX.y+=0.006*sin(world_xz.x*.8+TIME*.35)*cos(world_xz.y*.7-TIME*.2);
}
void fragment() {
 vec2 p=floor(world_xz*10.0)/10.0;
 float ripple=sin(p.x*2.1+TIME*.4)*cos(p.y*1.7-TIME*.3);
 ALBEDO=vec3(.10,.30,.31)*(1.0+.055*ripple);
 ROUGHNESS=.24;
 SPECULAR=.55;
 ALPHA=.79;
}
