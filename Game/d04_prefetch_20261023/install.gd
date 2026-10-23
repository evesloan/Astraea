extends RefCounted
# Call only at runtime-ready safe boundary in an explicitly opted-in comparison.
static func install(ship:Node3D)->Dictionary:
 if OS.get_environment("ASTRAEA_D04_PREFETCH")!="1":return {"installed":false,"reason":"default_off"}
 var manager:Node=ship.d04_detail_residency
 if not ship.get_meta("runtime_ready",false)or manager==null:return {"installed":false,"reason":"runtime_not_ready"}
 if manager.entries.size()!=120 or not ship.has_meta("d04_exact_batches_installed"):return {"installed":false,"reason":"shared_D04_predecessor_required"}
 var original:="res://scripts/startup_residency_20261020/d04_detail_residency.gd"
 if manager.get_script().resource_path!=original or FileAccess.get_sha256(original)!="4c0c914f7bfafdd9f29c9b45e2c4c08b4aab148a5ed38ddddedce7813d0efed7":return {"installed":false,"reason":"unexpected_manager"}
 var fields:Dictionary={}
 for key in ["host","index","entries","elapsed","loads","releases"]:fields[key]=manager.get(key)
 var identity:=manager.get_instance_id();var physics:=manager.is_physics_processing()
 manager.set_script(load("res://d04_prefetch_20261023/manager.gd"))
 for key in fields:manager.set(key,fields[key])
 manager.set_physics_process(physics);manager.set_process(true)
 return {"installed":true,"manager_identity_preserved":manager.get_instance_id()==identity,"registered_rooms":manager.entries.size(),"production_default_changed":false}
