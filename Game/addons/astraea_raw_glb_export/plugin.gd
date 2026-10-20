@tool
extends EditorPlugin

const RawGlbExport = preload("res://addons/astraea_raw_glb_export/export_plugin.gd")
var exporter: EditorExportPlugin

func _enter_tree() -> void:
	exporter = RawGlbExport.new()
	add_export_plugin(exporter)

func _exit_tree() -> void:
	remove_export_plugin(exporter)
	exporter = null
