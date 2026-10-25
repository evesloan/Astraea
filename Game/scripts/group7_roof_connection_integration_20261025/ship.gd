extends "res://scripts/clinical_transfer_junctions_integration_20261024/ship.gd"
# Append after all original deferred receiving work, before readiness admission.
func finish_runtime_startup()->void:
 startup_deferred_builders.append(_install_group7_roof_connection)
 await super.finish_runtime_startup()
func _install_group7_roof_connection()->void:
 if not load("res://group7_aft_fixture_clearance_20261025/adapter.gd").build(self):
  push_error("Aft fixture clearance installation failed");get_tree().quit(1);return
 var roof:Node3D=load("res://group7_terminal_roof_links_20261025/runtime_adapter.gd").build(self)
 if roof==null:push_error("Group7 roof connection installation failed");get_tree().quit(1)
