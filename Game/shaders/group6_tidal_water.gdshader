shader_type spatial;
render_mode blend_mix, cull_disabled, depth_prepass_alpha;
// Northern bath appearance only. Source boundary/nominal height stay pinned;
// displacement is <=0.006m, without fluid or swimming collision/logic.
uniform vec3 deep_tint : source_color = vec3(0.045,0.26,0.30);
uniform vec3 edge_tint : source_color = vec3(0.18,0.56,0.55);
uniform vec4 basin_xz = vec4(29.2,40.8,-427.8,-408.2);
varying vec2 world_xz;
void vertex() {
 world_xz = (MODEL_MATRIX * vec4(VERTEX,1.0)).xz;
 VERTEX.y += 0.003 * sin(world_xz.x*1.55+TIME*0.42) * cos(world_xz.y*1.25-TIME*0.33);
}
void fragment() {
 vec2 p=floor(world_xz*12.0)/12.0;
 float a=sin(p.x*1.55+TIME*0.42);
 float b=cos(p.y*1.25-TIME*0.33);
 vec3 wave_normal=normalize(vec3(0.15*cos(p.x*1.55+TIME*0.42)*b,1.0,-0.15*a*sin(p.y*1.25-TIME*0.33)));
 NORMAL=normalize((VIEW_MATRIX*vec4(wave_normal,0.0)).xyz);
 float edge=min(min(world_xz.x-basin_xz.x,basin_xz.y-world_xz.x),min(world_xz.y-basin_xz.z,basin_xz.w-world_xz.y));
 float shallow=1.0-smoothstep(0.10,1.5,edge);
 float crest=pow(max(0.0,sin(p.x*2.9+p.y*1.65+TIME*0.42)*cos(p.x*0.6-p.y*2.6-TIME*0.33)),12.0);
 float small_ripple=0.03*sin(p.x*3.8+p.y*2.7+TIME*0.30);
 ALBEDO=mix(deep_tint,edge_tint,0.35+shallow*0.55)+vec3(small_ripple*0.35)+vec3(0.045,0.075,0.072)*crest;
 ROUGHNESS=0.20;
 SPECULAR=0.85;
 METALLIC=0.05;
 ALPHA=0.70+shallow*0.14;
}
