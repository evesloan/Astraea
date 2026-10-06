# Grand Pool leisure display source candidate

Status: scratch recipe and content prepared. Blender has not been launched. No .blend or GLB has been created, no export or scene render has run, and no catalogue or Game file has been changed. This is not visual acceptance or a room-completion claim.

## Approved ownership and scope

Four new representations of AST-LIB-010, existing `library_use` family, intended for the approved sibling `assets/grand_pool_first_pass/comfort_greenery/media`. Physical wall and floor interfaces refer to existing AST-AQU-016 supports. There are no new catalogue IDs. The existing 51 furnishings and retained 48 additions stay intact. The optional wet planting beds are outside this candidate.

- `market_rest_0_screen`: exact westward body reservation X −52.05..−50.35, Y 54.03..55.03, Z −446.30..−446.10. Image stays X −51.97..−50.43, Y 54.11..54.95, Z −446.28.
- `market_rest_1_screen`: body X −51.48..−49.92, Y 53.68..54.58, Z −434.44..−434.26. Image X −51.40..−50.00, Y 53.76..54.50, Z −434.42.
- `market_rest_2_screen`: same X/Y as screen 1, body Z −417.44..−417.26; image Z −417.42.
- `wet_end_rest_floor_display`: complete reserved stand/body X −41.35..−40.88, Y 46.2..48.6, Z −403.6..−401.4. Image X −41.35, Y 47.12..48.38, Z −403.48..−401.52. Actual recipe fits slightly inside the reservation: X −41.35..−40.89, Y 46.2..48.48, Z −403.58..−401.42.

World coordinates above use Godot/glTF Y-up. The source builder maps world (x,y,z) to Blender (x,−z,y). Artwork U is world −X on wall screens and world +Z on the floor screen; V is +Y. Both bases are right-handed. Independent reopen derives and tests those directions from actual vertex UVs rather than assuming readable PNGs imply readable screen geometry.

## Believable source construction

The builder opens an isolated empty source scene, appends only the named original LIB-010 shell/frame/gasket/glazing, bearing, service, foot and spine prototypes, links them and updates the view layer before inspecting their transforms. It records their geometry and material lineage, then removes the temporary prototypes. It re-authors dimensioned, editable family profiles rather than scaling a whole terminal onto a wall. The original FIND A BOOK plane, controls, and UI image are never appended.

Each wall unit has a closed ivory body, walnut ring, gasket, optical backing, original full-frame image, rear service case with separate fasteners, four real backplates and bearing arms, and a closed feed boss. The floor unit has two shaped ski shoes over elastomer floor pads, swept load spines, timber joints and a service bridge. Its image is necessarily flush at the frontmost reserved X plane; no bezel is pushed outside the envelope to pretend it is recessed.

The wall plates use actual retained exported triangle planes, not the rounded architectural labels:

- Orange return: Z −446.1000061035156
- Upper pier 1: Z −434.260009765625
- Upper pier 2: Z −417.260009765625

Each wall has 20 exact triangle witnesses. The stand has 10 witnesses on the pinned D08_grand_pool_wet compiler floor triangles at Y 46.2. The source decorative underlay at Y 45.96 is explicitly not used as the walking surface. Construction/reopen float tolerance is 50 micrometres. This is static visual support evidence, not electrical, structural certification, accessibility or actor/species approval.

## Original content and retained materials

Four purpose-authored SVG/PNG works are in `content/` and `textures/`:

1. SunCorp / Grand Pool: lagoon, foliage, sunset; “PAUSE BY THE WATER.”
2. SunCorp / Orchard Market: botanical still life; “LIVING GIFTS” and a clear-walkways courtesy notice.
3. SunCorp / Quiet Moments: calm orbital-tide image; “A MOMENT TO UNWIND.”
4. SunCorp / Grand Pool: broad water vista and a walk-on-wet-decks courtesy notice.

The geometry and layouts are original. The existing family’s compact letter alphabet is retained as an explicit source dependency, with no copied reference pixels, photographs, library UI, fake controls, invented live state, video or streaming claims. Large imagery carries the view; tiny text is not the viewing accommodation.

`material_provenance.json` and `content_manifest.json` record all image hashes, SVG sources, texture sizes, copy and shader settings. The actual LIB-010 ivory, walnut, champagne, rubber and display-glass materials are appended unchanged. New solid parts receive their real material-scaled UVs. Artwork uses a single 0..1 image face. The new image material has local emission strength 0.18, roughness 0.34, no transparency and no light objects. There is no shared renderer, palette, light budget or shader edit.

## Prepared checks and current evidence

- `qa/PURE_PREFLIGHT.json`: 99 editable mesh recipes, 5,708 pre-modifier triangles; all four exact envelope checks, 120 actual recipe image-plane probes, and no intersections with all six full low/high foliage reservations or the five small wet-whorl reservations.
- `qa/PURE_CONTACT_QA.json`: 95 internal joining relationships confirmed by actual recipe triangle SAT, not just bounding-box overlap.
- `qa/STATIC_QA.json`: Python AST checks, no export/render operation in the source builder, explicit source-slot argument, refusal to overwrite an existing candidate, and all 67 retained dependency pins verified.
- `qa/REFERENCE_AND_ART_INSPECTION.json`: actual market, retro-atrium, aquatic and source-terminal pixels inspected; four original content images inspected. This is content review only.

Pure preparation commands may run without Blender:

    python content/make_pool_leisure_art.py
    python source/prepare_contract.py
    python qa/pure_contact_check.py

The parent must allocate the one two-thread Blender source slot before either following command:

    blender --background --threads 2 --python-exit-code 1 --python source/build_media_source.py -- --allow-source-build
    blender --background --threads 2 --python-exit-code 1 --python qa/reopen_media_qa.py

The build is source-only. It refuses an existing source file and saves only `source/AST-LIB-010_pool_leisure_displays.blend` and `qa/SOURCE_BUILD_REPORT.json` in its current media package. If later installed in the approved catalogue sibling, the builder and QA reports explicitly list their new derivative catalogue writes, while preserving all original sources/exports and the Game. It includes no export function. Reopen starts with the actual original source for material ground truth and then opens the candidate afresh. It validates evaluated closed geometry, exact support witnesses, a complete grounded bearing graph, metric source UVs, actual underlying image-node/socket links, packed image bytes, UV viewing handedness, and 120 first-hit image visibility probes against all media, retained architecture, the 51 original/48 planned instances, staged finish envelopes and complete reserved vegetation volumes. It writes `qa/INDEPENDENT_REOPEN_QA.json` only after those checks pass.

## Remaining gates

1. Parent code review, source slot, actual build and independent fresh reopen. None has happened yet.
2. Independent source retention and hash verification.
3. Parent-coordinated visual comparison with actual full leafy geometry, both bench seats and stand approach, source support detail, and 640×360 market/long-pool views. Housing, meaningful content and full planting must coexist visibly; counts and rays alone do not establish visual quality.
4. Export and promotion only after the required source-QA and retention gates. No export, catalogue write, Game write, runtime collision, room lighting or loaded-engine acceptance is part of this handoff.

## Portable reference archive

All audit input JSON is read unchanged from the sibling `../reference_audit`. The nine inspected baseline and source-terminal image archives are resolved through its `REFERENCE_RELOCATION.json` against the comfort_greenery package root and pinned by exact image hash. Volatile Game capture paths are historical attribution only, never dependencies of this candidate. `source/media_paths.py` discovers the containing catalogue after installation, or uses the retained read-only scratch fallback in `retained_roots.json`; dependency keys use package/catalogue/game-relative scopes. The build and reopen source paths are relative to the media package and original catalogue.
