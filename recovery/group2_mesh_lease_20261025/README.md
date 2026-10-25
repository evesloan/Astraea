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

## Inherited private-detail scheduling

The received queue retry reached readiness at 100.231 seconds with empty stderr,
but crossed the RAM safety floor before producing a roof view. This does not
prove resolution under sustained movement. Private and D04 detail managers had
the same unbounded visibility callback path, including loads before final
readiness. Their visibility-only work now waits for readiness, deduplicates,
waits two renderer frames and rechecks visibility before one load per manager
per frame. Nearby/explicit arrival preparation is unchanged. The inherited
queue controls passed for both managers; no geometry or collision change.

The active Night Garden controller pin and exactly two source-manifest entries
were reconciled, together with preparation metadata. Read-only preparation
verification passed all 17,927 contracts, 80 canonical repairs and 11 retained
targets, with zero missing files or writes. Manifest SHA256:
`a0d1ab11d9795f6e59838bf343cf738d243a958555b21c61145f5e88e4b36748`.
The roof check now records stage/resource/manager counts to distinguish candidate
build, arrival preparation and subsequent visibility loads if safety stops again.

## Latest actual-ship boundary: ddf13c227

The D04 adapter rejected a diagnostic-only print added to its exact pinned
controller. That print was removed and the original bytes independently verified;
the inherited queue remains. The subsequent run reached runtime_ready at
109.114 seconds with zero stderr bytes. The new Group 7 candidate built and
the real player arrival to the fore neck passed the ordinary floor/capsule gate.
Candidate construction added 10,832,820 static bytes; arrival preparation added
12,047,252 static bytes in 0.074 seconds. These stages are not the multi-GiB
post-ready allocation source. See installed_006/RESULT.json for exact measured
deltas and the named Star Atlas private-detail loads afterward.

The run began with 15.150 GiB available RAM and stopped at the unchanged
5 GiB safety floor: minimum 4.722 GiB, peak private 12.782 GiB, resident
10.811 GiB. No RID or script errors occurred in this bounded run. It did not
reach screenshot capture, full route clearance, sustained movement or FPS
acceptance. The roof remains unselected and the Windows package is not rebuilt.
Do not retry the unchanged full run at the same headroom. Further work must
reduce or bound live visible-detail/render resources, or establish sufficient
free RAM for a decision-relevant profiler run; no allocator-limit increase,
required-view removal or user-application termination is implied.
