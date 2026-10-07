shader_type spatial;
render_mode cull_disabled;
uniform sampler2D warm_stone_texture : source_color, filter_nearest, repeat_enable;
uniform sampler2D oatmeal_texture : source_color, filter_nearest, repeat_enable;
uniform sampler2D enamel_texture : source_color, filter_nearest, repeat_enable;
varying vec3 world_position;
void vertex() { world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz; }
void fragment() {
    bool dry = world_position.x >= 18.9 && world_position.x <= 29.1 && world_position.z >= 400.0 && world_position.z <= 452.0;
    bool wet = world_position.x >= 29.0 && world_position.x <= 49.7 && world_position.z >= 398.4 && world_position.z <= 425.0;
    // Exact source preview metric coordinates, single compiler-owned receiving top.
    vec2 metric = vec2(world_position.x - 8.0, 460.0 - world_position.z);
    ALBEDO = wet ? texture(enamel_texture, metric).rgb : (dry ? texture(oatmeal_texture, metric / 0.8).rgb : texture(warm_stone_texture, metric).rgb);
    ROUGHNESS = wet ? 0.68 : (dry ? 0.92 : 0.78);
    METALLIC = 0.0;
}
