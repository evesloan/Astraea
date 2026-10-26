# Transient contact extraction correction — incomplete movement acceptance

The shared static-contact builder now extracts ArrayMesh triangles through a temporary TriangleMesh, preserving native welded face order without retaining Mesh.generate_triangle_mesh() intersection BVHs on render resources. PrimitiveMesh and other Mesh types retain the original native extraction. Geometry, render resources/materials, contact pooling, collision nodes/transforms and persistent state are unchanged. Required work is executed outside assertions.

The protected prerequisite probe at 9bf39430 measured 242,211,164 bytes of additional retained cache on the 1,816-mesh Upper Atrium source, and 8,395,376 bytes on the 290-mesh D07 source. These are focused static-memory measurements, not whole-ship savings or RSS.

Focused run 004 passes 2,106 exact imported mesh/contact comparisons, indexed/non-indexed strips, multiple surfaces and transformed primitive groups. Exit 0; stderr empty; 5.69 seconds. Earlier test failures (type binding, strip order, PrimitiveMesh API) are preserved, not production outcomes. Original source files remain immutable. The separate disposable static-bank representation is unselected and not part of this production correction.

Actual ship movement, full route, hardware FPS and matching Windows export remain pending. Lower Arrivals and visual-completion limitations remain unchanged. The next bounded movement comparison must retain existing RAM/RID safety gates.

## Actual selected-ship run 012

Protected source d367e29deb600f8fe79d548249989e457641edbb passed 35 checks, zero failures, real boarding and CENTRAL +10 m/return (20 m accumulated). Original player maximum carried-local displacement 0.018293 m; original cart remained at its prior world location, so loaded-cart and whole-route acceptance remain untested. Exit 0, normal teardown, stderr empty, no resource safety stop. Elapsed 317.48 seconds including construction and teardown.

At identical final construction step 205 and 439,460 nodes, Godot static memory fell from 7,866,023,016 to 6,258,051,972 bytes: 1,607,971,044 bytes (1.498 GiB) lower. This is matched constructor static memory, not an RSS delta or proof of full-route stability. Peak private memory was 12.616 GiB; minimum available RAM 6.047 GiB under unchanged 5 GiB floor.

Actual 1920x1080 Compatibility player-camera movement still fails the performance objective: 603 frames, median 240.632 ms and p95 562.779 ms. Observed draw submissions remain around 97,000 on the outward/return interval (51,913 at final dock). Current memory correction does not reduce render submissions. No new Windows export was made. The next production correction must reduce the dominant visible rendering/scene cost while retaining visual/physics semantics; no unchanged route repetition is justified.

The preserved central_aboard_actual.png is a real player view from the run, inspected: close car door/window framing and distant interior circulation, dark and visually unfinished. It is diagnostic evidence, not a grand-space design approval or new art deliverable.
