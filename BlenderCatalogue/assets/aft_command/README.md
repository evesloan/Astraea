# Aft D18 command construction · AST-CMD-002

Editable construction for Ship status (`D18_directory_08`) and Emergency control (`D18_directory_10`), their screened approach, and an expressed keel/roof/platform support chain. This is an unfurnished architectural platform, not a finished command simulation or structural load certification.

## Source and integration

- `source/AST-CMD-002.blend`: 1,006 independently editable closed outward mesh parts and 33 exported datum empties
- `exports/AST-CMD-002.glb`: 12,072 triangles in 196 spatial/material batches, no batch over12m
- `source/build_aft_command.py`: deterministic source authoring and optimized export
- `source/section_contract.json`: world-origin coordinates, programmes, four working-door anchors,24 light markers, support interfaces and remaining runtime requirements
- `source/geometry_parts.json`: every authored part's world vertices, material role, group and bounds
- Blender coordinates `(X,-Z,Y)` correspond to runtime `(X,Y,Z)` with glTF Y-up export
- Parent owns two new floor rectangles: X−36..−4 and X4..36, Z80..102, Y106.26..106.5. Their total1408m² excludes the unchanged176m² central route. No floor slab or duplicate moving door is in this kit
- Use the existing `AST-STF-008.glb` and shared controller for all doors. No access-control system, dedicated all-deck staff lift or new controller is asserted

## Connected architecture

The two936m² room shells occupy X−36..−10 and X10..36, Z66..102. Two5m gross side corridors sit between X±5 and X±10. New doors at X±7.5/Z66.2 face the retained6m street. Room doors at X±10/Z82 connect to these corridors. The X±4 public route remains clear.

Two audited0.8×1.2m full-height piers at X±35.5/Z86 meet the actual keel datumY−3.2. Their newZ86 transfer frame connects to the existingZ71 frame through seven longitudinal roof members. Eight wall-zone hangers connect to four underfloor edge girders and twelve transverse bearer spans. Four ties positively embed into actual compiled D18 apron triangles atZ80. Three small saddles at X−32/0/+32/Z66 connect the forward purlin to the lower existing roof beams. Maximum roof height is114.44m.

The institutional textured materials, deep thresholds, ceiling bay hierarchy and visible fixture lenses carry this shell increment. The supplied reference pixels were reopened for composition and ceiling/threshold relationships. Broad interiors and activity zones remain unfinished; no furnishing detour or final-art claim is made.

## Bounded existing-crown revision

`AST-CMD-001` retains all six room identities, ten prior doors,74 fixtures, glazing, roof and four original spines. Only two existing side-corridor endcaps atZ59.81..60 receive fitted apertures, plus two door anchors at X±7.5/Y106.5/Z59.8. No new threshold canopies were added there. Actual-source comparison records no out-of-scope mesh or marker changes in `../central_crown/qa/aft_endcap_interface_diff.json`.

Central source now has2,727 parts/32,724triangles/634 batches. The earlier export remains recoverable from Git commit `5918f89a9ff913bd6077f2a7464f4bef66292dac`; it was not restored over any newer work.

The old end-door complete fixed-frame/moving-mesh union spansZ58.63..59.98; the new fronts spanZ66.02..67.37. The full6m public belt is clear. Public/staff crossover through that street is explicit.

## Verification

Run from the catalogue root with Blender4.3.2:

1. `blender -b -t 2 --python assets/aft_command/qa/verify_aft_command.py`
2. `blender -b -t 2 --python assets/central_crown/qa/verify_central_crown.py`
3. `blender -b -t 2 --python assets/aft_command/qa/verify_material_fidelity.py`

Checks include closed/outward source parts, nondegenerate faces, metric UVs, complete triangle/material/UV roundtrip, exact bidirectional source/export vertex positions, preserved datum markers, bounded batches, actual shared-door moving geometry and fixed-frame seals, fixture exits, all purlin bearings and positive support-chain contacts. The combined16-door one-degree sweep evaluates13,104 moving-part poses. Independent review repeats all six new/revised door assemblies at0.5° and intersects actual compiled floor triangles.

The initial independent review found the forward purlin lacked a direct beam seat. The added three saddles resolved that finding; final verification is `PASS_SOURCE_GEOMETRY_PENDING_PARENT_RUNTIME`.

`qa/material_fidelity.json` separately verifies all used material parameters, effective emitted RGB and packed texture bytes for both revised exports. All159 other catalogue entries and477 source/export/manifest files match their protected baselines.

`qa/source_*.png` are source-only construction diagnostics, including temporary context floor/door/light objects. These context objects are not saved or exported. They are not Godot views or target-hardware measurements.

## Remaining acceptance

Parent must adopt the single compiled floor owner and updated source contracts, refresh model imports, run actual collision/support/light queries, operate all six added doors, walk and guide the loaded cart through both rooms and both crossings, and revalidate affected central/whole-ship routes. Review ordinary first-person views and moving camera behavior in the existing renderer. Final architecture, furnishing, command use, species/occupancy behavior and target-GPU performance remain open.
