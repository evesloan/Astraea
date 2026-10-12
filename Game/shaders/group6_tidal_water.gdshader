shader_type spatial;
render_mode blend_mix, cull_disabled, depth_prepass_alpha;
// Visual thermal water only: same protected boundary/height, displacement<=.003m.
uniform vec3 deep_tint : source_color = vec3(0.12,0.39,0.42);
uniform vec3 edge_tint : source_color = vec3(0.23,0.58,0.54);
uniform vec4 basin_xz = vec4(29.2,40.8,-427.8,-408.2);
varying vec2 world_xz;
void vertex() {
 world_xz=(MODEL_MATRIX*vec4(VERTEX,1.0)).xz;
 VERTEX.y+=.0015*sin(dot(world_xz,vec2(1.6,.9))+TIME*.31)+.0015*cos(dot(world_xz,vec2(-.7,2.2))-TIME*.23);
}
void fragment() {
 vec2 p=world_xz;
 float n1=cos(dot(p,vec2(2.1,1.3))+TIME*.31);
 float n2=cos(dot(p,vec2(-1.2,3.0))-TIME*.24);
 float n3=sin(dot(p,vec2(.8,-.55))+TIME*.19);
 vec3 wave_normal=normalize(vec3(.035*n1-.022*n2+.014*n3,1.0,.023*n1+.034*n2-.009*n3));
 NORMAL=normalize((VIEW_MATRIX*vec4(wave_normal,0.0)).xyz);
 float edge=min(min(p.x-basin_xz.x,basin_xz.y-p.x),min(p.y-basin_xz.z,basin_xz.w-p.y));
 float shallow=1.0-smoothstep(.10,1.25,edge);
 float fresnel=pow(1.0-clamp(dot(normalize(NORMAL),normalize(VIEW)),0.0,1.0),3.0);
 ALBEDO=mix(deep_tint,edge_tint,.24+shallow*.60)+vec3(.008,.011,.009)*(n1*n2);
 ROUGHNESS=.30;
 SPECULAR=.62;
 METALLIC=0.0;
 ALPHA=mix(.48,.76,fresnel)+shallow*.07;
}
