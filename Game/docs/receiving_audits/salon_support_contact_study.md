# Listening Salon / Tidal receiving-contact study

Read-only fictional game-architecture fit study. No Blender run, native/GLB edits, scene edits, engine run, or construction was performed. All coordinates are world engine XYZ, Y up, metres. This establishes geometric support paths, not real-world load capacity or certification.

## Recommendation

Use a clearly named composite cap successor whose visible skin preserves `WP07_opaque_ceiling_cap`, with five hidden longitudinal receiving strips at X = -45.8, -42.2, -28.75, -12.4, -8.55. Integrate the strips inside the cap and terminate their upper faces at Tidal underside Y83.76. Do not independently superimpose an unnamed structural layer and then count the decorative cap as its support.

Two source-derived alternatives are available:

1. **Wall-supported composite cap:** cleanest visual preservation and simplest geometric graph. Cross-ribs bear on exact existing perimeter wall tops at Y83.60. Longest transverse clear interval is 44.93 m; fictionally authored ship composite action must be explicit. No new object below 83.50 is needed.
2. **Wall + retained-arch crown support:** improves the graph using the twelve piers, twelve capitals, and six existing curved fascias. Small profile-matched crown saddles connect fascias at about 83.48 to the composite cap. This avoids exposed 0.85 m pier continuations. Longest cross-rib clear interval becomes 28.065 m, while each existing arch remains 23.12 m clear between capital-top bearing edges. The 20–21.7 mm saddle band below the cap needs a close visual preservation check. The source fascia material role is ivory_enamel, not a verified structural role, so explicitly name/document a composite arch/cap successor instead of silently treating decorative metadata as certification.

## Verified inputs and coordinate mapping

Salon package: `/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4/BlenderCatalogue/assets/remaining_sections_20261009/E/01_listening_salon`.

- `exports/D12_directory_03.glb` SHA256: `bea516d8227f76ba5c1436d225392877a942679a2c7409e3bcbc3e17cb94f36c`
- `source/D12_directory_03.blend` SHA256: `0ded1f518e6fe5ce9c9fcf53527010f64dda910f1d2dfe9087c040b4d5a5fc66`
- Both hashes match retained `qa/INDEPENDENT_NATIVE_EXPORT_QA.json`; its native/export bound parity passes. Native source descriptions and saved inspection reports were read; the native file was not opened in Blender in this study.
- Native Blender local(x,y,z) maps to GLB local(x,z,-y), then add(-31,78,-324), from `docs/PLACEMENT.json`.
- Actual transformed GLB triangles, not bounds alone, supplied the top-contact polygons below. Exact floating-point coordinates are in `salon_support_top_contacts.json`; displayed dimensions below round to micrometres/millimetres as appropriate.

## Full-height retained walls: exact horizontal top-face footprints

All five wall meshes start at Y78.00 and have flat tops at Y83.5999999046, nominal 83.60. The flat top is 25 mm inset from the mesh AABB because of the bevel. These are contact rectangles, not AABB rectangles.

| Actual GLB/native object ID | Flat-top X interval | Flat-top Z interval |
|---|---|---|
| WP07_west_acoustic_wall | -53.975 .. -53.465 | -357.975 .. -290.025 |
| WP07_north_wall | -53.700 .. -8.300 | -357.975 .. -357.465 |
| WP07_south_wall | -53.700 .. -8.300 | -290.535 .. -290.025 |
| WP07_east_wall | -8.535 .. -8.025 | -321.975 .. -290.025 |
| WP07_east_wall.001 | -8.535 .. -8.025 | -357.975 .. -326.025 |

`WP07_portal_head` also has a top at 83.60, X[-8.535,-8.025], Z[-325.975,-322.025], but its bottom is 81.40. It is a lintel over the 4 m portal, not a floor-to-cap column. Prefer side-wall contact stations outside Z[-326.025,-321.975] for the cleanest graph.

`WP07_opaque_ceiling_cap` occupies Y83.50..83.75. Its total AABB is X[-53.725,-8.275], Z[-357.725,-290.275]. Its actual flat horizontal top is X[-53.700,-8.300], Z[-357.700,-290.300]. Preserve its visible underside, boundary bevel, material, and room-facing surfaces. The existing wall tops already lie 0.10 m inside its vertical envelope; integrating receiving ribs there does not require room cuts.

## The twelve piers and capitals

There are no separate floor-to-Y83.50 interior columns in the retained source. The twelve named gallery piers are floor-to-arch piers:

- Every `WP07_bay_{b}_pier{suffix}`: Y78.00..82.52; actual flat top X=cx±0.20, Z=cz±0.23; area 0.184000 m².
- Matching `WP07_bay_{b}_capital{suffix}`: Y82.35..82.65; actual flat top X=cx±0.44, Z=cz±0.425; area 0.748000 m².
- Each pier top intersects its matching capital solid over the full 0.184000 m² flat top. Every capital top intersects its matching curved fascia solid over approximately 0.122965 m². These are measured source contact/interpenetration footprints, not inferred solely from names.

| Bay | Suffix | cx | cz | Matching fascia |
|---|---|---:|---:|---|
| 0 | none | -49 | -298 | WP07_bay_0_curved_fascia |
| 0 | .001 | -25 | -298 | WP07_bay_0_curved_fascia |
| 0 | .002 | -49 | -312 | WP07_bay_0_curved_fascia.001 |
| 0 | .003 | -25 | -312 | WP07_bay_0_curved_fascia.001 |
| 1 | none | -49 | -317 | WP07_bay_1_curved_fascia |
| 1 | .001 | -25 | -317 | WP07_bay_1_curved_fascia |
| 1 | .002 | -49 | -331 | WP07_bay_1_curved_fascia.001 |
| 1 | .003 | -25 | -331 | WP07_bay_1_curved_fascia.001 |
| 2 | none | -49 | -336 | WP07_bay_2_curved_fascia |
| 2 | .001 | -25 | -336 | WP07_bay_2_curved_fascia |
| 2 | .002 | -49 | -350 | WP07_bay_2_curved_fascia.001 |
| 2 | .003 | -25 | -350 | WP07_bay_2_curved_fascia.001 |

Exact capital/fascia intersection polygons, including bevel-shaped ends, are in `salon_support_graph_contacts.json`. Each left bearing occupies approximately X[-49,-48.56], Z=cz±0.14 with bevel-clipped outer corners; each right bearing approximately X[-25.44,-25], same Z width. Do not claim the whole 0.748 m² capital top contacts the fascia.

Low quiet-bay bearings end at 81.60; arrival-rest roof bearings end at 82.00. Neither is a cap-level support. Furnishings and acoustic fins are excluded from the receiving graph.

## Alternative A: wall-only composite-cap graph

Suggested graph: Tidal floor underside -> five longitudinal receiving strips -> transverse cap-integrated cross-ribs -> existing west/east wall tops, with north/south wall-top end bearings -> retained floor-level wall feet at Y78. Root still owns the Salon receiving floor; this delivered Salon GLB intentionally excludes its preview floor slab.

Concrete dimensional starting point for root construction:

- Five longitudinal strips: X=listed centre±0.17, Y83.60..83.76, Z[-358.30,-289.70]. This is a 0.16 m hidden-depth successor member rather than a continuation of the old 0.68 m-deep member through the room. Its 0.15 m overlap with the old cap is intentional composite integration; its top bridges the 10 mm cap-to-floor gap.
- Transverse cross-ribs: X[-53.70,-8.30], Y83.60..83.76, Z=station±0.17. At each unbroken wall station, actual west/east top bearing overlap is 0.235×0.34=0.0799 m² per end. Keep the station away from portal-head breaks if using only full-height walls.
- Example wall-only stations: Z=-351,-343,-335,-327,-319,-311,-303,-295. Largest longitudinal centre spacing 8 m, clear distance between 0.34 m-wide ribs 7.66 m. North/south wall tops support the end strips as well.
- Longest transverse clear wall-top interval: -53.465 to-8.535 =44.93 m. West/east wall centreline spacing 45.44 m. A full unsplit longitudinal span between north/south inner wall-top edges would be 66.93 m, so merely adding five uninterrupted strips is a visibly weaker support graph than adding cross-ribs.
- North/south strip contact area for each 0.34 m-wide strip:0.34×0.51=0.1734 m²; all five strip X footprints fit the respective wall-top horizontal extent.
- Retained longitudinal source end faces lie at Z=-358.30 and-289.70, Y83.08..83.76; the new strip ends share 0.16 m of face height. Preserve those retained members, making the changed depth explicit in the successor definition.

## Alternative B: wall + crown-saddle composite-cap graph

Suggested graph: Tidal floor -> same five receiving strips -> cross-ribs at the six existing fascia Z stations -> wall bearings plus crown saddles -> retained/composite curved fascia arches -> existing capital contacts -> existing piers -> their feet at Y78.

Use a saddle for each of the six named fascias, with plan patch X[-37.4,-36.6], Z=cz±0.10. This lies safely inside the fascia's actual central top width of approximately cz±0.12, avoiding its side bevels. The actual fascia is triangulated, not an analytic smooth arch; the central patch is two planar slopes meeting at X=-37:

- At X=-37, upper surface Y=83.480000019.
- At X=-38 and-36, upper surface Y=83.475694656.
- For X in[-37.4,-36.6], match lower saddle surface to Y=83.480000019 -0.004305363×abs(X+37).
- Lower saddle surface therefore ranges 83.478277874..83.480000019. A flat bottom at 83.48 would touch only a ridge and falsely claim a finite contact patch.
- Top of saddle can be 83.60, intersecting the intended composite-cap core. Its plan contact is 0.8×0.2=0.16 m²; true sloped area is negligibly larger.
- The saddle's exposed-height band between fascia top and cap underside is 20.000..21.722 mm. Preserve the fascia underside and the opaque cap underside. Small band visibility must be reviewed from retained arrival/activity/quiet cameras; do not claim pixel-identical preservation without that check.

Cross-ribs at Z=-298,-312,-317,-331,-336,-350 yield 14 m maximum longitudinal support-centre spacing (13.66 m between 0.34 m rib edges),5 m between close bay ends, and 7.72 m from end-wall centrelines to the nearest fascia stations. With the 0.8 m-wide crown patch:

- west-wall-top inner edge to crown patch left edge:16.065 m;
- crown patch right edge to east-wall-top inner edge:28.065 m (largest transverse interval);
- each arch capital-top inner-edge clear span:23.12 m, bearing centrelines 24 m apart;
- pier centre rows along Z are spaced 14 m and 5 m, not a new invented grid.

The three `WP07_bay_{0,1,2}_acoustic_vault` meshes have maxima 83.46, with no finite horizontal top face at that maximum; their crowns are 20 mm below the fascia crowns. They are not interchangeable targets for the 83.48 saddle formula. If using a vault contact instead, match its own triangle surfaces and 40–41.7 mm approach envelope separately.

## Tidal floor and retained-member contact targets

Actual inspected successor GLB: `/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4/BlenderCatalogue/assets/tidal_garden_receiving_successor_20261009/exports/architecture_floor_winding.glb`.

Node `TG_Batch_2` carries `source_part_ranges` for `TG_InnerDryGardenBase_0` and `D13_PairedBankStreet_1`. Actual bottom triangles over the Salon footprint establish these continuous rectangles at nominalY83.76:

- `TG_InnerDryGardenBase_0`: X[-29.05,-8.20], Z[-358,-290].
- `D13_PairedBankStreet_1`: X[-46.05,-41.95], Z[-358,-290].

All five proposed receiving strips contact one of these exact existing floor strips across their full 0.34 m width: -45.8/-42.2 under PairedBankStreet, -28.75/-12.4/-8.55 under InnerDryGarden. Do not treat the entire Salon plan as one uninterrupted Tidal slab. Other Tidal room floors have separate source identities and were not needed to establish these five contacts.

The retained source `PLAN.json` explicitly interrupts `TG_BaseLongitudinal_{x}_1` at Z=-358.30 and starts `TG_BaseLongitudinal_{x}_2` at Z=-289.70 for each of the five X centres. These are 0.34 m wide,0.68 m deep at centreY83.42, giving Y83.08..83.76. The Salon gap is 68.60 m. Reintroducing that whole original section through this gap would cross acoustic/vault/fascia/opaque-cap geometry; do not insert it unchanged.

Exact inspected Tidal bottom polygons and source GLB hash are in `tidal_actual_floor_over_salon.json`.

## Conflicts and required root checks

- Only 10 mm exists above the old cap. A separate conventional-depth beam layer entirely above it will not fit. Cap-integrated shallow receiving members or an explicit composite successor resolve the geometric ownership, without moving the Tidal floor or cutting visible rooms.
- The arch-crown alternative is geometrically connected through real retained objects, but the source's decorative material tags do not establish their structural purpose. A named fictional composite arch/cap assembly should record the intended graph.
- None of the gallery piers reaches cap height. Direct new risers from capital 82.65 to cap 83.50 would be 0.85 m tall and are not automatically concealed. The crown route avoids that issue.
- All source wall, capital and cap bevels matter. Use the measured flat/sliced contact regions, not full AABBs; a flat crown saddle only touching an apex is insufficient.
- Where receiving ribs overlap the old cap by design, classify them as part of the successor rather than reporting an unexplained self-collision or claiming they float above it.
- Preserve room openings, fascia/vault visible faces, furniture, source place IDs and routes. No portal cut or new room post is needed for either alternative.
- Source-preservation, composite-contact graph, actual exported geometry, normals, collision ownership and visual review remain construction acceptance checks for root. Missing real-world load certification is not a blocker to this fictional geometric treatment, and none is claimed here.

## Machine-readable study sidecars

All beside this report in `/workspace/scratch/375c2e438292/`:

- `salon_support_top_contacts.json`: exact transformed top-face geometries and areas, object bounds and source hash.
- `salon_support_graph_contacts.json`: measured pier-capital and capital-fascia contact patches, source-plane Ys and areas. Slice vertices rounded to 1 micrometre.
- `salon_support_triangles.json`: extracted relevant source triangles for the measured arch/cap/pier objects; inspection data only.
- `tidal_actual_floor_over_salon.json`: actual successor floor bottom footprints over the Salon.
