shader_type spatial;
render_mode diffuse_burley,specular_schlick_ggx;
varying vec2 ship_xz;
void vertex(){ship_xz=(MODEL_MATRIX*vec4(VERTEX,1.0)).xz;}
uniform sampler2D warm_stone: source_color,filter_nearest_mipmap,repeat_enable;
uniform sampler2D warm_walnut: source_color,filter_nearest_mipmap,repeat_enable;
uniform sampler2D teal_weave: source_color,filter_nearest_mipmap,repeat_enable;
uniform sampler2D clay_weave: source_color,filter_nearest_mipmap,repeat_enable;
uniform sampler2D staff_zinc: source_color,filter_nearest_mipmap,repeat_enable;
void fragment(){
 float u=ship_xz.x+54.0;float v=ship_xz.y-182.0;
 vec2 uv=vec2(ship_xz.x+31.0,216.0-ship_xz.y);
 if(true){ALBEDO=texture(warm_stone,uv/vec2(1.0,1.0)).rgb;ROUGHNESS=0.78;METALLIC=0.0;}
 if(u>=2.0&&u<44.0&&v>=2.0&&v<29.0){ALBEDO=texture(teal_weave,uv/vec2(0.8,0.8)).rgb;ROUGHNESS=0.91;METALLIC=0.0;}
 if(u>=2.0&&u<44.0&&v>=39.0&&v<66.0){ALBEDO=texture(clay_weave,uv/vec2(0.8,0.8)).rgb;ROUGHNESS=0.91;METALLIC=0.0;}
 if(u>=22.0&&u<25.0&&((v>=2.0&&v<29.0)||(v>=39.0&&v<66.0))){ALBEDO=texture(warm_walnut,uv/vec2(0.65,1.3)).rgb;ROUGHNESS=0.65;METALLIC=0.0;}
 if(u<26.0&&v>=30.0&&v<38.0){ALBEDO=texture(staff_zinc,uv/vec2(0.75,0.75)).rgb;ROUGHNESS=0.61;METALLIC=0.65;}
}
