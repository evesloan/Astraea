# Central D18 crown construction kit

AST-CMD-001 is one new editable architectural design, increasing the catalogue from159 to160. It is a bounded six-programme shell and roof-frame increment, not a completed command deck.

## Scope and ownership

The original keys D18_directory_02 through D18_directory_07 remain Navigation gallery, Communications, Solar enclosure chart, Officer respite, Bridge briefing and Astrometric station. Existing D18 floors at106.5m remain owned by the original cap/apron; this source adds no general floor. Bridge terminal, two aft command programmes, large aft foyer/Upper Horizon and luxury dwellings remain outside this increment. No bed, guest or crew capacity, operational command simulation or access-control gameplay is introduced.

The source contains six enclosed shells, screened side circulation, ten apertures fitted to actual AST-STF-008 fixed-frame geometry, selected outward-canted windows, coordinated ceilings/source fixtures, four segmented bearing spines and a restrained roof/transfer frame. The three windowed rooms use canted glazing with continuous sill/head pockets and end reveals. Communications, Bridge briefing and Astrometric station remain deliberately enclosed. Ceiling bay rhythms and threshold profiles use the retained institutional staff palette with a restrained warmer Officer respite accent.

## Integration contract

- Source: source/AST-CMD-001.blend
- Export: exports/AST-CMD-001.glb
- Exact coordinates, programmes, ten doors,74 source fixtures,16 ties and glazing: source/section_contract.json
- Editable part geometry: source/geometry_parts.json
- All positions are Godot world coordinates; Blender mapping is(X,−Z,Y), exported Y-up at world origin
- Parent supplies working AST-STF-008 doors. This export contains neither their fixed frames nor duplicate static leaves
- Source wall apertures are2.750m wide and2.815m high. Actual fixed frames are2.760m wide by2.820m high and0.360m deep. The5mm overlap seals the outer seam while preserving the moving opening
- Parent labels use corridor-facing room headers atY109.65; backing remains solid and no source signage is included
- Exact downward light markers sit10mm below visible opal lens undersides; warm/cool colours and local ranges are recorded in the contract
- Glass material: ASTRAEA_crown_tinted_glass. Runtime batches use CMD_CELL_X{cell}_Y{cell}_Z{cell}_ASTRAEA_crown_tinted_glass
- All runtime meshes use concave static surface collision. Glass is visibly present and has real closed faces. Do not replace the whole kit with convex collision
- The full6m northern public belt X±48/Z−80..−74 and public route X±4 stay clear. North control door planes areX±8/Z−73.80, facing north and opening south; full-width returns join the actual screen-to-room boundary. Navigation and Communications retain1172m² each after the explicit north-wing revision. Side corridors keep the bounded controlled crossings from the construction brief

## Bearing frame

Four0.8m×1.2m spines remain centred atX±51.5/Z±71, fromY−3.2 to114. Every chord, collar and shoe stays inside the audited footprint; the outboard X faces never exceed±51.9. Principal-band edge ties fit inside the slab depth and stay below walking level. Their source-tested contacts are0.20m into the slab edge and0.02m into the pier chord envelope. These are edge-seated ties, not underside-bearing plates.

Transverse transfer girders occupyZ±71 aboveY111.25. Longitudinal members sit atX−32,0,+32 within the roof. The roof body staysX±36/Z−78..64; its stepped outer skin stops atY114.44. No opaque outboard canopy blankets the gap between windows and the spines.

This is architectural game-space contact evidence, not certification of structural load adequacy. The new ties require actual-scene collision/contact queries; the earlier four-pier runtime audit alone does not cover them.

## Reproduction and review

Run source/make_section_contract.py only when intentionally regenerating the brief-derived contract, then run source/build_central_crown.py with Blender4.3.2. The builder asserts catalogue ownership before export. Run qa/verify_central_crown.py with Blender for closedness, metric UV, exact triangle/material/UV signatures, forward/reverse vertex agreement, bounded batches, real shared-door sweep samples, source lens exits, glazing/frame bounds, contacts and protected prior hashes.

qa/render_source_preview.py produces bounded two-thread source diagnostics. Its temporary D18 support floor and imported shared doors are review context only; they are never saved or exported into this kit. These images cannot establish actual main-scene lighting, supported runtime walking or final art acceptance.

See qa/crown_tie_source_interfaces.json for the independent compiled-slab/source-model checks. The nearest protected allocation is D11 Backstage workshop,0.16m outboard of the port-aft D12 tie. No outboard hardware expansion is allowed.

## Remaining acceptance

Parent owns Godot integration, actual player/cart walking and door operation, actual-scene pier/tie contact and clearance queries, lighting response, normal/effects-off views and catalogue adoption counts. Broad empty shells are intentional at this platform stage; furniture, celestial views, adjacent pavilion composition, inhabited use, final architectural finish and target-hardware performance remain unfinished.
