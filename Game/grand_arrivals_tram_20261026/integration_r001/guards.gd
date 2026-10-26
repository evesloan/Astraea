extends RefCounted
static func verify()->bool:
	var pins:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://grand_arrivals_tram_20261026/integration_r001/CONTRACTS.json"))
	for bucket:Dictionary in [pins.prerequisites,pins.owned]:
		for path:String in bucket:
			if FileAccess.get_sha256(path)!=str(bucket[path]):
				push_error("Lower Arrivals candidate source differs: "+path);return false
	return true
