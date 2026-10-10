# Group4 central secondary-stair receivers004

Uninstalled additive source delivery, catalogue proposal AST-TRM-G4-018. Place the GLB at world identity (X/Y/Z=0, yaw0); all vertices already use retained ship coordinates in metres and glTF Y-up. The station, rail and prior receivers are separate frozen assets. This module contains52 new editable members,624 triangles and20 receiver datums. It does not replace or duplicate frozen station/guideway exports.

## Exact receiving interfaces
- Twenty0.32×0.40m pads meet current D09 floor topY52.5. Each has a full positive0.128m² source-triangle footprint owned solely by D09_fore_apron or D09_atrium_circulation. Short receiver piers rise to eight landing/return beams and four closed inclined shoes.
- Landing beams receive the lower faces of V2_Central__Emergency_MidLanding, V2_Central__Emergency_UpperLanding, V2_Central__Emergency_TopApproach and V2_Central_StairReturn. Four shoes follow the actual frozen lower planes of V2_Central__Emergency_Profiled_Stringer0/1. Intentional source overlap is0.0125m;32 positive vertical witness checks are recorded.
- New frame bounds are approximately X−12.96..−7.84/Y52.5..55.8625/Z−79.85..−67.8. It remains inside existing stair/landing/return footprints. Lower4m axial circulation has zero new intrusion.
- Central root-owned receiving proposal stays exactly X−7.8..−3.4/Z−68.4..−64.4,17.6m², current floor owner D09_atrium_circulation. No floor is cut. New module has zero recess intrusion.
- Existing commons_lift.gd/AST-CIR-003 cabin, E/RMB controls and central starboard bypass remain root-owned unchanged inputs. This module supplies no moving cabin, door, bridge, new controller or cart.

## Bounded evidence
SOURCE_BATCH_CHECKS.json records finite export geometry, native/export world bounds, zero degenerate triangles, exact floor footprint clipping, positive internal/source joints and local exact-triangle adjacent checks against the frozen central station, current primary core and nearby atrium shapes. No unintended adjacent contacts were found. Both actual source-review images were inspected. NATIVE_PORTABILITY_CHECK.json proves the saved editable native reopens with five packed material images and produces the exact same GLB bytes. RETAINED_SOURCE_PINS.json binds all actual inputs, including the three unchanged prior slices.

## Retention and next gates
This compact batch is frozen for parent-owned Library checkpoint; helper has made no Game, catalogue/global-ledger, Git-ref, backup or upload change. No Godot import/full test or whole-route sampling was run. Load capacity, hull/slab transfer, deflection/vibration, actual-main receiving, normal stair traversal and all-species fit remain open. Existing secondary stairs remain1.44m source candidates. See REMAINING_GROUP4_CHECKLIST.json for every unfinished Group4 lane, including five pit/fill arrangements, fore-midship annex, five boarding lifts, gates/bridges, restraints, core transfers, neighborhood links, guest transit and runtime integration. Whole Group4 is not complete.

## Reproduce from retained sources
Run plan_central_stair.py, then Blender4.3.2 --background --factory-startup --python build_central_stair.py; run validate_central_stair.py with NumPy. Run audit_native.py in Blender for packed-native and identical-export proof. render_source_review.py makes the two bounded source views without saving imported context into the native. finalize_batch.py freezes the stable receipt after review.
