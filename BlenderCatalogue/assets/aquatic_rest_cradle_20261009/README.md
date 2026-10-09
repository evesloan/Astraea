# Lagoon Immersed Rest Cradle

AST-RST-AQ-001 is one original editable aquatic-rest component for proposed Astraea specialty-home construction. A continuous thick glazed basin contains a broad concave rest liner, a raised rear rest contour and lateral bolsters. The support is substantially immersed at the design waterline. Warm ash rim detailing, a low transfer nose, a grounded foot ledge and a front-right service dock explain how the fixture can be approached and maintained.

The master requires genuinely aquatic accommodations for Baelins; this component is a construction proposal addressing that functional direction. It has no recovered room assignment, species assignment, fixed species quota or verified body fit. It does not establish a complete room or working aquatic environment.

## Files and repeatability

- `AST-RST-AQ-001.blend`: compact native Blender 4.3.2 source with separately editable meshes/materials and named datums. Preview collection is separate.
- `AST-RST-AQ-001.glb`: fixture meshes and datums only, standard Y-up export. No preview floor, camera or lights.
- `build_aquatic_cradle.py`: original deterministic geometry/material/export recipe. Run `/usr/bin/blender -b --threads 3 --python build_aquatic_cradle.py`; append `-- --no-render` to omit the preview. Full catalogue ID is checked before creation. A later registration is accepted only for this exact family.
- `component_metadata.json`: dimensions, actual support/water/contact information, unassigned status and explicit limitations.
- `collision_proposal.json`: every native/exported mesh name, role, bounds and proposed collision policy. No runtime collision bodies are supplied.
- `validate_component.py`: independent native topology and GLB hierarchy/triangle/contact checks. Run under Blender first, then system Python with installed NumPy. No dependencies are downloaded.
- `native_mesh_validation.json`, `validation_report.json`, `deterministic_rebuild_validation.json`: bounded validation receipts.
- `preview_front_threequarter.png`: inspected component-only 960 × 860 Cycles preview without denoising. This is not in-engine art acceptance.
- `SHA256.json`: file hashes, excluding itself.

## Coordinates and physical surfaces

All metadata is metres in Godot/glTF coordinates: +X right, +Y up, front −Z. Native Blender front is deliberately +Y, an explicit exception to the catalogue default; export uses Blender (x,y,z) → glTF (x,z,−y). Floor datum is (0,0,0). Do not convert already-exported GLB positions again.

Actual bounds are X[-1.442657,1.560000], Y[0,1.235795], Z[-2.072000,1.907000]. Size is 3.002656 × 1.235795 × 3.979000 m, within the 3.6 × 1.6 × 4.2 m target. No engine placement scale is required.

The basin is a closed material mesh around an open cavity, with a real interior floor at Y0.16 m and an underside at Y0.025 m. The rim's horizontal material thickness is approximately 0.23–0.24 m. Its front height is Y0.635 m, and the rear height is Y1.115 m. A vertical probe at the basin center hits only interior floor/underside, not an invisible top cap.

The 65 mm thick contoured support runs Z[-1.37,1.35] and is 1.28–1.965121 m wide. The central contact is Y0.24125 m, the front center Y0.27 m and rear center Y0.70 m. The support's analytic shape and exact actual-mesh contact samples are in the metadata; they are proposed construction dimensions, not invented biological requirements.

Actual GLB support-contact datums:
- Front: [0,0.255596,-1.078571]
- Center: [0,0.241250,-0.010000]
- Rear: [0,0.442225,0.961429]
- Left/right: [±0.588000,0.289850,-0.010000]

## Water and collision

The original water surface is flat at Y0.57 m. It spans X[-1.141217,1.141217], Z[-1.609395,1.528261], with a clipped opening around the emerging rear support and lateral bolsters. The central support lies 0.32875 m below this plane. Minimum front rim freeboard is 0.065 m. Translucent teal water and six original mesh ripple ribbons make immersion readable without external textures.

WaterSurface_VisualOnly and all six Water ripple ribbon objects carry `NO_SOLID_COLLISION`. They must never become solid walkable surfaces. The water has no closed volume mesh and no implemented flow, quantity, buoyancy, splash, thermal/chemical regulation or persistent environmental state. The supplied water broad-phase AABB, Y[0.16,0.57] with the surface's X/Z limits, is planning metadata only: actual future fluid must follow the cavity and exclude support material. A nonblocking detection volume would require separate authoring and integration tests.

The six `static_concave_candidate` objects are the hollow basin, actual rest support, two lateral bolsters and two side transfer handles. Preserve their hollow/contoured surfaces with static concave triangles or a validated multi-convex decomposition. A single convex hull across the basin would cap the water cavity and is specifically inappropriate. The 17 `simplified_box_candidate` objects cover real contact/support/service pieces, including transfer slats. Thirty-two `no_collision_detail` objects are decorative seams, trim, small bearings and fittings. The complete per-mesh table is authoritative for this proposal. No physics bodies, layers or engine import choices are certified.

## Approach and service reservation

The transfer nose is 1.24 m wide and Y0.672 m high at the actual slat-top contact; the grounded foot ledge is 0.20 m high. There is no center-front bar. This is a low transfer edge, not a walk-through doorway, ramp or certified accessible facility.

Keep the front prism X[-0.67,0.67], Y[0.005,1.75], Z[-3.15,-2.08] clear. Keep the service prism X[1.59,2.49], Y[0.005,1.75], Z[-0.95,0.01] clear. Both are clear of this component's actual exported triangles. Room contents and actor/cart routes remain untested. The combined proposed room reservation is X[-1.48,2.49], Y[0,1.75], Z[-3.15,1.90], which includes external approach/service space beyond the component envelope.

The front-right service mounting point is [1.355,0.920,-0.50]; its external floor stance is [2.05,0,-0.47]. The control face, removable panel and supply spout are visible nonfunctional interfaces. Plumbing, control interactions and special-cleaner workflow remain integration tasks.

## Validation and limits

- 62 editable source meshes: 55 closed positive-volume solids and seven intentionally open, non-solid water/highlight surfaces. No degenerate faces or invalid/loose edges were found.
- 10,415 exported triangles, 12 original simple materials, no image textures.
- Exported node hierarchy, actual bounds, support contact samples, front/service clear prisms and water policies are checked independently from the builder. Wrong-axis negative control is rejected.
- Water triangles face upward. Centroid tests find no overlap with the actual exported raised support/bolster contact geometry. Very small clipped slivers are discarded below 1e-8 square metres before export; this is a visual surface, not a watertight fluid solver.
- A deterministic rebuild verifies byte-identical GLB, component metadata and collision proposal output. Native `.blend` save bytes are not claimed deterministic.
- Final source-preview pixels were inspected for open cavity, thick rim, immersed broad support, raised rear, water readability, approach and service mount.

An initial analytic water mask was replaced after bounded checks found two support-overlap samples. Exact convex-polygon subtraction of raised source triangles now constructs the water cutout. Tiny clipped facets and open-surface normals were also corrected before the accepted validation.

No Game import, room fit, species/body/animation compatibility, live water or environmental behavior, structural loading, accessibility, target hardware or final art acceptance is claimed. No Game files, existing families, catalogue registration, backups or publication were modified. The full current master application, complete chapters 6 and 8, coordinate contract, aquatic/intimate reference pixels and prior cocoon preview were consulted. All production meshes/materials here are newly authored; no downloads, paid services, credential/permission changes or engine switches were used.
