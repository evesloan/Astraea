# Astraea catalogue continuation — batch 01

New independent asset production, 2 October 2026. This is not restoration of the lost game. Original game path is untouched. Godot integration, room fit, physics, actor contact, motion and target-PC performance remain pending.

## Scope
One coherent view-facing day-use family: sculpted two-person window bench, companion reading chair, small useful table; compatible deep window-reveal jamb, header and sill pieces with explicit ends/corners. No new room allocation, glass shader, controller or playable world. Component inspection arrangements are labelled asset QA only.

## Source authority
The supplied warm residential and generous premium references are shape/material/use guidance. View scale and suite counts are not copied. User allows direct sleeping-to-court views; existing optional blind and bath privacy policy remain. Low-poly early-2000s tactile material craft must work before CRT; no universal yellow tint, luminous outlines or untextured boxes.

## Authoring and exchange
Blender 4.3.2. Metres, Z up, X across width, front faces -Y; GLB export performs standard Y-up conversion. Floor/support-origin asset pivot at (0,0,0), except joinable architecture pieces use stated seam datums. Apply scale before export. Editable named semantic objects, retained non-destructive bevel/subdivision where useful, ordinary Principled materials. A reproducible Python authoring script is allowed and disclosed as script-assisted intentional design, not literal manual GUI modelling. Export evaluated meshes but save editable source.

Visual meshes use semantic material roles: ivory_enamel, warm_walnut, teal_weave, clay_weave, oatmeal_weave, champagne_metal, dark_rubber, warm_stone. Common shared source materials are maintained in standards/materials.py, expose materials() -> dict. Do not bake multiple semantic roles into a single opaque atlas surface. Physical glass is outside this batch; mark optional pane interface only.

Textures: original tileable 256px color with metric UV scale, restrained grain/weave, export mip-compatible ordinary textures, no renderer-specific procedural-only final material. Wood grain aligns with each part; fabrics retain readable broad color and coarser woven variation. Geometry makes upholstered crown/taper, seams, shell transitions and load-bearing supports visible at 640x360. Use restrained intentional silhouette geometry, no default-box body with decorative bevel-only pass.

## Handoff
Each unique authored asset gets stable catalogue ID, .blend, GLB, manifest (dimensions, min/max, material roles, triangle counts, pivot, joins, intended use, contact/approach annotations, export settings, source hashes, provenance). LODs/export copies are not unique artistic assets. Supply simplified collision proposal data separately, never an automatic whole-chair convex shape that fills approach space. Floor contact must reach exactly Z0; seat contact is measured. Any interaction positions are proposals pending original engine/rig.

## Gates
Reload every .blend; independently parse GLB and verify semantic material/texture references, transforms, unit dimensions, finite geometry, normal/winding and visible joins. Render neutral three-quarter plus ordinary standing/seated context at640x360 and high-resolution detail; this is Blender component evidence, not Godot game evidence or CRT output. Verify floor/support contact, named piece relationships and seam gap/overlap. Independent review against actual three references before broadening. Complete batch must be frozen, hashed and durably backed up to durable storage before another batch.

## Export lesson verified in this batch

Before joining evaluated export copies, normalize their active UV-layer name and discard unused extra layers only after preserving the correct data. Source renders alone are insufficient: an actual GLB can lose UVs during consolidation while the editable source still looks correct. Check nonzero UV area on the exported triangle data and render the imported GLB. Preserve editable source parts, consolidate static visual exports by semantic material role, and retain proposed interactions/contact records outside automatic collisions.

Embedded texture copies make assets portable. Future Godot adoption must map these explicit shared material roles to shared runtime resources where appropriate, rather than treating every embedded copy as a unique per-instance material. That adoption remains untested while the original game is unavailable.
