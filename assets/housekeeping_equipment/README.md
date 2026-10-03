# Original housekeeping equipment

Two original editable Blender designs for the historical D01 housekeeping/laundry programme. The technical blueprint and both staff-corridor photographs were inspected: pale folded surfaces, zinc protective returns, dark kicks and organised service faces informed these components. No reference pixels are runtime assets. These are unplaced components; the original ship is absent.

- AST-HSK-001, faceted cloth-treatment appliance housing: clipped protective plinth, deliberately sloped white casing, actual eight-sided loading chamber, supported full hatch, original inactive controls and a removable reverse maintenance face. The dark inspection inset is opaque and inactive. The useful chamber and optional capped interfaces assign no process, plumbing, electrical connection or species compatibility.
- AST-HSK-002, open tier drying and conditioning rack: three real rail-supported tiers, a modest hollow folded hood, a retained sliding middle carrier and a removable rear service panel. No floating cloth is used to imply operation. The rack's accessible rail volumes are distinct from storage cabinetry.

## Source and states

Source XYZ is metres, Z-up, with front −Y. Native GLB maps (x,y,z) to (x,z,−y). The floor origin sits between real supported runners. Each source retains named semantic meshes, real movement roots and separate physical/contact and nonphysical proposal markers. Moving markers belong to their actual moving roots. Exports join only by material role and real moving ownership.

Open source/AST-HSK-001.blend or source/AST-HSK-002.blend. Primary files are exports/AST-HSK-001.glb and exports/AST-HSK-002.glb. The _hatch_open, _retrieval and _service_open derivatives are states of those two designs, not additional catalogue designs. Hatch and carrier motion starts at true zero. Rear service panels are detached handling poses and require hand support; their translated display does not claim a floating or retained mechanism.

The appliance closed envelope is 1.20×1.15×1.70 m, including both grips. The rack is 1.20×0.826×1.98 m. These are adjustable source proposals; no actual room, aperture, overhead-services or body fit is proved. Whole motion/reservation limits live in qa/geometry_checks.json, separated from useful empty receiver volumes in each manifest.

## Rebuild and evidence

From the catalogue root run:

`blender --background --threads 2 --python-exit-code 1 --python assets/housekeeping_equipment/source/build_housekeeping_equipment.py`

The generator regenerates both original control images through source/draw_controls.py. That script uses explicit original encoded glyphs and Python/Pillow, with no machine-font dependency. Only the unchanged staff material helper, manifest and all nine loaded staff PNG roles accompany these two source scripts. dependency_manifest.json lists the exact original input closure. No old .blend, .glb, generated artwork or QA report is needed as a seed.

The primary appliance has 1,108 evaluated triangles and 11 material/ownership groups; the rack has 780 triangles and eight groups. All common materials remain unchanged. Detailed collision descriptions retain each exact authored convex solid and real mechanism. The optional body candidate is a literal subset selected while authoring, not a new asset-sized hull. Fine journal sleeves, pins and caps stay in the precise mechanism set with separately stated omission-distance limits; useful floor, loading, controls, grips, rails and empty chambers remain explicit. The candidate is not adopted engine collision and is not a target-PC performance result.

qa/check_sources.py reloads actual editable sources, verifies whole convex parts, packed materials, nondegenerate triangles/UVs, physical marker normals and exact support witnesses. qa/check_geometry.py tests complete movement and useful voids with full finite solids; rotation uses two-degree bounded arc enclosures rather than sampling a few grip points. The entire octagonal bore and the declared hood service volume are tested against every whole part. A positive inserted-solid control checks the chamber test. Retained journals have actual annular sleeves, through pins, supporting brackets and axial retainers; rack guides have real fixed bearing support and upper retaining lips. These are geometric proposals, without load, wear, locking or tolerance certification.

Failed early contact and motion evidence is retained under qa/failed_r02 and qa/failed_r05. Final source-bound imported pictures and independent receipts are separate evidence. No original game, room, staffing/capacity, player cart, chore loop, species role, biological process, active cleaning/drying cycle, heat, airflow, certification or runtime controller is added.
