extends "res://scripts/quiet_grove_integration_20261022/ship.gd"
const BANK:="res://quiet_grove_bank_20261022/"
func _construction_step(label:String)->void:
	await super._construction_step(label)
	if label=="quiet_grove_adoption.gd":
		assert(FileAccess.get_sha256(BANK+"adapter.gd")=="543c558ff283d2e744c85c2440b8750405b804337d7f36aa06f6df89a5b22538")
		assert(FileAccess.get_sha256(BANK+"adapter_r002.gd")=="5857bc664c6baaf20b69875eb7a09fd2d5890d9ed0ee76aa3a22330fb528f48d")
		assert(FileAccess.get_sha256(BANK+"PACKAGE.json")=="95bee981debbe7601e749d1903e99d1175578ebe16bbbf8a87df5b0445ae3a6a")
		assert(FileAccess.get_sha256(BANK+"ENCLOSURES_R002.json")=="c2482c211cba7a7cb2ff640d48ff957410d16036df49dbb689e9dc795c335866")
		assert(FileAccess.get_sha256(BANK+"evidence/INDEX.json")=="72b054d7d92e600aef4d7a0ce52587d3ff8a561d54636130872c3ebb1e12fd0d")
		assert(FileAccess.get_sha256(BANK+"evidence/GUARD_PLAN.json")=="81a42be31795bfb08f34a5169f36a2cfafed6a01c8a8ba088c7671e6c7ddeb6e")
		assert(FileAccess.get_sha256(BANK+"evidence/RECEIVING_BUILD.json")=="ca2e3fd8090252f2fa1da645654bb3ba99c8a3ef7d25e6479f2686a9b4c516cf")
		assert(FileAccess.get_sha256(BANK+"runtime/QuietGrove30Receiving_r001.scn")=="4b407dd4ac912310d48ce4ac1f1f13a9123d07438d1287d6a39347f06c9959c7")
		load(BANK+"adapter_r002.gd").build(self)
