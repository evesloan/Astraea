extends "res://scripts/atrium_terrace_integration_20261022/ship.gd"
const QUIET:="res://quiet_grove_specialty_20261022/"
func _construction_step(label:String)->void:
	await super._construction_step(label)
	if label=="quiet_grove_adoption.gd":
		assert(FileAccess.get_sha256(QUIET+"adapter_r002.gd") == "0d024ae2166c5cb9d7ca2f8448f728e2c2ceb1eed88868809136cdc11ac56217")
		assert(FileAccess.get_sha256(QUIET+"PACKAGE_R002.json") == "9345fedc659c690b77e2cc37d2981b5d03d56b7b469d585c7a415a927fca306d")
		assert(FileAccess.get_sha256(QUIET+"evidence/INDEX_R002.json") == "73ffd7e9227f7c2381720ca8c99c2c0e3209720aa4861dbe9dac59e23d47c915")
		assert(FileAccess.get_sha256(QUIET+"evidence/RECEIVING_BUILD.json") == "9858e7a976c8fe702d45210f03a778cbe9cea34eb8919dc773ea390d2edc8ac7")
		assert(FileAccess.get_sha256(QUIET+"evidence/GUARD_PLAN.json") == "1322362f2bff1170c51e7445780f4bc46efe7561bfe80456df9ebf6e1fc03d5e")
		assert(FileAccess.get_sha256(QUIET+"runtime/QuietGrove17Receiving_r001.scn") == "8eb5a6653c6a1b144985a139d1ff2195318ac8fd0c9ce877f2ba564d7b9ebe0b")
		assert(FileAccess.get_sha256(QUIET+"TARGET_BINDINGS.json")=="9dc4d337d4e709d2899b1f12bc145f9c4b81b9859fdc940b6885466134b0c3a8")
		load(QUIET+"adapter_r002.gd").build(self)
