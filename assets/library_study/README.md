# Astraea library study edges — two new assets

New independent catalogue geometry, 2 October 2026. These are two original editable Blender assets, not restoration of the unavailable original game. All work in this family is confined to `assets/library_study`. Batch01 and shared materials02 remain unchanged.

## Assets and use

- **AST-LIB-STUDY-01 — Open Shared Study Table:** 2.240 × 1.150 × 0.754m overall; the reading surface is 0.750m high and the optional receiver plate reaches 0.754m. Four proposed reading positions occupy two long edges. Each proposed writing rectangle is 0.70 × 0.38m. The table has shaped ivory end forks, timber bearing joins and a flush stone surface. There is no low foot stretcher. Nineteen editable semantic parts; 2,268 evaluated/export triangles.
- **AST-LIB-STUDY-02 — Sheltered Single Study Edge:** 1.7185 × 1.0220 × 1.39675m overall; reading surface 0.752m high. The inward-facing bookcase gives two useful shelves and a porous, rising privacy wing on the left. The writing edge opens forward and retains a central outlook. Two housed tenons connect its timber edge to the wing posts. Twenty-seven editable semantic parts; 2,316 evaluated/export triangles.

Both have floor/support origins `(0,0,0)`, metres, Blender Z up, X width and front −Y. GLB export converts to standard Y up. The paired GLB has one consolidated visual mesh with five material-role primitives. All textures are embedded, unchanged materials02 base-color images. The `.blend` sources retain named parts, UVs, edge-easing and weighted-normal modifiers; source files contain no QA studio, lights or cameras. The generator is script-assisted intentional extrusion and join authoring.

## Placement data and exact limitations

`integration_api.json` and the individual manifests define the proposed chair transforms, dimensions, stock mounts and fixture plates. The batch01 AST-FUR-002 chair is an external scale/QA dependency, never copied into a source asset or recounted as a new asset. Its seat crown is 0.475m. South shared chairs rotate 180° about Z and face +Y; north shared chairs rotate 0° and face −Y. The single candidate chair also rotates 180° and faces +Y.

The shared table's measured conservative clear central volume is X `[-0.960,0.960]`, Y `[-0.515,0.515]`, Z `[0,0.665]`. Each candidate also has its own knee box and outside-table approach rectangle. The single edge's conservative knee/foot volume is X `[-0.495,0.655]`, Y `[-0.415,0.299]`, Z `[0,0.686]`. Its forward entry rectangle and central outlook are separate annotations. Independent review tightened an early ±0.975m shared clearance claim to account for actual feet/braces. The declared final volumes have zero intersections with evaluated source part AABBs.

Single wing stock bases are `(-0.711,0.075,0.420)` and `(-0.711,0.075,0.830)`, rotation Z 90°, so stock fronts point +X. Each uses the nominal 0.68 × 0.24 × 0.29m stock envelope. Clear heights are 0.375m and a conservative 0.342m. The optional shared folio mount is `(0,0.20,0.750)` and uses AST-LIB-007's actual 0.370 × 0.256 × 0.0801m envelope; the writing rectangles stop at |X| 0.20, leaving 0.015m from its measured X bounds. No book asset is included in either study GLB. A future fixture is represented only by a receiver plate and orientation data, without a light, wiring or runtime system.

Each collision proposal is a numeric compound of independent per-part boxes, with decorative receivers/inlays omitted. Conservative box bounds need refinement around rounded and swept outlines during engine adoption. No collision hull fills the shared central void or the single entry. These are geometry/data proposals, not engine-tested physics. Candidate chair, stock and approach data do not claim original species/rig acceptance, reach, seated contact, pathfinding or venue capacity. Structure/room fit, Godot integration and performance remain untested.

## Rebuild and evidence

From this directory, run `blender -b -t 4 --python build_study.py`. Its only model dependencies are the unchanged `../../standards/materials.py`, `../../materials/material_manifest.json` and the eight source material PNGs. All four batch02 reference PNGs were visually inspected; the manifests preserve their Library IDs and SHA256 values. No reference pixels or geometry were copied.

Run `python qa/validate_glb.py` for the binary GLB audit. It checks actual triangle UV area, embedded texture hashes, dimensions, finite data, normals/winding and transforms. Run `blender -b -t 4 --python qa/render_and_audit.py` to reload the saved sources and render the actual imported GLBs. Its additional QA-only dependency is `../furniture/AST-FUR-002_day_reading_chair.glb`. Source reload reports check floor contact, packed images, positive transforms, editable part counts and the conservative empty volumes.

Five bounded views are provided: each exported study with the reused chair(s) at 640 × 360, a single-edge join/shelf detail at 1280 × 720, and two ordinary eye-height contexts at 640 × 360. The shared-table standing camera is exactly Z1.650m and the single-edge seated camera is exactly Z1.190m; camera positions and targets are in `qa/eye_context_camera_records.json`. The render manifest records exact asset hashes and labels the images as Blender component evidence. They are not native game screenshots or CRT output. The detail intentionally crops overall extents to show the wing/desk join. Reproduce the two added contexts with `blender -b -t 4 --python qa/render_eye_context.py`, then `python qa/label_eye_context.py`; this preserves the original three images.

`STUDY_SHA256SUMS.txt` hashes the deliverable family. Source `.blend`, `.glb`, generator, metadata and audit scripts are compact; render media can be packaged separately. No extra artistic assets, LOD variants or duplicated seating have been counted.
