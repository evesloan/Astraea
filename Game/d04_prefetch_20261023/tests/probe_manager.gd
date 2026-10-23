extends "res://d04_prefetch_20261023/manager.gd"
func _wanted(entry:Dictionary)->bool:return bool(entry.get("wanted",false))and not is_instance_valid(entry.detail)
func _prefetch_wanted(entry:Dictionary)->bool:return bool(entry.get("prefetch",false))and not is_instance_valid(entry.detail)
func _near_any(_entry:Dictionary,_margin:float)->bool:return false
func _points()->Array[Vector3]:return []
