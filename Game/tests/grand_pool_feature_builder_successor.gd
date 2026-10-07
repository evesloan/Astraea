extends RefCounted
# One reviewed pool feature call. Return a historical digest only after an exact
# byte reversal; all other historical proof documents remain unchanged.
const BUILDER := "scripts/grand_pool_architecture.gd"
const PREVIOUS_BUILDER_SHA := "a764584c22010fc5aaf6ef36cf257fb70be73b659e2d6ff189ec84ca8e4be2b4"
const CANDIDATE_BUILDER_SHA := "b0c348ee6af779bb1e7447e77fc178b63c873f393b1b2a4613d33da7e8f45333"
const ADDED_LINE := "\tload(\"res://scripts/grand_pool_feature_layers.gd\").build(parent,ship,root)\n"
const FEATURE_INPUTS := {"scripts/grand_pool_feature_layers.gd":"9e629e04335f4e5beb578c4ae40c44ccbba16ee074bb8acecd35b81519a343ea","data/architecture/GRAND_POOL_FEATURE_LAYERS_RUNTIME.json":"ae442888b8a06f0204cfeeacf1e3832b9b5b2d2dfbed941b181821de4eca751b"}
# The east gallery is one exact later append; normalize it before the retained feature proof.
const EAST_GALLERY_BUILDER_SHA := "2437bde87f2733636edb34f7e86cb2b11805e7693fc88566b1bdc345e7e495f4"
const EAST_GALLERY_ADDED_LINE := "\tload(\"res://scripts/grand_pool_east_gallery.gd\").build(parent,ship)\n"
const EAST_GALLERY_INPUTS := {"scripts/grand_pool_east_gallery.gd":"56ea19c414fca32277612583456fb9a8056ed2dc7ffefb842d4d2025b9c8b497","data/architecture/GRAND_POOL_EAST_GALLERY_RUNTIME.json":"ea1df244ad7e80fa45a471afda87a581a7cd923d3d50a1af403a828ece1d9dc7","scripts/grand_pool_connected_gallery_furniture.gd":"8266938a74f84e7feb037c228c6357bc0cf7eaf4d26325ed2d2a81a0e45a7149"}
const POOL_HELPER := "tests/secondary_engineering_pool_ship_successor.gd"
const PREVIOUS_HELPER_SHA := "07d0c1494b297763de23612ef9f7b6d9e145791a190c03a3be0bd9d4a7c72bd5"
const CANDIDATE_HELPER_SHA := "c4e757ca80bc85e8fe4f7c41df5d3a3d1d2deb96ac0aa087760f30cf3cf4c241"
const OLD_CHECK := "\tassert(FileAccess.get_sha256(\"res://\"+BUILDER)==BUILDER_SHA,\"Pool builder bytes changed\")\n"
const NEW_CHECK := "\tassert(load(\"res://tests/grand_pool_feature_builder_successor.gd\").retained_sha256(BUILDER)==BUILDER_SHA,\"Pool builder bytes changed\")\n"

static func retained_sha256(path: String) -> String:
	assert(path in [BUILDER,POOL_HELPER],"Pool feature successor has only two exact paths")
	var source := FileAccess.get_file_as_string("res://"+path)
	var actual := source.sha256_text()
	if path==BUILDER:
		if actual==EAST_GALLERY_BUILDER_SHA:
			assert(FileAccess.get_sha256("res://"+path)==EAST_GALLERY_BUILDER_SHA,"Exact east gallery builder bytes required")
			for input in EAST_GALLERY_INPUTS:
				assert(FileAccess.get_sha256("res://"+str(input))==str(EAST_GALLERY_INPUTS[input]),"East gallery input changed: "+str(input))
			assert(source.count(EAST_GALLERY_ADDED_LINE)==1 and source.ends_with(EAST_GALLERY_ADDED_LINE),"East gallery call must be appended exactly once")
			source=source.trim_suffix(EAST_GALLERY_ADDED_LINE)
			assert(source.sha256_text()==CANDIDATE_BUILDER_SHA,"Every prior feature builder byte must survive")
			actual=source.sha256_text()
		if actual==PREVIOUS_BUILDER_SHA: return actual
		assert(actual==CANDIDATE_BUILDER_SHA,"Unknown pool feature builder")
		for input in FEATURE_INPUTS:
			assert(FileAccess.get_sha256("res://"+str(input))==str(FEATURE_INPUTS[input]),"Pool feature input changed: "+str(input))
		assert(source.count(ADDED_LINE)==1 and source.ends_with(ADDED_LINE),"Feature call must be appended exactly once")
		source=source.trim_suffix(ADDED_LINE)
		assert(source.sha256_text()==PREVIOUS_BUILDER_SHA,"Every old pool builder byte must survive")
		return source.sha256_text()
	if actual==PREVIOUS_HELPER_SHA: return actual
	assert(actual==CANDIDATE_HELPER_SHA and source.count(NEW_CHECK)==1,"Unknown pool helper successor")
	source=source.replace(NEW_CHECK,OLD_CHECK)
	assert(source.sha256_text()==PREVIOUS_HELPER_SHA,"Every other old pool helper byte must survive")
	assert(retained_sha256(BUILDER)==PREVIOUS_BUILDER_SHA)
	return source.sha256_text()
