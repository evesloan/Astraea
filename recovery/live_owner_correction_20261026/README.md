# Live owner accounting and finite contact lifetime

Baseline 142a45f0cb3586321ff694efaa21612689509147. Selected aquatic ship stays selected; lower graded Grand Arrivals remains retained unfinished. This checkpoint is a measured resource correction, not full-route, visual, FPS or Windows acceptance.

## Actual configuration and cost evidence

Actual-player run008 used the selected ship, RTX5060Laptop8GiB/CoreUltra7 255HX/31.43GiB RAM, 1080p Compatibility. It completed its deliberately bounded accounting capture at 2.0297m and exited normally: private peak12.547GiB, resident10.609GiB, minimum available6.162GiB. This is not completion of the required route. Built-in script profiler was enabled; overhead differs from run007. The 2.337s owner traversal frame is diagnostic overhead and must be excluded from gameplay timing.

648,589 live+detached nodes (108,043 detached), including265,120 mesh instances,143,959 collision shapes,129,163 static bodies. Unique counted raw mesh buffers657,276,854bytes, concave face arrays416,319,372bytes. Renderer reports825,991,066bufferbytes and556,305,785texturebytes. Godot static memory before capture7,949,663,449bytes. These counts overlap engine/renderer allocation and are not an additive process-memory breakdown. Unique resources are attributed to first encountered owner, not exclusive ownership.

Group3RemainingCrewBank has65,522nodes but only2.47MB unique mesh buffers and1.84MB contact faces; its isolated original fixture used338MB static. Node count alone did not prove it dominates the multi-GiB deficit. A compact-cell proxy/shadow candidate increased memory to369MB, converted only365meshes under exact material/LOD constraints, and emitted shadow-surface errors. It is NOT selected. Original failed logs are retained. Adding tiny occluder triangles was also not selected: source coverage is already mostly large opaque faces, and a source-only coverage census is not installed occlusion proof.

Built-in profiler examples BEFORE capture: receivedensure41ms/visibleattach35ms/deferredensure34ms (nested inclusive, do not sum); Tidal contactrefresh28-29ms; original tramactuator14-15ms; NightGarden private_load76.6ms/contacts41.6ms. Example total frames167.5-297ms. Unattributed remainder is not proven GPU cost. This is streaming CPU work plus a very large visible scene, not evidence of texture-only exhaustion.

## Demonstrated lifetime defect and correction

ShipSystems retains18 finite exact contact resources,133,086,060bytes of raw faces before physics acceleration structures. In run008,11 of these18 rooms were unloaded, yet every shape remained strongly held by the dictionary and inactive collision node. release_room previously changed layers only.

The correction retains original18body identities and transforms, exact indexed resources, room eligibility, visual geometry/materials, independent receiver/door contacts and persistent state. After startup admission, unloaded contacts clear both strong references. Far-visible activation prefetches at most one exact resource at a time; stale completed requests are consumed/discarded. Nearby preparation still loads synchronously before admitting a room. Failed required preparation stops room activation and pauses the tree; it cannot silently enable a room without its required resource. Teardown consumes any one outstanding request. No room cap, hidden required views, safety-floor change or collision simplification.

Focused lifetime003: exit0, empty stderr,17.04s, privatepeak1,024,864,256bytes. Releasing all18inactive shapes saves621,065,652 staticbytes (592.29MiB); all weakrefs expire. All18reactivate with exact triangle hashes, original body IDs/poses and actual physics ray hits. Synchronous nearby reload and stale-request disposal pass, then zero retained shapes. Reload completion ranges37ms-1.335s; asynchronous completion duration is not frame-time cost or a near-load latency guarantee. This is the all-unloaded upper-bound saving, NOT the savings in the seven-loaded live configuration.

The first short ray probe against each resource's first triangle failed; the corrected probe chooses the largest original nondegenerate triangle and a0.5m two-sided segment. All18actual hits pass. No geometry changed to pass. Original failed result002 is retained, and this focused fixture does not replace installed walking/cart/door acceptance.

## Gates and next action

Selected assembly transitive verification passes. Global manifest is verified separately. A changed-state actual movement run is warranted after independent protection, under the unchanged5GiB available/16GiB private safety gates. It must measure actual savings and activation/frame-time behavior; no60FPS or universal RID-resolution claim yet. The Tidal full-entry contact scan and major scene/draw submission remain measured costs, not fixed by this checkpoint.

Windows prerequisites remain ready per recovery/exact_contact_sharing_20261026/BUILD_PREPARATION.json. No new export yet. A clearly labeled diagnostic package can technically be built with the current exact-source plugin and installed templates, but a package lacking a proven complete safe route cannot be called playable/final. A menu/startup-only smoke test would not clear the known movement failure. The prior Windows package is preserved and does not include these corrections.

## Changed-state actual tram run009: still held

Protected9b5e834c1. Original player boarded and travelled7.9963m before unchanged5GiB available-memory floor stopped the owned process at4.934GiB. Privatepeak13.786GiB/resident11.704GiB; startingavailable16.603GiB. Empty stderr, no allocation-limit errors; forced safety stop, not provenOOM. Outbound10m/return did not complete. No repeated unchanged run.

Last sample594061nodes/260908resources,96993drawcalls/7775286primitives,8,764,890,620staticbytes.248receivedrooms with242visibility-demand,60942active mesh nodes and43093detached cachedmesh nodes; private58resident/73loads/15releases. Last15-frame window269.454ms median/855.947ms p95. Streaming windows are not steady-state or matched-endpoint benchmarks.8m versus prior4.53m stopping distance is progress under similar starting headroom, not isolated whole-ship savings: the later endpoint contains substantially more active content.

Contact lifetime is focused verified, but visible-scene representation remains the next substantial blocker. Do not repeat notifier/grace experiments or small sharing tweaks followed by this same route. The next meaningful package must reduce actual visible render submission/instance cost while preserving authored surfaces/materials, dynamic doors, near contacts and state. Rejected bank batching is NOT selected. No60FPS or safe complete-route claim.

No new Windows export. A labeled diagnostic package is technically possible with installed templates, but the main scene still admits a failing movement configuration; menu-only smoke testing cannot establish playability. Export/release remains held on safe route/performance; lower Arrivals and guest visual finish remain unfinished. Prior Windows/source copies preserved.
