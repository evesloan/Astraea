# Main acoustic entrance: proposed bounded cap/track derivative

6 October 2026. **Dimensional proposal only; no cap cuts, new source meshes, Blender/export/import, engine work or Godot-project writes.** The 5.34m lift envelope approval is separate and unchanged. This proposal needs the parent's explicit cap-derivative approval before authoring. The saved `AST-CUL-005.blend` remains untouched at SHA256 c91193af1e4a14aac3a4e75c743e7c86b6a57a669981e9a7e7cfb0412e1cb5f5.

## Exact requested approval scope

In a **new theater source derivative**, replace only these six cap parts:

- D11/D12/D13 `door_pocket_fore_cap`
- D11/D12/D13 `door_pocket_aft_cap`

Preserve every other existing part, all pocket skins, vestibule returns/caps, architectural walls, floor ownership, 2200 chairs and materials. Add one matching channelled 5.2m central head at each entrance. It meets the two cap derivatives without an internal seam obstruction. Door track/trolleys/hangers are a new representation of AST-DOR-002. No new catalogue identity or shared-controller scaling is proposed. Original source bytes are never edited or overwritten.

World reference: floor y is69.5/78/84; local travel coordinate u=Z+126; local depth v=X+34.25; h=Y−floor.

### Cap channel and remaining section

- Existing pocket-cap envelopes remain X[-34.5,-34.0], h[3.40,3.65], u[-5.3,-2.6] or [2.6,5.3]. Gross cross-section500mm wide ×250mm high.
- Proposed underside channel: v[-0.09,+0.09], therefore X[-34.34,-34.16], h[3.40,3.60]. **180mm width ×200mm depth.**
- Keep a full-solid **180mm outer end block** in each pocket cap: |u|[5.12,5.30]. The channel is cut only through each inner2.52m length. Together with the new central head, the clear continuous channel runs u[-5.12,+5.12], length10.24m.
- Remaining roof thickness **50mm**, h[3.60,3.65]. Remaining side webs **160mm each**, v[-.25,-.09] and [.09,.25]. Minimum channelled section area0.089m² versus original0.125m², before small explicitly modelled fastener bores.
- Each160mm web retains **150mm actual bearing width** on the unchanged corresponding pocket skin. Four bearing strips per entrance are150mm ×2.7m, total **1.62m²**. These are real coplanar support areas at h3.40, not inferred support at an empty channel.
- Each cap's channel removal is0.18×0.20×2.52=**0.09072m³**. Six caps total0.54432m³, occurring only in a new derivative after approval. The full-solid end blocks and original exterior cap envelope remain.
- New central head occupies X[-34.5,-34.0], h[3.40,3.65], u[-2.6,+2.6], with the same open-bottom channel. It adds0.4628m³ per entrance before bores. Its5.2m span transfers into the two pocket caps through their continuous side webs/roof. This is a geometric bearing/span arrangement, not a load/stiffness certification.
- Do not merge or drill into the unchanged adjacent east acoustic wall or vestibule cap. They meet the new head at X=-34.5 without positive-volume penetration. No support credit is assigned to a merely touching vertical side face.

The complete fixed geometry begins at h3.40. Nothing is laid across the walking floor or below the clear opening's3.4m head.

## Genuine track, rollers and hangers

Use one continuous newly modelled track over u[-5.10,+5.10], length10.20m. It ends20mm before each retained full-solid cap end block. The open-bottom track cross-section is an inverted channel with two inward running ledges:

- Side plates: v[-.085,-.075] and [.075,.085], h[3.490,3.590]. Thickness10mm; outside faces have **5mm clearance** to the cap-channel side walls at v±.09.
- Running ledges: v[-.085,-.025] and [.025,.085], h[3.475,3.490]. Thickness15mm. Their inner edges leave a **50mm central hanger slot**. Join ledges to side plates at their intended shared edges, without duplicated internal solid faces.
- Top plate: v[-.085,+.085], h[3.590,3.600], thickness10mm. Its top meets the cap roof underside at h3.60. It must be hung with the modelled through-fasteners below; touching an overhead face alone does not support gravity load.
- Two trolleys per leaf, center offsets u=±0.900m from each leaf root, spacing1.800m.
- Each trolley has two coaxial rollers: nominal radius **40mm**, axial width18mm, centers v=±55mm and h3.530. Roller depth spans v[-.064,-.046] / [.046,.064]. Their lowest points meet the running-ledges' h3.490 plane; this is the named intentional bearing contact.
- Roller upper envelope h3.570 leaves **20mm** to track top-plate underside h3.590. Roller outer axial faces leave **11mm** to side-plate inner faces. Use actual wheel discs with central bores, not solid cylinders intersecting an axle.
- Axle radius8mm, v[-.070,+.070]. Roller bores radius8.5mm give nominal **0.5mm radial running clearance**. For the loaded circular-bearing rest pose, use axle center h3.5295 inside roller-bore center h3.530: its bottom contacts the bore bottom at h3.5215. Put the hanger bore center at h3.5290 so its top contacts axle top at h3.5375. This avoids calling concentrically floating loose-fit parts supported. These are proposed circular-bearing contacts; actual faceted source phases still require their own check. Axle ends retain **5mm** clearance to track side plates. Model collars/retention and real bore surfaces within this envelope.
- Hanger stem: depth v[-.012,+.012], travel width30mm (±15mm around its trolley center), h[3.397,3.550], with the bore at the axle connection. It passes the50mm rail slot with **13mm clearance per side**. Model its axle attachment/bore rather than a concealed solid intersection.
- Hanger footplate:100mm along u ×50mm depth, h[3.385,3.397]. Its bottom bears on the derivative leaf's real flat top at3.385. Model attachment holes/fasteners in this new leaf derivative; do not let a floating plate merely hover above it. The small moving hanger does not reduce fully-open headroom because it travels into the pocket with its leaf.

A smooth circular roller envelope is the dimensional calculation. A faceted source wheel must receive its own phase/contact check. For example, a64-sided40mm wheel has a48.2µm apothem deficit; blindly rotating it about a fixed center is not proof of continuous support. Preserve the calculated outer envelope and either verify the small support-height variation explicitly or distinguish the visual roller from a separately accepted physical bearing representation. No hidden roller/ledge penetration is permitted.

### Track suspension: explicit roof holes and fastener clearances

Propose paired M6-sized geometry at v=±0.055m and u=0.45k, k=−11…11:23 stations,46 fasteners per entrance. The farthest stations are u±4.95,350mm from the cap's outer edge. The closest station to each central-head/cap seam at|u|2.6 is100mm away, rather than placed on the seam.

- Shank radius3.0mm; model through-bores radius3.5mm through the new track top plate and new50mm cap roof. Nominal radial clearance0.5mm. These bores are part of the requested new-cap scope and do not touch an old source file.
- Lower head occupies h[3.580,3.590], radius9mm. Its top bears against the track top-plate underside. The head underside is **10mm above the roller's maximum3.570m envelope**, including when a trolley passes directly beneath the fastener.
- Washer on cap top h[3.650,3.655], outer radius12mm; nut h[3.655,3.665]. The washer bears on the retained/new cap roof top. Model the holes, shank, washer and nut as separate complementary geometry, avoiding solids concealed inside uncut roof material.
- Whole upper fastener envelope ends at h3.665,15mm above the original cap. At the three floors, maximum Y is73.165/81.665/87.665. This small additive height is included in the source-contact screen.

This explicitly transfers rail load through lower bolt head → shank → upper nut/washer → cap roof/webs → actual pocket skin bearing. It does not claim engineering load capacity.

## Main leaves, complete travel and positive endpoint margins

Retain the source AST-DOR-002 body, timber inset and offset meeting-seal construction as editable components, extending named width/height coordinates rather than scaling a root.

- Body leaf width2.600m, closed roots u=±1.310m. Body closed ranges[-2.610,-.010] and [.010,2.610]. Aperture remains u[-2.6,+2.6].
- Left meeting seal local range[1.292,1.332], giving closed global u[-.018,+.022]. Complete left leaf width is2.632m. Body width alone is insufficient for travel proof.
- Source body depth v[-.025,+.025], inset envelope to±.030, left seal depth[-.045,-.030]. Complete depth is75mm. The offset seal clears the opposing body's front face by **5mm**, while covering the center body gap in projection; this is not an acoustic-seal performance claim.
- Panel bottom h.035, top3.385. Commanded outward stroke **2.650m** each side. Fully open complete left u[-5.260,-2.628], right[2.660,5.260]. Leaf clearances remain **40mm outer pocket ends**, **28mm left throat** and60mm right throat.
- Left trolley centers move from[-2.210,-.410] to[-4.860,-3.060]; right centers mirror. Including40mm wheel radius, all normal roller motion stays within u[-4.900,+4.900], **200mm inside track ends** and220mm inside full-solid cap end blocks.
- A stationary welded end-stop block can occupy |u|[4.920,4.980], v[-.070,+.070], h[3.490,3.575]. It has45mm-wide bearing on each running ledge. It stays5mm from side plates,15mm below the top plate and5mm below the nearby suspension-bolt heads. Model it as supported new track geometry, not an unexplained floating stop.
- Normal roller-to-stop clearance is **20mm** at the commanded2.650m stroke. Mechanical contact begins at a2.670m overtravel stroke; then the complete leaf outer edge reaches|u|5.280, retaining **20mm** before the pocket outer boundary5.300. The stop engages before the leaf can leave its cavity.
- At mechanical-stop contact, the hanger stem/axle envelope still ends before the stop, and the footplate is below it. The intended contact is the outer roller/stop face, not an unexpected hanger collision. Actual stop/buffer/roller contact and deceleration remain later component/engine tests.
- Closest left/right trolley centers when closed are−.410/+ .410, leaving740mm between their40mm wheel envelopes. They diverge during opening; there is no crossing carriage motion.

No retained floor/threshold cut or raised rail is required. A motor/belt/closer and operating physics are not supplied by the existence of this track detail and remain future fitting/behavior work.

## Remaining-source contact proof and preservation

`proposed_cap_existing_source_contacts.json` screens each complete gross cap/track/fastener box against every unchanged source part, excluding only the exact six candidate cap replacements and the source's already excluded preview slab. At all three levels it finds **zero strict positive-volume AABB contacts**. Since the gross boxes contain all proposed hardware, this is conservative relative to the actual channelled geometry.

The reported boundary contacts are expected: four horizontal skin bearings per entrance and adjoining acoustic/vestibule faces at X=-34.5. These are listed explicitly; no zero-thickness touching face is silently treated as penetration or structural anchoring. The original cap meshes would obviously conflict if left installed alongside their replacements: future adoption must select the new derivative representation, never stack it onto the six old solid caps.

Before any source build, approve exact six-cap replacement/channel/fastener-hole scope, three new central heads and h3.665 maximum height. Then snapshot unaffected pure parts, source group ranges, materials and original chair bytes. Keep the original source and all frozen Godot files unchanged. Source is grouped into38 authored meshes with `pure_part_names`/`pure_part_ranges`; modifications must target the six semantic cap ranges, not rebuild or rescale unrelated members of a group.

Later acceptance requires actual new source and GLB measurements: closed/open and continuous leaf/hanger/trolley sweeps, all wheel phases and intended bearing contacts, holes versus bolts, end-stop overtravel, exact material/UV preservation, root-scale1 and correct source axes. Tiny bearing clearances are intentional component fits, not a claim that future engine-wide collider inflation can safely use them. Nothing in this report authorizes source cuts before parent approval.

Primary references: retained `contracts/fitted_door_pocket_contract.json`; `tools/extend_architecture.py` cap/skin dimensions; actual `source/geometry.json`; `tools/prepare_blender_source.py` grouping/preservation behavior; and `assets/guest_entry_door/source/build_guest_entry_door_wide.py` plus actual retained GLB evidence in `door_lift_retained_byte_evidence.json`.
