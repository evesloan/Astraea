# Central eighteen-deck circulation platform

The existing main ship now contains one central public core at Z=-100m. Its eighteen supported landing/bypass floors meet the existing north spine and atrium apron. Seventeen switchbacks use actual 4.5m, 6m and 8.5m rises; the authored stair geometry changes riser/going dimensions without scaling guards. One physically moving cabin serves all eighteen canonical floor heights through its eighteen-button panel.

## Evidence in progress

Focused checks have passed actual capsule ascent/descent through all seventeen stairs, supported bypass walks on every deck, loaded player/cart/four-product lift travel from D01 to D18 and back, and physical push-in/upper-deck pull-out with four loose products. The full regression and graphical acceptance are recorded below when completed. These are simulation checks, not target-device FPS or freehand usability acceptance.

The loaded boarding test exposed a real old player-controller defect: falling seven metres below the selected spawn deck teleported the player home, even when safely standing on a lower ship deck. Recovery now uses a below-ship datum at Y=-7m, independent of the selected spawn. The boarding regression keeps the default upper-deck spawn while entering D01, and separately verifies recovery from below the ship after the completed travel circuit.

## Authored sources

- AST-CIR-005: editable shaft/landing enclosure, fixed guards, source fixture bodies and deck datums, 8,940 triangles
- AST-CIR-001_H450 and AST-CIR-001_H600: editable rise-specific derivatives, 1,772 and 1,932 triangles; original 8.5m stair retained unchanged
- AST-CIR-003_eighteen_stop: previously validated cabin/panel derivative, now installed in this one core
- data/architecture/PRIMARY_ATRIUM_CORE.json: floor openings, elevations, physical cabin envelope and stair contract

The structural compiler resolves 167 floor regions to 2,801 triangles with valid polygons, area conservation and protected openings. The whole-ship accounting remains eighteen decks, 161 programmes, 1,000 guest units and 100 shop allocations. The current-opening audit finds no guest-envelope conflicts.

## Remaining scope

The other four public cores and all staff risers remain reservations. The hull section, local destination routes, luxury replacements, full crew fit, inhabited gameplay, final art, species ergonomics and full-network cart use are unfinished. This one core is a working-platform advance, not a finished ship or a claim that every destination can already be reached.

## Regression checkpoint
All58 runtime groups passed in255.1281seconds fixed60 simulation. Ten whole-layout planning checks and five vertical-programme checks pass. Source/export roundtrip for AST-CIR-005 has zero maximum coordinate deviation; source meshes have UVs. Runtime catalogue report identifies104 of157 designs present through1,506 whole-model instances, strictly presence rather than finished-space credit. Normal and effects-off player-height threshold, stairwell and eighteen-button panel views have now been inspected. The stairs and surrounding bypass are legible and the panel is readable; broad plain walls, lighting refinement and the unusual right-to-left button-column ordering remain unfinished presentation. This is acceptance of a functional circulation platform, not final resort art.
