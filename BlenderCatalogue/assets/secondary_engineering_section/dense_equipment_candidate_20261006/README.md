# Status: equipment source retained; flat-room direction superseded

The latest user direction requires real sectional architecture: recessed machinery, a secondary glazed SunCorp-only boundary, an overlooking service walkway and genuine maintenance access. No further flat-room build or render is authorized. Current source is reusable equipment only; it is not a room-completion or adoption candidate. No Game file changed.

# Dense secondary engineering: CONTROL + WORKBAY

AST-ENG-008 `dense_bays` is a new additive source derivative of `secondary_engineering_section`. It is the 120-control CONTROL + WORKBAY tranche of the planned six-bay/256-control pass, not a replacement of the original section or a completed department.

The editable source preserves 1,427 named modeled components and 410 semantic control/approach/cable/contact/fixture markers. The GLB carries 120 separate pivoted actuator nodes, 16 spatial/material static groups, 48,646 triangles and nine ordinary embedded material/texture roles. Static geometry is batched; moving actuators are intentionally kept separate.

No Game or catalogue file was changed. Original console, bench, toolboard, cabinet, glass, floor, ceiling, cap, fixture and controller sources remain in their retained owners. The additive GLB is authored in world Godot XYZ metres and is intended for identity placement beside the original section and essentials GLBs after review.

Source marker/control metadata and harmless-effect names are proposals. There is no runtime interaction, audio, cake spawning, save behavior or new runtime light. Physical supported task fixtures have explicit proposal markers and source diagnostic trial settings only.

Main source: `source/AST-ENG-008_dense_bays.blend`
Main export: `exports/AST-ENG-008_dense_bays.glb`
Plan/builder: `source/generate_dense_plan.py`, `source/build_dense_bays.py`
Control/contact/port handoff: `source/control_manifest.json`
Effect/light boundaries: `source/effect_and_light_proposals.json`

Final source/export/UV/reopen/ray/route receipts and actual source views are in `qa/`. Earlier failed builds remain under clearly labeled retained attempt folders. Reproduction must use the parent-allocated serial Blender route; scripts assert the bounded scratch output path and preserve previous outputs rather than overwrite them.
