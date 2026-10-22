@tool
extends EditorPlugin
var exporter:EditorExportPlugin
func _enter_tree():
 exporter=load("res://addons/astraea_contract_export/export_plugin.gd").new()
 add_export_plugin(exporter)
func _exit_tree():
 remove_export_plugin(exporter)
