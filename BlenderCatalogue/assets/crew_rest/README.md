# Crew rest and individual privacy

Two original script-assisted Blender designs, not a recovered ship interior. The shared-room photograph informs fitted privacy, reachable personal fittings, modest washable structure and warm cloth. The blueprint informs the technical crew programme only; old population/species/room labels are not renewed authority.

- **AST-CRW-001** is one dry single-place rest frame, 1.08 × 2.20 × 1.10 m. It has six low frame legs, supported slats, two floor-reaching headboard supports, a deliberately crowned mattress and pillow, and a draped blanket with an actual mattress contact. It is not the earlier three-pad clinical deck. The source has 34 editable mesh parts, exported as six material meshes.
- **AST-CRW-002** is one independently floor-supported side curtain and track, 0.192 × 2.50 × 2.12 m. Two honest posts support a round track; 25 open-hole rings support the accordion textile through small suspension tapes. The source has 63 editable mesh parts, exported as seven material/ownership meshes in either state. The separate gathered export is a state of the same design.

The common source datum is floor at the centre of the **foot end**, with footprint extending toward +Y. It is not a centred furniture pivot. +X is the curtained access side; +Z is up. Native GLB maps (x,y,z) to (x,z,−y). The frame is reused twice by the lead's relative QA arrangement; this creates no room assignment, person, registered berth or supported stack.

## Source and materials

`source/build_crew_rest.py` creates editable semantic parts and ordinary Principled materials in installed Blender 4.3.2. Frame resizing means editing those semantic meshes/coordinates and coordinating the interfaces/collision records. The configuration summary is not a live dimension rig or a mechanical adjustment claim. Only the exported dimensions are checked.

The shared staff material files remain unchanged. Three original deterministic 256px woven textures supply ecru bedding, terracotta blanket and muted sage privacy fabric. `textures/draw_crew_cloth.py` reproduces them. No reference pixels were copied. Ordinary solids use explicit metric UVs; curtain U is developed textile distance, V is height, at 0.4 m per tile. The same textile UVs are retained in both states. `dependency_manifest.json` closes every file loaded by the builder, including all shared staff roles.

## Curtain states and motion

The genuine `AST-CRW-002_CURTAIN_MOTION` root owns the fabric, rings, suspension tapes, grip and moving grip marker. Its source `gather` property drives root position, hanger spacing and two fabric shape keys. The closed state is t=0; gathered is t=1. Native exports retain the motion root and its markers, but contain authored static states, not a runtime actuator or cloth simulation.

For t in [0,1], leading Y = .02 + 1.8t and span = 2.16 − 1.8t. Trailing Y remains 2.18. Each of 24 pleat segments has developed length 0.10295630140987001 m; total developed width is 2.4709512338368804 m. Half-depth is solved from that length, growing from .025 to .05092887196865841 m. Gathered neutral fabric spans Y1.82–2.18. Cloth thickness is 3 mm and the lower edge stays at Z.28. This geometric model preserves developed width while gathering; it makes no prediction of gravity, friction, stretch, drape physics or interaction.

The complete conservative moving envelope is X.615071128–.734928872, Y.004–2.188, Z.28–2.104 m. It includes the leading grip and suspension tapes, not only fabric. The fabric has at least .087571128 m conservative separation from the bed's X=.54 outer rail. The leading grip stays 8 mm beyond the foot stop, and the last ring stays 16 mm before the head stop. The rings' inner upper edge bears on the rod's top edge throughout the authored interval. The separately marked physical rod facet has its actual sloped normal; an ideal +Z normal is not incorrectly assigned to that faceted surface.

`pose_contract.json`, `interface_api.json` and `collision_proposals.json` distinguish source formulas, physical contacts, use reservations, complete bounds and limitations. Eleven checked source poses include the true closed state, .001 and .999 near-boundary samples. The continuous bound is justified by the monotone analytic formulas; finite samples alone are not presented as proof of arbitrary cloth motion.

## Headboard fitting and privacy limits

The sibling AST-CRW-004 module places its rear contact plane at source translation (−.26,2.14,.88), without rotation. Its +Y rear normal opposes the real headboard −Y face. Four shared witnesses are X−.37/−.15, Y2.14, Z.76/1.00. The pillow maximum Z.657 leaves 78 mm below the shelf underside at Z.735. The central rest-use reservation is X±.40, Y.30–1.52, Z.565–1.10; it is a component proposal, not a sleeping body envelope.

Closed fabric occludes the declared three side test rays from source eyes at X2.0, Z1.15, Y.45/.90/1.40 to X0,Z.59 at the same Y. The gathered state clears those rays as a positive opening control. These are bounded side privacy observations. Top, end, under-hem and oblique views remain open or unverified; whole-room and acoustic privacy are not certified.

## Verification and limits

Actual native GLB parsing checks finite geometry, positive transforms, normals/winding, nonzero UV triangle areas and exact embedded source texture pixels. Evaluated source checks verify marker distances/normals, clear declared voids, supported hanger positions and both privacy outcomes. Final ordinary-height imported views and exact input/image/camera hashes are in `qa/render_evidence.json`; no source/export input changed during capture. Earlier collision-only corrections preserve their exact evidence in `qa/collision_metadata_revision_before_finish_join_revision.json`. A subsequent narrow geometry revision terminates headboard supports at the slab underside and separates the tape/ring side finishes by 1 mm; earlier source/export/images remain in `qa/before_finish_join_revision/`. Current final captures bind the corrected sources. The first failed curtain camera framing is retained in `qa/camera_preflight_attempt1.log`; final framing passes.

`qa/source_only_rebuild.json` records an actual fresh reconstruction with no prior blends, GLBs or QA input. All three GLBs and the interface/collision/pose records reproduce byte-for-byte. `qa/source_signature_comparison.json` also matches original and rebuilt source hierarchy, geometry, UVs, modifiers, shape keys, drivers, properties and packed materials. QA floors, lights and cameras are inspection aids only.

Collision is a separate proposal: supports/rails/slats preserve under-frame space; rounded mattress and pillow use convex support-ring profiles; blanket drape is explicitly omitted soft detail over mattress collision, with an 80 mm conservative complete-surface omission bound (actual maximum vertex-to-mattress-boundary distance .079626210 m). Curtain collision is a parameterized thin-pleat profile with a 3 mm conservative join/thickness approximation, not an all-enclosing berth hull; small ring/tape/grip detail is excluded from actor collision while remaining in complete visual motion bounds. No collision, body, structural load, real host, six-species suitability, Baelin aquatic home, Mantelid cocoon, Mindo service, room ownership or game implementation is certified.
