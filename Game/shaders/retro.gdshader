shader_type canvas_item;
uniform bool effects_enabled = true;
uniform float dither_strength : hint_range(0.0, 1.0) = 0.3;
uniform float scanline_strength : hint_range(0.0, 0.12) = 0.0;
void fragment() {
 vec4 c = texture(TEXTURE, UV);
 if (effects_enabled) {
  ivec2 p = ivec2(floor(UV / TEXTURE_PIXEL_SIZE));
  int x = p.x % 4; int y = p.y % 4;
  float b[16] = float[16](0.,8.,2.,10.,12.,4.,14.,6.,3.,11.,1.,9.,15.,7.,13.,5.);
  float threshold = (b[y*4+x] / 16.0 - 0.5) * dither_strength;
  c.rgb = floor(clamp(c.rgb + threshold / 63.0, 0.0, 1.0) * 63.0 + 0.5) / 63.0;
  c.rgb *= 1.0 - scanline_strength * float(p.y % 2);
 }
 COLOR = c;
}
