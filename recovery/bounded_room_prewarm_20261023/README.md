# Bounded complete-room prewarm candidate — DEFAULT OFF, UNACCEPTED

Experimental additive overlay on independently verified be4ec34880cdab7794592c2bff3bed789ad52c4f. Retained source, production selection, source assets, saved workspaces and original tests were not modified. This package is not production integration and does not claim to fix the reported crash, achieve 60 FPS, or complete residential art.

## Exact scope

The existing shared visibility scheduler owns at most one speculative job OR one complete off-tree ready lease across received/private managers. No second scheduler, ship-wide pool, resident eviction policy, new geometry or collision simplification is introduced. Strong references retain the exact prepared meshes/materials and contacts, including first shape-to-collider binding. Ready follows the complete body phase. Shader compilation/first draw are NOT prewarmed or certified.

The existing registered 3D AABBs select interest outside mandatory near admission and within retained keep bands: received 45/65 m, private 24/36 m. Actual visibility is never faked. A ready lease is atomically consumed before the original visibility, near or prepare_position load. Cold/late/unknown/oversize misses use the original synchronous path rather than deferring missing room coverage across staging frames. This deliberately retains cold hitches. Same-owner arrival promotes or cancels, rather than disappearing as a deduplicated request. A partial safety takeover can temporarily overlap the original synchronous resident and one cancelled orphan; ownership remains until threaded loading drains. There is no hard total memory promise.

Existing visible complete residents and eight-second hidden grace are preserved. Group2 cached/controller rooms, D04 and special Night Garden partition loaders retain their original exclusions. Only the two hash-verified prototypes have admission estimates: TIDAL_ROOM_01_r001.glb and StarAtlasSpecialty_103.glb. Unknown sources do not allocate speculative scenes and cannot starve eligible sources merely by being nearer.

ASTRAEA_ROOM_PREWARM=1 additionally requires the existing ASTRAEA_ROOM_ACTIVATION_QUEUE=1, ASTRAEA_STAGED_ROOM_ACTIVATION=1 and ASTRAEA_PACKED_CONTACT_FACES=1. Private details still require ASTRAEA_PRIVATE_CONTACT_SINGLE_PASS=1. All defaults remain off. Existing flags remain independently usable without prewarm.

## Bounds and identity

Admission checks the exact source GLB, source/import settings, PNGs and recovered imported .scn/.ctex bytes before allocation. Static GLB counts and decoded texture dimensions produce conservative data allowances of 35,515,232 bytes for Tidal and 64,980,528 for Star103. Caps are one lease, 2,048 nodes, 1,024 mesh instances, 240,000 face vertices, 4,096 estimated resource objects and 96 MiB estimated owned data. These estimates are NOT measured native allocator/GPU/RID limits. Instantiated node/mesh/face/resource checks fail closed before configuration or collision work if importer output exceeds the receipt.

This experiment assumes the source/import pack remains immutable while running. A source/policy replacement must increment entry.prewarm_generation before reuse (or tear down the scheduler and reload the receipt). Consumption checks exact owner and room/home identity, path, retained scene identity, record/collision policy, flags and generation, and rejects existing residents/double attachment. It deliberately does not hash files on the arrival path. In-place hot mutation without generation invalidation is not supported. Receipt verification cost is separately reported before preparation, including failed admissions.

## Verified headless results

Official Godot 4.6.3.stable.official.7d41c59c4, minimal empty cloud project, verified retained import pack plus hash-checked source overlay. No editor import, export, production main, full-ship launch or laptop access.

- Retained connected fixture: PASS with original criteria unchanged.
- Candidate with prewarm off: PASS with original criteria unchanged.
- New actual-manager prewarm fixture: 346 checks, zero failures. Covers six warm hits through explicit arrival, visible manager entry and queue promotion; immediate synchronous cold misses; oversize/unknown admission; threaded-load, configured and ready cancellation; neighborhood reversal; synchronous partial safety takeover; generation invalidation; preserved visible resident, shell/rest identity and supported-path flags.
- Three repeated warm/release cycles return to 121 nodes, 124 Resource objects and two persistent shell contact shapes. Baseline had 123 Resources; the extra helper script explains the extra object. Static allocated memory rose from 63,029,741 to 63,104,985 bytes across these samples; this is NOT a demonstrated whole-route memory plateau or RID-owner census.
- Full scheduler warm consumption (identity checks, exact attach/physics binding, disposal and scheduler bookkeeping): received 475/682/789 us; private 2,515/2,748/2,774 us. Private remains above the 2 ms soft budget.
- Cold original fallback observations: received 53,300–62,268 us; private 81,095–91,954 us. These include visibility, safety, generation-invalidated and visible-retention test flows, not only one uniform arrival condition.
- Preparation remains expensive: source verification up to 8,470/18,034 us, native shape creation up to 11,562/16,996 us and first body binding up to 11,278/14,375 us (received/private). These costs move ahead of arrival; they are not eliminated or hidden by the scheduler. Individual scene, material and native calls are not preemptible.

See RESULTS.json for compact measurements and evidence/PREWARM_RESULT.json for every recorded stage. Headless process time is not game FPS. First-visible render time and cold visible coverage under real renderer notifications remain unmeasured for this candidate.

## Render gate: UNEXECUTED

The prepared visual_gate.gd uses actual VisibleOnScreenNotifier3D, identical baseline/warm/cold cameras, exact geometry/contact signatures, floor rays, first-visible and final captures. Both first-visible and final image comparisons require ZERO changed channels. No tolerance was added.

No display existed. A transient existing Xorg/dummy-driver attempt failed to create local/unix listening sockets. The standard scoped escalation then failed in executor setup before Xorg launched. No permissions/settings changed, restricted path touched or alternate transport attempted. Thus no new rendered images exist and no visual acceptance is claimed. The retained prior private final one-pixel/three-channel mismatch remains unexplained and blocking; its gate was not relaxed. The initial unrelated headless attempt also failed before fixture execution because default user/cache directories were not writable; writable test-only XDG directories resolved that environment setup. Failed attempts remain indexed separately from successful tests.

## Reproduce and review

The source deliverable is payload/Game, candidate.patch and MANIFEST_DELTA.json (exact preimages and replacement/addition hashes). Do not overwrite retained production or apply over unknown source. Root publication owns independent retention; no publisher/watcher was started here.

Portable fixture inputs are fully enumerated in FIXTURE_INPUTS.json: each res:// URI, exact SHA256/byte count, retained repository path at be4ec348 and/or exact retained PCK entry. No prior workspace maps or absolute paths are needed. Materialize the referenced Git files at any repository root; supply the retained Astraea-e3af0334.pck with SHA256 20b4151d52eca611e4c05073d567dcba07ee2f37bf99c2a9f14f679be7da7329. These assets remain retained separately, not duplicated in the code package.

Set ASTRAEA_FIXTURE_REPO to that Git root and ASTRAEA_FIXTURE_BASE_PACK to the retained pack. prepare_fixture.py also accepts --repo/--base-pack directly. It verifies the entire pack hash, verifies precise source preimages, extracts only required imported entries with the included read-only PCK parser (no conversion), verifies each byte contract, then regenerates the small source map. Already materialized inputs must match; it never overwrites mismatched files. Runtime fixtures use a new minimal focused-project, never --main-pack or production main.

1. bash run_focused.sh baseline
2. bash run_focused.sh candidate
3. bash run_focused.sh candidate prewarm_check.gd
4. Only with an approved already-running display: DISPLAY=... bash run_visual.sh

The published prewarm_estimates.json is already pinned. build_estimates.py is the original static receipt-generation helper and additionally expects the documented takeover acquisition layout; regenerating estimates is not required to run either fixture. Metadata-only portable map resolution was added after final runtime tests; its Python syntax and all URI/hash mappings were checked without duplicating assets or rerunning Godot.

The connected fixture differs from retained connected_check.gd only in explicit map/pack/overlay path plumbing and omission of a redundant old nested source pack. Original assertions, samples and cancellation criteria remain unchanged. Test scripts and a compact failure index are published; raw failed-attempt logs remain local. Generated overlay PCKs, imported assets, XDG caches and temporary fixture project are disposable and excluded from publication.

Acceptance remains open: actual first-visible/final pixel gate, the prior private pixel discrepancy, broader prototype/prediction misses, sustained whole-route memory/RID behavior, whole-ship startup and target-hardware performance. Do not enable by default or advertise completed optimization from this package.
