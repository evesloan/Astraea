# Proposed native normal gate correction (not applied)

The current 0.0001 scalar keeper is preserved in historical results. It is not widened. The proposed criterion requires exact source-GLB position/UV/topology/cyclic correspondence plus bit-exact native normals after the documented Godot 4.6.3 source normal -> octahedral uint16 -> decoded float32 normal transformation.

The patch leaves immutable GLB hashes, disabled mesh compression, material/texture checks, node hierarchy/transforms, source/export equivalence, and every physical gate unchanged. It records each expected uint16 pair and the old scalar outcome. No alternate palette, geometry cleanup, reauthored normal, engine change, or production edit is proposed. Retain VISUAL_STUDY004's unconditional data-first dump approach in any future gated run.

Use only with the verified uncompressed-attribute format. Do not extrapolate to compressed tangent-frame packing, different engines/builds, or another importer. The GDScript helper explicitly rounds the uint16 multiplication intermediate to float32 because GDScript scalar arithmetic otherwise uses double precision. The source and proposed helpers have been statically inspected only; this patch has not been engine-parsed, applied or run.

A later parent-reviewed test must confirm the proposed helper against the frozen actual per-corner integer pairs and zero-residual normal correspondences. Broader native collision/contact/root checks and visual acceptance remain pending. No images are held up by this proposal.

Primary sources:
- https://raw.githubusercontent.com/godotengine/godot/4.6.3-stable/servers/rendering/rendering_server.cpp#L557
- https://raw.githubusercontent.com/godotengine/godot/4.6.3-stable/servers/rendering/rendering_server.cpp#L1377
- https://raw.githubusercontent.com/godotengine/godot/4.6.3-stable/core/math/vector3.cpp#L84
- https://raw.githubusercontent.com/godotengine/godot/4.6.3-stable/core/math/vector3.h#L500
