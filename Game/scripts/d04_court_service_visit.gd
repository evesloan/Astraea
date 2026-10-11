extends RefCounted
# A private visit requires positive consent/vacancy evidence from its owner.
# No live occupancy provider exists for these unadopted D04 home proposals.
# Production therefore supplies no visit. Tests use an explicit temporary visit.
var actor:WeakRef
var request_id:StringName
var court_ids:Array[StringName]=[]
var consent_known:=false
var consent_allowed:=false
var active:=false
func allows(candidate:CharacterBody3D,court_id:StringName)->bool:
	return active and consent_known and consent_allowed and not request_id.is_empty() and actor!=null and actor.get_ref()==candidate and court_id in court_ids
