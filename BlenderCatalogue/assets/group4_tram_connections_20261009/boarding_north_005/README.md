# Group4 batch005: reusable boarding bridge and north fore-midship source proposal

Frozen source-only construction. Neither asset is installed; Group4 remains open.

## Useful result
- AST-TRM-G4-019 is an editable 44-mesh / 732-triangle bridge component. Four unaffected station placements pass bounded deployed/intermediate/stowed checks against actual retained station and vehicle exports. Its source roots and pivot are explicit for the existing operating system.
- The original frozen fore-midship station intersects installed Paper Moon in 24 exact triangle-pair contacts. The old lower-annex proposal also overlaps 59.2 m² of actual received Paper Moon floor. Both existing sources are preserved; the old station/bridge placement is held.
- AST-TRM-G4-020 is one separately authored 173-mesh / 2,780-triangle north candidate. It keeps FORE_MIDSHIP and master catchment Z−216, while proposing physical docking Z−241. One bounded source screen is clear against Paper Moon, fore-midship public core, existing D09–D10 core stairs, Orchard Exchange, Thread & Shell and one actual long-body car pose. This does not adopt the new docking coordinate.

## Bridge receiving and operating interface
Use BRIDGE_INTERFACE.json. Source metres/Y-up; local +X faces the vehicle and local +Z runs along the portal. Both bridge roots have an explicit hinge datum at local (0,0,0). Width 2.18 m, nominal gap 1.0925925925925928 m, separate cabin tongue 20 mm; deployed reach 1.1125925925925928 m. Tongue top is 1.5 mm above boarding floor. The proposed stow is local Game Z+90°, without a supplied driver. Fixed root has 23 meshes and moving root 21.

Four screened placements: forward (−3.4,56.1,−432), aft (−3.4,56.1,432), aft-midship (−3.4,56.1,216), all yaw π; central (−2.2,56.1,−72), yaw 0. Vehicle anchors and exact source hashes are in the interface. Sixteen positive anchor volumes and four cabin tongue bearing areas of about 0.0436 m² are geometric receiving evidence. Root integrates the existing E/RMB controls, pause, docking, gates, interlock and physical carry/collision. No parallel controller or cart/stock copy is supplied.

The old fore-midship bridge placement (−7.8,56.1,−216), yaw 0, is held. Proposed north bridge datum (−7.8,56.1,−241), yaw 0, is an interface proposal only; its three-pose bridge fit remains unverified. Do not silently assign it to a runtime stop.

The first bridge fit found 16 moving collar/slab contact pairs at 45°. Only the owned collar profile was corrected to its forward quadrant. Final four-station 0°/45°/90° checks are clear. No continuous motion or exhaustive route campaign was performed.

## North candidate: exact root decision and receiving boundaries
Use NORTH_STATION_INTERFACE.json and NORTH_STATION_LOCAL_SCREEN.json. Old physical boarding Z−216 → proposed Z−241 (delta −25 m), retained master catchment −216, actual core −272. Root must explicitly accept that physical-stop change and bind route docking, destination arrival/wayfinding, two-stop lift root/IDs and bridge. No runtime stop or existing source has changed.

The proposed platform is X−13.2..−7.8 / Z−251..−229. Proposed lift root (−11.2,0,−225), yaw −π/2, stop IDs G4_FORE_MIDSHIP_LOWER and G4_FORE_MIDSHIP_BOARDING at Y52.5 and 56.1. Existing commons_lift.gd and AST-CIR-003 remain the intended system; no lift controller/cabin is duplicated here.

Three new lower cantilevers sit beneath actual wheel minimum Y55.74; they have three full 0.315 m² floor-pad contacts on retained owner D09_fore_route. The proposed annex is X−13.6..−4 / Z−265.5..−221.2 and excludes 51.3 m² of actual D09_fore_midship_public_core_floor. It has no overlap with Paper Moon floor/connection owners. Four exact missing-only floor rectangles are listed in the interface/screen. No annex floors are exported and no retained slab is cut. The wholly new 17.6 m² lift recess X−13.4..−9 / Z−225.2..−221.2 remains root-owned. Secondary stairs, upper return, lower-annex and lift-frame receiving remain unfinished; geometric contact is not load-capacity acceptance.

The retained central starboard polyline, port trunk, central 17.6 m² uncut recess/floor owner, all 83 installed sections, operating lifts/doors, house/aquatic allocations and all Gallery bypass reservations remain protected.

## Evidence and bounded acceptance
SOURCE_BATCH_CHECKS.json: actual exported geometry is finite, non-degenerate and matches native world recipe bounds; bridge checks cover only three stationary poses at four unaffected stations. NORTH_STATION_LOCAL_SCREEN.json: one local candidate and one actual car pose, plus actual generic and received floor owners. NATIVE_PORTABILITY_CHECK.json: both saved natives reopen, five verified material images packed in each, byte-identical compact GLB re-exports. Three actual source-view PNGs were inspected; north context partly obscures deck/stairs, so it does not establish full visual or access acceptance.

RETAINED_SOURCE_PINS.json binds actual architecture/registries, materials, reference pixels, master application, helper dependencies and all four unchanged prior frozen slices. Build scripts reuse those retained source materials/helper prefixes. A recovered project may relocate R in the authoring/check scripts before re-running; never overwrite prior frozen sources. Blender exports and source images are final for this batch.

No Godot import, main-world run, controller change, upload or publication was performed by the helper. Main-world receiving, live boarding/carry, all species, mechanical/structural capacity, remaining destination connections, guest transit and final performance remain open. See the complete 16-item REMAINING_GROUP4_CHECKLIST.json. Independent parent retention is the next delivery gate.
