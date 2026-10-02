# Hospitality service stations

Two original script-assisted editable Blender designs for Batch07. These are independent catalogue components, not recovered game geometry or a reconstructed room. The hospitality blueprint supplies dining/support purpose; the dining-edge photo guides rounded continuous joinery and broad timber rhythm; the premium reference guides ivory, walnut, stone and restrained champagne hierarchy. Reference images are not runtime textures, geometry, or ship-count authority.

- AST-HSP-003: twin-spout countertop beverage station, 0.650×0.452×0.577 m. Rounded side cheeks carry the crown; an ivory manifold joins the genuine hollow nozzles. A removable open catch tray supports two annular cup rests. Distinct physical buttons and original local STILL/SPARK labels form a small control hierarchy. Rear panel and exposed washable areas use the existing neutral staff zinc role
- AST-HSP-004: guest dirty-dish return, 1.100×0.792×1.2255 m. A shaped walnut front, ivory shoulders and stone entry ledge surround a true receiving opening. The zinc receiving caddy rests on two rails and withdraws toward the staff rear; the open lower compartment is reachable from that side

## Coordinates and use

Metres, Blender source Z-up, guest front−Y, staff rear+Y. GLB Y-up mapping is (x,y,z)→(x,z,−y). ASSET_DATUM and contact/motion nodes preserve both-frame metadata inside the actual GLB. The actual imported hierarchy is authoritative. Contact markers that belong to a removable tray/caddy are children of its actual motion root.

Beverage source support plane is Z0. Four pads bear at exactly Z0. Proposed placement on AST-HSP-001 is source translation (0.70,0,0.90), inside the counter's published usable top. Full-height guest approach stops at Y−0.41; staff approach begins at Y+0.44 so neither intersects the counter beneath its worktop. Separately labelled reaches are above the worktop.

Each cup pose is at (X±0.14,Y−0.095,Z0.079), inside an intentionally empty centre. It is not a surface contact. The actual annular base rests have inner/outer radii0.052/0.058 m and eight separate sampled contact markers at radius0.055 m. Outlet mouths are at Z0.374, above a reserved0.281 m clear cup envelope. DRIP_TRAY moves−Y0.32 m as a proposal; its catch-floor underside bears on the station base atZ0.052. The spout upper roots overlap the supporting manifold by5 mm, and the manifold overlaps the crown by5 mm.

Dirty-return stone drop ledge is Z0.900. The actual receiving floor is Z0.891; its clear inner footprint is approximately0.876×0.576 m, accepting the common0.45×0.32 m tray envelope. The straight receiving opening is unobstructed atZ1.04. A raised tray insertion path atZ1.01–1.07 clears the low front lip, then lowers onto the floor. RECEIVING_CADDY has a proposed+Y0.80 m translation, equivalent to GLB−Z0.80 m. Its staff grip centreline is (0,0.377,0.922). The extraction pose is a hand-supported removal proposal, not proof of supported full-extension loaded operation. The receiving surface and staff grip follow the caddy root; rail-bearing markers remain on the cabinet.

## Reproduce and evidence

Run Blender4.3.2 with source/build_hospitality_stations.py using --background --python-exit-code1. Source retains named semantic meshes and editable radius/weighted-normal modifiers. Evaluated exports normalize UV layers, remove degeneracies and consolidate by material role inside functional groups. Original station graphics are created by textures/draw_graphics.py. Shared material/helper dependencies are unchanged and hash-listed in dependency_manifest.json.

qa/source_reload_checks.json reloads both saved .blend files, tests true support Z0, verifies contact proximity, real hollow mouths and pass-through service cavities, and checks packed used textures. qa/glb_validation.json parses the actual GLB binary without Blender: finite vertices, hierarchy transforms, noncollapsed UVs, normals/winding, exact embedded texture pixels and measured cost. qa/native_motion_and_clearance_checks.json uses actual moving-group GLB bounds against per-body proposed colliders, plus correct-frame, wrong-axis, wrong-direction and artificial-blocker controls. Receiving space and extraction route are distinct. No whole-component collision wraps the openings.

Seven neutral actual-GLB views cover three-quarter, ordinary1.65 m standing height, cup bay, receiving opening and staff extraction. The beverage host block is a0.90 m inspection aid; the dirty-return extraction detail translates its actual caddy root0.40 m for inspection. Floors, lights and host aids are excluded from exports. All views use standards/qa_frame.py first and are bound to exact GLB hashes.

The sources contain no working food, fluid, power or device simulation. Collision, motion, approach, room/host fit, species usability and runtime adoption remain proposals. No food safety, structural, accessibility or target-PC performance certification is implied by geometry or image checks. Only two original designs are counted; their subassemblies, labels, contact nodes, derivatives and QA stages are not additional designs.
