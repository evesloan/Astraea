shader_type spatial;
render_mode diffuse_burley, specular_schlick_ggx;
uniform sampler2D warm_stone : source_color, filter_nearest_mipmap, repeat_enable;
uniform sampler2D ivory_enamel : source_color, filter_nearest_mipmap, repeat_enable;
varying vec2 ship_xz;
void vertex() { ship_xz = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xz; }
bool inside(vec2 p, vec4 r) { return p.x > r.x && p.x < r.y && p.y > r.z && p.y < r.w; }
void fragment() {
 vec2 p=vec2(-8.0-ship_xz.x,ship_xz.y+250.0);
 bool path=false;
 path = path || inside(p,vec4(7.900000,12.100000,10.000000,64.000000));
 path = path || inside(p,vec4(33.900000,38.100000,10.000000,64.000000));
 path = path || inside(p,vec4(8.000000,38.000000,9.900000,14.100000));
 path = path || inside(p,vec4(8.000000,38.000000,59.900000,64.100000));
 path = path || inside(p,vec4(0.000000,38.000000,31.900000,36.100000));
 path = path || inside(p,vec4(41.000000,45.000000,5.000000,65.000000));
 vec2 uv=vec2(ship_xz.x,-ship_xz.y);
 { ALBEDO=texture(warm_stone,uv/vec2(1.000000,1.000000)).rgb; ROUGHNESS=0.780000; }
 if (path) { ALBEDO=texture(ivory_enamel,uv/vec2(1.000000,1.000000)).rgb; ROUGHNESS=0.680000; }
 METALLIC=0.0;
}
