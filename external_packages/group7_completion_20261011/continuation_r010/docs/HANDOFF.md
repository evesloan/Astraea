# Group 7 R010: guarded local D18 floor edges

Both owned terminal necks now have coherent glazed edge protection around their actual retained eight-metre floors. Two new assemblies add218 closed parts: side/end rails, posts, glazed panels and52 contained underside clamps. The barrier stays outside the protected X±4 route and beyond the actual |Z|530 endpoint. No floor, room address, capacity, light, door or original source is added or changed. The86 previous model definitions,39 sources and eight doors remain exact; the selection now has88 models/39 sources/eight doors. The eight-source shadow budget remains unchanged.

## Implemented and tested

Editable native: `source/natives/G7_D18FloorEdges_r010.blend`, SHA256 `31efcfa8fcd32dd365992bfbccb8701e1188353d4cb57c6398daf537a75d4319`. Original metal/glass material data is appended from the immutable R009 native. The source audit passes11,534 checks, including closed positive-volume geometry and finite UVs. All316 planned member joints pass actual reopened native convex-solid half-space containment for both joined meshes at0.1mm tolerance. The two independently decoded exports contain2,616 triangles and match native points within0.1mm. Actual engine triangles also match within0.1mm, with maximum measured error0.000061035m. Only two new owned import settings disable compression.

Each underside plate has a measured positive projected contact polygon on the exact original D18 floor. The original floor is Y106.5 with0.24m thickness, so the receiving underside is Y106.26. Clamps connect through outside risers and posts to continuous rails and panel captures. End/side rails have actual corner joins. This is a complete geometric member graph for the local guard package; it is not a primary floor/fastener/guard load rating.

`qa/RUNTIME_CHECK.json` passes536 focused checks in actual baseline main with the opt-in candidate:218 protected-source queries with zero unexpected contacts,52 actual retained-floor underside witnesses, all166 unchanged full-eight-metre/four-metre air slices and30 original floor/worker poses. Twelve legs use the original player controller. Six normal-input guard stops contact the new barriers and preserve floor contact; side stops are at |X|≈3.87 and end stops at |Z|529.875, inside the original floor edges. Two fixture seeds locate the disconnected terminal starts. There are no position writes between walking legs or guard stops.

Source/underside identification excludes only the two new guard model RIDs. Air slices exclude only the player. Ordinary floor, worker, walking and guard-stop collision excludes none. Existing collision-cache margins are unchanged; their actual0.04m value is captured in the runtime report. New above-floor risers keep a0.10m boundary buffer. Only a plate's exact original floor receiver is permitted in its source-contact query; all other new parts require clear protected-source queries.

## Interfaces and visual review

This closes local floor-edge protection for the already constructed necks. The original floors terminate at |Z|530; end guards start beyond that endpoint. They block no retained route continuation or doorway. The glazing/end wall at |Z|531.5 and the original C2/source volumes remain intact. Group1/shared integration and Group4 travel/core owners must reconcile any future floor-end extension or core change explicitly. No current retained source guard was duplicated and no shared root/registry was edited.

`qa/views/SOURCE_R010_D18_FORE_GUARDED_NECK_PUBLIC_CONTEXT_WIDE.png` is the directly reviewed wide source-eye photograph. It shows the full floor/side/end guard sequence and raised neck roof, beams and lamps in their retained body landing. The review-helper floor exactly follows the existing compiler triangles. It uses actual source geometry/UV textures in neutral Workbench shading; it is not an in-game or final lighting/CRT/hardware image. Camera/native/source hashes and the140m local clip are in `qa/SOURCE_VIEW_RECEIPT.json`; Library identity is recorded separately. Original/native files are never resaved for rendering.

The first numeric plan had a smaller outward buffer. Before any native or Game import, that new geometry was moved outward to preserve existing contact margins as well as the full route air band. `qa/PREAUTHOR_PLAN001_MARGIN_BUFFER.json` and its script retain that preplan. No native/export/runtime failure occurred in this continuation, and no original criterion or source geometry was relaxed.

## Integration

1. Verify the branch manifest and exact independent remote receipt. All earlier original/selected/unselected source revisions remain retained.
2. Append only the two definitions in `docs/RUNTIME_APPEND.json` to `docs/PREIMAGE_GROUP7_COMPLETION.json`. No source/light/door replacement is required for this continuation.
3. Keep `group7_completion.gd` opt-in. Construction thread `01a11d7f-8ef6-70bc-858d-bdf8deb7000b` alone owns shared adoption; reconcile current Group1/4 floor-end and core interfaces before activation.
4. Refresh imports and run `godot --headless --path Game --script res://tests/group7_d18_floor_edges_check.gd`, then the independent source/export/import checks. This is baseline-scoped evidence, not the full project suite, largest-species/cart or current-main acceptance.

Group7 continues with ceiling/lighting review around the existing opaque D18 atrium cap and original two artificial-daylight coffers. No invented skylight or replacement cap is permitted. Primary receiver/member/connection capacity,293 original width reservations, Royalty790 and wet-roof/tank-bearing decisions, complete pressure/weatherproofing, service/care network, botanical/inhabited gameplay and final graphical/CRT/hardware/art acceptance remain held. No whole-group acceptance is claimed.
