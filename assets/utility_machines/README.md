# Astraea engineering machine pair

Original script-assisted asset-library work for batch 06, 2 October 2026. These are new editable catalogue designs, not recovered game geometry, room reconstruction or functioning process machinery. The inspected technical blueprint supplies engineering/water-recycling purpose; obsolete deck numbers do not change ship canon. Both staff corridor photographs guide practical finishes and organized service access rather than narrow circulation dimensions.

## Contents and use

- AST-ENG-001: compact transfer pump on a connected folded skid, integral cast feet, guarded shaft coupling, finned drive housing and hollow lateral nozzles. Its front service collar opens into the chamber; the bolted cover remains a separate export group, proposed to withdraw toward -Y. The coupling guard is a separate +Z group
- AST-ENG-002: hollow vertical filter vessel on three splayed closed legs, actual opposed nozzle holes, a gasketed removable domed lid, six captive clamps and two handles. The lid remains a separate +Z export group. No cartridge or fluid filtration behavior is claimed

The ordinary front is source -Y. Both origins are on the floor at (0, 0, 0), metres, Blender Z-up. Standard GLB exchange is Y-up using (x, y, z) → (x, z, -y). Every connection/contact/service record names both frames. Grip markers are explicitly centreline proposals; they are not physical surface contacts.

## Compatible interface

Both machines reuse the exact standards/utility_ports.py geometry and profile: bore 0.16 m, pipe outside diameter 0.20 m, flange 0.32 m, thickness 0.035 m, six 0.018 m holes on a 0.26 m bolt circle. Captive hardware stays behind the bare mating face. Pump faces are at source (±0.85, 0, 0.60) m; filter faces at (±0.64, 0, 0.60) m. Named PORT_ nodes preserve both-frame coordinates and normals in actual GLBs. Necks and bores are hollow; there are no false cap disks. These dimensions are artistic proposals with no operating rating.

## Maintenance reservations

Pump: front cover work prism X±0.38, Y-1.20 to-0.33, Z0.22 to1.20m; rear drive work prism Y1.12 to1.72m; coupling-guard lift to Z1.12m. Filter: front approach X±0.48, Y-1.30 to-0.47, Z0 to1.90m, plus vertical lid/cartridge-withdrawal reservation X/Y±0.35, Z1.57 to2.36m. These are open component-level design reservations, not certified actor reach, installation or safety clearances. Engine integration must preserve them or re-evaluate them.

## Reproduce

Run Blender 4.3.2 in background with source/build_utility_machines.py. It imports the unchanged shared staff material library and shared utility-port helper, creates named editable source meshes/modifiers, packs used PNGs, saves each .blend, then normalizes evaluated UVs and consolidates ordinary static export geometry by material role. Necessary service-cover/guard/lid groups remain separate. It also invokes source/build_collision_proposals.py. Collision proposals use separate coarse annular sectors and feet; they preserve pipe bores, inter-leg openings and maintenance volumes. They are not enabled physics and require engine-side simplification/performance review.

## Evidence

qa/source_reload_checks.json reloads saved .blend files, checks true Z0 floor pads, verifies support-cap vertices lie within the finished machinery shell, and casts multiple offset rays through both X ports. qa/glb_validation.json independently parses actual GLB accessors, triangles, UVs, normals, hierarchy transforms and embedded image pixels. qa/connection_node_checks.json compares actual node positions with converted source records and rejects wrong-axis controls. qa/camera_preflight.json bounds-checks the imported components before rendering. Actual imported-GLB standing views are 640×360; targeted and full details are 1280×960. All lighting/floors are neutral QA aids excluded from asset exports.

Runtime triangle/mesh/primitive/file costs are reported in qa/runtime_cost.json. Figures describe exported files only, not target-PC frame rate. Normal/winding and UV checks do not certify fluid, pressure, structural load, electricity or maintenance safety. Actual room fit, motion/controls, actor usability and original-engine adoption remain pending.
