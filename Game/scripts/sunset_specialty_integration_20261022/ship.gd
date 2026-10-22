extends "res://scripts/quiet_court_balance_integration_20261022/ship.gd"
func _construction_step(label:String)->void:
 await super._construction_step(label)
 if label=="sunset_adoption.gd":
  assert(FileAccess.get_sha256("res://sunset_specialty_bank_20261022/adapter_r004.gd") == "113f7b85703d7a67f0be8ed4aa6a8f21d83a46e73bc8feaa22b47d8ab037347a")
  assert(FileAccess.get_sha256("res://sunset_specialty_bank_20261022/PACKAGE_R002.json") == "d0a3bbc7db1db11574580c4a71a5fd3d54d1e553004015149aea6e731adb5acf")
  assert(FileAccess.get_sha256("res://sunset_specialty_bank_20261022/evidence/INDEX_R002.json") == "5d06379d1f6d1c5ee9aa1cc97893b4cb816023670bb6c5b6a100068c48222b9d")
  assert(FileAccess.get_sha256("res://sunset_specialty_bank_20261022/evidence/RECEIVING_BUILD_R003.json") == "9d986ed56c4ecb9c6ab29eaa6d16019f2ef6a8dddaa4ff9dada3dbcca9aa5f11")
  assert(FileAccess.get_sha256("res://sunset_specialty_bank_20261022/runtime/Sunset47Receiving_r003.scn") == "3df00a05c75a4cdc38c6f23d22bcd10d0a3962ff0fbe5af4b9225c8ebc622868")
  load("res://sunset_specialty_bank_20261022/adapter_r004.gd").build(self)
