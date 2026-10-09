# Cinema 5 read-only receiving audit

Audit date: 2026-10-09 UTC. Programme D11_directory_06. This audit read the source, current retained floor meshes, source/core exported triangles, current builders, and applicable master/reference documents. It did not edit the project or package, run Godot/Blender, import models, build, or touch backup processes. Root owns integration and runtime checks.

## Result and immediate decisions

1. Preserve the existing 258 m² D11_aquatic_cinema_interface. The source's rectangular 3600 m² floor proposal overlaps it and cannot be added wholesale.
2. Add only the 3342 m² missing room floor below. Its union with the retained cover supports all 106 exported datum-contact nodes.
3. The initial straight west connector reaches retained floor but crosses the intact core wall. It is rejected. Use the aft-mouth dogleg below, preserving AST-CIR-005_spine_core.
4. Keep the east opening physically closed until a separately supported route exists. Root's reversible full-aperture panel has supported footing and does not obstruct the internal cart route.
5. No source overhead-contact or retained upper-floor collision blocker was found. This does not certify structural load paths, occupied species, driven carts, final artwork, media, sound, or lighting.

## Verified inputs

- Source package: /workspace/shared/Astraea_remaining_e_intake_20261009_0604/cinema5/02_cinema_5
- Project: /workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4/Game
- All 97 manifest entries match both byte count and SHA-256.
- Delivered GLB SHA-256: 803ddfe94bc772a001a8d07d5c922c8b845262defb7d5fc3a0ce2242ef623548
- Editable native SHA-256: b33d8f86334f29c7fc1ec1b16e357226777da8bc50b77688e7339f5caf23f179
- Placement: identity XYZ metres; floor Y69.5; source top Y76.83999664336443.
- Source bounds: X[11.1249998212,60.8749992251], Y[69.4999964237,76.8399966434], Z[244.0799969509,315.9199877903]. The 3.6-micrometre below-datum discrepancy is float export error, not a real protrusion.
- Owner snapshot: 303 original + 116 previously received + 2 Salon + 2 Stillroom = 423 retained floor owners.
- Input hashes are recorded in cinema5_receiving_geometry.json. Root's new candidate is not counted as a retained prior owner.

## Receiving floor and preserved cover

All polygons below are world XZ metres. New slab top Y69.5; thickness 0.24 m; underside Y69.26. The old aquatic cover remains top Y69.5, thickness 0.4 m, underside Y69.1.

Preserve D11_aquatic_cinema_interface exactly:

```json
[[11,244],[54,244],[54,250],[11,250]]
```

Area: 258 m². It is a real existing structural cover, not a reservation rectangle.

Missing-only Cinema 5 receiver:

```json
[[11,316],[61,316],[61,244],[54,244],[54,250],[11,250]]
```

Area: 3342 m². It shares 49 m of boundary with the retained aquatic cover and has no positive-area same-datum overlap. Do not flatten or replace the older 0.4 m cover merely to make its underside match the new 0.24 m slab.

The entire 3600 m² allocation is valid as the union of old and new floor, not as one new owner. Exact unioned datum-contact area is 1413.6863506247403 m² across 106 nodes. No contact lies outside the allocation. The old cover supports 8.72860068335945 m² of unioned source contact, involving E_outer_west0, E_outer_south, and E_roofbearing0_0. The remaining source contact is supported by the new receiver. Small overlaps between the individual source contacts explain why their summed areas differ from their union.

No positive-volume source penetration into retained floor slabs was found. Corrected receiver/connector have no D11 protected-void overlap. Positive XZ projection over lower floors is not a clash across different datums.

## Connected west arrival: use the dogleg

The actual AFT_MIDSHIP_PUBLIC_CORE.json places AST-CIR-005_spine_core.glb at world [0,0,272]. Its source contract has portal_levels=[] and portal_sides=[]; the D11 lateral wall is intentionally closed. The original 12.8 m² X7.8–11, Z278–282 connector is geometrically adjacent to the core floor but cannot establish a usable lateral route through that wall.

Initially screened L-connector:

```json
[[7.8,278],[11,278],[11,297],[4,297],[4,293],[7.8,293]]
```

Area: 76 m². connection_to: D11_aft_route. It has a 4 m genuinely open contact on X4, Z293–297, and 14 m of adjacency to the closed core boundary. The latter is not an open portal.

Edge-safety refinement recommended before final adoption: fill the 3.8 m² slit at X4–7.8, Z292–293, preserving the existing core wing guard. This avoids an exposed one-metre floor slit on the crosslink side. The refined connector is:

```json
[[7.8,278],[11,278],[11,297],[4,297],[4,292],[7.8,292]]
```

Area: 79.8 m²; 5 m of contact to D11_aft_route. The extra strip is missing-only floor, not an alteration to the core. With this refinement, total added floor is 3421.8 m². If root retains the 76 m² option instead, that slit-facing edge requires a physical guard. Other exposed connector edges also remain subject to the existing receiving-edge policy.

Recommended route, all at Y69.5:

```json
[[0,295],[9.5,295],[9.5,280],[14.55,280]]
```

Actual exported Cinema and core triangles clipped to Y69.56–71.4 were used for obstacle checks. Radius 0.3, 0.65, 1.0, 1.5, and 1.6 m sweeps have zero source/core obstruction and zero unsupported floor-sweep area on the 76 m² L. The added slit fill only enlarges that support and does not affect the route. Minimum centerline obstacle distance is 1.6179998856 m, including the 2 mm allowance used for thin vertical faces.

Radius 1.7 m does not pass: it grazes E_outer_west_openingpier1, CORE_BATCH_ivory_enamel, and CORE_BATCH_champagne_metal. The local throat between core wall X7.88 and Cinema portal pier X11.125 is 3.245 m. Do not convert the narrower static pass into a claim that all species or the source's 3.4 m-diameter planning envelope can pass. The actual cart is much narrower, but its driven turn, handle/user stance, and loose load still need runtime evidence.

## East opening safety closure

No existing Y69.5 floor is adjacent to the east aperture. The nearest retained same-datum floor to its exterior query area is 28.66 m away, and provides no usable continuation. The source alone has an open fall edge.

Root's reversible panel bounds, independently screened:

- X60.46–60.64
- Y69.5–72.16
- Z277.88–282.12

The original opening is Z277.9–282.1, sill Y69.5, header Y72.15. Tiny perimeter overlap closes float cracks while retaining the original jamb/header meshes. The panel footprint is 0.7632 m², all supported by the new receiver. It has no intersection with any documented internal route. The nearest, the 1.7 m-radius east level-cart sweep, clears it by 1.31 m.

Keep the panel a root-owned reversible receiving closure, with matching visible geometry and collision. It is not a new door identity, outside platform, capacity allocation, or working guest exit.

## Interior route and rake interface

All five documented source level routes pass the independent actual-triangle band screen at their specified radii: left/right transfer cart, level guest cart, projection body, and screen-service cart. These tests only include the source itself; the separate core check above was necessary to reject the original arrival.

Source rakes and contacts:

- 10 rows, tier tops Y69.62 to Y71.96, with 20 existing place identities per row.
- Two return ramps: left X16.5–19.9, right X52.1–55.5; Z262.2–292; rise 2.46 m over 29.8 m, nominal 1:12.113821.
- Top landings span Z292–298 at Y71.96.
- Rear crossing spans X16.5–55.5, Z295.5–299 at Y71.96.
- Both ramp-to-landing joins contact at Z292; both landings overlap the rear crossing in plan and volume.
- Keep the local ground-supported tiers, center steps, ramps, and landing meshes. The new common floor belongs below them at Y69.5; it must not replace or flatten the rake.
- Nominal ramp width is not usable clear width after edge guards. The documented 1.7 m radius is used for level routes and has not been accepted on the elevated ramps.

All 200 expected stable IDs D11_directory_06_R01P01 through R10P20 are present, comprising 198 retained AST-CUL-003 seats and two replacement level transfer places. The transfers retain R01P01 at [22,69.5,259.6] and R01P20 at [50,69.5,259.6]. They add no capacity. Their 1 mm visual floor markers should not become raised collision obstacles.

The independently rerun finite projection-frustum check has zero source triangle hits, under its documented exclusion of the screen/content/projector. Occupied heads, species dimensions, sightline comfort, a running abstract-short programme, and real audio remain separate gates.

## Overhead and source-contact checks

116 simple-convex contact checks passed, using actual exported vertices and intersecting convex half-spaces. This is valid for the selected box/cylinder/prism members, not an arbitrary concave-mesh or structural engineering certificate. Checks cover:

- Roof beams against both bearing posts
- Ceiling against all six perimeter wall segments
- Fan ribs against their acoustic shoulders and opposite rib at each peak
- Fixture mounting stems, bodies, and lenses
- Screen lintel/backrails and projector support assembly
- Both ramp/landing and landing/rear-crossing interfaces

No separated overhead member was found. Eleven declared decorative support links have small actual offsets: seven original-still pieces sit 0.017504 m from the screen, screen notice 0.030004 m from screen, film lettering 0.018999 m from its notice, and two speaker grilles 0.005010 m from speaker bodies. These are visual offsets, not demonstrated physical contacts; they do not block receiving but should not be counted as touching structural support.

The retained D12_directory_08_room_floor (Reading Nooks) overlaps 106.2961229453384 m² of the Cinema allocation in plan. Its underside Y77.76 leaves 0.9200033566355756 m above the Cinema roof. This is the actual partial upper-floor overlap, not proof of a residential slab over the entire room.

## Mesh, lighting, and visual evidence

- 1469 mesh nodes, 209664 triangles, 12 embedded images; no external image URIs.
- All primitives have POSITION, NORMAL, and TEXCOORD_0. No non-finite components.
- Normal lengths range 0.9999998808–1.0000001192.
- Twelve degenerate triangles are confined to E_film_title lettering; no support or route mesh is implicated.
- No preview/QA floor is present in the actual GLB.
- 25 punctual source lights; source intensities/ranges need the shared bounded receiver adapter and budget. Raw authoring light values are not ready runtime settings.
- Master-current application, relevant spatial/architecture/acceptance requirements, source reference application, and original theater reference pixels were inspected. Source arrival/ramp images were directly viewed. Their preview floor is omitted from the source model and does not establish live receiving.
- The source visually preserves the low single-deck cinema identity, paired rakes, deep screen focus, side aisles, and ceiling frame. No extra exterior opening, balcony, deck, programme, or guest capacity is inferred from the grand-theater reference.

## Root-owned runtime reports, kept separate (updated 06:16 UTC)

Root reported the initial actual-world candidate test found four capsule-clearance hits at X7.5–8.0, Z280 against the retained core; all 106 floor contacts and the other 928 route samples passed. The failed straight-route receipt was retained. This agrees with the later source/core diagnosis; the early source-only clear route did not include the neighboring core.

The revised candidate's actual-world static test PASS was reported by root: 106 source contact checks and 1018 static route samples. That pass uses the 76 m² L; the 3.8 m² slit correction giving 79.8 m² remains recommended and unimplemented. Root has built the reversible east panel and reported reviewing five bounded Godot views under the existing eight-active-light budget, without claiming final art acceptance.

The subsequent player test FAIL was reported after 62.913 m / 1307 frames, at (21.99594,69.5,258.1024). Independent barycentric intersection against the actual source triangles identifies E_transfer_place_marker at that exact XZ, with top Y69.50100354006281 and bottom Y69.50000354001531. It retains source_place_id D11_directory_06_R01P01. Its exported metadata explicitly states role=visual_transfer_marking and collision_policy="visual floor marking; exclude from collision". The current candidate builder attaches static collision to all 1469 source meshes without honoring that exclusion.

This is a receiver collision-policy omission rather than missing base-floor coverage. Preserve the two marker meshes and stable place IDs visually, exclude their collision as the source instructs, and rerun the affected test. Do not paper over the issue by accepting a paint/marking mesh as a new structural support owner. The actual base floor remains Y69.5.

The combined retained-section test did NOT RUN because the command sequence stopped at the player failure. Root reports 62 accepted installations remain; Cinema 5's default hookup is still unaccepted. The audit did not run any of these engine tests. Root must read new matching receipts after the marker-collision and slit corrections before claiming the affected checks pass.

## Deliverables and reproducibility

- cinema5_receiving_geometry.json: hashes, floor polygons, contact bounds, source checks, 116 contact results, rejected and corrected route screens, panel screen, and root-reported runtime state.
- audit_cinema5_static.py: source-only manifest, contacts, owners, route bands, attributes.
- cinema5_contacts.py: simple-convex member contacts and retained cover support.
- cinema5_connector_audit.py: actual core/source triangle dogleg and east-panel screen.
- finalize_cinema5_audit.py: independent finite frustum, stable place identity checks, and final recommendation reconciliation.

All scripts are in the audit scratch directory. They read production/package inputs and write audit results only. The audit leaves the source, core enclosure, original floor owners, engine, controls, capacities, and backup processes unchanged.
