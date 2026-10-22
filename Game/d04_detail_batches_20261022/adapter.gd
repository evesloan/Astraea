extends RefCounted
static func install(ship:Node3D)->Dictionary:
 var manager:Node=ship.d04_detail_residency
 assert(manager!=null and manager.entries.is_empty() and not ship.has_meta("d04_exact_batches_installed"))
 assert(manager.get_script().resource_path=="res://scripts/startup_residency_20261020/d04_detail_residency.gd")
 assert(FileAccess.get_sha256(manager.get_script().resource_path)=="4c0c914f7bfafdd9f29c9b45e2c4c08b4aab148a5ed38ddddedce7813d0efed7")
 var path:="res://d04_detail_batches_20261022/runtime_r004/INDEX.json"
 assert(FileAccess.get_sha256(path)=="861eaa437da3f897303ac8e30115f30fcd7199c85121bf104f93706ec4e9fe84")
 var next:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(path))
 assert(next.rooms.size()==120 and manager.index.keys()==next.rooms.keys())
 for file:String in manager.index:
  var old:Dictionary=manager.index[file].duplicate(true)
  old.detail_path=next.rooms[file].detail_path;old.detail_sha256=next.rooms[file].detail_sha256
  assert(old==next.rooms[file],"Only exact detail paths and hashes may change")
 var pins_path:="res://d04_detail_batches_20261022/SHARED_PINS.json"
 assert(FileAccess.get_sha256(pins_path)=="027208f7596d8627ad351fc250bce46eb633a8b9afb54eea873c1c96059fb7aa")
 var pins:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(pins_path))
 for file:String in pins:assert(FileAccess.get_sha256(file)==str(pins[file]),"Shared immutable resource changed: "+file)
 manager.index=next.rooms
 var receipt:={"rooms":120,"shared_files_verified":pins.size(),"original_manager_preserved":true,"enter_m":manager.ENTER,"keep_m":manager.KEEP,"shells_contacts_identities_unchanged":true}
 ship.set_meta("d04_exact_batches_installed",receipt)
 return receipt
