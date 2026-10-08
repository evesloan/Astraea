shader_type spatial;
render_mode diffuse_burley,specular_schlick_ggx;
varying vec2 ship_xz;
uniform sampler2D staff_floor:source_color,filter_nearest_mipmap,repeat_enable;
uniform sampler2D staff_spine:source_color,filter_nearest_mipmap,repeat_enable;
void vertex(){ship_xz=(MODEL_MATRIX*vec4(VERTEX,1.0)).xz;}
void fragment(){
 float u=ship_xz.x+54.0;float v=ship_xz.y+250.0;
 vec2 uv=vec2(ship_xz.x,-ship_xz.y);
 ALBEDO=texture(staff_floor,uv/0.8).rgb;ROUGHNESS=0.87;
 if(u>=0.24&&u<=45.76&&v>=30.0&&v<=38.0){ALBEDO=texture(staff_spine,uv).rgb;ROUGHNESS=0.78;}
 if(u>=1.0&&u<=45.5&&((v>=30.1&&v<=30.25)||(v>=37.75&&v<=37.9))){ALBEDO=vec3(0.84,0.70,0.36);ROUGHNESS=0.8;}
}
