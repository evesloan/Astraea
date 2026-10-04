# ASTRAEA — Visual Fidelity and Environment Production Contract

## Mission

Continue the existing Godot ship project. Bring its public interiors toward the supplied shopping promenade, aquatic/lazy-river, theater, and botanical-atrium references through real, traversable 3D architecture. Preserve the established game systems and the textured, pixelated early-2000s presentation inspired by Creature Kitchen. Use the supplied Logan's Run reference for architectural character, not its film narrative.

This is an execution and review specification, not confirmation that the current implementation meets it. Suggested numbers below are Astraea trial settings, not measurements of Creature Kitchen or the concept renders.

The next milestone is one approved, playable reference-matched section in the actual ship. It is not a ship-wide decorative pass. Do not propagate a visually unapproved kit.

## 1. Establish the source of truth

Read repository instructions, the pinned Godot version and renderer, existing architectural briefs, actual scene/build ownership, material and post-processing infrastructure, transit, physics, room registration, persistence, and navigation. Protect unrelated/uncommitted work. Do not upgrade the engine or migrate the renderer solely for this task.

Locate the supplied images. Confirm readable image files exist; do not substitute a prose recollection. Put their repository-relative locations in a reference manifest. Identify the main perspective panel and exclude graphic-design borders, captions, diagrams, and accidental generated text from architectural matching.

The current-layout atlas is a snapshot, not source code or proof of final visual quality. Verify its data against the live branch. The snapshot identifies ship.gd, auditoriums.gd, living_atrium.gd, full_game.gd, and SHIP_DESIGN.md; discover current equivalents rather than assuming paths.

Reference responsibilities:
- Live approved project: existing behavior, identities, coordinate system, dimensions, and interfaces.
- Atlas: baseline allocations, floor elevations, capacities, and documented limitations to verify.
- Supplied concept images: architectural character, composition, materials, and mood.
- Creature Kitchen: appearance inspiration, not an asserted polygon budget, shader implementation, or exact display resolution.
- This contract: proposed production and acceptance process.

Where they conflict, produce an explicit decision and affected-space report. Do not silently alter capacity or declare all images mutually consistent.

## 2. Protected baseline and reference conflicts

Maintain 1,000 guest units, 2,000 passenger berths, and 400 separate crew berths unless the owner explicitly changes the brief. Preserve persistent IDs, occupied allocations, actual deck elevations, and functioning travel/interaction interfaces.

Atlas checkpoints:
- D08: aquatic/wellness floor +44 m, with a 50 m main-pool lane footprint. D09 is +52.5 m: the difference is 8.5 m floor-to-floor, not 8.5 m guaranteed clear height.
- A multi-story aquatic hall and lazy river need an actual spatial fit/revision. The atlas does not establish them as a completed connected facility. Check the pool basin and structure below as well as occupied decks above. Do not erase the 50 m lane requirement or nearby wellness functions merely to resemble the concept image.
- D09: 100 addressed 12 x 12 m shops plus 10 larger destinations. Do not move all shops onto one atrium ring, invent businesses, or duplicate registered spaces.
- Grand Lantern Theater: 2,200 seats across D11-D13, 740/740/720, within a documented 22 m shell passing through the D14 floor zone. The visual board is not permission to invent extra tiers. Preserve backstage and registered gallery access.
- Atrium: 96 x 128 m slab opening on D02-D17; sixteen visible levels; major terraces on D06/D09/D12/D16. Preserve the clear central volume and approved limited crossings, rather than rebuilding a full bridge grid.
- Protect the live service-tram swept envelope, loaded cart clearance, arrival aprons, boarding states, express deck travel, and connecting portals. Do not equate decorative panoramic lift towers with functioning elevator cabins.

For any proposed envelope change, supply plan and section showing existing versus proposed boundaries, affected rooms/IDs, berths, access, headroom, floor openings, systems, and the smallest viable revision. Seek approval only for substantive unresolved conflicts, not routine mesh iteration.

## 3. Define the look through geometry, not labels

Architectural target: monumental pale textured columns; continuous sculpted balcony bands; rounded orange portals; integrated planters and conversation seating; layered recessed ceilings; restrained warm cove illumination; botanical depth; generous views alternating with intimate thresholds.

Reject generic spaceship paneling, industrial grunge, neon cyberpunk lighting, identical box rooms, arbitrary chamfering, flat-color primitives posing as final art, and photorealistic asset-pack mixing.

Low-poly is an economy of geometry, not a requirement to destroy curves. Spend triangles on silhouettes and important profiles. Use deliberately faceted arcs where appropriate, with intentional smooth/hard normal boundaries. Use texture work for small aggregate, fabric, tile, and panel detail. Do not manufacture voxel-like surface noise.

Every room family must have a meaningful plan decision and a meaningful sectional/threshold decision. Every major void must connect identifiable destinations, frame a view, support activity, or organize orientation. Do not fill openness with clutter merely to claim it has personality.

Keep each venue distinct. The promenade is a branching social street; the pool is a water-and-island circulation system; the theater is a focused fan-shaped performance space. They must not become the same atrium with swapped props.

## 4. Select the first playable fidelity sample

Use a real D09 frontage/terrace and its actual room, approximately 20-30 m of connected circulation where the live allocation allows it. Keep distant architectural representations needed for the view. This is an integrated section, not a disconnected showcase project.

Include a profiled column and ceiling junction; swept balcony fascia, railing and soffit; rounded orange entrance with wall depth; integrated curved bench/planter; one finished storefront interior; restrained foliage; cove lighting; actual signage; and a view across the atrium.

Create two kinds of saved cameras:
1. A diagnostic hero camera calibrated to the chosen reference composition.
2. Normal gameplay cameras using the actual player height, aspect ratio, and normal field of view.

Record transform, FOV/projection settings, aspect, render resolution, exposure/environment, and enabled effects. Adjust the diagnostic camera during initial calibration, then lock it. Do not widen gameplay FOV to conceal cramped rooms or use a camera position the player cannot occupy as the sole proof.

## 5. Produce a reusable architectural kit

Either use editable Blender source exported as glTF/GLB or deterministic Godot editor-time mesh generation. Use the existing project's approach where it is fit for purpose. Confirm available tooling; report missing capabilities rather than silently downgrading the visual requirement.

For continuous forms, define shared plan curves plus explicit cross-section profiles. Derive floor edges, fascia, soffit, railing alignment, and cove trim coherently. Supply corner, end-cap, doorway, and straight-to-curve transitions. Avoid separately hand-positioned approximations that leave seams.

Choose arc subdivisions from curvature and visible silhouette quality at review cameras, not one tiny fixed segment count for every object. Generate consistent normals, tangents where needed, arc-length UVs, and stable topology. Treat concave outlines, islands, and holes explicitly. Verify that triangulation does not fill atrium or water openings.

Retain useful source geometry and a reproducible build/export procedure. Use real generated/imported mesh resources for final static art. CSG is acceptable for prototype construction but final complex CSG should be baked/converted and checked rather than regenerated as an enormous Boolean tree each launch.

Deliver materials/UVs, correct pivots and scale, collision plans, interaction anchors, and tested import settings. Keep physics scripts and interaction state in appropriate wrapper/inherited scenes. Do not edit the .godot import cache as source content. Verify reimport does not lose material overrides, collision, or scripts.

Separate logical room allocation and identity from detailed architectural geometry, without introducing a second competing registry. Keep runtime systems attached to stable IDs/anchors. Replace placeholder collision intentionally; do not leave overlapping old and new colliders.

## 6. Build a shared material library

Start with a small family: pale aggregate/plaster, ivory molded surfaces, orange enamel/laminate, muted brass, terrazzo/tile, woven upholstery, glazing, foliage, and water. Reuse materials and trim sheets while allowing controlled per-instance variation.

Use painted low-resolution textures and consistent world-space texel density. Trial 128-256 px small-prop textures and 256-512 px repeatable tiles where appropriate; atlas dimensions may be larger. Final sizes are chosen from the approved sample, not treated as historical console limits.

Do not stretch one unique tiny texture over a giant wall. Generate continuous UV lengths across curved trim and test seams. Keep material UVs separate from non-overlapping lightmap UV2 where baking is used. Lightmap resolution does not have to match the low-resolution albedo aesthetic.

Inspect import compression and filtering on actual retro textures. A blanket nearest/no-mipmap rule is not acceptable: compare stills and movement for foliage, long floor patterns, railings, and signs. Preserve readability and avoid crawling moire.

Use restrained roughness/specular variation and designed highlights. Do not turn all surfaces into mirrors or assume all PBR-capable materials must be photorealistic. Require original, approved signage rather than copying malformed text from generated boards.

## 7. Choose lighting compatible with the existing build architecture

First determine whether relevant geometry exists only at runtime. Godot LightmapGI baking is an editor-time process; adding it to arbitrary runtime-created rooms does not generate their lighting.

Preferred path for fixed authored architecture, where compatible:
room/layout data -> deterministic editor-time assembly -> persisted static mesh groups with UV2 -> editor light/probe bake -> packaged static art and baked data.

Runtime retains simulation, actors, interactive lights, water, doors, and moving props. Keep baked meshes and transforms compatible with their baked scene data. Do not assume moving geometry or static light color after baking produces physically updated indirect light.

If this path would cause a disruptive rewrite, document a renderer-compatible alternative and validate it in the same sample before committing. Do not blindly add ship-wide dynamic GI as a substitute for a decision.

Compose lighting in layers: restrained general fill, warm local coves, destination accents, darker recesses, and controlled cool water/botanical contrast. Preserve white-surface detail. Do not flatten the room by increasing ambient energy or make everything orange through global grading.

Treat cove strips as visible fixtures plus a deliberate illumination solution. Emission appearance alone is not evidence the surrounding architecture is lit correctly.

Provide indirect-light probe coverage for moving people/props and suitable runtime direct lighting. Test an actual character and cart beneath overhangs and across lighting groups. Baked-only decorative illumination can otherwise disagree with dynamic objects.

Plan bake groups according to mutually visible spaces and current engine limits. Godot's stable guidance documents up to eight visible LightmapGI instances; verify the project's version and test cross-atrium views. Do not allocate one visible lightmap node per balcony or cabin.

Use bounded reflection probes or another justified solution for floors, brass, glazing, and water. Static reflection probes should not update every frame without need. Validate probe capture after required geometry loads; avoid capturing an empty unloaded sector. Test parallax artifacts in curved/non-box rooms rather than assuming box projection fixes them.

## 8. Preserve the retro presentation as a controlled pipeline

Reuse the existing rendering stack. Do not introduce duplicate WorldEnvironment ownership, pixelation passes, viewport trees, or color-grading systems.

Conceptual presentation order, adapted to the existing renderer:
3D scene and lighting at selected internal resolution -> approved tone mapping/color grade -> restrained palette quantization with stable ordered dithering -> nearest-neighbor presentation -> optional subtle CRT response -> readable UI.

Trial 640 x 360 and 960 x 540 for a 16:9 build only when no established target is already approved. Preserve the established aspect ratio. These are Astraea tests, not claims about Creature Kitchen. Use integer scaling where practical; correctly handle letterboxing and UI/input coordinate mapping.

Keep dithering locked to the intended internal pixel grid rather than per-frame random noise. Keep CRT, bloom, color reduction, and resolution separately controllable for review and accessibility. No compulsory vertex wobble, affine warping, severe aberration, or temporal smearing.

Explicitly verify shader color-space assumptions and avoid double tonemapping/gamma conversion. Depth-reading effects must match the project's renderer and depth convention; do not copy outdated depth reconstruction code blindly.

Review stills and slow camera pans. The effects-off scene must retain architectural quality and authored materials. The final low-resolution scene must retain recognizable doors, faces/silhouettes, signs, railings, and interaction targets.

## 9. Venue-specific production requirements

### Shopping promenade
Build several frontage/alcove variants within actual shop allocations. Create clear through-routes and smaller social courts. Use architectural framing, integrated seating, and visible destinations instead of depending only on floor stripes or text labels. Respect service and guest circulation.

### Swimming and lazy river
Keep the documented 50 m lane function. Design a real closed-loop river, usable entries/exits, dry circulation, planted islands, bridges where justified, and a basin with verified depth clearance. Separate hazardous/incompatible species environments according to existing rules rather than connecting all waters by default.

A full fluid simulation is not required to establish the look. Use a coherent water mesh/shader with flow-aligned UVs, restrained ripple/foam and caustic suggestions, suitable reflection, and readable waterline depth. Use existing swimming/buoyancy logic and a continuous authored flow direction for drifting bodies; do not fake gameplay solely by scrolling a texture.

Make moving rafts/props and swimmers obey existing physics/controller contracts. Profile waterfall, glass, and water transparency together. Validate depth effects from above, at the surface, underwater where supported, and through glazing.

### Grand Lantern Theater
Use fan-shaped seating, designed aisles, raked tiers, layered proscenium, acoustically suggestive forms, and restrained practical/stage lighting. Preserve the three-tier seating allocation and gallery interfaces unless an approved revision changes them.

Check representative seat-to-stage sightlines and usable routes; decorative columns must not dominate blocked views. Render repeated seating by spatial groups. Represent audience detail according to visibility and simulation requirements instead of assuming every distant seated person needs full AI and physics.

Do not claim real-world code, structural, acoustic, or evacuation certification from visual/gameplay checks.

## 10. Optimize without erasing the design

Profile actual hardware and the live gameplay route. Record resolution, renderer, build type, visible population, active physics, CPU/GPU timings where available, frame-time spikes, memory, and startup/streaming behavior. If the target is 60 FPS, 16.7 ms is the frame budget, not a promised result or a reason to invent arbitrary universal polygon limits.

Batch repeated static geometry by useful spatial/material/lightmap groups. A MultiMesh does not individually frustum-cull each instance; avoid one giant ship-wide batch. Keep persistent movable items individually represented where needed.

Keep visible opposite terraces present using suitable detailed or distant representations even when gameplay simulation is inactive. Do not put opaque occluders into open air to hide a streaming problem. Use actual walls and slabs for occlusion.

Inspect total shader/material cost, transparency overlap, shadows, reflection updates, and lightmap memory, not just triangle count. Protect silhouette-defining curves before microscopic details. Do not replace real interaction with decorative props merely to raise a benchmark.

## 11. Evidence gates

Gate A — Architectural form: material-neutral captures, plan, and section show the intended proportions, room identity, and coherent connections. The room must not still be a box behind a curved facade.

Gate B — Materials and lighting: effects-off and final-style captures match the intended material hierarchy, brightness structure, color balance, and depth. Inspect moving actors and reflective surfaces.

Gate C — Motion: normal gameplay capture includes walking, looking across levels, approaching signs, turning at corners, and moving the loaded cart. Check shimmer, pops, missing surfaces, transparency sorting, and interface readability.

Gate D — Integration: tests preserve IDs, counts, access, saved state, transit, collision, and navigation where implemented. State what was actually tested, on which build/platform.

Gate E — Approval and expansion: submit the first fidelity sample for visual approval before spreading its kit through the ship. Engineering assertions alone cannot approve appearance. Once approved, automate regression checks and continue routine changes without unnecessary pauses.

Save a compact review package per milestone:
- Build/commit, engine/renderer, hardware, configuration, and camera manifest.
- The chosen reference crop alongside the matching in-engine camera view.
- Neutral/material-lit/final-retro captures at identical transforms.
- Normal-player views and a short gameplay recording if available.
- Plan/section and useful wireframe/collision/overdraw diagnostics.
- Measured performance, actual integration test results, and unresolved mismatches.

Use image overlays and broad silhouette/value comparisons as diagnostics, not a single similarity score as proof. Do not game the framing, hide unbuilt areas behind fog, freeze the scene into a billboard, or submit a new AI concept render as an implementation screenshot.

If the available environment cannot render Godot with the intended graphics backend, report visual validation as blocked and request real captures from a suitable machine. Headless test success is not evidence of visual fidelity. Do not claim screenshots or walkthroughs that were not performed.

## Completion rule

An area is complete only when it has appropriate architecture, approved visual character from normal gameplay views, functioning integration, and recorded validation. More room count is not progress when the reusable kit is visibly wrong.

Begin by inspecting the live project, establishing the reference/camera manifest, and producing the real D09 room-plus-terrace fidelity sample. Do not restart the ship.

## Source notes

Project baseline: Astraea-current-layout-atlas(1).pdf, particularly pages 1-2, 10-11, 13, and 21. These describe the supplied snapshot, not an inspection of the current code. Supplied concept images provide visual intent; dimensions or implementation details cannot be recovered reliably from them alone.

Official documentation consulted for implementation constraints (use version-matched documentation for the pinned project):
- Godot, LightmapGI: https://docs.godotengine.org/en/stable/classes/class_lightmapgi.html
- Godot, Using Lightmap global illumination: https://docs.godotengine.org/en/stable/tutorials/3d/global_illumination/using_lightmap_gi.html
- Godot, Import configuration: https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/import_configuration.html
- Godot, Advanced Import Settings: https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/advanced_import_settings.html
- Godot, Procedural geometry: https://docs.godotengine.org/en/stable/tutorials/3d/procedural_geometry/index.html
- Godot, CSG prototyping: https://docs.godotengine.org/en/stable/tutorials/3d/csg_tools.html
- Godot, Multiple resolutions: https://docs.godotengine.org/en/stable/tutorials/rendering/multiple_resolutions.html
- Godot, Reflection probes: https://docs.godotengine.org/en/stable/tutorials/3d/global_illumination/reflection_probes.html
- Godot, MultiMeshes: https://docs.godotengine.org/en/stable/tutorials/performance/using_multimesh.html
- Godot, GPU optimization: https://docs.godotengine.org/en/stable/tutorials/performance/gpu_optimization.html
- Godot, Advanced post-processing: https://docs.godotengine.org/en/stable/tutorials/shaders/advanced_postprocessing.html
- Creature Kitchen developer page: https://the-rat-zone.itch.io/creature-kitchen
