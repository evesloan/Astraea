# AST-ENG-003 — wall utility control console

Original, editable component design for the separate Astraea catalogue. Cool practical staff finishes follow the inspected technical/staff reference pixels. The chamfered folded enclosure has a protected recessed control face, static water-recovery mimic, a separate analogue pointer, three tactile caps, a mode grip, removable ventilated hatch and supported rear mounting/cable hardware. No reference-photo pixels are used.

## Files and reproduction

- `source/AST-ENG-003.blend`: editable named source parts, ordinary Principled materials, packed PNGs, bevel modifiers and frame metadata
- `source/build_utility_console.py`: deterministic Blender generator; reads the shared staff role library unchanged
- `AST-ENG-003.glb`: evaluated portable mesh with embedded images, grouped static role geometry, retained button/selector/hatch hierarchy and explicit source/exchange numeric fields
- `textures/draw_console_graphics.py`, `console_graphics.png` and `console_graphics.json`: original local print source, bitmap and atlas/provenance record
- `AST-ENG-003.manifest.json`: dimension, cost, material, mounting, control and service records
- `collision_proposals.json` and `source/write_collision_proposals.py`: reproducible source/native GLB compound shapes that preserve the lower service bay and vent, pending engine adoption
- `qa/validate_glb.py`: binary accessor and resolved-node checks, including wrong-axis controls
- `qa/render_imported.py`: source reload, camera preflight and imported-GLB component evidence

Run the texture Python script with Pillow, then the Blender generator. Run the binary validator, then the render script with `-- --preflight-only`. The normal render invocation uses EEVEE_NEXT with no denoiser. It is a component QA arrangement, not a room or playable scene.

## Installation and frames

The source datum is the console centre on the wall contact plane, `(0, 0, 0)`, with source front `−Y` and up `+Z`. Standard GLB is Y-up with front `+Z`: `(x,y,z) → (x,z,−y)`. The actual exported root, contact markers and control nodes include both numeric frames; receiving code must resolve the native GLB hierarchy and must not transform native positions twice.

The case is 0.82 m wide, 0.68 m high and projects 0.212 m from the wall at its front rim. Maximum control projection is 0.248 m. The 0.7655 m overall height includes the short cable tails. A proposed centre mounting height of 1.45 m puts the three buttons at 1.317 m and the selector grip at 1.351 m above deck. A 1.65 m standing eye view is rendered. These are human-scale use proposals, not all-species reach or accessibility certification. Keep the approach and hatch withdrawal space open, then verify final room circulation and actor rig reach separately.

Four rear pads touch source `Y=0` exactly; their source centres are `X=±0.305, Z=±0.221`. Closed zinc standoffs join the rear case cleats. Short cable tails enter supported glands at the lower case; the tie bridge has closed straps back to the rear case. Final substrate fasteners, cable routing and load rating are unresolved.

## Functional groups and limits

`CTRL_button_START`, `CTRL_button_HOLD` and `CTRL_button_ISOLATE` preserve their cap/pivot identities. Their press direction is source `+Y`, native GLB `−Z`; a 3 mm travel is a proposal only. Their sockets are annular, with space around the cap. `CTRL_mode_selector` preserves a source `−Y` / GLB `+Z` rotation axis and retains the grip/index as children. Detent values are proposed geometric positions, not implemented device logic.

`SERVICE_removable_hatch` is a frame around an actual vent aperture. Its printed label, angled fins and four fastener assemblies follow it as exported child material groups. There is an open service bay behind the hatch; the fixed recessed upper face does not continue across it. A dark fixed rear vent baffle is intentional. Front withdrawal is source `−Y` / GLB `+Z`; no animation is implemented.

The schematic, labels and gauge are static original artwork. They carry no live readings, simulated fluid flow, electrical state, operating limits or safety claim. There is no emission/glow pipeline. The retained staff material roles and PNGs are unchanged.

Collision proposals split the case perimeter, rear closure and upper face, preserving the lower service bay. Four frame shapes follow the hatch, leaving its vent open. Separate small shapes follow the three buttons and selector; fine sockets and vent fins are deliberately omitted. A validation script checks intended open-space probes, while the superseded whole-case hull fails those same probes. Rear mounts remain separate. Engine collisions, interaction detection, room fit, shader appearance and target-PC performance remain pending.
