# Measured D09 route activation/contact successor

Minimal isolated-source overlay after the independently retained a3e713ed weak-texture baseline. Frozen delivered files, prior repair, D04 prefetch and batching candidates remain unchanged. The measured route had zero D04 residents/loads/releases; this package does not use either D04 candidate.

## Actual measured paths addressed

- private_detail_residency._load_visible -> NightGarden manager's non-Night delegation -> base _load_entry.
- received_homes residency._attach_visible_room -> source_dispatch.ensure -> deferred_home_visual.ensure.
- static_contact_cache.attach_group called from both the initial private contact_visual helper and private detail contacts after shell removal.

The measured4.53s frame includes11 private callbacks and81 attachment callbacks, not necessarily81 distinct completed rooms. Inclusive timings overlap. Diagnostic scanning cost0.646s; detailed GPU timing was compromised by timestamp-capacity errors. These observations do not identify the exhausted RID owner or prove reclamation failure.

## Bounded changes

Both visibility callbacks share ONE queue when ASTRAEA_ROOM_ACTIVATION_QUEUE=1. Requests are deduplicated per existing manager/room identity, rechecked immediately before execution, and discarded if stale, already active, detached or owner-destroyed. No extra nodes or resources are pre-instantiated/pooled. Pending descriptors reference only existing registry records; at most one pending descriptor exists per registered room per manager. The queue completes at most one activation per process tick across both managers, with a2ms soft dispatch budget, bounded64-event history, peak queue length, stale/duplicate counts, cost and overrun telemetry. A single activation cannot be preempted; it may still exceed the frame target.

Near-player/rigid-body refresh and explicit prepare_position remain synchronous with the original radii. Startup before runtime_ready retains its original behavior. Far visibility refresh requests join the same queue. Eligible releases now finish before new activations, preserving grace periods and wanted-content criteria. Received callbacks also recheck current visibility before attaching. These release-order/stale-request corrections apply to the patched source even with the queue switch off; keep the unchanged weak-texture baseline for an exact source A/B.

ASTRAEA_PRIVATE_CONTACT_SINGLE_PASS=1 chooses a helper with the same original imported visual/presentation/glass policy, but does not create full-room contacts that the original private path immediately deletes. Shell meshes are cleared as before and the unchanged contacts() builds only final private-detail contacts. No final triangles, margins, identities or material policy change. This switch is independent of the shared queue, weak-texture patch and D04 work.

No hard cap is imposed on legitimately visible or safety-required rooms; that would remove required content. This bounds activation bursts and avoids temporary discarded collision resources, but DOES NOT prove a resident-node plateau or reduce all near-demand bursts. Repeated-route profiling is still required. Individual deferred_home_visual activations still instantiate and build their necessary contacts; splitting/prebuilding those units requires further measured source work.

## Apply and compare through sole laptop owner

`python apply.py --repo PATH` validates the five exact payload files plus weak-texture prerequisite; `--apply` makes immutable preimage backups under `.astraea-delivery-backups/route-activation-20261023` and verifies hashes. It never launches/exports. The base is repaired release + a3e713ed interner; installation over an unknown manifest or strong-interner baseline is refused. No transitive live source pins referenced the old private/received scripts; historical validation hashes are preserved. SOURCE_CONTRACTS carries exact new source bytes into the established export mechanism.

Suggested isolated comparisons on the already measured route, with identical content/settings:
1. Existing weak-texture baseline, unchanged source.
2. Patched source with queue=1, single_pass=0.
3. Same patched source with queue=1, single_pass=1.
Use environment values ASTRAEA_ROOM_ACTIVATION_QUEUE and ASTRAEA_PRIVATE_CONTACT_SINGLE_PASS; unset/0 disables the corresponding feature. Do not enable D04 batching/prefetch for these comparisons. Record queue.statistics() from ShipSystems/VisibilityActivationQueue plus private/received/contact loads/releases and current resources.

Route: D09 spawn(63,52.6,-20.5), settles52.5;15s stationary; heading0-to90 movement toward(52.62286,52.49876,-20.5), then heading180.1920x1080 internal, effects off,60cap. Preserve safety limits; stop on allocation/nullmesh/collision errors or memory threshold. Capture return/repeated-route plateau if safe, p95/p99 transitions and unchanged collision/view behavior. No new target run or cloud full build was performed here.

## Focused evidence

- Shared callback fixture:173 calls ->92 unique requests;81 duplicates suppressed;11 stale private requests dropped;81 received activations drained with at most one completion per tick. This is synthetic lifecycle evidence, not a ship benchmark.
- Actual retained private room AST-UNIT-D13-f1b81969c5730258: identical final mesh faces/transforms and collision faces/transforms/margins. Contact groups/bodies created fell5 to2 by omitting discarded work. Timing values include unequal cache warmth and are NOT a target speed comparison.
- Release-order fixture: eligible old room detached before the near room attached; near preparation completed synchronously even with queue enabled.
- Source parses and installer dry/apply/idempotence checks. No gameplay, full ship or RID-crash acceptance.
