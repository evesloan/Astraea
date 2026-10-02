# Astraea guest-use expansion

Three original, script-assisted components in the continuing warm residential family. This directory is independent catalogue work; the missing original ship and its game were not changed or recreated.

- AST-GST-001: bent-blade reading floor lamp, 0.348 × 0.452 × 1.489 m. Twin narrow floor runners leave a real open front. A tapered walnut blade and joined metal neck support the hollow shield. The readable rocker, rear power-entry datum and downward diffuser retaining clips are static proposed interfaces.
- AST-GST-002: shielded wall reading sconce, 0.258 × 0.316 × 0.345 m. Its rear mounting plane is source Y0; the source origin is the wall-mount centre, not the floor. Two fixing locations, a braced arm, shield, separate rocker and concealed rear power-entry datum are explicit. The QA installation centre is 1.36 m above the inspection floor only.
- AST-GST-003: split-level luggage/personal console, 1.182 × 0.486 × 0.861 m. Four real padded slats bear into two rails, between substantial tapered cheeks. The luggage support plane is Z0.335 m, the personal tray Z0.8405 m and the open shelf Z0.499 m. The declared empty luggage volume is X−0.49…+0.14, Y−0.23…+0.17, Z0.35…0.92 m; these are proposed use dimensions, not a luggage-size or load certification. No drawer or other moving part was needed.

## Source authority and language

The actual supplied intimate, dense and premium reference pixels were inspected, along with AST-FUR-002 and AST-FUR-003 renders. Warm walnut supports, restrained ivory surfaces, champagne fittings, deliberate broad silhouettes and useful open space continue that family. Reference room counts, lighting behavior and species proportions were not copied or inferred.

## Rebuild

From the catalogue root:

`blender --background --threads 2 --python-exit-code 1 --python assets/guest_use/source/build_guest_use.py`

The generator creates source, exports and qa parents itself. It reads only standards/materials.py, materials/material_manifest.json and the eight original material PNGs in that manifest. It does not read any excluded QA, render, existing source or existing export file. Generated assets are original semantic meshes with editable easing modifiers, UV data and distinct ordinary Principled materials. They are not literal manual GUI modelling and no third-party geometry was used.

Source .blend files retain all named parts and packed textures. Evaluated static export copies are consolidated by material role after active-UV normalization. Native marker nodes retain physical contacts, wall mounts, switches, service-fastener/power entry locations, reading direction targets and the distinction between physical support and nonphysical receiver centres. There is no active light, interaction, animation or collision object.

## Frames and interfaces

Metres; source +X right, +Z up, −Y front. The source-to-GLB mapping is (x,y,z) → (x,z,−y). marker_api.json and each asset manifest state both frames. The independent native-node check resolves every GLB transform before comparing its marker positions; it does not assume each node has an identical rotation. Source coordinates must not be applied again to native GLB vertices.

collision_proposals.json keeps a few separate upright, runner, arm, hood, rail/slat and surface envelopes. Continuous void checks establish that these proposals preserve the declared front base split, space under the sconce, luggage opening, lower apron and shelf mouth. These remain proposals for future engine adoption, not solved physics.

## Evidence and limits

qa/glb_validation.json parses actual file triangles, transforms, finite positions/UVs, normals/winding and embedded pixels without Blender. qa/source_reload_checks.json reloads every source and checks physical marker surfaces, joined solids, packed materials and 49 cross-front rays per real void. qa/native_interfaces_and_voids.json independently binds native marker nodes, tests all proposed collider/void pairs, and checks the corrected chair/lamp inspection placement using the existing actual chair GLB. The chair front approach volume is an inspection proposal only.

qa/render_evidence.json records exact imported GLB/source hashes, cameras, resolutions, placement and framing for three ordinary 640×360 views, three higher-resolution details, and one compact chair/lamp context. Lighting, floor and wall are neutral Blender component inspection aids only. qa/review_media_manifest.json binds the final labelled image files.

No original-ship integration, engine compatibility, CRT appearance, target-PC performance, electrical/photometric function, physical stability, load rating, accessibility or species-fit claim is made. Lamp service clips express a fixed-geometry service proposal; no detachable hierarchy, motion or electrical maintenance procedure is implemented.
