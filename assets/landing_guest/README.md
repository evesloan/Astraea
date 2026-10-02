# Astraea guest landing interfaces — Batch11

Two new original script-assisted Blender components respond to the guest/private arrival reference and the warm residential material language. This is an independent component catalogue. The original ship, actual landing apertures, floor support, ceiling, door travel, bodies, lift behavior and native runtime remain unavailable.

## Designs

- AST-LND-001 — Guest arrival directory and rolled cove return. Exact designed envelope: X−0.70..0.70, Y0..0.65, Z0..2.80 m in Blender source. A rounded full-depth left return supports a localized cove. The inset original arrival field and its timber frame cant 20° toward source +X on an actual wedge joined to the rear spine. The artwork reads “GUEST ARRIVAL”; its nested silhouettes are abstract orientation art, not a live route or map. Timber caps, liner and inset field have real surface terminations. The original artwork is a5mm physical plate; its backing begins at the plate’s rear surface, avoiding distant coplanar interference. The directory wedge stops 6mm inside the visible frame caps. No core-spanning lintel, door casing, ceiling or full room is supplied.
- AST-LND-002 — Fitted single waiting seat and luggage edge. Exact designed envelope: X−0.70..0.70, Y0..0.75, Z0..1.05 m. One crowned clay seat has a 0.460 m top contact, a leaned teal back on a walnut shell, a shaped raised left cheek and a real load deck. A separate rounded timber luggage surface has 0.455 m soft contact strips. A fixed lower retrieval shelf is 0.122 m high and preserves its front opening. This is a useful waiting/storage combination, not a recolored chair or a moving drawer.

All dimensions are proposed component targets, not host dimensions or universal species-fit claims. Source .blend files retain named semantic objects, editable edge modifiers, ordinary role materials and packed images. GLBs contain evaluated static geometry consolidated by role, with actual marker nodes retained. Both are authored in metres, source X right/Z up/front−Y. Standard GLB conversion is(x,y,z)→(x,z,−y).

## Interfaces and context

Individual manifests include actual source/export bounds, semantic names, physical marker surfaces/normals, joins, voids, source hashes and proposed ship transforms. The axis mapping is explicit in marker_api.json and collision_proposals.json. Proposed ship placements keep the Batch11 central and front empty strips untouched; geometric screening of the combined proposal belongs to the lead review and is not an actor route test.

qa_context_placements.json is authoritative for inspection placements. Existing AST-GST-002 is shown only as disclosed QA context on 001 at source translation(0.49,0.47,1.93), with no rotation. It is excluded from the new source mesh, new export and new asset count. Its rear mounting plane has normal+Y and meets the real receiver’s−Y face atY0.47. The entire fixture projects only toY0.154, remaining inside the target envelope. Front withdrawal and underside diffuser access are geometric proposals; electrical isolation, tools and human access remain unverified. Physical mount/liner normals are separate from the proposed cove light-aim marker. No actual light output is present.

The 002 waiting-eye proposal is(−0.29,0.17,1.19)m; it is a nonphysical inspection datum. The real seat contact is(−0.29,0.30,0.46)m. No body model or pose rig is included.

Collision proposals use 9 structural shapes for 001 and 9 for 002. The cove’s concave profile is split into separate upper/lower roll compounds. The directory reading air, recessed cove, retrieval mouth and lower waiting opening remain empty under whole-volume tests. These are conservative structural compounds, not engine-tested physical collisions. Independent finite surface sampling at spacing at most 35mm observes 13.33mm maximum inflation for the revised left lower cheek, 0mm on the separate raised arm, and 36.07mm on the divider/right cheek compounds; the simplified seat/cushion compound retains 57.56mm at its corners. These are observed sample maxima, not certified continuous bounds. Exact shape measurements and report binding are in qa/collision_profile_approximation_notes.json. Positive structural probes and intentionally filled-void negative controls are in qa/native_coordinates_and_voids.json.

## Rebuild and evidence

Run Blender 4.3.2 from any directory:

    blender --background --threads 2 --python-exit-code 1 --python source/build_landing_guest.py

The generator resolves its own family/catalogue roots. Production inputs are its source script, the original textures/guest_arrival_original.png, standards/materials.py, materials/material_manifest.json and every loaded shared material PNG, including unused roles. No previous output, QA image or prior component silhouette is a build dependency. Generic mesh/UV/export construction methods follow existing catalogue conventions; the new semantic geometry and artwork are authored here. Original art can be regenerated with source/make_orientation_art.py using Python/Pillow; it uses no external font or image.

qa/source_only_rebuild_receipt.json proves a fresh source-only stage without pre-existing .blend, GLB, output manifest or QA inputs produces byte-identical final GLBs and identical semantic/marker/joins records. Rebuilt sources were then independently reloaded. Source .blend bytes can vary with saved file metadata, so geometric semantics and exact GLB bytes are compared.

qa/source_reload_checks.json records real evaluated source contact, opposing physical normals, support joins and dense void rays. qa/glb_validation.json independently parses native export geometry, normals, winding, UVs, embedded artwork/shared texture pixels and resolved node bounds. qa/camera_preflight.json records exact proposed camera frames. Final neutral imported-GLB captures, source freeze and evidence hashes are retained in qa. Existing fixture imports, floor and lights are labeled inspection aids. The earlier tight standing framing failure and superseded rectangular cheek collision proposal are preserved separately, not presented as a successful final capture.

The catalogue lead supplies independent profile/fixture/spatial review, promotion, packaging and durable backup. No subsequent batch is authorized by these author checks alone.
