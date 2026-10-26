# Static visual ownership correction — unfinished, not selected

Parent baseline: 1a51ed02ff3e6fc9873646940410639498f3caff. No production constructor, selected scene, residency manager, original asset, door controller or Windows package changed. This is a coherent candidate plus measured allocation evidence, not a movement-ready delivery.

## Ownership and representation

The two pinned Group3 remaining-crew imports are instantiated under Group3RemainingCrewBank by scripts/group3_remaining_crew_20261019/package.gd. Its 183 scripted doors and 549 physical lights are separate children. Repository search found no production reference to the imported decorative mesh paths or the two imported source-root names outside this builder. Player interaction walks collider ancestors looking for interact/get_interaction_label methods; no replaced leaf has scripts or these methods. Original source/allocation/provenance remains in immutable GLBs and PACKAGE.json; bank and source roots remain in the runtime.

The compiler refuses scripts, dynamic ancestors, gameplay metadata, groups, incoming/outgoing gameplay signal consumers, nondefault collision bodies, mutable/material-incompatible render state and unsupported children. Native MeshInstance3D::_mesh_changed and CollisionShape3D::_shape_changed/Node3D::update_gizmos connections were explicitly observed; their exact source resource, destination object, signal name and native callable identity are checked. Failed preflight attempts are retained, not passes. The previous guarded comparisons used incomplete native callback names; no source replacement occurred during those failures.

Final render_owner.gd retains original ArrayMesh resources, LODs, material identity/overrides, per-mesh culling bounds, transforms, layers, shadow/GI/occlusion flags and sorting/LOD settings. It creates ordinary RenderingServer instances without one MeshInstance3D scene node per immutable visual. Contacts retain the exact original Shape3D resources and transforms in spatially bounded StaticBody shape owners. Large original shape bounds remain individually owned rather than combined into a giant body. Disposable mesh/body/shape scene nodes are freed; there are no path proxies or active preimage arrays. Original door IDs, controllers and admission remain.

API mapping follows the retained engine's [official 4.6.3 VisualInstance/GeometryInstance implementation](https://raw.githubusercontent.com/godotengine/godot/4.6.3-stable/scene/3d/visual_instance_3d.cpp). This candidate is intentionally limited to these two source imports; arbitrary receiving rooms require a separate reference/lifecycle audit.

## Measurements and acceptance limits

Isolated bank ownership removal experiment: original static338,464,111 bytes; removing disposable contacts251,782,031; then visual leaves144,477,715. This is allocation accounting, not acceptable gameplay content removal.

Rejected instancing variant010: 10,742 fewer nodes, static337,803,115→313,755,679 bytes (22.9MiB saved), renderer+862,096 bytes, potential submissions−2177. Rejected merged variant011: 17,266 fewer nodes, static−44,673,409 bytes, but renderer21,884,949→262,699,521 bytes (+229.7MiB). Neither is selected. Their compiler snapshots are retained in variants; merge.gd is an unused diagnostic implementation, not called by the final compiler.

Final direct-instance variant012: nodes65,527→25,119 (−40,408); static337,803,115→244,877,685 bytes (88.6MiB saved); renderer21,884,949 bytes unchanged. It does NOT reduce renderer instance/draw count. No whole-ship extrapolation is accepted.

Correctness003: exit0/empty stderr; 1,464 retained floor/rest ray results compare exactly; all183 door identities and external-entry denials remain; all14,214 checked mesh weakrefs expire after owner teardown. Earlier correctness001 retained a temporary reference in the test collector; successor isolates reference collection and explicitly clears owner records on deletion. Original failure evidence is preserved. Full detach/reconstruction across a production streamed-room manager is not claimed; this bank is currently a permanently constructed owner.

At fixed1920×1080 camera, original/compiled both404 draws and90,292 primitives. Correctness003 median6.066→6.072ms, p956.254→6.232ms: no frame-time improvement. Both inspected correctness002 images show the same staff doorway, storage, walls, ceiling fixtures and floor; this is technical equivalence, not guest-space art acceptance. Pixel comparison002:328,257 pixels differ, only2 exceed8 channel levels, mean absolute RGB delta0.05652/255,max28. Not pixel-identical. Images and exact metrics are retained.

## Larger measured allocation target

Godot [Mesh::generate_triangle_mesh](https://raw.githubusercontent.com/godotengine/godot/4.6.3-stable/scene/resources/mesh.cpp) retains a TriangleMesh BVH when get_faces is used. An isolated probe compares this to transient [TriangleMesh.create_from_faces/get_faces](https://docs.godotengine.org/en/stable/classes/class_trianglemesh.html), preserving exact welding and face order.

Probe001: actual D07 source290 meshes/1,554,048 face bytes; retained cache adds8,395,376 bytes over transient. Exact face hashes match;20.645ms transient vs20.124ms cached.

Probe002: actual UpperAtriumInhabitation_r003.scn, SHA91c007f9fb31056a0eb1faca47c4841b30feb9e2ad1ef7374c626f6b7d135264;1816 meshes/48,463,488 face bytes. Static baseline218,538,940, after transient219,210,820, after cached461,421,984:242,211,164 bytes (231MiB) extra retained BVH. Exact face hashes match;680.492ms transient vs694.072ms cached. No production collision path changed yet, and this is not proof every live mesh has that cache. This is the next decision-relevant production candidate, not a speculative claim of multi-GiB savings.

Remaining: production integration and actual-owner memory measurement, full unchanged-safety tram route, hardware FPS and tested matching Windows export. Lower Arrivals and visual completion remain preserved/unfinished. No new full-route launch was spent on the insufficient bank-only savings; no user decision or permission blocker is pending.
