extends "res://tests/validate_medical_structure.gd"
# Same inherited functional assertions, physics rate and frame allowance.
# The prior480-second wall watchdog fired after all assertions printed PASS
# on this larger whole-ship scene. Preserve that failed receipt separately.
func _process(_delta:float)->bool:
 if started>0 and Time.get_ticks_msec()-started>900000 and not failed:
  require(false,"900-second bounded crew whole-scene watchdog")
 return false
