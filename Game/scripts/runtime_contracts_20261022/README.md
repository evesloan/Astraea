# Exact source contracts and mutable roof ownership — unfinished runtime repair

Parent source: 88bc4c36b95426d9bcac1b5ef16813baabe4d573. Original builders, native construction and source pins are unchanged.

The old e3af0334 export stripped import `[params]`, omitted raw scene and document bytes, and omitted imported texture source bytes needed by existing SHA guards. A sealed nested PCK restores exact source files at their original paths before the retained launcher loads; normal ResourceLoader remaps and compiled resources remain available. Export fails when any reviewed manifest input changes. Both Windows presets require the bootstrap feature. Regenerate SOURCE_CONTRACTS.json with build_manifest.py after intentional scene/import/texture changes, then review and retain the new manifest. Set ASTRAEA_CONTRACT_PACK_TMP to a fresh disposable pack path for export.

Precision evidence: all 18 affected models in the old PCK and local cache have zero compressed surfaces and identical ordered face hashes. Missing exported import metadata was not proof of compressed geometry. Original precision assertions remain intact.

The Tidal immutable-contact manager releases the distant original roof shape before the fitted roof builder reads its margin. The new successor restores that exact original contact, verifies triangles and margin/backface behavior, and transfers the one roof out of immutable residency before the unchanged cutter runs. The two-real-roof fixture reproduces the prior null and verifies both resulting shapes and margins. It does not claim whole-ship startup.

D04 investigation is separate: its loader uses partitioned detail scenes, not original whole GLBs. Three source scenes contain 130–164 unique mesh resources, no local-to-scene resources and no self-shadow meshes. Upstream Godot 4.6 RID_Alloc has a default threaded allocator ceiling of 262144 elements; the observed message is an element limit, not evidence of OS OOM. We have not yet established which lifetime/duplication path exhausted the actual run's allocator or resolved its buffered timing. No cap increase, detail deletion or visibility bypass is made here.

Court integration remains unchanged. Full startup, actual playable launch, directional frame rate, gameplay and final visual acceptance remain pending. Old e3af0334 transport bytes are untouched. Missing October20 08:49 WIP/tram source remains missing.

## Follow-up: transfer and D04 evidence
The Library app metadata action succeeds, but the required upload helper's connection to hosted-apps tools/list is rejected by the network proxy (tunnel HTTP403). Authorized retry again stopped before any preparation or remote mutation. This is now a confirmed route restriction, not an uncertain upload. No bypass or further retry was made after identifying403. Existing verified PCK is unchanged on temporary storage; it is not a retained backup.

A read-only census from the PCK covers all120 D04 partitioned detail scenes:19,908 main mesh resources and19,908 additional shadow meshes,39,816 summed per-room resources. None has resource_local_to_scene or a self-shadow mesh. In three real samples, two scene instances share the same164/164/130 main meshes (zero instance resource growth). This eliminates automatic per-instance mesh duplication in those samples as an explanation; it does not establish whole-ship lifetime, simultaneous residency, or the cause/timing of the laptop RID exhaustion.

Next coherent resource package: material-compatible opaque batching of immutable D04 private fittings, retaining original hierarchy/identity mappings, persistent shells and all exact independent contact cells. Include shadow-resource counts and exact triangles/material/drawing-state checks; do not remove shadowing, distant visibility or architecture merely to meet a resource count. No such optimization is implemented in this checkpoint.
