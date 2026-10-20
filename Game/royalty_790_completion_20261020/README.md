# Royalty790 upper construction candidate

## Open and edit manually

Open **Royalty790_UpperCandidate.tscn** in the existing Godot project. This is the single stable editor entry. Its mesh, material, fixture and collision nodes are explicitly saved and individually selectable; no generator is required to open or edit it. Select `UpperGallery/RG_UpperGalleryFloor` and press **F** to frame the construction because the retained geometry uses ship-world coordinates rather than a local origin.

The scene groups are RetainedArchitecture, UpperGallery, FittedStair, PitlessReceiver, Fixtures and SupportingFrame. Stair walking contacts are explicit named ConvexPolygonShape3D children, separate from the visible treads. The parked cabin is clearly marked reference-only: it illustrates the exact retained cabin fit but does not implement lift movement or admission.

For mesh remodeling, open **source/ROYALTY790_upper_candidate_r002.blend** in Blender. The individually named source meshes, UVs and packed original material textures remain editable. Save manual revisions under a new successor name; do not overwrite the original retained AST-RES-006 or the source baseline. Export only visible geometry/markers, not `PREVIEW_ONLY_*` floor-owner previews. The current corresponding runtime mesh is **exports/ROYALTY790_upper_candidate_r002.glb**.

`source/build_candidate.py` is an optional deterministic regeneration recipe, not a prerequisite for manual construction. Running it intentionally regenerates its named r002 output, so do not run it over a manually edited r002 file. Make a new revision and update the recipe/output names first. Earlier r001 stays under source/exports as provenance; it is not referenced by the editor entry.

## Placement and safe adoption

Canonical transform: position(0,0,0), rotation(0,0,0), scale(1,1,1). The whole source is already in exact ship coordinates. Main upper floorY106.5; lower ship floorY102 is unchanged; same-unit lower cabin boarding isY102.20 via the bounded ramp. This does not create a new deck, home, berth or lift stop outside the private home.

This is **a successor to AST-RES-006, not a second additive instance**. It includes that retained lower architecture, a carefully opened roof, the relocated complete CourtView fixture and new upper construction. Replace the original representation exactly once only after coordinated current-main review. Do not put this scene on top of the existing original. The ordinary lower slab remains owned by the existing ship floor compiler and is intentionally not duplicated. Current main bootstrap, registries, ship builders, original models and floor owners are untouched by this package.

For runtime candidate testing, `package.gd` imports the successor and reuses the unchanged private-lift/controller/gate family. Its default is held: physical receiving and private admission must be accepted before operation. The editor's reference-only parked cabin is not used by this runtime package. Do not instance both editor scene and runtime package.

## What is constructed

- Inset, faceted upper gallery with an inward private edge, quiet work niche and outboard sitting edge.
- Fitted family-derived two-flight stair, intermediate landing, guards, supported opening edges and faithful smooth walking contacts.
- Pitless lower ramp/receiver, source-sized cabin shaft and same-unit upper landing.
- Local upper roof, expressed supports, integrated fixture assemblies and matching light markers.
- Exact roof passage/headroom openings: stair20.37m² plus cabin17.248m², not the full72m² reservations.

The staircase is newly authored using the retained CIR-001 construction family because the existing6×10.55m public stair does not fit the reserved private envelope. The cabin itself is unchanged AST-CIR-003. This is not a claim that a completed historical790 upper was found.

## Evidence and limits

Saved native and actual GLB reimport match5,876 triangles, with zero missing/extra at0.1mm rounded world precision.256 unaffected original objects are fingerprint-preserved and all181 new meshes have positive closed volume. The exact original source and input hashes remain unchanged. The actual unchanged player passed the bounded stair ascent, upper-outlook approach and return, with cabin operation held and no-pit arithmetic checked.

`evidence/ENGINE_CANDIDATE_CHECKS.json` describes an isolated fixture using the exact retained lower-platform polygon. This is not full-main traversal acceptance. The first engine launch failed on its default unwritable userdata path; the scoped writable-XDG run passed. r001 source-view review caught coplanar upper floor ribs; r002 lowers those concealed ribs/fascia without changing stair geometry. Prior evidence remains under evidence/attempt001.

Source PNGs are diagnostic Blender views, not actual low-resolution game views. Their lower slabs are retained preview meshes enabled for the render only and never exported. The upper roof is hidden in the named cutaways. They do not establish final materials, ship-context sightlines or final art.

Still open before adoption: current-main owner/neighbor checks for590/614/814, full-context player/cart routes, actual moving-cabin boarding/transfer and safe closure, private-admission integration, fixture-light budget, normal first-person/CRT review and final architectural finish. This package alone does not certify those gates.
