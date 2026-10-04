# D11: Grand Lantern Theater and six cinemas

Species design now follows [SPECIES_CANON.md](SPECIES_CANON.md). The six canonical species include Humans; existing legacy body/seat tests are not acceptance of new rigs. Preserve the 3,400 real seats while checking actual new body envelopes, including Munko four-arm contact and Baelin support. No species demographic split or new seat count is implied.

This is an integrated main-ship module, `scripts/auditoriums.gd`, using the existing ship's shared box/cylinder/sphere meshes, material palette, collision helpers, static batching and local light budget. No separate prototype scene, purchased assets, licensed films or copied art are required.

## Capacity and geometry

| Venue | Exact numbered places | Center x/z | Registered width × depth × height |
|---|---:|---|---|
| Grand Lantern Theater | 2,200 | -76 / -190 m | 84 × 150 × 22 m |
| Cinema 1 | 200 | +36 / -432 m | 50 × 72 × 8.25 m |
| Cinema 2 | 200 | +36 / -280 m | 50 × 72 × 8.25 m |
| Cinema 3 | 200 | +36 / -128 m | 50 × 72 × 8.25 m |
| Cinema 4 | 200 | +36 / +128 m | 50 × 72 × 8.25 m |
| Cinema 5 | 200 | +36 / +280 m | 50 × 72 × 8.25 m |
| Cinema 6 | 200 | +36 / +432 m | 50 × 72 × 8.25 m |
| **Total** | **3,400** | | |

The theater has three raked audience levels: Lantern Stalls 740, First Gallery 740 and Crown Gallery 720. Each has four ten-chair blocks per full row, with an additional twenty-chair central row on the two lower levels. There are 2,200 individually positioned five-part chairs and corresponding floor anchors. Each cinema has ten rows of twenty chairs, split into two ten-chair blocks, for another 1,200 actual chairs.

The theater's registered footprint is **x -118 to -34 m; z -265 to -115 m**. Walls and decorative door trim have small construction thickness outside the registration box. Threshold floors are clamped to the 240 m beam; the port service threshold reaches x -120 m, never beyond it. All seven registered envelopes lie within the actual tapered hull plan and avoid the main central atrium.

The theater has a 36 m-wide stage and a 16 m-clear proscenium. The ceiling is 22 m above D11. Tier base floors are **0 / 8.5 / 14.5 m** relative to D11, aligning with the canonical D11 / D12 / D13 floors at world y 69.5 / 78 / 84 m. The highest seat floor is 16.54 m above D11. The raised rear galleries, open lower chamber, balcony noses, slender supports and full-height stage provide a genuine vertical volume.

Cinema ceilings terminate at 8.25 m, below D12's floor at +8.5 m. Their screen faces, cornices, titles and ceiling fixtures remain inside that height budget.

## Entry, care and circulation

- Main theater entry: **(-34, 0, -126)**, repeated at local y **8.5** and **14.5** for entry from D12 and D13
- The theater's east wall has genuine holes at all three levels, rather than a high decorative door pasted onto a solid wall
- Nominal theater aperture: 5.2 m; cinema aperture: 4.8 m. Jambs reduce these by about 0.22 m, still comfortably exceeding the 3.4 m cart requirement
- Theater side aisles and upper side galleries have generous cart clearance; the lower foyer connects both sides ahead of the stair enclosure
- Three theater lift landings: **(-41.5, 0, -126)**, **(-41.5, 8.5, -126)** and **(-41.5, 14.5, -126)**, before adding the D11 world elevation
- Theater lift car center: **(-41.5, 0, -121)**. The 5 × 5 m platform is an actual `AnimatableBody3D`, travels at 0.72 m/s, and dwells eight seconds at each stop. Fixed landing gates open only when the platform is stopped at that level
- Gallery lift joins `ship_lifts` for the main game's existing custom pause integration. Its moving car and gate meshes use the renderer's existing moving-mesh exclusion flag
- A separate switchback stair connects all three levels, with 3.2 m clear flights, eight-meter half-flight runs and risers no greater than 150 mm. Stair openings are cut out of the upper rear gallery floors
- Theater tier gangways are inclined **collision** surfaces, not merely rotated visuals. Their main rise is approximately 1:12.08, with a three-meter transverse aisle between row groups
- Outer rake guards prevent a fall onto the adjacent level side gallery. A genuine 1:12 ramp connects the theater's stage floor
- Cinema entrances: **(11, 0, cinema center z + 25)**. All have rear foyers, level side circulation, raked middle/outer audience aisles and rear return ramps
- Viewing/transfer bays are identified at the front landings. They do not increase the venue's admission limit; accessible use substitutes for a numbered place

`anchors`, `activity_anchors` and `care_anchors` are deliberately a small set of level side-aisle and foyer positions. They do not send a generic flat-floor crowd through raised seating. Care residues can stay near the actual visitor instead of being snapped to the room's center z.

`circulation_route(room, target)` returns a path beginning at the actual door and ending at a supplied level amenity anchor. For cinemas, crossing to the far side occurs behind the audience return ramps and ahead of the projector booth. An unsafe central audience target is redirected to the foyer anchor. This helper is for ordinary amenity routing; it is not a complete reserved-chair audience scheduler.

## Original performance and film program

The Grand Lantern's original live-light production is **A Thousand Small Worlds**, with a sculpted mechanical orrery, twelve suspended light-worlds, proscenium curtains, practical stage fixtures and a procedural moving constellation backdrop.

The six cinema programs are original real-time abstract shorts:

1. **The Tide Remembers**: layered moving ocean-light ribbons
2. **A Map of Small Suns**: slowly evolving stars and small luminous worlds
3. **The Patient Orchard**: growing stems and glowing canopies
4. **Letters from the Quiet Moon**: a shaded moon and drifting paper forms
5. **The Last Lantern Home**: a breathing city of lit windows
6. **Clouds Borrow the Sea**: drifting, layered cloud currents

These are locally generated shader animations, not full feature-length narrative films. Each screen has its own title, visual treatment, palette, original program description, speakers and projector booth. The `TIME`-driven shader survives static mesh batching; no mesh animation or per-seat script is required.

## Integration contract

```gdscript
const Auditoriums = preload("res://scripts/auditoriums.gd")

# Replace D11's legacy miniature theater / paired-cinema definitions.
all_rooms.append_array(Auditoriums.register_rooms())

# Specialized rooms bypass build_public_shell / generic furniture / thresholds.
Auditoriums.build(self, room)

# Use this before the generic door -> center -> anchor shortcut.
var path: Array[Vector3] = Auditoriums.circulation_route(room, target)
```

- Numbered audience places use **`entertainment_seats`**, never the meal system's reserved `seats` key
- Capacities are explicit in `entertainment_capacity`; `capabilities` is `amenity, culture`
- Every construction position adds `room.center`, including its y component. A dependency room rendered while visiting D12/D13 can therefore be shifted by the main ship's canonical deck-elevation delta
- Registration anchors are initially D11-local. If the main ship transforms registered room data, transform anchor/door arrays consistently with `center`
- Suppress generic D11 shell furnishing, side service furniture, stock islands and hull-gallery props inside the seven specialized envelopes
- Remove intermediate D12–D14 slab/ceiling geometry throughout the theater's real footprint, and render its dependency geometry from the upper entrances
- The parent ship remains responsible for hull construction, deck dependency selection, neighboring room relocation, main-street connection, generic crowd routing and light/sector activation

## Focused verification

Performed against the actual module with Godot **4.6.3 stable**:

- Headless script compilation passed
- Registry invariant check passed: seven venues, 2,200 + 1,200 = 3,400 capacity, exact tier counts 740 / 740 / 720
- All 3,400 seat anchors are unique within their venue and inside its registered envelope
- No auditorium has the meal-only `seats` key
- Maximum seat-floor height: 16.540001 m; cinema shell height: 8.25 m
- All 28 supplied amenity paths begin at their actual venue door, end at the requested anchor, and remain at the room's floor elevation
- Seat-anchor world extents: x -104.470 to +48.460 m; z -448.000 to +437.600 m

These are focused count, bounds and path-contract checks. Integrated physics route sweeps, cross-deck rendering, lift/cart riding and actual render inspection still belong to the main-ship acceptance pass. The existence of 3,400 actual chairs does not claim that 3,400 guests are simultaneously seated or ticketed by the life simulation.

### Integrated D11 clearance pass

After the parent integrated the module, the existing `spatial_mainship_tests.gd` flow was run against **the actual `main.tscn` and `game.travel_deck(11)`**, limited to D11. A temporary copy added open-auditorium portal and care-route cart sweeps; the copy/result are under `/tmp`, not a new ship scene or benchmark.

- All seven auditorium arrival routes passed the player sweep
- All seven open auditorium entrance apertures and their turning landings passed both player and 1.14 × 1.4 × 0.77 m cart query-shape checks
- All 28 auditorium care/amenity paths passed the cart query-shape sweep
- Across the integrated D11 deck, 822 route-floor samples had no missing floor; all 38 cleaning positions had a clear cleaning stance; all three central crossing checks passed
- The complete D11 sample included 19 entrances/turning landings (seven custom plus twelve ordinary), all clear
- One unrelated legacy integration blocker was reported to the lead: the cultural gallery's route at z=324 crossed a stock cabinet at (-49, 0.5, 324.6). No auditorium route was blocked

The integrated pass is still a static shape-sweep check, not a claim of live spring-cart driving, lift riding or visual approval. While D11 is active, leaving either upper east portal also requires the lead's exterior upper-deck landing/dependency geometry or deck transition; the local threshold extends only 1.4 m beyond the auditorium wall.
