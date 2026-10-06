# Seven-asset offline diagnosis

Completed from VISUAL_STUDY004's actual graphical import-time and after-first-candidate-draw dumps. No engine was launched and no study, source, cache, gate or production file was changed. The prior plant00 diagnostic revision remains preserved.

## Concrete result

All seven exact accepted-source GLBs, 33 mesh batches and 42,540 native triangles have exact float32 position/UV correspondence with a complete cyclic triangle bijection after the documented winding conversion. Native normals match the source-derived Godot 4.6.3 octahedral uint16 encode/decode prediction bit-for-bit for every matched corner. The source-codec residual is zero.

The old scalar 0.0001 keeper remains unchanged in the evidence. It would reject 2,103 plant corners across 701 triangles. Maximum source-to-native normal delta is 0.00012435222743079066, on plant03. The deterministic documented codec accounts for that delta exactly. No position, UV, topology or native normal corruption was identified.

Every recorded array slot, including generated tangents, is byte-identical between import and after-draw snapshots on all 33 surfaces. Surface-format flags are unchanged, with attribute compression disabled. This evidence does not support a graphical buffer-readiness difference. Tangents were not authored in the source GLBs; the diagnostic establishes their presence and timing stability, not an independently regenerated tangent-authoring result.

Imported material names/classes, metallic/roughness factors, source-derived linear-to-sRGB albedo/emission values, opacity/culling, UV transforms and texture sampler settings match their exact accepted GLBs. All 32 stored texture occurrences have exact embedded-source base-level pixels and dimensions. All recorded source-node import transforms and final six replacement placements match float32 expectations; original/candidate placement transforms are identical. No material/transform discrepancy was found. A second material snapshot after draw was not recorded, so no repeated-material-state claim is made.

## Evidence

- SEVEN_ASSET_SUMMARY.json: concise per-asset findings and retained old-bound outcomes
- asset00 through asset06/DIAGNOSIS.json: independent position/UV/cyclic comparison, reproduced old matcher first failure, normal category, source-codec proof, tangent details, flags and before/after array comparisons
- asset00 through asset06/*_PAIRS.json: every triangle's source-part correspondence, predicted encoded uint16 pairs, expected/actual float32 normals and residuals
- asset00 through asset06/MATERIALS_TRANSFORMS.json: exact source-backed imported material, texture-pixel and transform diagnostics
- proposed_gate_correction/source_derived_normal_codec.patch: small, unapplied proposal replacing a guessed scalar normal-error acceptance condition with exact documented codec correspondence
- proposed_gate_correction/PROPOSED_NATIVE_GATE_CORRECTION.md: scope, sources and later review requirements

## Acceptance limits

The proposed patch has not been applied, engine-parsed or executed. It does not raise the old tolerance, change source normals or imports, or substitute material data. Exact source/export geometry and every existing physical gate remain required. Native root/soil, fixture host/receiver, route, optical leaf-shadow, visual and final adoption acceptance are separate and remain pending. This diagnostic is still labeled UNVERIFIED_IMPORT_EQUIVALENCE with installed=false and geometry_acceptance=false, matching the uninstalled study's status until the parent reviews and runs an appropriate gated acceptance step.
