# D04 opaque surface cells — opt-in performance successor

## Status and boundary

Implementation candidate, default OFF. Clean delivery remains frozen f94cc1c8 plus the cumulative Quiet/Family patch protected at854dc6db. No existing production file, project main setting, native asset or laptop export is replaced. This separate launcher uses the original menu/settings and ship hierarchy through named successors. It is not a new accepted Windows build or whole-ship FPS claim.

Select `res://d04_surface_cells_20261023/bootstrap.tscn` with the retained Godot4.6.3 editor only when the laptop test owner coordinates the run. `ASTRAEA_D04_SURFACE_CELLS=1` enables the candidate; absent/0 preserves original rendering. `ASTRAEA_OCCLUSION=0` disables occlusion only for this successor's world viewport; absent/1 preserves existing enabled occlusion. Do not change the default project scene or frozen binary.

## Research applied to actual source

Official Godot4.6 guidance: Compatibility does not automatically instance ordinary MeshInstances. Spatially bounded manual consolidation is useful, but whole-batch culling and per-object lighting limits must be respected. Visibility HLOD needs fade-disabled hysteresis on this renderer. Existing authored sightlines must remain open.

- https://docs.godotengine.org/en/4.6/tutorials/performance/optimizing_3d_performance.html
- https://docs.godotengine.org/en/4.6/classes/class_multimesh.html
- https://docs.godotengine.org/en/4.6/tutorials/3d/occlusion_culling.html
- https://docs.godotengine.org/en/4.6/tutorials/3d/visibility_ranges.html
- https://docs.godotengine.org/en/4.6/tutorials/scripting/debug/debugger_panel.html

Actual project findings: private details already have24m entry/36m hold/8s release hysteresis and visibility witnesses; public shells, doors and lights persist. D04 already uses exact small-cell MultiMeshes and shared resources across120 scenes. Static opaque face occluders are installed across received ship geometry and private shells; world viewport occlusion is enabled. An existing eight-shadow-source selector remains unchanged; this is a project policy, not a claim that Godot allows only eight lights per scene. The three public receiving banks already use four/five-mesh plant exports:540 placements yield1754 render meshes, not the previously suspected huge native expansion.

The remaining D04 details contain18432 ordinary MeshInstances. This successor consolidates only compatible opaque, single-surface, non-LOD geometry inside four-metre room cells. Existing MultiMeshes,5052 LOD-bearing candidates, alpha/glass, shader materials, scripted/dynamic objects, double-sided shadow modes, visibility-range objects, skin/custom vertex channels and unsupported transforms remain separate. No HLOD geometry is invented and no architecture is deleted.

## Preservation and safety

Batch key includes room/cell, exact material resource, vertex format, render/shadow/layer state and potential-light set. Tight combined bounds may not exceed4m on any axis or gain another light. More than8 potential omni or8 potential spot lights rejects the affected grouping. All potential lights count even if hidden by the existing budget. The controller monitors light transform/range/layers and room transform; a changed/added/removed light restores originals and disables the candidate rather than retaining an invalid selection.

Raw render triangles are checked to0.00001m during construction. Original nodes, mesh resources, metadata and contacts remain. Combined meshes cast no shadows: original per-object shadow resources continue unchanged via shadows-only mode. Toggling off restores original visibility/shadow state. Original detail residency owns lifetime; no merged resource cache survives unload. At most one room is processed per frame after actual runtime readiness. This is a bounded activation count, NOT a hard millisecond guarantee.

## Measured focused results

All120 retained D04 detail scenes passed source node/mesh/transform/contact/visibility restoration and geometry checks. No-light fixture maximum:7255 fewer main-pass submissions,2208 merged batches,397692 triangles re-encoded without removing geometry. Actual ship lights can reduce the saving. Most recent complete fixture recorded about1.2s total build work across120 rooms; this software-machine number is not target timing.

Three isolated actual detail-room pairs at640x360 on software Compatibility: visible draws184→135,184→135,192→117; visible primitives unchanged10078/11102/16002. Two image pairs are byte-identical; one differs in3 of921600 colour channels (maximum channel difference4/255). Images deliberately omit room shells and are renderer diagnostics, not residential design pictures or art acceptance.

Five focused guard cases passed (opaque positive/restore, transparency rejection, light-limit rejection, separated cells, visibility-range/double-sided-shadow exclusion). Actual D04 load/release/reload and light-movement fallback passed. No full-ship launch was performed in cloud.

## Next controlled test, owned by the existing laptop worker

Use the same fixed content, camera/pitch and settings as the clean baseline. Compare baseline, batching-only, occlusion-only and combined where authorized; record actual world viewport resolution, room residency counts, activation logs and light rejections. Occlusion can affect visibility-based residency, so differing resident content is a confound, not a pure render comparison. Include warm and cold transitions and actual1080p internal resolution separately from the earlier640x360 case. Use Windows Compatibility Visual Profiler for render CPU/GPU and normal profiler for scripts/physics; retain draw/object/primitive counts, memory, p95/p99 and activation spikes.

Acceptance is lower worst-view draw work AND improved target frame time with identical close content, preserved openings/contacts/identities, and no streaming or memory regression. If draws fall without frame-time improvement, stop extending this method and follow measured cost. The controller's per-frame light guards and on-demand geometry build can themselves cost time; their measured target overhead is still open. Do not enable by default until the target comparison passes. No missing October20 source or held construction is recovered by this optimization.
