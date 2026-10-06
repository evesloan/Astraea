# Grand Pool / Orchard Market: coordinated first-pass finish envelope

Status: proposal for parent scope review, before authoring. Scratch-only source screening has run. No Blender/Godot job, new geometry, live edit, fixture, sign or stock placement was created by this proposal.

## Recommendation

Finish the connected public section as one composition: a legible Grand Pool arrival, four roof spans tied to its three structural ribs, a continuous sheltered wet-rest edge, and three fully composed market bays behind the retained glazed gallery. Develop the wall/ceiling profiles, material hierarchy, visible fixtures, physical signs and supported stock together. Do not approve another furnished but gray shell, or a single decorated bay surrounded by unfinished surfaces.

The current furnishings are correctly placed and source-like. In the new clear market view, however, the only merchandise is one small case on a mostly empty display and a disproportionately large terracotta field surrounds it. The normal presentation shows the same composition at the intended low resolution. The long pool and arrival views are dominated by blank gray roof/soffit fields; the upper overlook loses substantial contrast through the dark glazing. These are first-pass presentation failures, not later polish.

The reopened cruise/retro references support substantial pale structure, darker timber hospitality framing, restrained warm metal, planted usable edges, deliberate ceiling levels and visible illumination. Their crowds, crystal complexity, extra storeys, new shop names, skylights and exterior views are not proposed additions.

## Exact source and file scope to approve

One new subordinate package, proposed as assets/grand_pool_first_pass/finish_envelope/, with its own source/, exports/ and qa/. Keep the corrected 51-placement assembly and all original families unchanged.

1. source/build_finish_envelope.py and source/finish_contract.json: deterministic, dimensioned geometry/material/fixture/mount contract
2. source/grand_pool_finish_envelope.blend: independently editable architecture and physical fixture parts, retaining source-part identities and metric UVs
3. exports/AST-AQU-016_finish_envelope.glb: additive derivative of the existing connected section, with bounded geometry references to AST-AQU-012 ceiling and AST-DIN-005 dry-market wall families. Never overwrite AST-AQU-016.glb or those originals
4. source/build_pool_wayfinding.py, source/grand_pool_wayfinding.blend and exports/AST-RES-001_pool_wayfinding.glb: fitted physical board/frame/glyph derivative from the retained RES_MapFrame/RES_MapBacking construction
5. source/stock_placement_contract.json: additional instances of existing retained catalogue exports; no giant combined furnishing export
6. qa/: source preservation, exact contact/clearance, UV/texture, fixture/source-to-receiver, sign mounting/legibility and labelled source-render evidence

Parent must confirm both proposed derivative filenames/ownership before export/registration. They are derived representations, not new unique-design counts or new business/programme IDs. The full catalogue was checked by exact IDs for the referenced families.

Runtime work would be a separate additive grand_pool_finish_envelope.gd plus its contract and focused check, called once from ship.gd. Keep grand_pool_section.gd, the 51-instance builder, original GLBs, compiler floors, current controllers and shared rendering/light-budget code byte-identical. Parent owns integration and test registration. No live authoring starts from this proposal alone.

## A. Architectural and material scope

### Four connected roof fields

Use the real three GP_RoofRib supports at Z−451/−433/−416. Their source envelopes are Y59.16..60.76. Organize the intervening/end roof spans approximately at Z−465.6..−451.6, −450.4..−433.6, −432.4..−416.6 and −415.4..−398.4. Those are starting control bounds, not fabricated accepted meshes.

Adapt the stepped fields, splayed returns and bearing-coffer construction from AST-AQU-012 to this section. Use a pale central field, darker warm-walnut recess/frame and narrow muted terracotta/champagne junctions. Fit real returns and support attachments around the existing ribs, ceiling closure and glazing head seals. Preserve all six old vault lenses/markers and their unobstructed exits. New overhead finish must stay above Y59.16 and at/below the real Y60.76 soffit, except the separately declared small mounted fixture housings.

Do not drop in AST-AQU-012's existing 46×68 m assembly: it belongs to another fitted location. Do not add a second walkable slab, cut the D10 Shared Table floor, close the gallery void or make a skylight. Every liner, return and fixture must have an actual support connection; no suspended anonymous gray plane.

### Complete three market bays

Retain the orange recessed shells and exact GP_BayCanopy_0/1/2 geometry. Their existing canopies are Y57.95..58.25. Compose a full rear display/stock field, shallow fitted backing, intentional header/end returns and a materially legible canopy underside in each bay. Use AST-DIN-005's shaped return/dado/junction language in the dry area rather than copying its entire restaurant wall or stretching its textile through the full height.

A rear lining control strip X−53.34..−53.25 can meet the existing backing without occupying the display fronts. Existing displays end at X−53.15 on their back side, leaving a nominal 0.10 m gap after this trial lining; final source faces and attachment contacts still need checking. Clip all returns around the actual pier and orange-reveal geometry. Preserve all nine existing canopy lenses and source/cone clearance. No material sheet or new lower soffit may hide their light exits.

Add one existing AST-RTL-001 display per bay, making two per bay, at the source-screened candidate positions listed below. This uses the real bay depth and separates displays around the large piers; it does not turn the gallery loop into a row of freestanding stalls.

### Connected wet-rest / arrival edge

Give the west wet-rest wall a finished, coherent base/field/upper-return composition between its actual pier and service-threshold breaks. Reuse warm stone and wet-appropriate enamel/aquatic roles, with hospitality timber limited to sheltered upper framing. The source west guest wall's inner face is X−53.72; use a maximum 0.12 m additive lining depth into the room as a planning bound, keeping its source apertures untouched. Compose the end conditions at the fore towel/service arrival and aft level bench, rather than stopping a repeated panel arbitrarily.

Carry the same pale structural / warm recess hierarchy into the dry arrival fascia and actual pier profiles through fitted surface derivatives. Any pier addition must remain within an explicitly checked envelope and cannot silently consume the ramp, landing or cart margin. The large pool/upper-gallery sightlines remain open. No raised finish strip, floor overlay, new platform or narrowing of the ceremonial stair is proposed.

### Materials and textures

Reuse the existing warm_stone, ivory_enamel, warm_walnut, champagne_metal, retail_terracotta_enamel and aquatic material families; keep furniture textile and botanical roles intact. Regenerate metric UVs for newly dimensioned surfaces, retain image hashes/nearest-filter policy and inspect scale under both normal and effects-off rendering. Use wood/metal to clarify actual depth and support, not as thin cosmetic stripes over unfinished boxes. No shared palette replacement, new global grading or ambient-light rescue.

## B. Supported market stock and exact additional display candidates

Three additional AST-RTL-001 candidates, all yaw +π/2:
- Bay 0: (−52.7, 52.5, −453.5)
- Bay 1: (−52.7, 52.5, −430.6)
- Bay 2: (−52.7, 52.5, −412.2)

DISPLAY_CANDIDATE_SCREEN.json uses the complete retained GLB vertices/transforms, all original section-part envelopes, all 51 existing furnishings and real D09 floor triangles. It passes 3,990 floor-footprint and 348 conservative 0.32 m-radius approach samples. Earlier trial centres −454.2 and −430.3 intersected orange reveals and were rejected. This is source screening only; actual capsule/cart and new-finish interaction checks remain mandatory.

Stock all six displays using their real support patches, with variation in composition:
- Existing AST-RTL-004 cases on main surfaces; add one to each new display
- One retained curio per display, varying AST-CUR-001/002/003 across bays, on the main right patch
- Two AST-LIB-006 book groups on the broad left shelf where full source envelopes fit
- One AST-BOT-012_low pot plus AST-BOT-003 rosette on the upper right shelf only if both pot support and complete foliage/back/head clearance pass
- Up to two AST-RTL-004 closed cases on actual lower storage-floor contacts; derive their height from evaluated triangles, not the nominal empty-volume bounds

This is capped at three additional displays plus 45 additional retained stock/plant instances, giving at most 99 total first-pass furnishing instances. Reduce a slot if its full geometry fails; do not scale an item to disguise clipping. Keep the existing case, plants, seats, towel stations and every checked approach. These are static scenic goods, not new shops, prices, transactions or operated inventory.

## C. Physical fixtures and lighting allocation

Keep all 25 old fixtures, their calibrated values and identities unchanged. The proposed additive roster is bounded at 14 source-backed lights:
- Six roof washes: one on each fore/aft face of each of the three existing roof ribs, mounted on real source faces and aimed at the neighbouring coffer field
- Six display lights: one physically housed under the actual upper surround of each of the six displays, illuminating its supported stock rather than merely brightening the surrounding floor
- Two wet-rest wall/seat washes: fitted to the west wall treatment near the two main lounger groups, around Z−444 and −425, outside all circulation and towel extraction envelopes

Each requires an editable housing, attachment, lens, unique marker, actual source exit and named receiver. Final marker coordinates, ranges, cone angles and energies must come from source geometry and in-engine trials; these are not accepted lamp settings. A roof wash must reach a real overhead face without traversing its mounting beam. A display light must clear its hood/shelves and reach merchandise. Retain warm guest hierarchy and cooler utilitarian service areas.

All 39 total section sources would use the unchanged shared eight-shadow-source cap and bounded candidate selector. No unshadowed fallback, light-budget increase or renderer replacement. If the new selection starves walking-floor/face/cart illumination or pops during a pan, revise source placement/optics before acceptance. Test actual source-to-receiver visibility and stable selections at arrival, west seating, market browsing and the long-pool view, then moving foreground response.

## D. Eleven physical wayfinding boards

Rebuild the retained AST-RES-001 frame/backing construction at suitable dimensions; keep its original residential bay unchanged. Use modelled front/mount/frame and editable high-contrast glyph meshes. No invisible text markers, external business branding or invented depth/safety claims.

- Two main arrival boards: Grand Pool at D08 and Orchard Market at D09, mounted above their actual source portal headers without reducing the 3.2 m clear aperture
- Two upper wet/dry threshold boards identifying Pool stairs and Pool lift at the existing gate headers
- One lower local-lift board identifying Orchard Market at its real header
- Two step-free route boards at the actual lower ramp decision and upper arrival; arrow orientation must be derived from the current route projected into the sign's viewing plane
- Two station boards: Towels and Used towels, mounted to fixed housings without covering existing DRY/RETURN glyphs, the retrieval mouths or the rear container motion envelope
- Two Staff only plaques on the existing screened service door assemblies, clear of controls and moving leaves

Nominal board families: main 2.4×0.6 m, threshold 1.4×0.4 m, direction 1.2×0.6 m and small station/service plaques sized to the verified fixed mounting face. These are starting bounds, not permission to hang geometry in a route. Existing-room names remain authoritative. Verify letter size and direction from the actual approach at 640×360 and effects off.

## E. Glazing: a separate local-material review, not a hidden renderer change

The current overlook is substantially darkened by the pane treatment. The existing shared shader exposes pane_tint=(0.19,0.37,0.38) and face_opacity=0.23; the closed physical pane has multiple visible surfaces, which can compound opacity. That observation does not prove a renderer bug.

First inspect the fully lit finish candidate with its existing panes. If the cross-pool view still fails, request a separately recorded A/B of only the Grand Pool material instance, keeping the same shader and all pane geometry/collision/mullions. A bounded trial could reduce face_opacity toward 0.14 and use a lighter muted tint while retaining visible edge response. Do not silently include this in authoring or change the shared shader/defaults. Parent should explicitly decide whether that local material trial is part of integration.

## Protected acceptance contract

Preserve the 50×18 m lane, Y44 arrival, Y46.2 wet floor, Y52.5 market, full D10 programme above Y61 and D07 lower protection. Keep the central/gallery/local-link voids, all panes, doors, lift IDs, ramp/stair profiles, original routes and exact compiler owners. In particular, never move the retained X−45.9 walk or the closed-door dry market loop to accommodate this finish.

Before adoption: pin original files; source contacts and full envelopes; stock supports; modelled sign/fixture attachments; material/image/UV integrity; derivative source/export equivalence; independently retain editable source. After adoption: imports; old and new capsule/floor/door/fixture checks; local lift and real loaded-cart/reverse/regrip checks; matched aggregate regression; ordinary normal/effects-off views plus short pans. Existing six inspected images document deficiencies, not full-room approval. This bounded public finish must not be represented as a complete ship, operational retail/laundry/swimming or occupied/species acceptance.
