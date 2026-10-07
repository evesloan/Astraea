# Actual r007 bathroom export verification

Status: PASS for the three named r007 source units. This replaces analytic-only evidence for these units, not for any other prototype or runtime installation.

Input revision: /workspace/scratch/375c2e438292/residential-batch-neighborhood-20261006/outputs/court_domestic_r007

Actual exported shell triangles were tested with actual retained/candidate component GLBs placed according to each SOURCE_RECEIPT.json. No analytic corner closure or head-stop geometry was added to the tests. Every receipt-listed shell/source assembly hash matched before verification and remained unchanged afterward. No Blender/Godot job, shared edit, import, commit or upload was performed.

## Verified units

- AST-UNIT-D14-abfdd528ff9b68bc (B_twin_retreat): shell SHA-256 587c96006c666e18fe251648b904e2a18e9f4f80854b3a007575724fd99ef540
  - Both added solids contain 12 actual exported triangles each; all six planar faces have the expected area. Corner material is ivory_enamel; head-stop material is warm_walnut.
  - Maximum exported corner-coordinate error: 1.4249375147112182e-07 m. DATUM_bath_door agrees with the separate door placement.
  - 29,762 privacy/enclosure rays: zero unblocked. 903 bathroom contact tests and 903 suite-entry contact tests: zero fixed-geometry intersections.
- AST-UNIT-D14-c1157ff6ab3561ec (B_twin_retreat): shell SHA-256 587c96006c666e18fe251648b904e2a18e9f4f80854b3a007575724fd99ef540
  - Both added solids contain 12 actual exported triangles each; all six planar faces have the expected area. Corner material is ivory_enamel; head-stop material is warm_walnut.
  - Maximum exported corner-coordinate error: 1.4249375147112182e-07 m. DATUM_bath_door agrees with the separate door placement.
  - 29,762 privacy/enclosure rays: zero unblocked. 903 bathroom contact tests and 903 suite-entry contact tests: zero fixed-geometry intersections.
- AST-UNIT-D14-fbfbe316e3a58c68 (D_garden_salon): shell SHA-256 f971a4588a0f1eb12fea7ec1d832b1a1366ee46ceed563ba76b158dfa0c83744
  - Both added solids contain 12 actual exported triangles each; all six planar faces have the expected area. Corner material is ivory_enamel; head-stop material is warm_walnut.
  - Maximum exported corner-coordinate error: 1.4249375147112182e-07 m. DATUM_bath_door agrees with the separate door placement.
  - 29,762 privacy/enclosure rays: zero unblocked. 903 bathroom contact tests and 903 suite-entry contact tests: zero fixed-geometry intersections.

## Scope and result

- 89,286 total rays cover targeted prior defects, the surrounding enclosure, dense 5 mm head/chamfer samples, and dry-room/street eyes toward occupied bathroom volume. Only actual shell and opaque bathroom-door geometry count as privacy; fixtures cannot hide a failure.
- 5,418 contact tests cover 301 full bathroom-angle samples and 301 entry-slide positions per unit, using the retained controller contact boxes enlarged by 2 mm in each direction. Fixed geometry includes the real shell, door frames, retained fixtures/furnishings, and the new kitchenette export.
- Separate AST-DOR-001 is still byte-identical to CurrentGame. The door is not baked into shell meshes, and its existing HINGE_LEFT hierarchy is retained.
- Source fixture and door placements remain correct in both B_twin_retreat and the replanned D_garden_salon.
- Existing master chapters 6/21/32 and intimate/premium/source-view inspection evidence remains in REFERENCE_INSPECTION.md. Every exact path/hash in REFERENCE_INSPECTION_SHA256.json was rechecked unchanged; the earlier pixel observations and body-index locators remain valid.

## Remaining gates

This is finite offline geometry validation, not in-engine operation or final visual acceptance. The later isolated runtime gate still needs both-side RMB/E targeting, real open/close/collision states, occupied-swing inhibition/recovery including the grazing-handle edge outside the current adapter query, player/cart approach, and normal eye-level captures with the bathroom ceiling present. The 25 mm floor undercut remains intentional. No lock, save, water or all-species fit is claimed.

The r007 SOURCE_RECEIPT files contain correct door placements and file hashes but do not include the optional bathroom_enclosure_contract metadata proposed in the narrow integration patch. This does not invalidate the directly verified geometry; carry this verification receipt into the next adoption manifest so the correction and runtime-unverified status remain explicit.

Machine-readable evidence: R007_ACTUAL_EXPORT_VERIFICATION.json. Reproduction: python verify_r007_exports.py. No engine is invoked.
