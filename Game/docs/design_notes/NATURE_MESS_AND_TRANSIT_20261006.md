# Nature relaxation sanctuary, distinctive messes and transit

Date: 2026-10-06 UTC
User request provenance: Sentinel_a5319480c8ac8191bd34855264dcefc2
Status: project design notes only. No gameplay implementation or layout approval.

## Requested direction

The user wants a larger, relaxing nature sanctuary with birds, cute small animals and possibly a bear. Animals should contribute to a living, peaceful place rather than become a source of unavoidable guest disruption. Different messes should require distinct tools and strategies. Cleaning should involve reading the situation and protecting guest comfort, safety and routes, rather than applying one universal action to every incident. Animal behavior, incident generation, tool mechanics and guest/cleaning logic are deferred.

## Recorded lazy-river placement

The confirmed requirement is a floatable AFK lazy river and tubes in the D08 aquatic programme. The amenity audit assigns AME-111 and AME-112 to parent programmes D08_directory_01 (The grand aquatic pool) and D08_directory_08 (Gentle waters). These parent assignments do not identify a final loop, split between venues, boarding point, recovery point or tube count.

Reference programme envelopes are X−54…−8/Z−466…−398 for the Grand Aquatic Pool, and X+8…+54/Z+182…+250 for Gentle waters. They are historical destination allocations, not a lazy-river footprint. The production forward pool and the connected Gentle Waters district contain partial architecture; neither is a completed lazy river. The exact loop is still unresolved. The restaurant watercourse must not be presented as the river.

Sources:
- [Amenity audit, AME-109–112](../BLUEPRINT_AMENITY_SCOPE_AUDIT.md#ame-111-floatable-afk-lazy-river)
- [Machine audit](../../data/architecture/AMENITY_SCOPE_AUDIT.json), keys AME-111 and AME-112
- [Programme ledger](../../data/programme_ledger.json), D08_directory_01 and D08_directory_08; unresolved requirement “Lazy river, tube ride and slide park”
- [Aquatic vertical coordination](../AQUATIC_VERTICAL_COORDINATION.md), architectural requirements and hold points
- [Grand Pool connected section](../GRAND_POOL_CONNECTED_SECTION.md), unfinished wider-waterpark boundary

## Recorded tram placement and present evidence

The retained service Townline has longitudinal catchments at Z−432, −216, −72, +216 and +432 m. Its protected local atrium bypass runs through X/Z points (0,−72), (0,−56), (40,−52), (40,+52), (0,+56), (0,+72), passing on the starboard side of the hero tree. The recorded central express arrival is X5.5/Z−72, subject to a documented current revision.

A four-metre-wide support reservation around that local polyline has recorded checks for D02–D17. D01 separately retains axial support X−4…+4/Z−80…+80. These are floor-support reservations, not a working tram, final swept-cart clearance, boarding acceptance, or a verified complete deck-length line. The local polyline must not be extrapolated into undocumented full-length alignment or new stops. No current physical-tram implementation is claimed. No reviewed current source selects a unique operating deck/elevation, built track or complete deck-length alignment. The protected multi-deck pedestrian/transport bypass must not be read as a tram simultaneously running on every checked level.

The master also distinguishes the player's physical service tram/cart from future guest transit: guests use screened boarding vestibules and finite-time abstract travel; they do not board the player's physical tram. A nature-sanctuary visitor tram or animal ride is not an existing approved programme.

Sources:
- [Complete master content index](../master_source/MASTER_FULL_CONTENT_INDEX.json), body_index 136 (catchments), 138 (guest/service distinction), 564 (protected polyline and arrival)
- [Current master application](../master_source/MASTER_CURRENT_APPLICATION.json), historical implementation claims superseded; current trams/travel pending
- [Recorded route support checks](../ATRIUM_ROUTE_SUPPORT_CHECKS.json), D02–D17 and scope disclaimer
- [Route-check source](../../tools/validate_atrium_routes.py), line 7 defines the buffered local polyline; it was inspected, not run for this note
- [Spatial reservations](../../data/spatial_layout.json), D01_central_service_axis
- [Whole-ship layout finalization](../WHOLE_SHIP_LAYOUT_FINALIZATION.md), catchments versus offset public cores; these are distinct systems

## Nature allocations available for design consideration

D06, floor Y+27 m, is already the botanical programme deck. The following existing allocations offer a basis for developing the sanctuary character without inventing an extra room or silently relocating other programmes. All bounds are historical envelopes and must be fitted against actual routes, cores, hull and adjacent reservations before approval.

| Programme key | Existing destination | Historical X/Z envelope (m) | Present programme status |
|---|---|---|---|
| D06_directory_01 | The living grove | X−54…−8; Z−466…−398 | Architecture pending |
| D06_directory_02 | Cloud conservatory | X+8…+54; Z−466…−398 | Architecture pending |
| D06_directory_03 | Moss sanctuary | X−54…−8; Z−250…−182 | Architecture pending |
| D06_directory_04 | Botanical nursery | X+8…+54; Z−250…−182 | Architecture pending |
| D06_directory_05 | Canopy terrace | X−98…−52; Z−34…+34 | Partial authored architecture; full programme/final art unfinished |
| D06_directory_06 | Sheltered walk | X+52…+98; Z−34…+34 | Architecture pending |
| D06_directory_07 | Orchard gardens | X−54…−8; Z+182…+250 | Architecture pending |
| D06_directory_08 | Fern cathedral | X+8…+54; Z+182…+250 | Architecture pending |
| D06_directory_09 | The waterside grove | X−54…−8; Z+398…+466 | Architecture pending |
| D06_directory_10 | Sunset garden cafe | X+8…+54; Z+398…+466 | Architecture pending |

Sources: [programme ledger](../../data/programme_ledger.json), matching keys; [directory allocation evidence](../../data/reference/directory_allocations.json), matching keys; [amenity audit](../BLUEPRINT_AMENITY_SCOPE_AUDIT.md), D06 destinations. “Pending” means an existing programme needs architecture, not that the space is unallocated or available to erase.

## Recommendation, not an approved relocation

Develop the sanctuary as an expanded nature experience within the existing D06 botanical family, beginning with the Moss sanctuary and studying connections to the groves, conservatory and sheltered walk. It need not mean one enormous newly cleared footprint. Preserve each destination's purpose and all existing authored work. The Moss sanctuary and nursery occupy opposite sides of the fore-midship catchment; Orchard gardens and Fern cathedral form the equivalent aft-midship botanical pair. Living grove/Cloud conservatory and Waterside grove/Sunset garden cafe offer forward/aft nature anchors. Canopy terrace and Sheltered walk frame the central atrium, with Canopy already partially authored. These are candidates for a connected experience, not contiguous empty space. Exact expansion boundaries and connections remain a later coordinated design decision; no area, capacity, deck change or programme reassignment is made here.

Parent recommendation for the next tram study: use the busy D09 public/shopping promenade level (Y+52.5 m) as the primary candidate, with five longitudinal interchange catchments and lift connections to other decks. Keep the guideway and boarding areas separate from pedestrian routes. This is a recommendation, not an adopted deck or track. D06 remains an alternative study if the three-dimensional fit or transfer experience is better there; its quiet nature areas should not be cut by animal/guest/vehicle crossings. The recorded starboard atrium bypass is a protected alignment envelope, not proof that a vehicle clears existing lift cores or occupied architecture. Exact running elevation, core detours, station aprons and full-length clearances must be checked before adoption.

Birds and small animals could bring quiet life to planted pockets, with species-appropriate retreat areas and controlled guest-facing access. A bear remains an optional idea requiring a later decision about species, temperament, welfare, habitat scale and separation. Do not presume a free-roaming bear in the shared promenade or a safely usable enclosure from these notes alone.

Architectural considerations to carry forward: screened animal care and cleaning access; controlled animal/guest thresholds; secure retreats; washable service surfaces where appropriate; storage separate from food and water recreation; visibility without uncontrolled contact; quiet seating; and uninterrupted accessible guest circulation. These are review considerations, not new spatial reservations or installed geometry.

## Future mess-specific problem solving

Illustrative possibilities, not an implemented tool list:

- Leaves, seed husks and nesting litter: gentle collection, sorting and dry pickup that avoids scattering material or disturbing occupied nests
- Mud, tracked soil and wet footprints: isolate the affected patch, remove solids first, then use surface-appropriate wet cleaning and drying
- Animal droppings: targeted hygienic pickup, appropriate sanitation and contained waste handling; distinguish this from ordinary loose litter
- Sap or sticky fruit residue: a material-specific treatment and dwell/removal strategy rather than stronger force everywhere
- Fur, feathers and fine debris: controlled collection suited to the surface and airflow, avoiding contamination of food or water
- Spilled water or algae-prone edges: contain the slip exposure, clean with a compatible method, dry or mark the surface and verify that the route can reopen

Future incidents should make tool choice, sequence, location and timing meaningful. Animal-care access and ways to move or distract an animal safely can be explored as future game-design options, with room for the gentle comedy the owner described.

Guest comfort should be part of solving the problem: keep a usable bypass open, work in small contained sections, screen noisy or unpleasant servicing where possible, avoid moving mess into another guest route, and reopen only when the hazard is resolved. Signs or temporary closure alone should not strand guests or obstruct evacuation. Where a safe bypass is impossible, a later operating plan must address timing and alternative access rather than treating inconvenience as unavoidable gameplay.

## Deferred decisions and scope boundary

Later work must decide habitat/species suitability, whether to include the bear, the exact sanctuary expansion, lazy-river alignment/boarding/recovery, complete tram route and stops, incident taxonomy, cleaning tools, animal/guest behavior and safe route management. It must reconcile these with the existing capacity, destination ownership, accessible circulation, service network and protected transit envelope.

This note changes none of those systems. This is documentation only; no geometry, gameplay, programme ledger or capacity is changed. All examples above remain notes for future design and implementation.
