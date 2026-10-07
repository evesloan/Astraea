shader_type spatial;
render_mode cull_disabled;
uniform sampler2D quiet_stone_texture : source_color, filter_nearest, repeat_enable;
uniform sampler2D warm_walnut_texture : source_color, filter_nearest, repeat_enable;
varying vec3 world_position;
void vertex() { world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz; }
void fragment() {
    bool practice = world_position.x >= 23.0 && world_position.x <= 43.0 && world_position.z >= -449.0 && world_position.z <= -406.0;
    // Source preview boxes use one-metre local Blender X/Y UVs. Receiving adds no extra mesh or floor height.
    vec2 uv_stone = vec2(world_position.x - 31.0, -(world_position.z + 432.0));
    vec2 uv_wood = vec2(world_position.x - 33.0, -(world_position.z + 427.5));
    ALBEDO = practice ? texture(warm_walnut_texture, uv_wood).rgb : texture(quiet_stone_texture, uv_stone).rgb * vec3(0.55, 0.58, 0.53);
    ROUGHNESS = practice ? 0.65 : 0.78;
    METALLIC = 0.0;
}
