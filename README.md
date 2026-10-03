# The Astraea — Godot production restart

Godot 4.6.3 Compatibility. One metre per unit; X port/starboard, bow toward -Z, canonical floor-origin Y datums. This is the permanent reconstruction project, distinct from the missing original and preserved Unity work.

## Current state
The main world has 18 nonuniform structural datums and compiled circulation slabs. D09 has a partial conversation-salon terrace. An aligned D08 Gentle Waters / D09 Living Gifts / D10 Vesper section has offset openings, a basin, traversable switchback stairs, profiled columns and one sheltered wet-rest bay. Interiors and public programmes remain unfinished. No whole room, district or full-game acceptance is claimed.

The presentation uses a real 640×360 world, nearest-neighbor integer scaling, restrained ordered dithering, optional scanlines and local fixture lighting. The latest main-scene inspection found 24 source designs instantiated 70 times; these are not completed-room counts. The catalogue has 94 authored designs, including 5 new drafts awaiting fuller review.

## Controls
- WASD and mouse: walk/look
- Hold RMB: focus zoom and pixel-cluster reticle; press E to operate supported objects (currently the staff service door). Depth-of-field remains to implement
- Escape: release mouse; left-click: capture mouse
- M: temporary express deck/destination directory; actual physical transit remains incomplete
- F3: cycle 360p / 540p / native 1080p world rendering for style and geometry inspection
- F11: toggle fullscreen; integer scaling fits a 1080p display at the default world resolution
- F4: toggle display effects, glow and SSAO
- F12: save raw world, processed world and presentation captures in artifacts

## Organization
- scenes/main.tscn: presentation entry; scenes/ship.tscn: single main ship world
- data/design_contract.json: latest reconciled owner decisions
- data/spatial_layout.json: authored floor polygons, holes, relative elevations and ownership
- tools/compile_layout.py: offline cached structural meshes; requires tools/requirements-geometry.txt
- data/programme_ledger.json: historical programme continuity and pending work, not a replacement room registry
- data/reference: historical source evidence; allocation rectangles are not mandatory room geometry
- assets/models: source catalogue GLB imports; editable Blender sources remain separately versioned
- docs/PRODUCTION_STATUS.md: scoped implementation, tests and limitations

## Validation
Run python3 tools/validate.py with Godot 4.6.3 on PATH. It isolates Godot cache/config under the project and checks import, baseline, main-world support/arrivals and actual capsule stair traversal, door targeting/sweep behavior and shared-contact release. Run tools/test_multilevel_compiler.py with the pinned geometry dependencies to verify stacked floor ownership. Target-GPU frame rate, cart clearance, NPCs, persistence, physical lifts, swimming and final visual quality have not passed acceptance.

## Backups
Local Git alone is not an independent backup. Verified source snapshots are retained in Library; the first baseline is independently hash-verified on Workshop. Automatic Workshop delivery is not established. Preserve original inputs and Unity work. Exclude authentication state and disposable import caches from archives.
