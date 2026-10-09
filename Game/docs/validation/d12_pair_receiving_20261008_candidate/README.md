# D12 pair isolated integration candidate

## Result

Prepared, not applied. The isolated full structural compiler passes with 300 compiled owners: all 296 prior complete records and order remain exact, followed by precisely four additions. New floor area is 5,204.789214440626 m². The prior layout's 310 records, all voids and other metadata survive exactly. The inverse restores the exact predecessor layout and compiled documents, including their source checks. No live Game, catalogue, corrected room source, Crown output, registry count, controller, runtime import, engine, render, backup or network write occurred.

The four schema-correct records are `D12_directory_07_room_floor`, `D12_directory_07_branch_floor`, `D12_directory_08_room_floor`, and `D12_directory_08_branch_floor`. Boundaries come unchanged from the actual-bearing proposal. The generated slab datum is Y78, thickness 0.24m, underside77.76. These are supported-footprint construction proposals, not structural-load or engineering acceptance.

The corrected native/runtime files for both rooms were compared byte-for-byte to the independently received retained archive associated with Library libfile_826ebf53172c8191ba50418c19511611 v0. RETAINED_SOURCE_MATCH.json records exact paths, members and hashes. No new retrieval or publication was performed.

## Guards: actual construction geometry

GUARD_SOLIDS.json describes 116 separately named closed solids for one proposed receiving asset, AST-RCV-D12-PAIR-001. The entire 172-entry catalogue was inspected by exact ID; this ID is unused. Nothing was registered and neither source room was assigned a replacement ID. Existing source and receiving construction conventions are retained: world metres, Blender(X,-Z,Y), editable native geometry, role materials, named support references and visible-mesh static contacts via ship.model.

For each side:
- Branch floor is Z213.7–218.3, from the existing route edge |X|4 to the room's actual support boundary |X|8.450000047683716.
- Guard centrelines are Z213.85/218.15. Feet are 0.20×0.20m, posts 0.10×0.10m, solid infill 0.05m thick, top rails 0.10m wide. Feet occupy Z213.75–213.95 and218.05–218.25, retaining 0.05m margin outside the full Z214–218 clear strip.
- Route-end closure pieces terminate exactly at |X|4 without fencing across or adding floor over the shared route. Stations |X|4.1,5.6,7.1,8.65 keep all feet on actual candidate floor. All components are supported by exact planar contacts; posts sit on shoes, rails meet post/cap faces, panels meet posts/shoes/curbs. No floating rails, coarse interpenetrating guard joints or hidden collision-only walls are used.
- At |X|8.65, each guard turns across the wider mouth wing to the unchanged source jamb. The jamb inner face is approximately Z212.225 or219.775. The receiving terminal uses measured source-triangle profiles at every lower-bevel height, verified invariant over its complete 0.10m X-width. It closes the lower corner wedge too; a box stopped at the flat jamb face would leave that wedge open.
- The solid barrier runs continuously from the route edge to the jamb across its entire Y78–79.10 height. Height-event and interval checks verify the piecewise-linear barrier. Both wider mouth wings are blocked against walking onto the exposed front ledge, while the central4m approach remains fully open. Existing room enclosure/jamb geometry is untouched.

GUARD_SOURCE_CHECKS.json measures every part's complete plan support and source-interior clearance. GUARD_CONTACT_GRAPH.json proves all116 components connect to floor-contact parts with no positive-volume pair overlaps. GUARD_VERTICAL_CONTINUITY.json checks every vertex-height event and interval. The fitted terminal/source interface uses actual triangle intersections, not nominal jamb bounds. These checks prove geometry only: proposed 1.1m guard height is not a regulatory/species or strength certification.

build_guards.py is deterministic native-authoring preparation only and WAS NOT RUN. It requires a new output directory, rechecks input hashes and the full catalogue exact ID, builds the named solids using retained role materials, and saves an editable BLEND plus GLB. It intentionally applies no bevel that could break exact interfaces. Its first outputs will need native reopen, export-triangle parity, manifold/contact tests and engine review before use.

## Compiler and reversibility

The existing compiler has strict predecessor allowlists. Its isolated successor adds a pinned four-owner wrapper before running every existing predecessor preservation function unchanged on the authenticated old-layout projection. It does not bypass the theater void/source-part checks, priority/void clipping, exact old geometry, chunk equivalence or slab-volume tests. Four new expected compiled records are authenticated. All other owner shapes are checked against the predecessor; all296 complete records are then required equal. The isolated full compiler verifies all applicable voids, triangle areas and slab overlaps. COMPILER_PRESERVATION.json also records the complete4×299 new/other-owner matrix.

The new proof lives at isolated/Game/data/architecture/packages/d12_pair_candidate/D12_PAIR_COMPILER_PROOF.json. The predecessor files in that package are exact preimages, not current outputs. Removing four records alone is insufficient for byte-exact rollback of the generated document: restore its original source_checks and exact serialized predecessor bytes too. Restore the original compiler from its pinned preimage; remove only the new wrapper/package/loader/assets installed by this transaction, and remove only the single loader invocation from ship.gd. Preserve any later unrelated work; a drifted receiver requires reconciliation, never wholesale preimage overwrite.

Nine new negative controls reject duplicate owners, old owner edits, new boundary edits, void edits, old compiled datum corruption, new thickness corruption, missing jamb terminals, missing mouth wings and clear-strip intrusion. The earlier retained floor/source packet supplies its distinct original sealed-entry, underbearing centreline floor, narrow branch, route overlap and void controls; those are inherited evidence, not represented as newly rerun here.

## Proposed application map (none applied)

1. Game/data/spatial_layout.json: append only FLOOR_OWNER_ADDITIONS.json to the exact pinned current layout, retaining all prior records/metadata.
2. Game/tools/compile_layout.py: adopt only the isolated additive-wrapper diff; preserve every other line. Game/tools/d12_pair_incremental_preservation.py: new wrapper.
3. Game/data/architecture/packages/d12_pair_candidate/: install the proof plus its exact predecessor data/spatial_layout.json, data/generated/structural_meshes.json and docs/LAYOUT_COMPILE_CHECKS.json. Never overwrite another package.
4. Game/data/generated/structural_meshes.json and Game/docs/LAYOUT_COMPILE_CHECKS.json: regenerate through the final compiler; require exact match to isolated new ownership and full predecessor preservation. Existing compiler canonicalization diagnostic output paths may refresh only as part of that later authorized compiler run.
5. Game/assets/models/D12_directory_07_entry_successor.glb and D12_directory_08_entry_successor.glb: new, hash-verified copies from runtime_manifest.json source_local_path. Assert destinations absent or exact same hashes before copying. Identity placement only, no added translation/yaw/scale.
6. Game/data/architecture/d12_pair/runtime_manifest.json and Game/scripts/d12_pair_receiving.gd: candidate manifest/loader. Loader refuses activation until the generated guards have a verified runtime SHA256. It uses existing ship.model static contacts; no source collision is disabled, and it changes no shared controller.
7. Game/scripts/ship.gd: later insert exactly one invocation, load("res://scripts/d12_pair_receiving.gd").build(self), alongside existing receiving loaders before lighting_budget.configure. No full-file replacement from this candidate and no unrelated Crown edits.
8. BlenderCatalogue/assets/receiving_structure/d12_pair_20261008_candidate_r001/: eventual build_guards.py, GUARD_SOLIDS.json, native/export/proof outputs. Game/assets/models/AST-RCV-D12-PAIR-001.glb only after native/export acceptance and final identity/hash pin. Catalogue registration/count decisions are outside this transaction and were not made.
9. Preserve both corrected editable room sources separately under Game/data/architecture/packages/d12_pair_sources/{D12_directory_07,D12_directory_08}/source/section_entry_successor.blend with their corrected build_section.py and native/runtime proof records, or use an explicitly mapped retained source-package location. These are partial successor overlays, not replacements for original complete source packages/dependencies. Never run their generators from the partial overlay alone.
10. Retain this candidate/proofs under a new Game/docs/validation/d12_pair_receiving_20261008_candidate path only when root authorizes application. No existing validation files are targets.

## Remaining gates and precise limitations

- Recheck all input pins and live296-owner baseline immediately before application. Crown-only work does not authorize ignoring drift; a changed ship.gd must receive a narrowly rebased one-line insertion. Recheck exact destination identities and full catalogue lookup.
- Root must satisfy the current production backup/retention gate and separately retain this new transaction plus final authored guards before live adoption. Earlier retained sources do not independently retain this new compiler/guard packet.
- Structural adequacy remains unresolved: 0.24m slabs cover measured ground-bearing footprints but do not establish primary-deck spans, vertical load paths, post anchor capacity, edge distances under load, upper/lower structure or hull/imported-family separation. Do not present static footprint coverage as engineering approval. No new geometric interface blocker was found within the measured branch/jamb envelope.
- Execute the deferred Blender build in the authorized single lane, reopen saved native, verify exported vertex/triangle/material/support correspondence, then pin final native/runtime hashes and retain independently. Recheck all guard-source contacts, the entire barrier, no interior overlap, exact clear strip and collision on exported/imported geometry.
- Run current Godot4.6.3 Compatibility import, focused receiving/identity/contact tests, the full tools/validate.py suite and graphical outside-to-inside arrival. Test both directions across each floor seam with the actual player and loaded cart, turns, both4.6m branches, shared-route crossing/opposing traffic, guard contact, jamb/crown clearance and lower/upper structure. Original source sweeps alone are not runtime passage acceptance.
- Runtime loader syntax, GLB import, physics, visual review, source light budget, seating/species/capacity and operational/final room acceptance were not run or claimed. No new suite/source-room/furniture work was added.

## Reproduce isolated preparation

Run prepare.py; then run isolated/Game/tools/compile_layout.py with the existing Shapely2.1.2 dependency path, then guards.py and check_transaction.py. Everything writes only within this scratch candidate. prepare.py refreshes the isolated copy from the current receiver and therefore must not be used after unexplained input drift without first reconciling it. Final INPUT_PINS includes extra convention/helper pins added after preparation; keep those when intentionally rebuilding the packet.

Two compiler diagnostics remain preserved: first missing the theater GLB in the isolated copy, then expected-record ring ordering that did not yet reproduce compiler void/priority difference operations. The final isolated run fixes the dependency copy and reproduces those operations; no guards were loosened and no live input was changed.
