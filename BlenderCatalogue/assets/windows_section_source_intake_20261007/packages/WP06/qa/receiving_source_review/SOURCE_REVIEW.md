# WP06 Long Library source and residential interface review

Review date: 2026-10-07 UTC. Status: rebuilt isolated source candidate; source/reload/export checks PASS. No render, receiving-engine adoption, structural certification or gameplay acceptance.

## Immediate interface decision

The Library's closed roof is world X8.4–53.6, Z−465.6–−398.4, Y82.9–83.2. Its enclosing perimeter reaches Y83.2 and its total footprint is X8–54, Z−466–−398. The current hash-verified residential plan has its overlapping slab underside at Y83.76, providing 0.56 m nominal geometric separation (0.557 m to the conservative Y83.203 cap). A Y84 underside would give 0.8 m, but is not the current slab geometry. Clearance does not assign the remaining interdeck band or establish load capacity. Descending residential diagonals must remain excluded until their actual geometry is checked, and may not cross the closed roof. This is a defensible geometric interface, conditional on the residential underside and later joint/engine validation, not a load-path design.

Fresh exact GLB vertex bounds with translation [8,78,−466]: min [8,77.9999998808,−466], max [54,83.2000001967,−397.9999969453]. Float-rounding excursions are less than 0.004 mm. Fresh native bounds: min [8,77.9999998808,−466], max [54,83.2000002861,−398]. No native exported shape above Y83.203. The 0.8 m buffer has not been silently converted into a permission to lower residential structure.

## Concrete vertical/plan bounds

Coordinates below are world metres, rounded from fresh native evaluated AABBs. Main lattice members are individually recorded in NATIVE_INTERFACE_AUDIT.json.

| Element | X | Z | Y |
|---|---|---|---|
| Closed roof | 8.4–53.6 | −465.6–−398.4 | 82.9–83.2 |
| Arrival panel | 8.7–38.1 | −465.3–−451.9 | 81.2–81.4 |
| Care ceiling | 39.6–53.4 | −465.6–−452.4 | 81.6–81.8 |
| Seven cross beams, aggregate | 8.4–53.6 | −451.01–−399.99 | 82.55–82.93 |
| Four longitudinal beams, aggregate | 8.79–52.91 | −465–−399 | 82.54–82.9 |
| Sixteen pier cores, aggregate | 8.74–52.96 | −451.06–−399.94 | 78.12–82.8 |
| Sixteen capitals, aggregate | 8.525–53.175 | −451.275–−399.725 | 82.645–82.895 |
| Main ceiling fixture meshes, aggregate | 14.25–45.75 | −451.1225–−399.8775 | 82.3125–82.75 |
| Arrival pendants/lenses | 12.3–36.7 | −458.26–−457.74 | 80.7125–80.89 |
| Arrival fixture mount/stem | 12.85–36.15 | −458.15–−457.85 | 80.84–81.2 |
| Care ceiling fixtures | 41.4–52.6 | −459.15–−458.85 | 81.49–81.63 |
| Care worktop task fixtures | 43.85–48.15 | −464.18–−463.82 | 80.772–81.6 |
| Oval canopy arcs, aggregate | 24.0993–43.9007 | −417.25–−400.75 | 81.175–81.425 |
| Oval bookface fixtures/arms, aggregate | 25.4282–42.5718 | −416.468–−401.532 | 81.098–81.27 |

Pier centres: X9,25,40,52.7 at Z−450.8,−435,−419,−400.2. Crossbeam Z centres: −450.8,−443,−435,−427,−419,−411,−400.2. Main fixtures lie on those crossbeams at X15,30.5,45. Longitudinal beams end at Z−465 and −399.

The source-only preview floor is Y77.85–78 over the full footprint and is positively excluded from the architecture GLB. Floor/slab ownership below Y78 and the west X4–8 external connection remain unresolved. Portal remains a source proposal, not an installed connection.

## Dependency closure and immutable inputs

All 13 dependency-map native files, totalling 6,191,254 bytes, match their expected exact hashes and byte counts in /workspace/shared/astraea-catalogue-continuation-20261002 and in the isolated staging copy. The map exactly matches WP06 asset_sources in coordination_snapshot.json; basenames are unique. The runtime builder loads all 13 prototypes even though AST-LGT-001 is not instantiated. No catalogue regeneration or other component source scripts are required.

Archive: WP06_D12_directory_02_SOURCE_REBUILD.zip, 47,553 bytes, SHA256 48d57c210af685d379c02cf3a9a185b97c1a09e0d18cda75d9f4758835193a09. All source files, catalogue dependency files and archive were rehashed after execution, unchanged. Full per-file hashes are in INPUT_HASH_RECEIPT.json and TERMINAL_RECEIPT.json.

Fresh native reload proves 81 image datablocks packed and no linked external libraries; fresh GLB contains 78 embedded images and no external image references. Together with successful reconstruction from only the verified staged files, this closes the consumed native/texture dependency set. Generated textures remain isolated outputs.

## Source safety and execution

Reviewed build_library.py SHA256 8f700e5879d798328944a5fd093ad722ed1a85fcac7d6b4ad7873bf3084bee08. No subprocess, network, exec/eval or Game/Catalogue write. SHIP/CAT variables are unused. All actual output effects are rooted at the isolated package. Top-level import creates package directories, and --build overwrites its generated output names; therefore do not run it in a surviving work tree or execute it merely to inspect it. It appends native objects with link=False, verifies each component hash and preserves/embeds image data.

Reviewed copy_dependencies.py SHA256 765e14117f207330cb64c570b51c345074c8b62b304dc4bbe929220822a51b78 confines both source/target paths, rejects mismatched surviving targets and preflights every file before writes. Root performed its restoration. Reviewed tests/check_export.py SHA256 2ddd66522f5097f96ccfc9915bd6df87945bd8c0df305174d1a53c61987dcb69 reads actual GLB vertices/transforms and writes only the isolated test receipt.

Executed /usr/bin/blender 4.3.2 with --factory-startup --disable-autoexec -t 2 --python-exit-code 1. Build, native reload plus independent audit, and exact export test each exited 0. Slot explicitly released. No render launched. Build log prints a Draco-library availability error, but Draco compression is not requested and the resulting uncompressed GLB passed vertex/material/image/light checks. No IMAGE_PRESERVE_WARNING or traceback occurred.

Current native: SHA256 fb173afafc5cbf8b0f6decd7e36303d8996458b2ed5aa5d276a87a5a80adfb0b.
Current GLB: SHA256 43dc6c2d716badcdacec5a7c66a34b88f3ced51f388862b267d259bf30e0b364.
Export: 1,360 nodes, 644 unique position accessors, 156 punctual lights, no preview floor, no bad bounds. Native audit includes 1,201 mesh/font/curve shapes.

## Remaining source/acceptance risks

1. Closed roof AABBs meet all perimeter walls, crossbeams and longitudinal beams. Capitals stop 5 mm below the roof, but intersect the beam lattice. This is a geometric contact screen, not engineering validation.
2. The 29.4 × 13.4 m arrival suspended panel's only nearby bearing architecture is the portal lintel/reveals at its west end. No broader suspended support system is authored. The care ceiling only meets the fore perimeter; it does not meet the care west/north screens. Fresh independent AABB checks confirm those limitations. Resolve credible support/termination details before visual/source acceptance; do not assume the prose promise establishes them.
3. Actual longitudinal-beam underside is Y82.54, 1 cm below the plan's rounded main underside Y82.55. Main roof underside is Y82.9; fixtures hang below beams to Y82.3125. Use actual geometry for clearance, not the simplified plan value.
4. root_review.json and EVIDENCE_SUMMARY.json refer to the historical source/GLB and images, which are not included in this source-only package. Five historical guest views predate its care-only change. They are retained provenance, not fresh visual review. Current rebuild hashes differ as expected. Contemporary visual review is still required.
5. Runtime handling/baking of 156 lights, floors, collision/traversal with loaded cart, species fit, controls and the parent-owned receiving connector remain unverified.

## Residential counterpart update

Residential coordinator supplied sf_house_r002/PLAN.json, independently hash-verified here as d0bf2e894aa2347ff50ea8580f0ff1d94c16754708732bb7ac94357f61a5775a. Its reported D13 slab underside is Y83.76, leaving 0.5599998 m above the fresh Library top, or 0.557 m over the conservative Y83.203 cap. Thus the current coexistence check uses 83.76, not the earlier conditional 84 example. No buffer ownership or support capacity is assigned by that clearance.

Excluded residential diagonals at Z−459 and −406 ran from [4.1,78.24,Z] toward court outer X−0.25,Y83.5, with 0.42 m width/depth. Removed longitudinal members at X12.1,42.2,45.8 spanned Z−466.2–−397.8, centre Y83.42/depth0.68 and would enter the Library roof. The two missing cross rows do not align with Library pier/crossbeam stations; simply adding a shoe touching roof at those rows does not establish a load path. No top bearing shoe is included in WP06. The residential coordinator will prepare a separately reviewed aligned proposal; roof/frame/downstream capacity remains unresolved.
