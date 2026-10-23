# D04 bounded prefetch candidate — default off, not production-integrated

Separate successor after a3e713ed texture-lifetime repair. The texture fix, frozen delivery and original managers remain independently identifiable. This package does NOT establish a RID-exhaustion fix, playable frame rates or crash causality.

## Evidence and scope

The actual installed D04 manager uses the120 runtime_r004 shared-resource scenes. Its _load_entry synchronously loads/instantiates scenes; visibility callbacks and refresh can request multiple rooms together. This successor retains those exact scene paths, identities, shells, collision manager and release policy. It does not pool nodes or the whole ship.

At most TWO resource requests/ready PackedScenes exist in this manager at once. ResourceLoader.CACHE_MODE_REUSE preserves shared immutable resources. Prefetch is limited to existing visible demand or the32m neighborhood. Resources are evicted immediately when no longer relevant; ready speculative slots can yield to actual visible demand. Near-but-not-yet-visible ready resources may remain within that neighborhood, bounded by the two-slot cap, avoiding periodic unload/reload churn. There is no global strong warm cache.

Threaded loading and main-thread activation are separate. load_threaded_get is called only after THREAD_LOAD_LOADED. Stale completed requests are retrieved/drained but never instantiated. No rendering node is instantiated on a worker thread. A queued far-visibility path activates at most one room per process tick and stops dispatching when its2ms scheduling budget is spent. Individual SHA verification or PackedScene.instantiate cannot be preempted: activation_max_us and activation_overruns expose overruns. This is NOT a hard2ms frame guarantee.

Explicit arrivals/startup and near-player/rigid-body demand keep the original synchronous fallback. This protects preparation behavior and means some movement activation spikes remain possible. Actual target profiling must justify any later expansion of scheduling. Active instantiated MeshInstance3D/materials retain their Resource references; a ready PackedScene provides a strong lease only while in its counted slot. No RID-only pseudo-ownership is used.

## Opt-in integration boundary

No production entry scene, source manifest or manager file is changed. After runtime_ready, with ASTRAEA_D04_PREFETCH=1, a separately coordinated test can call `load("res://d04_prefetch_20261023/install.gd").install(ship)` once. Default returns disabled without mutation. Installer requires the exact predecessor manager hash,120 entries and existing shared-D04 predecessor receipt. It changes the SAME manager node's script and restores host/index/entry/counter state; shell, room and manager identities remain unchanged. Existing inherited release, contact preparation and visibility thresholds remain.

Do not combine first comparison with D04 surface batching or the texture fix in a way that obscures effects. Keep weak-texture fix on its own named baseline when measuring this successor. A native export would need a separately verified manifest/entry integration; none was built here.

## Focused checks

- Synthetic request lifecycle: cap2, duplicate suppression, stale invalidation, at most one queued activation/tick, ready resource eviction and inherited release passed.
- Installer: default-off and same manager identity/index/120 records/counters preserved passed.
- One actual retained D04 scene:150 meshes, exact faces/transforms/surface counts and shared Mesh resource IDs equal the direct control; release cleared owner and pool. Existing PCK supplied previously imported textures; no import/build. First attempt without that retained import mount failed on missing ctex dependencies, not counted as a pass.
- No full ship, laptop run, target FPS or native release acceptance.

## RID diagnosis and remaining gate

User crash logs report33459 allocation-limit errors followed by null GLES3 meshes/collision failures. A per-owner live RID limit is not cumulative allocations. RendererSceneCull's instance owner has a different explicit limit from default GLES3 mesh/texture owners. Error count and downstream null meshes do not identify the failing owner. Do not raise limits or claim this candidate resolves exhaustion.

Correlate the laptop's preserved callsites and built-in CPU/render profiler with room loads/releases, current mesh/texture resources, memory, queued requests, activation cost and fallback loads along the same route. Verify no missing distant views/pop-in, collision regressions or sustained resource growth before adoption. Full fidelity and whole-ship acceptance remain separate.

Official references:
https://docs.godotengine.org/en/4.6/tutorials/io/background_loading.html
https://docs.godotengine.org/en/4.6/classes/class_resourceloader.html
https://docs.godotengine.org/en/4.6/tutorials/performance/thread_safe_apis.html
https://raw.githubusercontent.com/godotengine/godot/4.6.3-stable/core/templates/rid_owner.h
https://raw.githubusercontent.com/godotengine/godot/4.6.3-stable/servers/rendering/renderer_scene_cull.h
