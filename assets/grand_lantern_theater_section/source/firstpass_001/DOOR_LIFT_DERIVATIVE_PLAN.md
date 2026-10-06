# Theater doors and lift: read-only source fitting plan

**Latest review:** `PROPOSED_534_SWEEP_REVIEW.md` and `proposed_534_full_vertical_sweep.json` supersede the provisional 5.40m rail/shoe allowance below. The only checked proposed full moving envelope is 5.34m wide; it remains unapproved. All future moving hardware must fit it or receive a new proof/approval.

6 October 2026. No Blender, Godot, export, runtime, shared-source or catalogue writes were performed. This plan is dimensional evidence and a proposed derivative contract, not an authored or working lift/door acceptance.

## Current recommended bounded option

The final addendum quantifies the parent-requested 4.98×4.98m centered platform. It resolves the zero-gap issue without moving any fixed source. A 4.4m turn disk fits while retaining the compact rear side benches. The gate is 5.34m wide, with 180mm overhang each side of this smaller platform; separately allocated rail/shoe geometry may need a 5.40m moving envelope. All are approval candidates, not authored outcomes.

## Result and decisions

The retained families can supply appropriately shaped theater derivatives without scaling a common controller or changing catalogue identity. The main paired leaves fit the existing longitudinal cavities. A genuine four-panel telescoping lift landing gate fits behind the existing solid jambs without cutting them. The cabin needs a purpose-authored enlarged derivative, rather than calling the current cabin “5×5 clear.”

Do not approve the entire mechanism as fitting yet. Parent disposition is needed on:

1. **Moving envelope:** authorize a cabin gate/chassis envelope wider than the 5m platform, within the existing shaft. The proposed gate is 5.34m wide; the 5m platform remains 5m wide. If all moving geometry must instead fit the exact 5×5 reserved rectangle, this four-leaf topology cannot fit a 3.4m opening. It would require a different number/rank arrangement or changed opening, not controller scaling.
2. **Threshold running gap:** the preserved fixed sill ends at Z=-123.5, precisely where the reserved platform starts. A literal 5×5 platform in the exact reservation has zero running gap. A positive gap needs a bounded platform relocation/envelope interpretation, a slightly smaller platform, or a sill modification. The plan does not silently choose one. For example, moving an exact 5m-depth platform 10mm into the shaft gives Z[-123.49,-118.49], a 10mm sill gap and 240mm rear gap, but exceeds the old dynamic rectangle by 10mm at the rear. That is a contract delta, even though it remains inside the shaft.
3. **Lift height and rail construction:** the contract specifies a 3.4m-wide gate and a structural head at +3.4m; it does not give a final clear cabin-height requirement. The retained gate is 2.65m clear and cabin roof is 2.8m nominal clear, with lower light wells. Retaining those heights, or creating a taller cabin/gate, must be stated explicitly. Neither old generator models a complete engineered track/roller/drive system. New rail/support meshes and their entire sweeps remain required.

## Verified retained evidence

The theater saved source SHA256 remains:

`c91193af1e4a14aac3a4e75c743e7c86b6a57a669981e9a7e7cfb0412e1cb5f5`

A small independent reader decoded the actual GLB BIN vertex data and accumulated parent translations. It did not trust accessor min/max alone. All inspected source/export hashes agree with the corresponding manifests. Full numeric evidence: `door_lift_retained_byte_evidence.json`; reproducible reader: `check_door_lift_bytes.py` in this directory.

- AST-DOR-002: 272 triangles; fixed overall width 3.48m; height 2.66m. Nominal opening 1.6m; body leaf 0.78m, travel 0.84m. Complete moving leaf depth includes inset/seal geometry, not just the 50mm panel body.
- AST-DOR-002_wide: 296 triangles; fixed overall width 5.16m; height 2.66m. Nominal opening 2.4m; body leaf 1.18m, travel 1.24m; real hollow pocket width 1.36m per side. Two separate physical call plates/markers exist.
- AST-DOR-002_wide270: source derivative changes selected upper vertices/UVs only to 2.7m clear and 2.86m overall. It remains **2.4m wide**, not a theater-width solution. Its preservation script is useful precedent for preserving unchanged objects and materials while editing explicit dimensional coordinates.
- AST-DOR-003: 456 triangles; overall 3.84m width, 2.85m height, 0.20m header depth. It is already a genuine two-rank/four-leaf telescoping design with real empty pocket channels. Body widths are 0.595m inner / 0.615m outer, roots ±0.30 / ±0.90m, travels ±1.21 / ±0.61m. Do not invent a telescoping mechanism by renaming a paired gate.
- AST-CIR-003_three_stop: 312 triangles; actual outer platform/cabin footprint bounds are 4.0×3.6m. Bottom -0.18m, roof top +2.94m. Source hash `aed933163f5248de2fea2076b666f0200381dac7f303832eaf9ff416c539a0a8`, GLB hash `7724dbf3152b486aa7d01354beacd009eb6ba2a67fb8f7a72238ebcc9f6de6d9`. The three markers are physical destinations, not a functioning controller or correct theater-stop proof.

### Existing gate travel defect relevant to reuse

Actual retained AST-DOR-003 fully-open left inner seal reaches local X=-1.182500026m. It intrudes 17.499974mm into the nominal left aperture boundary X=-1.2m. The right side clears. The fully open intersection with the nominal opening is therefore about 2.3825m, not a proven 2.4m. Preserve the retained original; recalculate the derivative stroke from every moving vertex, including seal and glazing beads.

## Main 5.2m acoustic entrances

The three portals are centered at world (-34, stop, -126), stops 69.5/78/84m. Actual aperture Z[-128.6,-123.4], height 3.4m. Actual pocket intervals are Z[-131.3,-128.6] and [-123.4,-120.7], not the wider preliminary [-134,-118] reservation in aperture metadata. Each is 2.7m long. Empty depth channel X[-34.35,-34.15] is 0.20m wide. Pocket skins occupy the adjacent 0.15m bands; cap occupies +3.4…+3.65m.

Use a new AST-DOR-002 theater representation with separate editable leaf roots, retained faceted body outline, timber insets, seal, material graphs and physical call detail. Use the existing theater pockets rather than placing a second enclosure on top of them. No source root scale or runtime controller scale.

One viable leaf-only numerical target, in local width coordinate u=world Z+126:

- Body width 2.600m, half-width 1.300m; closed root centers ±1.310m. This yields 20mm between body meeting edges and 10mm of body behind each aperture jamb edge.
- Retain the original left offset meeting-seal logic: local seal [1.292,1.332], producing closed world-local interval [-0.018,+0.022]. Its full leaf width is therefore 2.632m, not just the 2.600m body.
- Outward travel 2.650m per leaf. Fully open left complete bound is [-5.260,-2.628], fitting pocket [-5.3,-2.6] with 40mm outer and 28mm throat margin. Right complete bound [2.660,5.260] leaves 60mm throat and 40mm outer margin.
- Preserve the existing 0.075m complete moving depth unless a separately reviewed acoustic construction changes it. With that source envelope centered at X=-34.25, it occupies X[-34.295,-34.22], leaving 55mm/70mm to channel walls. A 0.12m reserved thickness is a maximum allowance, not evidence the retained door is 0.12m thick.
- Extend selected top vertices to +3.385m and preserve +0.035m lower datum, so leaves fit the +3.4m structural cap with 15mm top and 35mm bottom clearance. Update affected metre UVs, not the material graph.

These linear translation bounds prove only a leaf/pocket envelope candidate. The family generators have pocket skins/base/header but no complete roller/track geometry. A conventional overhead rail located above +3.4m in the pocket center would enter the preserved solid caps; a rail below +3.4m reduces the declared clear height. A supported bottom-running/flush-track solution or a specifically approved cap/track detail must be designed and checked before claiming real mechanism support. Do not silently notch the retained source, lay an obstruction across the 5.2m threshold, or hide a rail in a solid wall. Whole-leaf support, release/regrip, handles and user/body/carts remain separate tests.

## Lift landing gate: no-cut jamb solution

Actual shaft outer X[-44.5,-38.5], Z[-124,-118]. Existing 0.25m side/rear construction reduces usable inner width to X[-44.25,-38.75], **5.5m**, not 6m. Cabin center X=-41.5. Actual solid front jambs are X[-44.5,-43.2] and [-39.8,-38.5], Z[-124,-123.75], continuous vertically 69.5…87.65. They contain no storage cavities.

Put the derivative's own hollow pockets on the shaft-side faces, entirely in the 250mm slot behind the jambs and ahead of the moving platform. Proposed root/plane Z=-123.63, using source depth directly toward +Z:

- Header depth [-0.105,+0.095] gives world Z[-123.735,-123.535]. It clears jamb back by 15mm and old platform front by 35mm.
- Pockets depth [-0.095,+0.085] gives Z[-123.725,-123.545]. Add real bracket attachments to the solid jamb back outside the 3.4m clear aperture; pockets cannot be claimed floor-supported where the fixed sill is absent.
- Target width 3.4m. Inner/outer body widths 0.845/0.865m; closed centers ±0.425/±1.275m. Preserve original depth channels and the offset meeting seal, updating its width-relative coordinates explicitly.
- Proposed strokes ±1.740m inner and ±0.890m outer. Both ranks gather at centers ±2.165m. The left inner seal retreats to -1.7125m; limiting right opening edge is +1.7325m. Therefore the exact [-1.7,+1.7] aperture is clear, unlike the saved original stroke.
- Complete open outer-rank edge reaches ±2.5975m. Pockets X-local [1.7,2.65] / [-2.65,-1.7] are 0.95m long. End caps begin at ±2.63m, leaving 32.5mm leaf/end clearance. Header reaches ±2.67m: total 5.34m, within the shaft's 5.5m interior with 80mm side clearance.
- Retained channels leave 19mm between worst seal and inner pocket skin, 27mm between outer panel and opposite pocket skin, and at least 35mm between relevant rank surfaces. Retained leaf bottom +0.03 and pocket base top +0.02 leave 10mm. Header/leaf top separation is 20mm before newly designed rollers/rails, which must not consume these margins invisibly.

The source depth/width calculations can support all three landing gates with no change to the original jamb meshes. A gate on the foyer side would reduce the explicitly protected boarding stance; prefer the shaft-side solution.

## Cabin derivative and full moving sweep

Retain the actual AST-CIR-003 three-stop design language, material hierarchy, side benches, faceted rear corners, roof wells, control panel and marker ownership. Author explicit dimensional extensions, not global scaling. For a nominal 5×5 outer derivative, extend sides by 0.5m each and rearward features by 1.4m, retaining material thicknesses and local trim/seat dimensions. Declare whether the platform keeps the family rear corner chamfers or is an exact square; an overall 5×5 bounding box is not proof of a full 25m² clear surface.

**Clear is not outer:** original wall-to-wall width is 3.76m, rear inner panel depth is 3.47m, and benches reduce a rear band to 2.8m between their inner edges. The three-stop panel projects inward to X=1.75m. Original nominal roof underside is 2.8m; lens underside is 2.63m. For the straightforward 5×5 outer extension these become 4.76m wall-to-wall, rear panel at depth 4.87m (backrest at 4.84m), and 3.8m between rear benches. Control panel projects to ±2.25m. Actual door depth and controls reduce particular usable rectangles further. Never label this cabin “5×5 clear.”

Proposed moving gate plane is +0.14m inside the platform front, Z=-123.36 before any running-gap adjustment. Its header spans Z[-123.465,-123.265], safely behind the fixed landing header; set cabin sidewall front edges back to depth ≥0.30m to avoid embedding the gate pockets in its own walls. The gate extends 0.17m outside each platform side; support it from a purpose-authored chassis/roof bridge. That overhang is inside the 6m shaft but outside the exact 5m dynamic rectangle, so obtain the explicit envelope disposition noted above.

Guide rails can occupy the side strips away from the front gate pocket zone, e.g. alongside the cabin mid-depth rather than its front. The 250mm side strip between a 5m cabin body and each shaft inner wall is real space; it is not a certified rail/shoe allowance. Add source-authored shoes/brackets, preserve their intended bearing contact, and test actual triangles against all static shaft, stop headers and sill meshes. Do not attach structural rail loads to an unexplained glass face or claim unsupported bottom ends are anchored.

Stops are exactly 69.5, 78, 84m: relative to D11, 0, 8.5, 14.5m. The original 0.18m platform extends to Y69.32 at the lower stop. A roof +2.94m reaches 86.94m at the top stop, leaving 0.71m below the modeled shaft's 87.65m upper edge; that edge is not a verified ceiling or machinery headroom. A +3.4m roof underside with 0.14m roof reaches 87.54m; a 3.4m-clear gate's 0.2m header reaches 87.60m. Its light wells would still reduce clear height unless separately redesigned. A taller +3.6m roof underside preserves >3.4m under the old wells but would put roof top at 87.74m, 90mm above the current shaft enclosure. No height choice, pit, buffer or head-frame acceptance is inferred.

## Implementation and verification boundary

1. Pin retained source/export bytes and copy into new derivative destinations only; never overwrite surviving originals. Preserve saved AST-CUL-005, all 2200 chair instances and chair bytes, place IDs, voids and the eight exact upper surface exceptions.
2. Parent settles moving-envelope/running-gap/clear-height and rail-detail contract. Reuse AST-DOR-002, AST-DOR-003 and AST-CIR-003 IDs with bounded theater representations.
3. In an allocated later Blender slot, load retained source datablocks; author only named derivative coordinates/new attachment geometry. Save semantic editable source before export batching; preserve original material/texture signatures, unchanged geometry/UVs and leaf/control hierarchy.
4. Verify every complete leaf, seal, bead, hanger, pocket, rail and shoe through continuous linear sweep bounds plus actual triangle contacts. Include open/closed/interrupted states, cavity ends, cap interfaces, all station gates, the cabin gate and the complete vertical cabin/chassis sweep.
5. Independently read new GLB binary vertices, source round trip and material/texture hashes. Demonstrate physical supports, precise fixed/moving floor ownership and positive sill/running gaps.
6. Only then consider authorized runtime data/instances. No shared-controller rewrite or controller scaling. Interlocks, blocked thresholds, load carry, loose props, pause/save and actual cart/species movement remain independent acceptance gates. External guest landings, secondary exits and backstage connector remain unbuilt parent work.

## Primary retained files

- `assets/grand_lantern_theater_section/contracts/fitted_door_pocket_contract.json`
- `assets/grand_lantern_theater_section/contracts/aperture_reservations.json`
- `assets/grand_lantern_theater_section/tools/extend_architecture.py`, especially lines 74–100
- `assets/grand_lantern_theater_section/source/geometry.json`
- `assets/guest_entry_door/source/build_guest_entry_door_wide.py`
- `assets/telescoping_gate/source/build_telescoping_gate.py`
- `assets/commons_lift_cabin/source/build_commons_lift_cabin.py`
- `assets/secondary_engineering_access_interfaces/source/build_access_derivatives.py`
- Relevant `.manifest.json`, retained `.glb`, and `AST-CIR-003_three_stop_geometry_checks.json`
- `assets/vertical_commons/source/architecture_contract.json` supplies a prior explicitly separated fixed sill/moving-platform running-gap precedent; it does not authorize copying its dimensions into the theater.

## Requested bounded approval option: 4.98m platform and 4.4m turning circle

This addendum responds to the parent's 6 October request. It is a quantified proposal for root approval before authoring; it does not revise the saved source or imply that approval has already been granted.

### Exact floor, gate and cabin coordinates

Keep the original 5×5 reservation X[-44,-39], Z[-123.5,-118.5] unchanged as the architectural reservation. Put a **4.98×4.98m outer platform** concentrically inside it:

- Platform X[-43.99,-39.01], Z[-123.49,-118.51], floor Y=69.5/78/84 at the three stops.
- 10mm stationary-sill/moving-platform horizontal running gap, between Z=-123.50 and -123.49. The platform is 10mm inside each other old reservation edge. No existing sill, jamb, foyer, shaft or theater mesh moves.
- The actual side/rear shaft inner faces are X=-44.25/-38.75 and Z=-118.25, yielding **260mm** platform-edge clearance on both sides and at the rear. Platform-front to jamb-back clearance is also 260mm.
- New source local coordinates: width u centered on X=-41.5; depth d starts at the platform front Z=-123.49 and increases into the cabin. Conversion is X=-41.5+u, Z=-123.49+d, Y=stop+h. This is a proposed semantic coordinate frame, not an unexamined GLB yaw. The retained Blender/GLB handedness must be applied explicitly on export/placement.
- Cabin sidewall outer faces u=±2.49, inner faces u=±2.37, retaining 120mm wall thickness. Width extension from the retained source is 490mm per side, rear-depth extension 1.38m.
- Rear panel: d=4.85…4.98; backrest face d=4.82. Preserve 350mm rear corner facets. They begin at exterior d=4.63, with source-derived inner facet point (|u|=2.37,d=4.57), and meet the rear interior near |u|=2.09,d=4.85.
- Moving gate center Z=-123.35 (d=0.14); header world Z[-123.455,-123.255]. Landing header remains Z[-123.735,-123.535], leaving **80mm header-to-header longitudinal gap** and **45mm fixed-header-to-platform gap**. Actual leaf and lower pocket envelopes are smaller. Use the already computed 3.4m-clear gate dimensions/strokes from the preceding section.
- The moving gate's lateral motion envelope is X[-44.17,-38.83] (5.34m wide), **180mm overhang per side**, since 2.67−2.49=0.18m. It clears the shaft inside walls by **80mm**. Keep this separate motion-envelope ownership record; do not assign it the platform polygon.
- Set cabin sidewall front depth to ≥0.30m, behind the full moving-gate header rear depth 0.235m. That gives a 65mm axial separation; gate-support connections must use explicit source geometry rather than overlapping a wall through the pocket.

### Furniture can be retained, with a genuinely clear 4.4m circle

Do not remove the retained side benches merely because their rear aisle is narrower than 4.4m. Their peripheral arrangement still permits the required circular footprint farther forward.

With dimensional extension while preserving the bench bodies, their two footprints are |u|=1.89…2.39, d=3.98…4.53, with pads at h=0.42…0.49. The 3.78m rear band between inner bench edges is **not** the diameter of the largest free circle. The right-hand three-stop control panel occupies u=2.24…2.37, d=0.43…1.25; physical button datums shift to u=2.22, d=0.55/0.84/1.13, h=1.27. Neither benches nor panel need be deleted for this plan-view fit.

Proposed clear turn disk: **diameter 4.400m, center u=0,d=2.53**, world center **X=-41.5,Z=-120.96**. Its world bounding box is X[-43.7,-39.3], Z[-123.16,-118.76]. Exact conservative geometric margins:

- Sidewall faces: 2.37−2.20 = **170mm** minimum.
- Conservative front clear line d=0.24 (behind the entire gate header footprint): disk front is d=0.33, giving **90mm**.
- Rear backrest d=4.82: disk rear d=4.73, giving **90mm**.
- Nearest bench front/inner corner: sqrt(1.89² + (3.98−2.53)²)−2.20 = **182.14mm** radial gap. Other bench points are farther away.
- Nearest control-panel corner: sqrt(2.24² + (1.25−2.53)²)−2.20 = **379.92mm** radial gap.
- Rear facets are farther away than the backrest and sidewalls for this disk. They remain retained; do not square off the source to claim extra clear area.

The 4.74m wall-to-wall width and the conservative front/back useful depth **4.58m** (d=0.24…4.82) support this disk. It is not a 4.74×4.58m wholly empty rectangle because rear bench corners occupy part of that rectangle. The disk itself avoids them. The floor inlay remains a retained raised detail (up to 4mm), not an assumed perfectly smooth collision plane.

If “4.98×4.98 platform” means a full square rather than bounding dimensions, state that explicitly. Retaining two 350mm corner chamfers leaves **24.6779m²** of platform versus **24.8004m²** for a full square. The circle fits either variant, but filling those corners changes derivative geometry and must not happen silently.

This disk is a source-plan clearance candidate, not a tested cart/operator turn, species/body envelope, operating reach or evacuation acceptance. Actual cart length, handle/regrip and operator pose sweeps still decide usability.

### Rail, pit and headroom proposal limits

The unchanged shaft leaves side hardware strips of 260mm between platform outer faces and shaft inner faces. Locate guide rails at cabin mid-depth, away from the front telescoping pockets: a planning centerline is |u|≈2.64,d≈2.49. A complete future rail/shoe/mount section should stay within |u|≤2.70 (5.40m maximum moving hardware width if that shoe allowance is used), preserving ≥50mm to the side walls. The 5.40m guide/shoe envelope is distinct again from the 5.34m gate and 4.98m floor. Do not instantiate a solid box there and call it a guide: actual shoe channels, bearing contact and fixed-bracket pass-by must be authored and triangle-swept. A fixed mount occupying the back of a rail can collide with a wrapping shoe even when their global envelopes fit. Rail supports to real jamb/head/post structure, rather than glass alone, remain necessary.

- Minimum moving floor underside at D11 remains **Y69.32** for the retained 180mm platform thickness. There is no authored pit floor, buffer or lower machinery clearance proving acceptance. Any new below-platform hardware lowers that minimum and needs its own continuous sweep. The current no-cut proposal does not claim a pit is complete or that permission extends into a lower deck.
- Highest retained-height roof is **Y86.94**, 710mm below the shaft enclosure's modeled top Y87.65. Lowest retained lens is only 2.63m above the floor. If 3.0m clear headroom is required through the turning area, unchanged vertical furniture/roof positions do not meet it.
- A bounded **optional 3.0m-clear** cabin variant can retain the 170mm ceiling-well/lens offset by raising nominal roof underside to **h=3.17m**, roof top to **h=3.31m**. At D13 the roof top is **Y87.31**, leaving 340mm below the current shaft top. Make the gate clear height **3.00m**, leaf top 2.98m, header top 3.20m; its header top is Y87.20. Add only derivative-owned stationary fascia between +3.20 and the existing +3.40 structural head, within the same shaft-side gate plane. This preserves all old shaft/jamb geometry and allows a 3.0m-high turn cylinder in principle. Root must approve this height target and later rail/roof hardware before authoring; the 340mm top allowance is not a certified drive/machinery space.
- A requirement for **3.4m clear everywhere under the retained well proportions** instead needs roof underside 3.57m and roof top 3.71m (Y87.71), 60mm above the present modeled shaft top. That is a different enclosure/headroom decision; do not confuse structural doorway height with a current approved all-cabin clear-height requirement.

The requested 4.98m option therefore resolves the zero-gap conflict without changing fixed source, and the 4.4m disk permits retaining the compact rear benches. Remaining approvals concern the small platform nominal-size delta, separate full moving-envelope ownership, final clear height and real mechanical support/pit details.
