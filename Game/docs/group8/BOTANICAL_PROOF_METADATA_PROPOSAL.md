# Botanical successor proof: scoped metadata proposal

The existing gate still fails before Godot, with exactly five current-pin mismatches. No shared proof, guard, runner, root or registry was edited. The proposed bytes target only inspected main `bc731d6d6d54bb2595331ee2f4368558d4d24fda`; the integration owner must regenerate against its exact final HEAD if it adds other root calls.

Four old pins match actual source at consolidation commit `61d08dc0c1f27226df961aa43327a60f81bace77`. The old cache pin matches the exact immutable `predecessors300/scripts/static_contact_cache.gd` source; the consolidation already had a different cache successor. Every old/current byte set was compared with independent GitHub-derived objects in a clone with no local alternates. `BOTANICAL_PROOF_METADATA_PROPOSAL.json` records complete old/new SHA256, source paths, commits and Git blob IDs.

| Game path | Old proof pin | Actual current-main pin |
| --- | --- | --- |
| data/architecture/botanical_pair/runtime_manifest.json | ed4a2b791837f11968ef72ccde57f2ac1307324b9bedbf178381eb7d713c011b | 7a02ef52703793f88ab36b5d48d96022bb5c48d28e602edd618c08cd9aafede0 |
| scripts/lighting_budget.gd | 73366f8831a591473355c9d15a5de8ae0e63c59bdf3b8cd1b1abe7663d1f7337 | 99a1b9c1e986acc11c9b03a9a65515108e38a217a58a648b21cc68abac9d4c3a |
| scripts/ship.gd | 93f7145ffdb78f735f961f5c632dc9f1017ebd261af909b16c126c28ca297f32 | a41443e83359b1a2d9642d178faf804dbcdaf6ed5e0ca715ea98ab53967aff24 |
| scripts/static_contact_cache.gd | d3440479423f19660a6e68af2f730549644eb9ff1f86ccf3254a4e0589c58e35 | 4ebe68081d5bf1d0b433ce93c4cb2d9c8bca0192a301fa11a0c2b58d5a86b049 |
| tools/validate.py | bc51129177f8f268805e30efe7e4634f2feb644699c65e2ebf1a2487f5b3fbc8 | 85dc65990258161db9710d0a194f3caeceadd9dcbc147e5638a8e7dc42302b95 |

A five-hash update alone is insufficient: ship.gd and tools/validate.py also have exact whole-file inverse records whose `after` strings contain the old complete files. The concrete proposal changes those two `after` values to verified complete current-main source, preserving each original `before` and count1. All six inverse chains then reduce exactly to their immutable predecessors. The other131 of136 current proof inputs match; all27 predecessor hashes pass. Static source checks reproduce the exact303→300 region/order/void/compiler/receipt predicates, including only three additions and unchanged original records. This is source authentication, not a runtime or acceptance result.

The Botanical manifest changes only its top-level `lighting_budget` metadata. Actual shared code successors include local light selection/cache optimizations, added destination construction/trace/residency calls and added unrelated runner checks. Their exact old/new source diffs are retained. Original Botanical validation/build, runner/preflight/checks and timeout predicates survive. Current lighting/cache behavior still requires runtime regression; it is not represented as unchanged old behavior.

Concrete proposed payloads are in `BlenderCatalogue/assets/group8_arrivals_service_20261011/`: `BOTANICAL_RUNTIME_PROOF_PROPOSED.json`, `PROPOSED_botanical_pair_successor_guard.gd.txt`, and the single-literal `BOTANICAL_GUARD_PIN_PROPOSAL.patch`. Original proof SHA256 is `2f50c3b696485769ee7c37480f33e4f4858efe71edeae34b342a047864390039`; proposed proof SHA256 is `8c366679f70d93a051186ac168129d80592f07b991d7502440dc2035c7499f14`. The normalized guard SHA256 remains `2b285c89ad6dfe989eec9307b1256d6500b6826ec8e0f26918a69f8fff63c1df`; no assertions, prerequisites, compiler pins, counts, original predecessor bytes or acceptance flags change.

The owner may apply those two exact files after rechecking its final HEAD, run the unchanged preflight and guarded Botanical checks, and then the appropriate shared validation. A cleared metadata preflight permits tests to run; it does not establish a shared-suite pass, ordinary visual approval, loaded-cart operation or Botanical acceptance. Until then the original gate is deliberately failing. Source/proposal receipts and the first rejected audit comparison remain retained.
