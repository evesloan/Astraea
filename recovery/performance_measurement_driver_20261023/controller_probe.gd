extends "res://d04_surface_cells_20261023/controller.gd"
# Measurement-only subclass installed before original setup; production bytes untouched.
var measured_calls:=0
var measured_total_us:=0
var measured_max_us:=0
var fallback_events:Array=[]
func _process(delta:float)->void:
 var started_us:=Time.get_ticks_usec()
 super._process(delta)
 var duration:=Time.get_ticks_usec()-started_us
 measured_calls+=1;measured_total_us+=duration;measured_max_us=maxi(measured_max_us,duration)
func restore_all(reason:String)->void:
 fallback_events.append({"ticks_us":Time.get_ticks_usec(),"reason":reason})
 super.restore_all(reason)
func telemetry()->Dictionary:
 return {"controller_calls":measured_calls,"controller_total_us":measured_total_us,"controller_max_us":measured_max_us,"existing_light_guard_max_us":guard_max_us,"fallback_events":fallback_events.duplicate(true),"activations":reports.duplicate(true),"enabled":enabled,"stopped":stopped,"optimized_resident_count":observed.size()}
