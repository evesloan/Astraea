# Aquatic wet-use components

Two original editable catalogue designs for the D08 aquatic family. These are adjustable components, not recovered ship fixtures or working fluid systems. They add no room, changing slot, seat, guest capacity or species acceptance.

- AST-AQU-009, Crescent optional refreshment pedestal: 0.720 × 0.625 × 1.500 m in Blender X width / Y depth / Z up. Twin pearl crescent ribs carry an orange recessed hood, closed optional outlet, teal splash back and bounded select pad. Three actual alloy landing rails sit above an open collector floor, with useful gaps rather than a solid basin proxy. The vessel contact is Z0.915 m, with a separate unoccupied vessel volume above it. The 25 editable semantic parts have an actual geometric support path to the continuous floor isolator.
- AST-AQU-010, Supported rinse control blade: 0.640 × 0.6415 × 2.180 m. Two tapered perimeter rails and explicit orange gussets carry a shaped protective head into a real floor plinth. The teal control web has a deliberate 3 mm front reveal from the pearl rail faces. Select/stop areas are uncalibrated. The down-facing head and low connection are closed caps. The documented useful front air volume ends at Z1.82 m below the gussets; it is not whole-body or shower clearance.

## Coordinates and interfaces

Metres. Blender source X right, Y depth, Z up, front −Y. Native GLB maps source (x,y,z) to (x,z,−y), with front +Z and up +Y. Sources use the local floor plane as datum; real host support and apertures are unknown. Physical contact normals are distinct from approach reservations. `marker_api.json` and each asset manifest give both frames, named physical source parts, closed/default positions and intended contact types. Native GLB nodes and actual transformed triangles are checked in `qa/native_interface_collision_checks.json`.

Each orange rear service plate and its two solid relief grips is retained below its own purposeful removal root in both source and GLB. The zero pose is the closed source assembly; proposed withdrawal is source +Y0.40 m / native GLB −Z0.40 m, without a preliminary lift or rotation. Service-face markers are children of their plate root. The body is consolidated separately. Release hardware, handling force, tool reach and a real maintenance route are unassigned. No open-state derivative or operating animation is included.

The 009 removable plate starts at Z0.255 m, above its fixed sill. A full translated AABB reserve is tested against the fixed assembly, with a 1 mm departure from the intentional seating plane. The independent reviewer also checks the initial seating boundary. Rear approach proposals are separate from the extraction reserve. Front guest approach and low capped connection markers remain fixed.

## Editable source and export

Run:

    blender --background --threads 2 --python-exit-code 1 --python assets/aquatic_wet_use/source/build_aquatic_wet_use.py

The builder opens only itself, the unchanged `standards/aquatic_materials.py`, the aquatic material manifest and its seven PNGs. It creates missing output directories. It does not read existing new outputs, QA records or images. `dependency_manifest.json` records the exact ten input files and hashes.

Each `.blend` preserves 25 named semantic meshes, editable edge easing where useful, packed original shared material images, named markers and the independent removable plate root. Evaluated GLB copies are consolidated into five static material meshes plus two plate/grip material meshes. Textures are ordinary opaque Principled color maps, with metric UVs and no water shader or emission. The unused two sling textures are declared closure inputs because the shared helper loads them.

The original vessel-outline and three-stroke optional rinse symbols are simple attached mesh reliefs. They have no separate collision hulls. They do not certify a substance or species. No third-party graphic or organizational logo was copied.

## Evidence and limits

`qa/source_reload_checks.json` checks every part's support graph, named source contacts/normals, complete triangle/AABB receiver volumes and plate reserves. `qa/glb_validation.json` checks actual native transformed geometry, normals, UVs, texture pixels, bounds and triangles. `qa/native_interface_collision_checks.json` verifies native marker nodes against actual exported surfaces and tests complete clear boxes against the 28 / 22 structural convex compounds. Small cosmetic reliefs are intentionally noncolliding. Head and hood compounds follow convex profile bands so they preserve the actual underside recesses. Local convex overreach is described per compound: independent finite samples found up to 36.3 mm at an AST-AQU-010 rail taper and 24.5 mm between plate pulls, outside declared clear volumes. Those samples are not maximum-distance proofs.

`qa/source_only_rebuild_report.json` starts with no generated assets or QA inputs. It compares dimensions, parts, contacts, joins, voids, removal roots and metadata, and reproduces both GLBs byte for byte. `.blend` byte identity is not expected across relocated builds because Blender embeds file/session paths; source semantics are checked instead.

The ordinary-height imported render plan is recorded in `qa/camera_preflight.json`. The six final image hashes, source/export/interface hashes and before/after unchanged status are recorded in `qa/render_evidence.json`. Studio floor, lights and cameras are inspection aids. Failed first geometry and framing checks are preserved, including the unsupported early outlet, plate/sill sweep interference and excessive first rinse-void claim.

Both actual reference images were inspected: the rounded ivory/orange/teal waterpark artwork and original public blueprint. Existing aquatic float and edge renders informed material continuity. Historical D08 changing at longitudinal station 216 and aft staff towel care at 432 are distinct allocations; no connecting aperture, privacy opening or service route is invented. The older blueprint's D09 wellness label and capacities remain illustrative.

Host apertures, mounts, load capacity, headroom, drainage, plumbing, fluids, temperature, pressure, chemistry, consumption needs, species/body compatibility, operating safety, hygiene, game behavior and target-PC performance remain unvalidated. The capped fixtures do not imply functioning water or a real treatment process.
