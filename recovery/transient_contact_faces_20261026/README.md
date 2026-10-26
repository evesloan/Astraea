# Transient contact extraction correction — incomplete movement acceptance

The shared static-contact builder now extracts ArrayMesh triangles through a temporary TriangleMesh, preserving native welded face order without retaining Mesh.generate_triangle_mesh() intersection BVHs on render resources. PrimitiveMesh and other Mesh types retain the original native extraction. Geometry, render resources/materials, contact pooling, collision nodes/transforms and persistent state are unchanged. Required work is executed outside assertions.

The protected prerequisite probe at 9bf39430 measured 242,211,164 bytes of additional retained cache on the 1,816-mesh Upper Atrium source, and 8,395,376 bytes on the 290-mesh D07 source. These are focused static-memory measurements, not whole-ship savings or RSS.

Focused run 004 passes 2,106 exact imported mesh/contact comparisons, indexed/non-indexed strips, multiple surfaces and transformed primitive groups. Exit 0; stderr empty; 5.69 seconds. Earlier test failures (type binding, strip order, PrimitiveMesh API) are preserved, not production outcomes. Original source files remain immutable. The separate disposable static-bank representation is unselected and not part of this production correction.

Actual ship movement, full route, hardware FPS and matching Windows export remain pending. Lower Arrivals and visual-completion limitations remain unchanged. The next bounded movement comparison must retain existing RAM/RID safety gates.
