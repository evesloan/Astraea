# Exact material-free shadow sharing

Baseline9ace1ca5. Only production mesh_lease.bind/resume call the new weak shadow_mesh_pool helper. One existing contract updated, one added:18139 total. Original GLBs, main meshes, material resources, UVs, controllers and collision resources remain unchanged.

Source788 owns1324 main and1324 shadow Mesh RIDs. Its meshes expire after source release. Normal laptop execution succeeds; sandboxed diagnostic launches crashed before their first script marker. Those startup failures do not establish a production fault. Windows Application-log read was denied; no permission changed.

Material-free shadows duplicate geometry under material-name labels. Sharing compares exact complete stored bytes, including LODs, bounds, vertex/index layout and format, excluding only display/resource labels and shadow surface names. Main surface names and materials remain untouched. Scripted, local, morph, nested or material-bearing shadows are skipped. Weak cache references cannot retain GPU meshes. Digest matches also require byte equality; changed resources invalidate cache entries. No runtime shadow-geometry authoring is introduced.

Two-cycle focused test:39724 checks, zero failures;6620 main RIDs unchanged, shadow RIDs reduced from6620 to424. All mesh weak references expire after each cycle and cache prunes fully. Three integrated rooms788/812/818 retain exact geometry/material values, transforms/parents, two door identities/states and21 collision identities each through suspend/restore. Original live-release/source-mismatch/independent-replacement negative guards all pass, with exactly two expected rejection messages. No relaxed assertions.

The moving-run allocation/initialization/null GLES3 mesh sequence supports MeshStorage.mesh_owner as the exhausted category: official source maps mesh_allocate/mesh_initialize to that owner. This remains an inference, not a captured symbolic native allocator backtrace or proof of OOM. Reference: https://github.com/godotengine/godot/blob/4.6.3-stable/drivers/gles3/storage/mesh_storage.cpp . The retained executable reports7d41c59c4; tag metadata alone does not prove binary identity.

Whole-ship changed-state movement remains to be tested. No FPS, complete route, loaded-cart, capacity or final visual acceptance claim. Grand Arrivals interpretation remains pending and untouched. Existing Windows package has not been rebuilt.

## Changed-state actual moving result004

Actual1080p Compatibility run reached boarding and moving stages, then stopped at the unchanged5 GiB available-RAM floor (4.958 GiB sampled). Peak private14.489 GiB/resident12.423 GiB. stderr empty; no allocation error observed. Last sample231active received rooms/56034active mesh nodes,40979cached detached mesh nodes,560deferred rooms,255674resources/586725nodes,87256draw calls/7555845primitives. Private detail56resident,71loads,15releases. Static memory9629167135bytes. This exceeds the earlier failed baseline's162active rooms, but route did not complete and frame median/p95 were not finalized. Single sampled process times are not FPS. No OOM/crash/fullroute/60FPS claim. Next blocker is live memory headroom, not permission or missing source. No further full run performed.
