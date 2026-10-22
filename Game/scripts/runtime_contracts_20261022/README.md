# Exact source contracts and mutable roof ownership — unfinished runtime repair

Parent source: 88bc4c36b95426d9bcac1b5ef16813baabe4d573. Original builders, native construction and source pins are unchanged.

The old e3af0334 export stripped import `[params]`, omitted raw scene and document bytes, and omitted imported texture source bytes needed by existing SHA guards. A sealed nested PCK restores exact source files at their original paths before the retained launcher loads; normal ResourceLoader remaps and compiled resources remain available. Export fails when any reviewed manifest input changes. Both Windows presets require the bootstrap feature. Regenerate SOURCE_CONTRACTS.json with build_manifest.py after intentional scene/import/texture changes, then review and retain the new manifest. Set ASTRAEA_CONTRACT_PACK_TMP to a fresh disposable pack path for export.

Precision evidence: all 18 affected models in the old PCK and local cache have zero compressed surfaces and identical ordered face hashes. Missing exported import metadata was not proof of compressed geometry. Original precision assertions remain intact.

The Tidal immutable-contact manager releases the distant original roof shape before the fitted roof builder reads its margin. The new successor restores that exact original contact, verifies triangles and margin/backface behavior, and transfers the one roof out of immutable residency before the unchanged cutter runs. The two-real-roof fixture reproduces the prior null and verifies both resulting shapes and margins. It does not claim whole-ship startup.

D04 investigation is separate: its loader uses partitioned detail scenes, not original whole GLBs. Three source scenes contain 130–164 unique mesh resources, no local-to-scene resources and no self-shadow meshes. Upstream Godot 4.6 RID_Alloc has a default threaded allocator ceiling of 262144 elements; the observed message is an element limit, not evidence of OS OOM. We have not yet established which lifetime/duplication path exhausted the actual run's allocator or resolved its buffered timing. No cap increase, detail deletion or visibility bypass is made here.

Court integration remains unchanged. Full startup, actual playable launch, directional frame rate, gameplay and final visual acceptance remain pending. Old e3af0334 transport bytes are untouched. Missing October20 08:49 WIP/tram source remains missing.
