# ASTRAEA — authored architecture and retro environment integration

You are continuing an existing Godot ship project. Implement an architectural and environment-art refinement inside that project, not a replacement ship generator, isolated demonstration scene, or rewrite of functioning systems.

**Goal:** bring the ship's spaces, beginning with its central atrium and connected destinations, close to the supplied luxury-cruise diorama in architectural composition and personality. Translate that ambition into our Creature Kitchen-inspired pixelated early-2000s aesthetic, preserving the established low-poly, CRT-dithered presentation and tactile physics gameplay.

**Core rule: modular construction, authored spaces. Repeat compatible building components, not identical rectangular experiences.** A functioning room registry is not finished architecture; a floor cut-out is not automatically a compelling space; a pixelation filter is not an art direction.

## 1. Work with the existing project and reconcile the references

Inspect repository instructions, project.godot, SHIP_DESIGN.md, and the current owners of room registration, geometry, rendering, transit, physics, navigation, and persistence. The atlas names ship.gd, auditoriums.gd, living_atrium.gd, and full_game.gd; locate their actual current equivalents instead of assuming paths or responsibilities.

Record the pinned Godot version, renderer, coordinate convention, room/door IDs, scene or procedural-generation architecture, player/cart dimensions, retro shader stack, and implemented streaming or visibility behavior. Capture baseline gameplay views and measurements. Protect unrelated and uncommitted work.

The live branch determines what exists. `Astraea-current-layout-atlas.pdf` supplies a spatial baseline to verify against it, especially pages 1–2 and 21. The blueprints and dioramas supply architectural intent, not authoritative occupancy, deck counts, dimensions, or proof of functioning features. Creature Kitchen supplies visual character, not its setting, assets, characters, or implementation.

The atlas deliberately simplifies rooms and omits much furnishing and finish. Inspect actual geometry before diagnosing it. Treat its room rectangles as allocation envelopes, not instructions to construct literal box interiors.

Preserve working controls, cart behavior, transit, interactions, persistent identities, and save compatibility. Do not upgrade Godot, change renderer, replace the main scene, introduce duplicate controllers, or create a second world-state or post-processing system for this task. Improve existing builders where they exist.

## 2. Protect the established spatial and operational baseline

Verify these atlas values against the live branch; report meaningful deviations instead of overwriting newer work:

| Item | Atlas baseline |
|---|---|
| Ship | 18 decks; 1,082 m length; 240 m maximum beam; 118 m reference envelope |
| Accommodation | 1,000 guest units; 2,000 guest berths; 400 separate crew berths including the player |
| Guest breakdown | 300 standard doubles; 300 family triples; 300 specialty singles; 100 specialty doubles |
| Atrium | 96 × 128 m slab opening across D02–D17; sculpted terraces occupy part of that opening |
| Vertical hierarchy | 16 visible levels: broad terraces on D06, D09, D12, D16; twelve smaller galleries |
| Key floor elevations | D02 +6 m; D06 +27 m; D09 +52.5 m; D12 +78 m; D16 +97.5 m; D17 +102 m |
| Crossings | Clear central void; optional narrow crossings on D09/D12 only; no full cross-bridge grid |
| Connections | 16 m fore/aft entry aprons; side portals X ±52, Z 0; cross-street portals X ±52, Z ±42 |

Retain the actual nonuniform deck elevations. Do not revert to an evenly spaced conceptual stack, an eighteen-level atrium, or the diorama's apparent four-story physical arrangement. The four main terraces should provide four strong visual bands within the existing sixteen-level volume.

Protect the starboard service-tram route and its full swept clearance, including a loaded cart:

`X/Z: (0,-72) → (0,-56) → (40,-52) → (40,52) → (0,56) → (0,72)`

Protect Townline stops at Z = -432, -216, -72, +216, +432 m and the central express arrival at X +5.5, Z -72 m, unless the live branch documents a revision. Preserve boarding areas, approach visibility, and guest crossings, not merely the track centerline.

The atlas distinguishes functional transit from scenery: the service tram carries the cart; Townline uses boarding/ride/exit states; express deck travel supplies usable inter-deck travel; panoramic lift towers are modeled architecture, not verified functioning cabins. Do not claim the last category already works or silently replace existing travel.

Protect neighboring allocations, residential privacy/access, and the theater's D12–D14 floor openings. Do not obtain visual grandeur by deleting cabins, reducing usable berths, moving interfaces, or cutting new unapproved holes through occupied decks.

## 3. Make open volume earn its place

Design the atrium as a vertical community, not a gigantic empty shaft surrounded by repeated corridors. Its openness should connect destinations, reveal activity, establish orientation, carry a coherent botanical composition, and contrast grand views with intimate places to stop.

For every major void, identify its purpose, the places overlooking it, what occupies its edges, the intended sightline or vertical activity, and why its height/width is useful. An existing required opening may gain meaning through its edges and section without changing its dimensions.

Give each principal terrace a readable arrival, a destination or activity, a comfortable stopping place, and a distinctive relationship to the garden and opposite decks. Use sheltered approaches opening into grand views, low canopies beside tall volumes, overlook bays, planting islands, and framed glimpses of other destinations. Do not rely on painted corridor ribbons alone to make circulation feel authored.

Keep the center visually legible. Meaningful openness does not mean filling all empty air with bridges, sculptures, foliage, or floating platforms. Preserve breathing room and the sense of height. Where additional floor area genuinely needs revision, identify the specific boundary conflict rather than improvising a new deck plan.

Use the botanical diorama for garden/water massing, layered terraces, and lounge composition. Treat the later concept board's celestial artwork as supplementary inspiration, not a competing full-height monument. Establish one principal focal composition; do not enlarge a single tree indiscriminately to fill the entire shaft or place a second spectacle in front of it.

Give visible upper and lower levels coherent lighting, destinations, and planted edges. Do not invent exterior windows through occupied rooms or a skylight through the bridge. Use genuinely exterior-facing geometry or clearly intentional panoramic displays where appropriate.

## 4. Replace box-room thinking with an architectural language

No guest-facing room should be delivered as an unchanged rectangular box with themed props. Rounded furniture, clipped corners, random diagonal walls, or a curved trim strip alone do not satisfy this requirement.

Develop a shared luxury-liner language: tapered hull-responsive rooms, faceted sweeping walls, crescent gathering spaces, nested alcoves, branching thresholds, layered ceiling ribs, recessed service elements, and coordinated floor/ceiling contours. Apply variation because it supports use, privacy, views, circulation, or species needs—not because every polygon must look unusual.

Every room family needs a meaningful plan decision and a meaningful sectional or threshold decision. A standard suite might use an offset entry protecting the bed, a curved seating recess facing its view, and a ceiling that opens toward the lounge. A family suite might organize sleeping alcoves around a shared gathering space. Preserve the existing bed count, usable clearances, and environmental equipment.

Use the full room volume. Coordinate walls, overhead structure, lighting, built-in seating, floor inlays, and entrances so they feel designed together. Do not leave the ceiling as an unrelated flat lid over a decorated floor. Keep every change inside real headroom and structural constraints; reserve double-height gestures for already available volumes.

Design around diverse bodies and modes of use: low resting surfaces, broad turning zones, perching alcoves, aquatic viewing interfaces, quiet recesses, and varied table approaches where the existing species profiles support them. Adaptation must shape access and spatial experience, not merely change a room's color.

A rectangular functional element can remain rectangular: a basketball court needs its playing envelope, while the surrounding hall can have a ribbed roof, fan-shaped spectator bays, and sculpted circulation. Kitchen work zones should remain usable. Architectural ingenuity must not become obstructive geometry.

Use several coherent room families and authored variants, not 1,000 bespoke meshes and not one repeated box. Back-of-house spaces should express service purpose through work bays, storage integration, thresholds, and structure rather than becoming generic leftover voids.

## 5. Give the actual destinations distinct identities

These are proposed architectural treatments within existing allocations, not extra registered rooms or businesses:

| Location | Form, purpose, and personality |
|---|---|
| D02 garden basin | A deliberate waterline, planted islands, framed botanical base, and sheltered maintenance interfaces; preserve engineering access. |
| D06 botanical terrace | Branching conservatory ribs, leaf-like seating pockets, a recognizable garden-cafe threshold, and views into the grove. |
| D09 retail terrace | Small social courts, recessed boutique entrances, angled display bays, and a legible transit arrival; storefronts should not read as identical vending-machine doors. |
| D12 gallery/library | Crescent reading bays, quiet screened alcoves, framed art and garden views, and clear existing theater-gallery access. |
| D16 family gardens | Shared garden commons, clustered seating for different bodies, playful but unobstructive niches, and calm thresholds to residences. |

Keep smaller connecting galleries quieter, but give them deliberate proportions, ceiling treatment, edge details, and occasional useful stopping places. Do not decorate all sixteen levels with identical sofas and planters.

D09 already has 100 addressed 12 × 12 m shop footprints and ten larger destinations. Develop their real connections; do not relocate all 100 shops onto the atrium ring or fabricate additional shop rows. Use existing destinations such as the garden cafe, library, bakery, or commons where their actual locations support the composition.

Extend the language through representative rooms: fan-shaped theater seating within its reserved volume; a dining room gathered around a curved service island; a lounge with nested conversation bays; a quiet habitat with a sheltered entry and cocoon-like resting recess. Treat these as layout studies, not permission to overwrite established room functions.

Create identity through architectural form, furnishings, signs, local sound/light character, and appropriate traces of use. Avoid random clutter as a substitute for personality. A space should remain identifiable with its sign hidden.

## 6. Build a modular kit that supports authored shapes

Follow the repository's current scene/procedural conventions. Use shared resources, instanced scenes, or parameterized mesh builders as appropriate; do not force a project-wide migration.

Create a compact kit of straight and angled wall bays, faceted arc sections, tapered floor pieces, matching ceilings/soffits, branching junctions, alcove inserts, portal surrounds, terrace fascias, railings, structural ribs, and integrated seating/planter modules. Include transition pieces: attractive individual modules are insufficient when their seams do not meet.

Derive components from existing deck contours and room data. Keep a stable placement system and compatible pivots, seam dimensions, normals, UVs, and materials. Do not snap working doors or transit routes to an arbitrary new grid. Avoid stretching modules into broken proportions.

Keep each registered room's identity and allocation separate from its authored interior profile. Where necessary, add backward-compatible local footprint/ceiling-profile data to the existing builder. Preserve registry envelopes for consumers that depend on them; do not pretend those rectangles are precise walkable shapes. Do not create a second competing room registry.

Generate or validate visual surfaces, simplified collision, navigable areas, thresholds, and furnishing clearance from the same architectural intent. Handle holes and concave boundaries explicitly; never let automatic triangulation or one convex collider bridge an atrium opening or fill a room interior.

For procedural static forms, reuse the current mesh helpers or suitable ArrayMesh/SurfaceTool builders. Cache generated meshes or produce them at authoring/load time, not every frame. Maintain explicit control over material regions and UV scale.

Author hero compositions. Use deterministic approved variants for repeated rooms, not per-load random geometry. Share meshes/materials while keeping meaningful interactive objects individual and connected to existing persistence. Do not register decorative niches as new passenger accommodations.

## 7. Apply Creature Kitchen-inspired art at every layer

Target textured, pixelated early-2000s 3D with inviting, slightly strange personality. Creature Kitchen is the appearance reference; the numerical settings below are proposed Astraea starting points, not claims about that game's internals.

Use economical, intentional silhouettes and visibly segmented curves where appropriate. Low polygon count must not mean primitive-box architecture or indiscriminately flat-shaded triangles. Spend geometry where it changes room silhouette, furniture usability, branch shapes, or important curves. Large balcony arcs need sufficient segments to retain elegance from ordinary player views.

Use low-resolution textures with coherent texel density, restrained wear, readable patterns, and painted/baked-looking tonal variation. Where the project lacks standards, trial 128–256 px small-prop textures and 256–512 px reusable tiles/trims; shared atlases may be larger. Do not stretch one tiny unique texture across a giant floor or substitute untextured flat colors everywhere.

Translate luxury through ivory/pale panels, muted champagne or brass details, dark blue-green recesses, varied foliage, warm local light, and restrained cool water accents. Keep whites reasonably neutral rather than tinting everything yellow. Use light/shadow to reveal form and create intimacy, without making a working passenger space unreadably dark.

Avoid modern photorealistic gloss, microdetail-heavy PBR, voxel forms, generic low-poly asset-pack mixing, and automatic PS1 wobble/affine distortion. Those effects are not required simply because the reference is retro. Match the chosen appearance rather than an indiscriminate collection of nostalgia effects.

## 8. Preserve the display pipeline instead of stacking filters

Inspect and reuse the existing pixelation, color grading, dithering, and CRT treatment. Keep UI legible and mouse interaction correctly mapped to the rendered world.

Where no world-resolution target exists, test an optional 640 × 360 widescreen baseline with aspect-preserving nearest-neighbor presentation and integer scaling where practical. Preserve the established aspect ratio and provide a clearer setting. This is a trial configuration, not a mandate to replace working rendering infrastructure.

Distinguish low-resolution world rendering from simply covering a full-resolution render with a mosaic effect. Ordinary 3D resolution scaling does not itself specify our desired nearest-neighbor aesthetic; implement the presentation through the existing viewport/compositing approach and verify it visually.

Keep dithering bounded and stable at the intended pixel grid. Treat color reduction, pixel scaling, and CRT presentation as separate adjustable stages. Avoid frame-random noise, excessive bloom, severe chromatic aberration, blurred interaction targets, or compulsory scanlines. Inspect foliage, patterned floors, railings, and signs in motion before deciding filtering/mipmap policy.

The architecture and materials must still look intentionally authored with display effects disabled. Present both versions during review. Do not conceal weak geometry or missing texture work beneath stronger pixelation.

## 9. Integrate physics, visibility, and performance honestly

Preserve the cart's existing awkward, tactile handling and meaningful physics interactions. Validate curves, thresholds, floor seams, corners, and furniture spacing using the actual loaded cart and character sizes. Keep navigable surfaces smooth enough for reliable movement beneath visibly segmented construction.

Use simplified static collision for architecture and suitable primitive/convex shapes for moving props. Keep collision faithful to important openings and contact surfaces; do not use a solid convex hull around a hollow room. Avoid turning every decorative leaf or fixture into an active rigid body.

Separate visible architectural representations from active simulation. Opposite terraces and upper galleries may remain visible across many levels even when their detailed gameplay sectors are inactive. Preserve those representations and important silhouettes. Do not rely solely on current-floor loading or hide visibly open air behind opaque occluders.

Use actual opaque structure for occlusion and suitable distant representations for exposed views. Group repeated static MultiMesh instances by terrace or spatial section, not one entire-ship group expecting per-instance culling. Keep movable/persistent props out of static-only batching.

Control transparent glazing, foliage layers, water overdraw, live reflections, and shadow-casting lights. Preserve their visual roles with restrained implementation rather than deleting them. Respect existing lighting/baking organization; do not add independent lightmaps or another shader stack to every module.

Measure comparable before/after gameplay routes on available hardware. Record settings, frame-time behavior, memory, visible geometry/material cost, and active physics load where measurable. Do not trade away core interactions to improve an empty-scene benchmark or claim target-platform validation that was not performed.

## 10. Implement in architectural checkpoints, not a ship-wide blind rollout

**A — Audit and protect.** Capture current gameplay views and inspect the named builders. Mark door, portal, transit, bed, service-access, headroom, and structural exclusion volumes. Record baseline counts and existing limitations. Describe the smallest compatible changes; do not stop at a proposal when implementation is possible.

**B — Author a room and a connected terrace together.** Select a real D09 destination or eligible connected frontage near an atrium entrance. Build an approximately 20–30 m terrace sample and one actual room within its existing allocation. Include a non-box spatial arrangement, designed ceiling/threshold, planted seating pocket, railing/soffit family, and a framed view across the atrium. Keep the actual controller, physics, transit context, and retro pipeline.

First review the sample with simple materials: can its purpose be understood from plan, section, and eye-level views without labels? Then finish its materials, lighting, and selected props. Do not propagate an attractive facade hiding an unchanged box interior.

**C — Compose the whole atrium.** Apply the successful component family to the four main terraces and quieter galleries. Resolve the botanical/water focal sequence, visible supports, active edges, and cross-level views. Preserve existing openings and limited crossings. Review from normal player height before adding more detail.

**D — Prove repeatability.** Apply distinct approved profiles to a standard suite, family suite, specialty habitat, and another public room. Preserve all berth/access requirements. Refine transitions and shared builders before expanding the approach across the ship. Do not claim every room is reauthored after completing only samples.

**E — Test and deliver evidence.** Test ordinary arrival, walking, loaded-cart travel, tram passage, existing inter-deck travel, navigation where implemented, interaction, persistence, and relevant streaming transitions. Validate room/berth counts, blocked interfaces, floor holes, collision seams, shader errors, viewport input mapping, and performance regressions.

Provide before/after in-engine captures using repeatable normal-gameplay cameras, including entry, room interior, D06, D09, D12 looking down, and D16. Include a plan and section for the sample, a diagnostic cutaway, and effects-on/effects-off comparisons. Do not substitute new generated concept art for evidence of the built result.

## Acceptance and handoff

The atrium must resemble the diorama through its spatial hierarchy, layered architecture, inhabited edges, garden/water composition, and sense of hospitality—not just color or camera angle. Its large open volume must connect meaningful places rather than expose repetitive empty levels.

The tested room families must have architectural identity in plan and section, not merely different furniture. Straight functional surfaces may exist, but the guest experience must not reduce to decorated boxes. Circulation, usable area, diverse bodies, physics, and existing systems must remain supported.

Deliver changed files/components, actual test results, comparable captures, a room-profile/module summary, known limitations, and a reversible change path. Distinguish completed work, placeholders, estimates, and untested behavior. Proceed without routine clarification; ask only when a genuine unresolved conflict would alter protected interfaces, capacity, or engineering.

**Begin with the live-project audit and one connected room-plus-terrace architectural sample. Repeat the construction system—not the experience.**
