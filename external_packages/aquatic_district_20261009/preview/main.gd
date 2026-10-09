extends Node3D
# Standalone review only. Imports both temporary floor and architecture proposals.
func _ready() -> void:
 for path in ["res://models/AQD_architecture.glb", "res://models/AQD_floor_proposals.glb"]:
  add_child(load(path).instantiate())
 var plan = JSON.parse_string(FileAccess.get_file_as_string("res://plan.json"))
 for rec in plan.lights:
  var light = OmniLight3D.new()
  add_child(light)
  light.position = Vector3(rec.xyz[0],rec.xyz[1],rec.xyz[2])
  light.light_color = Color(1,.87,.69)
  light.light_energy = rec.energy
  light.omni_range = rec.range_m
 var env = WorldEnvironment.new()
 env.environment = Environment.new()
 env.environment.background_mode = Environment.BG_COLOR
 env.environment.background_color = Color(.06,.07,.08)
 env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
 env.environment.ambient_light_color = Color(.6,.7,.8)
 env.environment.ambient_light_energy = .35
 add_child(env)
 var camera = Camera3D.new()
 add_child(camera)
 camera.position = Vector3(62,47.15,242)
 camera.look_at(Vector3(80,46.25,212))
 camera.fov = 75
 camera.current = true
