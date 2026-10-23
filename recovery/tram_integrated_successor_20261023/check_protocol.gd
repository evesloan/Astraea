extends SceneTree
# Small protocol check only; never instantiates the ship or moves a real actor.
func _initialize()->void:
 var script=load(get_script().resource_path.get_base_dir()+"/route_profile.gd")
 if script==null or not script.can_instantiate():push_error("route observer cannot parse");quit(1);return
 var assembly:=Node3D.new();var motor:=Node3D.new();var safety:=Node3D.new();var restraint:=Node3D.new()
 assert(not script.admission_error(assembly,motor,safety,restraint).is_empty())
 assembly.set_meta("tram_operations_admitted",true)
 assert(not script.admission_error(assembly,motor,safety,restraint).is_empty())
 motor.set_meta("integration_motion_admitted",true)
 assert(not script.admission_error(assembly,motor,safety,restraint).is_empty())
 safety.set_meta("integration_boarding_admitted",true)
 assert(not script.admission_error(assembly,motor,safety,restraint).is_empty())
 restraint.set_meta("integration_joint_admitted",true)
 assert(script.admission_error(assembly,motor,safety,restraint).is_empty())
 assert(script.STATIONARY_FRAMES==15)
 var observer:Node=script.new();root.add_child(observer)
 assert(observer.cycles==2 and observer.dwell_us==12000000)
 observer.cancel();assert(observer.phase=="finished")
 observer.free();assembly.free();motor.free();safety.free();restraint.free()
 print("TRAM_ROUTE_PROTOCOL PASS 8 protocol checks; no physical motion or render validation")
 quit()
