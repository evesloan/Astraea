# Inward stair guard channels 020: source-only handoff

Status: source construction, independent reopen and the prescribed 90 tread-center ray/contact/route gates PASS. A supplementary exact-corner diagnostic found retained-tread occlusion; full-tread lighting remains unresolved. No Game write, render, GLB export, runtime light, or native illumination claim.

## Deliverable

- `AST-CUL-005_inward_stair_channels_020.blend`
- Exactly 24 meshes: eight fitted closed metal C-channel/backings, eight closed opal lenses, eight simple continuous protective caps
- 256 vertices and 416 triangles total; no modifiers, hidden fasteners, manufacturing internals or unsupported load claims
- Eight non-light attachment empties, each parented to its actual lens, with energy intentionally unset
- Lightweight additive only. Original theater context remains in its existing source files, referenced by hashes rather than duplicated into this scene

## Actual source proof

The build appends four retained guard/tread groups read-only from the dfb source, verifies all 98 source-part fingerprints (eight mount guards and 90 treads), extracts the actual saved geometry, then removes those temporary reference groups before authoring. It never opens an original for editing or saves to any original path.

Every backing has a broad rear contact face on the actual retained guard plane. The channels follow each guard slope, sit 160 mm below its top and stop 20 mm short of each end. Their maximum inward depth is 16 mm, and each lens is 25 mm high. The protective cap and lens are in real contact with the closed channel profile.

Actual reopened checks:

- All 24 meshes closed, nondegenerate and consistently wound, with positive signed volume
- Eight exact mount-plane contacts; zero fitted-volume penetration into retained static geometry
- 14.003754 mm minimum new-geometry clearance beyond the unchanged 3.2 m tread edge; 13.003754 mm remains after the existing 1 mm collision margin
- Zero new-geometry intrusions in all 90 full-width tread footprints through 2.1 m above each tread
- Eight actual lens optical exits, each 4.001617 mm behind its source attachment
- 90/90 tread-center rays clear against retained static, actual guard/tread references and the newly authored fixture geometry
- Geometric range proposals remain 4.8–5.7 m; energy, in-engine selection, illumination and budget acceptance remain untested

## Supplementary corner diagnostic and important limit

After the prescribed gates passed, a pure diagnostic added four exact tread-corner receivers per tread, 50 mm above each top, alongside the 90 centers. Of the 450 samples, 270 are clear and 180 corner rays hit retained stair geometry. Among those, 118 are exact shared-edge endpoint contacts and 62 encounter retained geometry before reaching the receiver. The new fixture geometry blocks none of the 450 samples. The original 90 centers remain clear.

This negative result is preserved in `TREAD_CORNERS_QA.json` and classified in `TREAD_CORNER_CLASSIFICATION.json`. It prevents any claim of complete tread-surface illumination. The source geometry and the agreed eight attachment positions are unchanged; no extra fill source or energy change was introduced. Actual illumination, shadows and any later lighting decision require a separately authorized native trial.

## Retained finish contracts

- `ASTRAEA_champagne_metal`: exact retained graph and packed texture, 0.6 m × 0.6 m tiles
- `FP_PRACTICAL_AST-CUL-004_staff_opal`: exact retained textured opal graph, 0.75 m × 0.75 m tiles
- Every face has orthonormal physical metric UVs divided by its assigned material's tile scale. Maximum reopened UV error is 0.000000318.
- The retained opal graph's source appearance is unchanged. No light datablock or watt/energy setting was authored.

The original public GardenOpal graph is untextured, so it was not substituted for the requested actual textured opal contract.

## Evidence

- `SOURCE_CONTRACT.json`: initial recipe, exact input hashes, material and fit contracts
- `PURE_GEOMETRY_QA.json`: preparation-stage gates
- `EXECUTION_MANIFEST.json`: pinned two-thread, serial source job
- `BUILD_RECEIPT.json`: actual source-part and material fingerprints
- `ACTUAL_SOURCE_RECIPE.json`: geometry derived from actual source references
- `SOURCE_REOPEN_REPORT.json`: saved mesh, material, UV and attachment read-back
- `REOPENED_GEOMETRY.json`: actual saved world vertices and attachment positions
- `SOURCE_GEOMETRY_QA.json`: closed meshes, mount contact, route/headroom, optical exit and 90 receiver checks
- `TREAD_CORNERS_QA.json`: preserved negative supplementary corner diagnostic
- `TREAD_CORNER_CLASSIFICATION.json`: 62 pre-receiver occlusions and 118 endpoint-only contacts
- `SOURCE_JOB_RECEIPT.json`: successful build/reopen/prescribed QA execution
- `FINAL_PRESERVATION_CHECK.json`: original c911, dfb, walking-contact source and all other pinned inputs remain byte-exact

## Boundaries

This is complete as a scratch-only source derivative, with the lighting limit above. It is not installed, independently retained outside this workspace, exported, rendered or accepted for native illumination. Original outward fixture architecture remains unchanged. Whole-theater headroom, runtime traversal, structural safety and photometry are not established by these additive-geometry checks. Any later source-only GLB, scene integration, rendering or Game change needs its separately coordinated scope.
