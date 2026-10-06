# Gate-sweep v2: bounded frozen source correction

This is a new versioned derivative of the user-approved workbay section. The copied prior candidate remains immutable and retained. No Game, floor owner, existing controller, source material, aperture, gate identity/travel or120calibration-control identity was changed here.

## Canonical files

- source/AST-ENG-008_workbay_section_gate_v2.blend
- exports/AST-ENG-008_workbay_section_gate_v2.glb
- source/runtime_contract.final_source.json
- qa/section_independent_export_check.json
- qa/final_source_reopen.json and qa/reopened_final_source_triangles.npz
- qa/actual_sweep_and_bottle_check.json

SourceSHA256:0e4d89ac3a76b4f15c67ef41b5179b0a0780dbc1199eea31562b90b92737a6c3
GLBSHA256:6896d757c5a248d0fcf37a2ae7a197de24566a3fec3f80ce80cdc12186e34368

The final actual contract names153mesh groups,47,930triangles, the same120calibration controls, the same gate leaf and two real gate targets. Source/export geometry/material triangles match with no geometry/UV/normal failures; saved-source reopen has zero bounds error and unchanged bytes.

## Why the correction was required

Closed-state rays and route checks did not exercise the entire gate sweep. Independent integration review found22fixed-triangle penetrations: the outside control housing crossed the moving glass travel plane, and two handrail upper tips crossed the actual closed leaf frame. A separate actual-size lying-bottle witness could enter a hidden cavity beneath the0.12m-thick inclined contact, inside visibly solid stair blocks. The exact previous failure witnesses are retained in qa/prior_failure_witnesses.

## Exact changes

1. Outside housing, button and its existing source target move0.11m west. Their names and gate link stay unchanged; the target is now(21.654,7.10,−405.23), from the same supported approach(20.85,6,−405.23) with the unchanged2.5m ray limit. A new real upper-floor foot and stem support the housing. Nothing mounts through the moving leaf plane.
2. Each handrail upper end moves along its existing slope from(21.9,6.95,Z) to(21.96,6.92,Z), while lower ends/radii stay unchanged. The shortened ends seat within the fixed jambs and have approximately52.9mm geometric clearance to the leaf.
3. CONTACT_CellStairFlight becomes a true six-vertex/eight-triangle solid triangular prism. The exact inclined upper quad and0.9×1.2m footprint stay unchanged. Its bottom bears on the lower floor atY5.55. The compiler slab remains sole physical underside owner atY5.31; there is no second slab owner and no collider extending beneath the reserved limit. The old0.12m-thickness contract is removed.

The liked layout, glazing, gate opening/closed bounds,1.22m travel,1.2m aperture, target identities, floor cut and lower-floor owner remain unchanged. The upper west passage has approximately1.45mclear at the small pedestal foot; the actual doorway/landing remains1.2mclear. Cart remains upper; this is a staff/portable-tool approach.

## Proof scope

The exact union of the axis-aligned closed BoxShape translated along its authoredZ travel covers every opening fraction. Actual exported fixed triangles have zero interior intersections with that continuous sweep at0.1mm boundary tolerance;101supplemental poses also pass. Intentional tangent guide bearing is unchanged, not misreported as a forbidden penetration.

The actual cleaning-bottle shape is a0.057m-radius,0.25m-height cylinder. For the lying-axisZ witness, all32rim points and centre are blocked from both stair sides; the contact underside isY5.55. Six unique wedge vertices and eight nondegenerate triangles are verified. This is exact geometry evidence, not a substitute for the parent's released-bottle physics test.

Both real gate target rays, all120calibration target rays and all six protected prisms pass. The old candidate's source/GLB hashes remain unchanged. Current Game traversal, full gate open/close/obstruction, loose-prop side contact and held-object behavior still require the planned runtime trial.

## Versioning and reproduction

Proposed new-only catalogue folder: assets/secondary_engineering_section/workbay_section_gate_v2_candidate_20261006.

Use the versioned GLB filename in the runtime importer; do not replace the previously copied candidate. The builder reads the pinned previous source, applies only the listed changes, saves this separate source and exports through the verified exact-loop exporter. Both saved sources and all previous witnesses remain retained. No extra visual render was requested or produced for this narrow correction; prior approved images establish the unchanged spatial direction, not current runtime acceptance.

## Independent review and runtime-margin nuance

Independent peer review passes27checks:47,930material triangles match the actual reopened source, exactly five existing parts changed and two supports added, all120control geometry/material/UV data remain unchanged, the continuous actual-leaf sweep and201poses are clear,128bottle side rays are blocked, and135vertical probes show solid contact toY5.55. See qa/independent_review/CELL_CORRECTED_SOURCE_REOPEN_REVIEW.json.

Nominal decimal leaf bounds versus float32 guide surfaces can produce submicron tangent witnesses at the intentional guide support; actual exported bounds resolve those. The Game trial must handle its1mmshape margin using exact named guide/contact evidence. Do not exempt the entire merged static-zinc group or loosen the whole sweep tolerance to hide unrelated collisions.
