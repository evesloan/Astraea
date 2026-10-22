extends "res://scripts/consolidated_construction_20261022/ship.gd"
# Additive successor: every original builder and readiness gate executes unchanged.
var tidal_contacts: Node
func _construction_step(label: String) -> void:
	if label == "tidal_garden_adoption.gd":
		assert(tidal_contacts == null, "Tidal contacts may be adopted only once")
		assert(FileAccess.get_sha256("res://scripts/consolidated_construction_20261022/ship.gd") == "e06bd5351b10b3174a0dae3fc9959dde57eaec5e7d34491898f7b6910a694215")
		tidal_contacts = load("res://scripts/startup_contact_residency_20261022/manager.gd").new()
		tidal_contacts.name = "TidalImmutableContactResidency"
		$ShipSystems.add_child(tidal_contacts)
		tidal_contacts.setup(self)
		var house := $ShipSpace/Districts/TidalGardenReceivingCandidate
		assert(house.get_meta("installed_guest_units") == 131)
		assert(find_child("ForwardStaffUpperInterfaces",true,false).get_meta("upper_operation_enabled"))
		tidal_contacts.adopt(house)
		tidal_contacts.adopt($ShipSpace/Districts/SpecialtyHomeCandidates)
		assert(tidal_contacts.entries.size() == 7666, "Reviewed immutable contact set changed")
		tidal_contacts.refresh()
		print("TIDAL_IMMUTABLE_CONTACTS ",JSON.stringify(tidal_contacts.statistics()))
	await super._construction_step(label)

func arrive_at(arrival: Vector3, facing_y: float) -> bool:
	if tidal_contacts != null: tidal_contacts.prepare_position(arrival)
	return super.arrive_at(arrival,facing_y)
