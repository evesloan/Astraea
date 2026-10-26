# Actual settled rendering attribution

Source base dad22eb7d74f3693163bb185ed906a0531bc52b0 plus the retained diagnostic check_ship.gd and its exact manifest entry. Production selection unchanged. Same 1080p Compatibility hardware/editor as run030, instrumented debug/script profiler. No render backend or lighting budget changes.

Run031 failed before construction due to a missing local timer declaration in the new harness; original failed script and logs retained. Run032 exited0 with38 checks but its20s settle window expired, so no attribution ran. Run033 used60s maximum settle, then temporarily paused the two residency schedulers and blocked their witness signals ONLY during render attribution, restoring their original process/signal states afterward. Original physics/contact support stayed running. This is stationary attribution, not a movement/streaming or release FPS result.

Run033:39 checks,zero failures,zero engine errors,normal exit0. Peak private11.663GiB,resident9.507GiB,minavailable6.964GiB. The96 baselineframes and ten32-frame stages have unchanged room transition markers/light IDs; every stage eligible. All temporary mesh render layers, occlusion and shadow flags restored. Actual ship contains3176occluder instances and1077visible lights,only3shadowed; visible-light count alone is not intersecting-light or GPU cost.

| Stage | Draws | RenderCPU median ms | RenderGPU median ms | Wall median ms |
|---|---:|---:|---:|---:|
| Initial settled baseline |46933|83.499|72.178|132.569|
| Occlusion disabled only |146796|251.357|230.304|318.733|
| Occlusion restored |46933|81.569|69.923|127.319|
| Three shadow passes disabled |46933|81.749|70.152|125.887|
| Shadows restored |46933|81.368|70.757|129.353|
| FamilySpecialty47 excluded |44693|74.985|64.211|119.055|
| Family restored |46933|81.736|69.700|125.581|
| ReceivedSections excluded |37101|67.717|57.792|109.864|
| Received restored |46933|81.417|69.740|126.599|
| Aquatic/Vesper excluded |41896|76.419|65.458|121.274|
| Aquatic restored |46933|81.763|69.981|127.297|

Raw sample ranges/p95 are in run033/ANALYSIS.json; no addition/subtraction of overlapping profiler categories to infer total frame time. Marginal exclusions identify contributors, not deployable content removal or achievable full savings. Occlusion demonstrably removes~99863submissions; do not repeat the premise that enabling it is the solution. Active shadowpasses are not the dominant measured cost here. ReceivedSections is largest of the tested owners:9832submissions and~13.7ms renderCPU marginal,versus5037/~5.3ms aquatic and2240/~6.8ms Family. Untested owners still contribute; this is not an exhaustive cost decomposition.

Decision: target original static components within ReceivedSections, with real light-compatible spatial grouping and preserved LOD/material/door/contact identities; do not extend rejected full-resolution merging or hide this owner. Aquatic Vesper source has240chairs*10meshparts and240place-settings*5parts (3600meshinstances), a secondary repeated-component target. Source counts are not measured savings. A production representation correction and its actual comparison remain pending; no optimization has been selected from these exclusions.

Final conservative contact ownership and real boarded rider support passed again. Original editable sources, lower Arrivals candidate and prior Windows output untouched. Windows prerequisites/path recorded separately; fullroute,loadedcart,visual,60FPS and matchingrelease remain open. No engine process left running after normal exit.
