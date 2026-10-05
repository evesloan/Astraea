# AST-CMD-004 — D18 connected fan bridge shell

Architectural source kit, not an operating bridge or final art acceptance. Editable Blender and optimized bounded GLB use the existing world-coordinate convention: Blender=(GodotX,-GodotZ,GodotY). The model origin remains world zero.

## Fitted scope
- One connected fan enclosure on the originalY106.5 floor; no floor, furniture, static door leaves, new lights or controllers
- Real collidable principal starboard glazing, fore-right sky glazing and fore-left gallery-directed glazing; chiefly opaque port/aft enclosure uses the retained full-height003guards as its lower wall
- Exact mitred perimeter, fitted nose/shoulder hanger collars, shaped shallow perimeter/entry soffits, six unchanged fixture-housing reliefs, supported roof carriers and skin atY114.32
- Primary service-door placement(0,106.5,-118.3),yaw0; fore placement(0,106.5,-171.7),yawPI. Reuse actual AST-STF-008 with its existing controller. Apertures2.75×2.815m,5mm fixed-frame overlap;1638 actual leaf-mesh sweep samples pass
- Aft vestibule joins the unchanged core cover atY109.73…109.85 andZ-113 with20mm plan overlap. Side infill atZ-115 is sealed and demountable; future staff crosslink is unbuilt
- Fore approach spans only the old spine toZ-173. Public bypass and full fore street remain independent of both doors

## Paired003 revision
Only32 bounded mesh pieces belonging to8 approved guard-back/cap assemblies changed: starboard fore/diagonal/longitudinal and port fore. Backs endY107.10; caps spanY107.08…107.12. Every other3362 mesh and all33 marker objects match the old editable Blender source exactly. All24 bypass panes,20 fixtures, bearing/transfer/hanger geometry, toes, shoes and terminal returns are retained. The new glazing sill and opaque cheeks close the interfaces. No old protection tests were weakened; historical stage1 acceptance remains historical and the paired stage2 proof is explicit.

## Evidence
- qa/source_export_validation.json and exact_roundtrip.json: exact oriented triangles, float32 coordinates, UVs/material identities; manifold positive-volume parts; bounded runtime batches
- qa/material_fidelity.json: actual material parameters and packed texture bytes match both exports
- qa/003_actual_mesh_preservation.json: reopen old/new003Blender sources and compare actual full mesh/marker data
- qa/preservation_comparison.json: exact all-parts comparison, all unrelated161catalogue records and7494protected unrelated files unchanged
- qa/actual_door_sweep.json: actual unchanged shared-door leaf sweeps and fitted fixed-frame overlap
- qa/retained_light_cones.json: all20 full downward76degree receiver cones clear of004geometry by conservativeAABB exclusion; no new lights
- qa/source_preview_receipt.json and source_diagnostic_review.json:11matching source views, openly dark/noisy in places; actual Godot framing/lighting acceptance remains pending

## Parent integration gate
Do not treat this as installed acceptance. Import the paired003and004exports, preserve original floor owners/geometry, place the existing shared doors and update only the actual controlled centreline subregion. Run source-hash checks, positive contacts, perimeter collision, old24pane/20light protections, core/D17 clearance, both threshold interactions/sweeps, closed-door public walking/loaded-cart routes in both directions, normal/effects-off views and final full regression. No sky rotation or ambient compensation is part of this kit.

Geometric contacts do not certify structural adequacy or ship-wide pressure/life-support integrity. Species fit, command functionality, final materials/light balance and broader ship completion remain open.
