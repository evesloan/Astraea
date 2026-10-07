extends RefCounted
# Authenticate a bounded byte-exact inverse before retaining historical proofs.
const PROOF := "res://docs/GRAND_POOL_CONNECTED_FINISH_SUCCESSOR.json"
const PROOF_SHA := "43fc79d9bf38f0b921eacf06a694dc95c5da72a1535a6a1cdcc8db37c4ef878c"
static func retained_sha256(path: String) -> String:
	assert(path in ["scripts/grand_pool_east_gallery.gd","data/architecture/GRAND_POOL_EAST_GALLERY_RUNTIME.json","scripts/grand_pool_connected_gallery_furniture.gd"])
	assert(FileAccess.get_sha256(PROOF)==PROOF_SHA,"Finish inverse proof changed")
	var proof: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(PROOF))
	for required in proof.required_new_files:
		assert(FileAccess.get_sha256("res://"+str(required))==str(proof.required_new_files[required]),"Finish input changed: "+str(required))
	for current in proof.files:
		assert(FileAccess.get_sha256("res://"+str(current))==str(proof.files[current].after_sha256),"Finish candidate changed: "+str(current))
	var row: Dictionary=proof.files[path]
	var text:=FileAccess.get_file_as_string("res://"+path)
	for i in range(row.inverse.size()-1,-1,-1):
		var edit: Dictionary=row.inverse[i]
		var offset:=int(edit.after_start)
		assert(text.substr(offset,str(edit.after).length())==str(edit.after),"Exact inverse span differs")
		text=text.substr(0,offset)+str(edit.before)+text.substr(offset+str(edit.after).length())
	assert(text.sha256_text()==str(row.before_sha256),"Every retained predecessor byte must survive")
	return text.sha256_text()
