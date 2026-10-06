# AST-CUL-005 Grand Lantern Theater: first source-construction increment

Source planning and pure meshes only, 6 October 2026. Parent reserved identity; catalogue unmodified. Eight upper surface IDs retained. No Blender run, .blend/export, Godot import, render, runtime integration or independent retention yet.

## Implemented reference language
Actual full-size theater reference and public blueprint were inspected. Source realizes three coherent fan terraces, deep 36 m proscenium, substantial rear hospitality piers, and a faceted elliptical canopy. Source motifs derive from the image's swept audience, balcony noses, ivory columns, red acoustic stage reveal and warm ring ceiling. Four extra illustrative gallery bands are not audience floors. Mosaics, NPC crowds, orchestra/pit, projection/show machinery and light performance are not represented as finished systems.

X transverse, Y up, Z longitudinal in metres. Assembly stays inside X[-118,-34], Z[-265,-115], Y[69.05,91.35]. World-authoring meshes map to Blender (X,-Z,Y); glTF export must restore world XYZ equivalence. Stable D11_directory_01/D12_directory_11/D13_directory_01 remain one destination.

- Stalls datum69.5, First Gallery78, Crown84
- 740/740/720 exactly; all2200 IDs preserved, one existing AST-CUL-003 design instance family
- Fan centre(-76,-238); inner radius19.5, outer46.4, angles ±54°, one-degree editable facets
- Stalls eighteen rows from radius20, pitch1.5, rise0.12; first/crown seventeen from radius22, same pitch/rise
- Gallery construction depth0.45. No guest D14 slab, D15 cut or added storey
- Stage X[-94,-58], Z[-252,-238], top70.1; opening36×16, head86.1; inward deep reveals and head to87.4
- Stage1:12 ramp X[-55,-51], Z[-246,-238.8], raised0.6 with actual level landing meshes
- Roof canopy ring centred(-76,-207), outer ellipse24×15 radii, top91.35/bottom91.0; pressure roof not authored
- Rear lounge piers centred X-105/-47, Z-160/-149, 1.1×1.1, top87.1; load certification pending

## Parent-approved NEW partition revision
Original reviewed policy subtracted broad rear returns from the rake. Exact source screen found136 unsupported upper places (68 per gallery), e.g. first_gallery_R14_B2_05 top79.56 above return78. This NEW source proposal instead assigns actual raked annular fan to each unchanged gallery_seating ID; rear_public_returns subtracts that exact polygon. No overlap or missing surface is intentionally hidden by a nominal rectangle.

Rear flat returns connect the elevated outer fan via a real 1:12 inclined annular ramp in angles[-3,+3], radii46.4–69.44. Start height datum+1.92, end datum; 23.04 m horizontal radial run. Entrance chord4.857 m minimum, ending7.268 m. The ramp belongs to the unchanged rear_public_returns ID and replaces flat triangles there, rather than being stacked. It stays within the existing return-union containment. Sector exit matches exact faceted outer fan vertices.

Twenty first-gallery rear replaceable places keep exact IDs and X/Y, moving proposed Z-183 to-163 inside the same rear return so they do not sit on this ramp. Original positions and reasons are retained beside new coordinates in place_instances.json. No third-party registry or original proposal was changed. Counts stay740. These are initial level candidates, not certified species/transfer bays.

Source centre/elevation screening now reports ZERO unsupported upper places and ZERO vertices outside allocation. Full-chair bearing footprint, bodies, seat pan sweeps, accessibility, sightlines and exact structural/guard contacts remain separate gates. The radial fan access is stepped; the single rear1:12 route only proves a level-change source surface, not universal row access.

## Exact floor/collision ownership
D11 flat base is parent COMPILER OWNED and absent from exported source. Diagnostic preview slab is marked preview_only and Blender adapter excludes it. Compiler must subtract the actual stalls rake footprint, stage/ramp and landing footprints from flat walkable ownership; a retained substrate may be structural only. Without the compiler slab, D11 base/foyer/backstage support is still missing and this source cannot be adopted.

Exactly eight D12/D13 named static ownership records: gallery_seating, rear_public_returns, foyer_landings, stair_upper_landing at each deck. Foyers exclude full stair rectangle[-59,-146,-50,-122] and shaft[-44.5,-124,-38.5,-118]. Upper landings occupy only[-59,-123.8,-50,-122]. The compiler must validate boundary/holes manifest hash, account actual elevations, retain all OTHER protected voids and emit no duplicate triangles. No broad owner-prefix exemption. Surface manifest hashes are real source-JSON hashes, NOT a future Blender/export equivalence claim.

All generated solids and inclines are static collision proposals owned by AST-CUL-005. Preview has no collision owner. Lift cabin remains dynamic parent-owned; no static floor fills its hole. Door leaves/gates and controllers remain parent-owned fitted family derivatives. No engine-scaled cabin/door or invented occupancy behavior.

## Routes, fixture and aperture reservations
route_reservations.json keeps3.4 m side/rear cart routes and1.4 m audience radial reservations. Existing side/rear routes remain flat at each datum: no raised west route silently consumes shell clearance. Recomputed three-metre provisional headroom margins use actual inclined-ramp heights as well as exact existing route polygons. Minimum remains Crown port0.323036 m after0.80 m normal shell band. Raised rear ramp minimum normal margin is recorded independently. Pressure enclosure is separate and unadopted; longitudinal end-return contacts and six-species headroom remain gated.

aperture_reservations.json records exact main5.2 m clear opening, second3.4 m candidates, staff3.4 m, full6×6 shaft and target5×5 cabin/3.4 gate, plus four-flight58/40-riser stair reservation. These are dimensioned architectural interfaces, NOT fabricated doors or flight meshes. Deep fitted acoustic vestibules, thresholds, usable walls/guards, lift pit/roof/gates, stairs and exterior landing support still require a next source increment and parent interfaces. No source-supported continuous circulation claim is made across these missing elements.

Backstage80×11/4.8 clear, orchestra/support wings16×20/4.8 clear, royal-box return zones, foyer and rear lounge remain exact reviewed functional allocations. This increment includes actual upper box-support surfaces and place IDs, but no finished backstage partition/rooms, guest/service separation walls, booth, stow semantics or delivery connector. Those functions must be completed before room acceptance.

fixture_markers.json has actual source-coordinate positions/aims and existing AST-STF-006/AST-CUL-004 families. Marker/source positions alone are not powered/illuminated fixtures. Approved shared material families are tagged in meshes; adapter intentionally does not invent material substitutes. Actual library linkage is serial-source-slot work.

## Delivery and remaining sequence
Reproduce pure source with python tools/build_geometry.py, then python tools/screen_geometry.py. Both write only this package. prepare_blender_source.py is a future serial-slot adapter, NOT executed; grouped editable region meshes and instance markers preserve provenance. Parent review NEW policy/height witnesses before any source application. Next: exact floor and return QA, supported connected entry/stair/lift/aperture geometry, approved material linkage, controlled Blender/export, source/export equivalence and preservation, parent retention/compiler integration, then actual engine capsule/cart/species/doors/lift and normal-height review.
