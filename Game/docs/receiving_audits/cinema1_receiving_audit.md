# Cinema 1 minimal receiving audit

## Actionable installation geometry
- Retain exact recovered WP13 native and GLB. Place one root at [11, 69.5, -468], zero rotation and unit scale; the GLB already uses Godot axis order.
- Add missing floor X11..61 / Z-468..-396, top Y69.5, thickness 0.24, underside Y69.26. Area 3600 m². All actual datum contacts are supported; no geometry below datum was found.
- Do not reuse the inset source floor polygon unchanged: it leaves 41.125802 m² of actual wall/base contact unsupported. The rectangular allocation floor avoids that error without extending Cinema's allocation.
- Add parent-owned connector X4..11 / Z-409.4..-404.6, top Y69.5, thickness 0.24. Area 33.6 m². It meets existing D11_fore_route at X4 over 4.8 m, and Cinema at X11. Connection endpoints are existing public route [0,69.5,-407], portal [11,69.5,-407], and interior landing [14.5,69.5,-407].
- The actual current forward enclosure is AST-CIR-005_forward_breakroom_d03.glb translated by [0, 0, -432]. The connector is beyond the core's aft end, not through its closed sidewall. The connector volume's ordinary-height core obstruction screen returned 0 hits.

## Fast overlap and interface results
No same-datum floor ownership overlap, floor slab volume overlap, protected D11 void overlap, source/retained-slab intersection, or actual neighboring mesh intrusion into Cinema's occupied height was found in the tested local receiving geometry. Existing floor owners were read from current structural/received meshes and all current receiving-floor candidates; their hashes are in the JSON. No floor owner occupies this allocation at Y69.5.

Actual source bounds: [[11.01999631036424, 69.5, -467.9800000041723], [60.98000355444517, 77.75, -396.01999511395366]]. Mesh instances: 1227; triangles: 280710.

The recovered Library was parsed at [8,78,-466]. Its actual bottom is approximately Y78; proposed Library floor underside Y77.76 is 0.01 m above Cinema roof Y77.75. This is geometric separation, not approved bearing or load transfer. The four western Library piers at X9 are outside Cinema; preserve the parent-owned X8..11 support strip and protected D10 dining volume below Y69.26. No Cinema support is proposed into that lower programme.

## Import prerequisites
- Preserve 198 fixed seat places plus two transfer viewing bays, 200 places total, with explicit new WP13 IDs. These are not 200 ordinary chairs.
- No collision-exclusion or body-candidate metadata is present in the actual GLB. Six transfer-bay side/front marking meshes are only 0.018 m tall at Y69.5..69.518. Root should give these named decorative markings a deliberate nonblocking collision policy rather than blindly creating triangle collision; do not exempt the separate raised label/back/cap furnishings by a broad bay-name filter.
- Transfer markings: WP13_C1_R01_P01_bay_front, WP13_C1_R01_P01_bay_side, WP13_C1_R01_P01_bay_side.001, WP13_C1_R01_P20_bay_front, WP13_C1_R01_P20_bay_side, WP13_C1_R01_P20_bay_side.001.
- Quarantine 78 raw lights and use the current production lighting adapter/budget. Optional ocean shader remains source-only; it does not supply working playback/audio controls.
- GLB SHA256 e73065b2e2213f3743ba4bf79a27d4ce90a1ed131337ab0b20cce19762616af3; native SHA256 bbb7221545eb9dc073ff2ee5b7bae6965214a32250b5c82c0ef835a45d064aa5.

## Scope and limits
Read-only audit and scratch reports only. No Game or Catalogue changes, builds, engine import, backup action, or external agents. Per latest user direction, exhaustive route/movement/cart checks and detailed player-path planning were intentionally omitted; this report establishes installation prerequisites and a connecting endpoint, not traversal acceptance. No source-reference art re-review or structural load certification.
