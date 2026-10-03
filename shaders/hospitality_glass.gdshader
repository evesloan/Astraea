shader_type spatial;
render_mode blend_mix, depth_prepass_alpha, cull_disabled;
uniform vec3 pane_tint : source_color = vec3(0.19,0.37,0.38);
uniform float face_opacity : hint_range(0.0,1.0) = 0.23;
void fragment() {
 float facing=clamp(abs(dot(normalize(NORMAL),normalize(VIEW))),0.0,1.0);
 float edge=pow(1.0-facing,4.0);
 ALBEDO=mix(pane_tint,vec3(.56,.66,.65),edge*.45);
 ROUGHNESS=.30;
 SPECULAR=.5;
 ALPHA=face_opacity+edge*.30;
}
