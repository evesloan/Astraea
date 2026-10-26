# Actual paired LOD comparison — not selected for performance

Source 442fd75674a0da4b13eb46c9be4b823d2fae3e94. Windows Compatibility, retained official Godot 4.6.3, Intel Ultra 7 255HX, RTX 5060 Laptop 8 GiB, 1920x1080. Instrumented debug/script profiler; viewport render CPU/GPU categories overlap and are not additive. This is stationary aboard the original tram, not a completed trip or loaded-cart test.

Run030 exited normally with code 0, 39 checks, zero failures and zero engine errors. Runtime 308.88 s; peak private 11.456 GiB, resident 9.297 GiB; minimum available RAM 7.849 GiB. Safety limits unchanged. Final conservative contact ownership, rider support and source checks pass together.

Same camera, unchanged room transition markers [1169,29,0,0,0], identical light IDs and empty activation queues. Two 96-frame settled windows, with 24 warm-up frames after switching 4,582 merged cells to 12,391 original renderer records. Each window has constant node/resource/draw/primitive counts. Original source LODs and per-object bounds are restored, not newly authored geometry.

| Metric | Merged cells | Original imported LODs |
|---|---:|---:|
| Wall median ms | 131.6785 | 130.1905 |
| Wall p95 ms (nearest rank) | 221.155 | 233.288 |
| Wall sample SD ms | 36.9997 | 39.4790 |
| Render CPU median ms | 81.7755 | 82.7000 |
| Render GPU median ms | 70.0315 | 70.9325 |
| Physics median ms | 33.030 | 32.709 |
| Visible draws | 46,933 | 47,901 |
| Rendered primitives | 5,356,478 | 5,021,474 |
| Nodes | 515,270 | 515,270 |
| Resources | 241,882 | 240,214 |

Primitives fall 6.25%, but draws rise 2.06%, both render timings worsen, and wall-time p95 worsens. The roughly 1.13% median change is not a supported performance improvement. Keep this opt-in comparison unselected; normal startup remains unchanged. Retaining original records for the baseline confounds absolute production-memory comparisons.

Late built-in script-profiler refresh samples for the FINAL conservative contact-index implementation span about 13.65–14.57 ms (one call/sample). Do not promote run029's earlier 7–8 ms result as final. Current final ownership snapshot has 7,665 transform checks, zero near candidates/distance tests at this stationary pose, 36 index bins and two bounds updates. This validates ownership at the tested pose, not every route position.

Both settled images were inspected: same cab/window framing and surrounding atrium remain visible without an obvious gross discontinuity. The dark, flat architecture remains visually unfinished; a single view is not full visual equivalence or artistic acceptance.

Decision: imported LOD preservation alone does not solve this view's dominant submission cost. Further work must target the remaining actual visible owners with spatial/light-compatible representation and evidence of real frame-time benefit, not another cohort compilation or unchanged route. Full route, stocked cart, final visual quality, 60 FPS and matching Windows export remain open. No Windows build was produced by this comparison.
