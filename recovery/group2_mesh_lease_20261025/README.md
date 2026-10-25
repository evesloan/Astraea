# Exact Group 2 mesh lifetime correction

The selected received-room release path detached and cached complete Group 2
source subtrees. Their Mesh resources, including imported shadow meshes, stayed
owned. This is the demonstrated retention defect. The actual cached-room class
already frees detached sources in its PREDELETE handler; the initial generic
Node3D fixture did not model that cleanup and does not prove a production
destruction leak. The correction remains compatible with the existing cleanup.
This evidence is not proof that one allocator owner caused the whole-ship RID
failure recorded by the preceding roof checkpoint.

The correction preserves all original scene nodes, persistent IDs, controller
states, poses, collision shapes and visibility decisions. A detached room keeps
its owned subtree and releases only the exact originally bound mesh references.
Before it is reused, those same nodes receive mesh resources from the same
hash-checked source. Independent mesh replacements are preserved. Live rooms
cannot be suspended; changed source bytes fail before restoration. Exported
resource remaps are supported, but actual Windows export validation remains due.

`BASELINE.json` demonstrates retention and reclamation for three room types.
`ALL_86_SOURCES.json` records zero failures across all 86 source contracts:
99,581 mesh nodes, 160 door controllers and 1,705 collision shapes. All tracked
mesh references expired while detached. Geometry/material fingerprints,
node/parent identities, poses, door state, contact nodes/shapes and room-owned
destruction passed. The serial test took 136.8 seconds and peaked at 0.323 GiB
sampled private memory. This is not a simultaneous ship-memory or FPS result.

`GUARDS.log` records the expected two refusal errors and successful controls.
Raw logs, including a harness parse failure corrected before execution, remain
in `Astraea-resume-20261025/group2-*` beside the source workspace. Optional load/
release trace prints were added during the serial check; the subsequently run
guard test exercised those final script versions with tracing disabled.

No original GLB, room allocation, collision mesh, source-contract manifest or
prior evidence was altered. The roof remains unselected. Next is the bounded
complete-ship check; no claim of resolving its RID failure or reaching 60 FPS
is made from these source-level results.

## Complete-ship retry and scheduling correction

The retry reached runtime_ready in 101.163 seconds, then a visibility callback
burst loaded Group 2 sources with no release events before the safety stop.
See INSTALLED_RETRY.json. Thus the lease is not itself a startup/RID resolution.
The received-room callback previously admitted every deferred screen-entered
request without checking current camera demand. It now deduplicates requests,
waits two renderer frames, rechecks current visibility or proximity, and admits
at most one visual activation per frame. Synchronous near-room and explicit
arrival preparation are retained. No room, collision or required view is removed.
QUEUE_GUARDS.log records stale/duplicate rejection, frame delay and synchronous
near admission. Actual full-ship outcome remains to be checked.
