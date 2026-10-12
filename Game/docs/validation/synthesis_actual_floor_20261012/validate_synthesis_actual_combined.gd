extends "/workspace/astraea-protected-integration-20261012/Game/tests/group8/validate_synthesis_candidate.gd"
func _initialize()->void:
 assert(ProjectSettings.load_resource_pack("/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip",true))
 super._initialize()
