# Secondary engineering essentials: bounded additive candidate

## Scope and disposition

Parent-approved scratch-only source authoring. The parent inspected actual imported workbay/control images and accepted the bounded furnishing direction for runtime evaluation, subject to final corrected labels, source retention and integration review. This is not first-pass completion of the department. Large blank walls/ceilings, blocky retained control plinths, visitor plant visibility, working doors/control systems and wider engineering connections remain unfinished.

No production file, existing catalogue identity, existing model, glass material, collision, fixture marker, floor ownership, renderer or shared light profile was edited. Do not overwrite the original AST-ENG-008 .blend or GLB. This is a derivative under the existing secondary_engineering_section family, not an additional unique design.

## Source and placement

- Editable source: source/AST-ENG-008_essentials.blend
- Portable export: exports/AST-ENG-008_essentials.glb
- Reproducible scratch generator: source/build_essentials.py; source/draw_graphics.py
- World coordinates are Godot XYZ metres. Blender uses (x,-z,y). Instantiate the additive GLB at world origin, zero yaw, unit scale, alongside existing geometry.
- Build scripts deliberately assert the approved scratch output path. They never output into production. Reproduction is through the same scratch staging route or a separately reviewed output-path adjustment.
- All furnishings are static. The reused cabinet door/control source hierarchy does not create working interactions. Console graphics state that panels are static/uncommissioned, with no live telemetry.

## Actual additions

1. Retained AST-STF-007 shaped work/storage cabinet at world origin (31,6,-400.49), yaw pi, unit scale. Its four feet meet the compiler Y6 floor; its rear splashboard meets the workbay south-wall inside face Z-400.18. The staging gap and workbay turning square remain open.
2. The original six-metre maintenance bench and cuboid instrument remain. Separate seated worktop panels avoid the instrument's footprint; a folded zinc front edge and supported pulls give the retained base material/readability hierarchy. A 0.55-scale source-derived control face sits on the existing instrument casing.
3. A supported chamfered toolboard on the south wall has three actual open-jaw spanners, two drivers, supported clips and a rail of hollow sockets. These are modeled silhouettes, not a flat tool image or generic boxes.
4. Three retained-source console derivatives sit against backed extensions of the existing control-display faces. The existing isolation support receives a fourth full-scale face. New static printed engineering diagrams replace the water-return artwork only in these local appended material copies. Original source bytes remain unchanged.
5. Existing spares, quarantine, consumable and bagged-return cabinet blocks receive seated profiled faces, hinges, handles, louvers and purpose-correct labels. The quarantine and consumable labels are distinct in the final atlas.
6. Framed printed workbay/tool/control signs and a visitor interpretation plaque on the opaque visitor south wall. No plaque covers a pane or becomes a light source.

## Source and export verification

Final machine-readable receipts are qa/source_build.json, qa/independent_glb_check.json and qa/source_reload.json. The final delivery inventory pins their exact bytes and both assets.

- 584editable source meshes;582retained/local editable modifiers;69,748evaluated/exported triangles
- 9 export mesh/material groups and9embedded images; no added lights or floor mesh
- Saved source reload: zero bounds difference
- Independent binary-accessor verification: finite vertices/normals/UVs, valid indices, zero degenerate geometry, zero collapsed UV triangles, zero opposed normals
- Source/export triangle counts match; maximum aggregate bounds difference is approximately0.00000258m. This is not a claim of bit-identical vertex arrays
- 13 evaluated-source support/seat plane checks pass
- All 6 protected prisms have zero actual-export triangle AABB intersections: north/south3.6m cart strips, east5.4m street, control/workbay3.6m turning squares,1.5m control operating face
- All pinned retained source/export/material-library inputs remain hash-identical

Earlier checks caught 6 then 4 collapsed UV triangles on the reused cabinet's tiny bevels. The scratch exporter now triangulates evaluated copies before repairing small/collapsed UV faces; the final exported UV gate passes. Original assets were never rewritten. Failed reports and earlier reviewed images remain clearly separated in qa history folders.

## Collision and integration

Export groups carry collision_contract=static_surface or none. Printed sign faces are none; their physical mounting plates remain solid. The current ship.model helper appears to add static trimesh contact to every visible mesh without honoring that metadata. The runtime owner should either preserve the ordinary supported helper's behavior (the tiny faces are outside all protected routes) or locally instantiate this new additive model and honor its per-group contact contract. Do not change the shared collision helper or fill hollow cabinet/tool spaces with whole-body convex collision.

Source clearance is not physical controller acceptance. Re-run the actual new-candidate capsule/loaded-cart route and contact checks. No existing collision may be removed to make a test pass. Existing model pins and all retained architecture remain unchanged.

## Lighting diagnosis and proposed bounded trial

source/runtime_light_trial_proposal.json contains local instance aims/ranges/energy candidates. Keep marker positions, visible housings, shadows, shared profiles, transparency handling and the eight-active-source cap unchanged. No new lights were authored.

The old downward lights placed useful receivers near their cone margins: control faces at 70-74 degrees, machine shoulder/sleeve at 71-72 degrees; the far bench is 7.211 m from a 6 m source. The front west machine nose is 7.228 m from the north inspection source and its own profiled housing blocks that ray at 5.556 m. The opposite cap has the corresponding limitation. Brighter/re-aimed rearward sources cannot directly light those front-facing caps. Do not compensate with unexplained fill, unshadowed light or changed glass.

The workbay aim is (26.5,7,-401.4), centering coverage between bench and side cabinet. The earlier (24,7,-401.4) trial left the cabinet outside the proposed 65-degree cone.

## Actual images and their limits

qa/imported_workbay.png and qa/imported_control.png are the final actual imported-GLB source diagnostic views, with eye Y7.65. They use the retained original AST-ENG-008 source/export as context, not the latest receiving-shoulders runtime derivative or whole main scene.

The final source render has zero world/ambient fill, no neutral area lights, and exactly one enabled real source-marker task fixture per view. All nine physical source markers exist in the diagnostic setup, but eight are disabled for each room image. The source renderer does not reproduce Godot's eight-source selector, source attenuation, energy values or display stack. Blender watt values are explicitly recorded; they are not calibration of Godot energy. The single QA floor matches compiler top Y6 and uses the exact retained staff_floor texture at 0.8 m UV scale; it is never exported.

The early build002 source images enabled all nine fixture lights, and the first floor preview used staff-white material. They are historical diagnostics only. Current render_manifest.json pins the actual final GLB, cameras, active light list and floor policy.

Do not call these in-game views or hardware performance evidence. The runtime owner still needs normal/effects-off images, selection/ray checks and a moving view/cart/light review against the unchanged shared renderer.

## Required next gates

1. Copy only the allowlisted new package files into a new derivative folder under the existing source family. Preserve all pinned source paths. Parent owns registration/commit/independent retention.
2. Verify the retained source checkpoint before live adoption; a scratch candidate is not an independent backup.
3. Install the additive model only, apply the bounded local-instance light trial, refresh Godot import and test actual geometry/contacts/loaded routes.
4. Inspect normal and effects-off workbay/control/visitor/maintenance views and source selection during movement. Do not accept visitor visibility merely because the new furniture passes.
5. Continue room-completeness work separately: blank broad surfaces/control plinth composition and front-cap source-light geometry remain open. No protected interface or new source is implicitly approved by this package.
