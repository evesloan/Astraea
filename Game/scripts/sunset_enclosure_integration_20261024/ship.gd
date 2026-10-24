extends "res://scripts/tram_section_integration_20261024/ship_r003.gd"
func _construction_step(label:String)->void:
 await super._construction_step(label)
 if label=="sunset_adoption.gd":
  if FileAccess.get_sha256("res://sunset_enclosure_finish_20261024/adapter_r002.gd")!="d0afd0cb8bd0fad9116591bc6448544cffb184db486261985358b85be4fa71d1":
   push_error("Sunset enclosure adapter bytes differ");get_tree().quit(1);return
  var result:Node3D=load("res://sunset_enclosure_finish_20261024/adapter_r002.gd").build(self)
  if result==null:
   push_error("Sunset enclosure integration prerequisites failed")
   get_tree().quit(1)
