# Independent residential source audit

## Decision

Approved for source-candidate retention: production_r005. This is not Game adoption or final room/district acceptance. Parent must complete the independent remote/predecessor retention gate separately.

## Verified

- Decoded all 17 actual shell GLBs: finite geometry, source bounds/triangle totals, at most 10 material batches, datum positions and glazing policy agree.
- Decoded the actual portable Blender file without running Blender: 498 instance transforms and 17 package-relative libraries agree with the production plan. Prototype assemblies have no nested Blender library dependencies.
- All 1,296 new rest bindings uniquely match actual prototype markers and world coordinates, with a maximum world-position difference of 0.000000197 m. IDs reuse the schedule's explicit proposed rest-slot namespace. The 500-unit plan retains 1,300 rest positions including four in the two preserved installed rooms.
- All 113 pinned upstream inputs remain unchanged. Current input, source/prototype and section hash references pass.
- Bidirectional triangle-edge testing covers all 183 placed components across all 17 source prototypes. No freestanding furniture/shell penetration, separate furniture-pair AABB overlap, or saved closed-door-leaf/shell penetration was detected.
- All 17 detail-prop GLBs exist; exported book geometry counts match actual shared prototype variants. The 303 different requested per-unit variants are explicitly deferred.
- 668 adjacent door pairs retain different layouts. The full 1,000-unit proposal remains distinct from the 500 supported production lane: 81 candidate luxury replacements, 2,238 proposed maximum rest places, unchanged 2,000 passenger admission cap. All finished flags remain false.

## Corrected findings

The failed r004 bench arrangements intersected the bath return or shaped wainscot in 12 prototypes serving 361 new instances. The r005 correction moves family benches/tables 0.10 m inward and 0.09 m deeper, family writing chairs to depth 7.04 m, and standard A benches/tables 0.05 m inward. Standard B remains unchanged. Both actual-output geometry and furniture-pair tests pass after these changes. Failed r004 evidence and the virtual-offset proposal are retained beside this report.

The original map also lacked explicit anchor ordinal crosswalks, root-relative paths and a reproducible prop layer. Those issues are corrected in r005. In particular, 38 instances reverse one or more prototype ordinals: consumers must use anchor_bindings rather than equating ordinal numbers.

## Explicit exceptions and limits

The broad probe reports 51 fixed mounting interface pairs: shower screen/post embedment at the entry-wall face, entry fixed casing/pocket/header joins, and bath fixed frame/header joins, in all 17 prototypes. No moving leaf is involved in these saved closed-state intersections. Treat these as declared candidate mounting seams, not proof of working door motion.

This audit does not establish door sweeps, body/cart/fixture approach fit, Game collision/import behavior, real atrium visibility, surrounding streets, floor ownership/support, protected-void safety, runtime persistence, species fit or district completion. Absence of mesh-edge crossings is a focused source screen, not a full physics/clearance proof. Shell GLBs contain no node extras, so use explicit datum names and the instance map for shell identity; apply the extras Dictionary convention only where extras exist.

## Evidence

- FINAL_REVIEW_r005.json: review scope and final artifact hashes
- NUMERICAL_AUDIT_r005.json: actual GLB and Blender byte-level checks
- CORRECTED_CONTRACT_AUDIT_r005.json: identities, paths, input hashes and prop exports
- BROAD_CLASSIFIED_BIDIRECTIONAL_CROSSINGS_r005.json: all component/shell tests and mounted seams
- BROAD_FURNITURE_PAIR_AABB_r005.json: independent component overlap screen
- PROTOTYPE_LIBRARY_PORTABILITY_r005.json: no nested source libraries
- FULL_SCHEDULE_CHECK.json: supported lane versus full proposal
- SOURCE_SURFACE_CROSSING_PROBE.json and BROAD_CLASSIFIED_SURFACE_CROSSINGS_r004.json: failed predecessor evidence
- PROPOSED_OFFSETS_CROSSING_PROBE.json: read-only virtual correction test
