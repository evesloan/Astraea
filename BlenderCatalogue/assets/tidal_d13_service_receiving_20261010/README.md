# Tidal D13 service receiving installation

This is a bounded house-side Group1 receiving slice, derived from retained Group3 AST-STF-G3-003. It installs only D13 corridor/collar geometry, two unscaled existing service doors, three missing-only floor regions and seven fixture lights. The five-deck/shaft source is not installed. Group1 and Group3 remain unfinished.

## Source and exact joins
- D13 floorY84. Clean supply receiverX−62.8/Z−493; sealed returnsX−62.8/Z−487. The retained master, actual sources and existing house floor/allocations govern.
-64 retained editable corridor/fixture parts plus nine new collar/header/closure members produce73 meshes/1076 triangles. Both compact source exports repeat byte-identically after fresh native reopen.
-Each service door reuses service_door.gd and AST-STF-008.glb unchanged, rootedX−63.16/Y84 at its receiverZ, yaw+π/2 and scale1. The3.6m gross mouth is filled around the2.76m overall frame. Fixed jamb gap2.30m; fully open existing leaf/push hardware gap2.168m (2.166m with1mm margin each side). Actual fixed header clearance2.54m. These dimensions do not certify cart/species fit.
-Collar boundsX−63.34..−62.8 andZcenter±1.8. Each reuses1.224m² actual court floor and0.504m² approach; only0.216m² new threshold is built. Total missing-only floor289.8408m², including289.4088m² approach. Both compiled/received structural triangles and all actual imported houseY84 surfaces are subtracted; no existing floor duplication or cut.
-Actual court guard/glass batches TG_Batch_144/145 receive two local doorway openings. The original house GLB remains unchanged; all2000 unaffected original triangle point sets are retained. Earlier specialty frontage changes target different batches and remain preserved. Replacement map and actual-source evidence are explicit.
-PrivateWindowVerge startsZ−482.2; the corridor endsZ−483.86 and does not touch it. Original floor/guest identities,131 Tidal home allocations,13 Salon receiving members and public passenger lift remain unchanged.
-The unfinished shaft is physically closed atX−23.18..−23.02/Y84..87.34/Z−492.2..−487.8. Original lower staff source/capY55.6..55.74 remains unchanged. Staff stops remain[0,6,12,46.2,52.5] with five physical cabin buttons. D14–17 joins and upper staff travel stay held.

## Runtime ownership
The only changed existing Game file is tidal_garden_adoption.gd: one call after all house/interior builds. Its exact pre-edit bytes are retained in predecessors/ and ADOPTION_DIFF.patch. The new receiving helper is idempotent and refreshes only the two patched guard contacts via static_contact_cache. Floors use structural_floor_builder’s established regions format. Seven lights bind the actual retained fixture markers and are discovered once by the existing lighting budget after assembly; a later explicit installation uses the established receiving adapter. No global registry, controls, inventory, rendering stack or operating controller was rewritten.

## Bounded actual-main evidence
Final import and actual-main check PASS with zero errors: unique installation, seven lights registered exactly once,48 floor/capsule points,2000 external door-sweep shape queries, two close/open cycles, six closed-guard rays and two obstruction checks. Shaft closure and retained cap, five staff stops/buttons, public lift,85 ordinary homes,46 specialty homes and13 Salon members pass preservation assertions. Factory rebate contacts are retained and excluded from the external-architecture sweep; no claim of a redesigned factory door is made. Peak childRSS6,965,300KiB is execution memory, not gameFPS or target hardware acceptance.

The first actual-main attempt failed because its temporary blocker lived in the outer viewport, outside World360 physics. Only the fixture parent was corrected; the same bounded test then passed. Failed logs/receipt are retained.

Two actual-source native/context views were inspected. The display-only open pose was corrected to a world-axis pivot; no native/export changed. Ordinary Godot/CRT visual capture is blocked by this executor’s absent graphical display/runner, so final in-engine appearance remains open.

## Remaining work
-Upper staff lift mechanism, valid expanded controls/cabin/shaft andD14–17 receiving joins remain held
-Local linen/product/soiled-waste cupboards and cart parking, stock/restock/returns operation
-Loaded-cart/species/whole-house traversal, privacy/environmental and autonomous routines
-Primary hull transfer, structural/mechanical capacity and final Godot/CRT/performance review
-No whole Group1, Group3 or whole-ship completion claim

## Retention and reproduction
FROZEN_D13_INTEGRATION_BATCH.json maps the exact frozen source files and every changed/added Game path/hash, with the original adoption bytes. Parent owns review and publication. All work must remain unchanged while retention runs. Scripts use pinned retained source dependencies; never copy the77MB Tidal native. The test_scratch directory contains disposable execution caches and is excluded from the source manifest; sources, QA, failed attempts and predecessor bytes are retained.
