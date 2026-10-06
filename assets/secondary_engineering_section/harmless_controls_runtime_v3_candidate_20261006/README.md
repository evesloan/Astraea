# Engineering controls: runtime integration draft v3

Revision: `engineering_controls_runtime_v3_20261006`

**Scratch only. Game has not been edited. No engine, imports, commits or real listening have been run.** The theatre lane owns Game. This candidate is based on observed Game HEAD `94ad78bad2173231af0ae5e00d5f09a42d95e964`; all shared-file changes/proofs must be rebased after theatre and gate signage settle, then approved by the parent. Both the control adoption flag and separate listener-proof approval remain false.

## What this adds to retained labels v2

- The same 120 source controls, all source motion/pose/target fields, human-readable SunCorp labels/faux statuses, six local effect mappings and four original WAVs remain unchanged.
- One **separate, explicit listener prerequisite** in `presentation.gd`: `world_view.audio_listener_enable_3d = true`, immediately after `world_view.own_world_3d = true`. This enables 3D audio in the existing World360, not the postprocessing viewport.
- One exact deferred original-player binding. The cell is built before `ShipSpace/PersistentActors/Player`, so the bank binds that exact node once after construction. Camera, owner and all four voices must share listener-enabled World360 and its World3D; the original camera must be current. There is no per-frame search or extra listener/camera node.
- Four finite audio leases supplement each voice's real `playing` state. They prevent audio-server start/finish races, keep a four-voice cap, enforce at least 80 ms between starts, and retain at most 64 start-history entries. Fixed-step scheduler evidence does not establish audibility.
- Startup rejection of duplicate/overlapping/widened targets and non-allowlisted effect mappings, before any target instances are created.
- A real-main-scene QA draft covering all 120 controls twice, with one supported initial arrival and ordinary-player walking connecting the ten panels. It records exact first-hit colliders/ranges, original capsule support/clearance, motion-envelope samples, null material restoration, real door/lift state preservation and emitted audio-start intervals.

The source `toggle` meshes still perform their approved bounded momentary travel/return. This revision does not invent persistent electrical/system state or alter their source travel limits.

## Findings and corrected draft risks

1. **Listener lifecycle:** a synchronous camera lookup during cell construction is too early. The new bank uses one deferred exact-path bind and refuses activation if the original listener topology is invalid.
2. **Earlier test occluder:** the old unrun draft added its temporary blocker to the root viewport. That is a different 3D world from World360. The v3 fixture is added under the ship and explicitly checks matching viewport/world.
3. **Connected-route obstruction:** isolated target poses passed, but a straight north-panel link intersected the fixed shelf at x27.19–28.08, z−407.03–−406.52. The failed attempt is retained in `reports/source_connected_route_screen_001_shelf_rejected.json`. Revision 002 detours north at z−407.7 and turns south at x28.6. Its **new-GLB-only** screen passes 137 edges / 1,178 capsule samples over 149.542 m. Old models, compiled floor topology and movable actors remain outside that screen; the full-scene walk is still unrun.
4. **Legacy presentation pins:** several existing regressions preserve presentation.gd through the engineering successor chain. A new listener line needs an explicit exact-reversal proof. Do not update historical caller pins or weaken broad byte checks.
5. **Gate signage:** forthcoming header/leaf printing is a separate visual-only addition. Controls bind exact ACT_/TARGET_ identities; they do not assume that every descendant MeshInstance3D is one of the 153 original core groups. Preserve the named core roster and source hashes separately from optional sign meshes. No sign collision, target, light or shader is added here.

## Review files

- `DRAFT_FILE_MAP.json`: exact prospective Game destinations and current scratch files; no installation authorization.
- `integration/presentation_listener_prerequisite.patch`: the isolated one-line listener prerequisite.
- `integration/secondary_engineering_cell_controls.patch`: one existing-visual builder invocation, with `(wrapper, visual, ship)`.
- `integration/validate_wrapper_controls.patch`: additive focused-check registration, 40,000-frame allowance and 1,200-second watchdog; preserves all old checks and fresh-import ordering.
- `integration/SHARED_GUARD_HOOK.txt`: future shared-guard composition contract, coordinated with the theatre successor worker. This lane does not create or edit the shared guard.
- `docs/ENGINEERING_CONTROLS_LISTENER_ADOPTION_DRAFT.json` and `tests/engineering_controls_listener_successor.gd`: separately pinned, currently unapproved, exact listener-line proof. It reverses precisely one addition to the approved section presentation predecessor and retains the original historical caller SHA.
- `scripts/engineering_calibration_{builder,bank,audio,control}.gd`: bounded v3 runtime drafts.
- `tests/validate_engineering_calibration.gd`: unrun actual-main-scene test; see `QA_PLAN.md` for implemented versus remaining cases.
- `data/ENGINEERING_CONTROLS_WALK_ROUTE_V3.json`: exact proposed connected itinerary and provenance.
- `data/ENGINEERING_CALIBRATION_DRAFT.json`: complete source-pinned contract, still disabled.
- `LABEL_REVIEW.md`, `data/SUNCORP_LABELS_V2.json`, `data/LOCAL_EFFECT_ALLOWLIST_V1.json`, `audio/*.wav`: unchanged label/effect/audio payload from v2.
- `reports/runtime_v3_pure_tests.json`: ten passing pure checks. No GDScript parsing/runtime evidence is implied.

## Unchanged bounds

Original RMB/E and 2.5 m first-hit dispatch; original 1.65 m eye and 1.8 m / radius0.3 capsule; source-marker radius0.018 targets; original full-mesh source-pivot motion; exact imported rest assignment; original-null surface override restoration; local duplicate-material pulse capped0.22; finite 0.52–0.68 s effects; 0.9 s per-control cooldown; four simultaneous effects; four spatial voices; minimum80 ms audio-start spacing; gain at most−12 dB; max distance6 m. No new dynamic lights or shared shader/material changes.

No actual reactor, security, airlock, real gate, door, lift, transport, damage, punishment, networking or persistence effects. Cake remains reserved, disabled, probability0 and spawn budget0. Gate prompts remain distinct from the fictional service controls. Existing printed calibration wording is still part of the unchanged source artwork; this runtime candidate does not revise it.

## Adoption sequence, owned by the accepting parent

1. Finish theatre/signage work and independently verify its retention. Re-read the actual Game files and successor guard. Do not apply whole-file scratch snapshots over new work.
2. Rebase the three small patches to their exact final predecessors. `prepare_runtime_v3.py` reads Game and only emits scratch files; it rejects a presentation predecessor outside the known section proof rather than silently adopting unknown bytes. The theatre worker said its successor preserves presentation bytes and handles only layout, compiled structure and ship.gd; verify this remains true.
3. Review the separate listener proof and its exact future shared-guard branch. Keep the historical presentation caller SHA and old capture audits. The standalone helper must be pinned to the final approved proof; the current proof deliberately has `adoption_approved:false`.
4. Only after approval, install the mapped files and one-line/call/validator additions. Revise the control and listener approval fields with their dependent proof hashes in the accepted package. No script in this bundle applies live changes.
5. Refresh through the original validation wrapper, parse all new GDScript, run the focused actual-world test, then the current full aggregate and legacy checks. A headless PASS never grants listening or graphical acceptance.
6. Listen in the real game at normal volume and inspect original-player renders. Enabling World360 audio can expose any other post-theatre 3D audio sources in that viewport; record that census and check their behavior too. Do not claim heard sound solely from a valid listener, `play()`, leases or waveform measurements.

## Reproduction and preservation

Use the v3 tools only: `prepare_runtime_v3.py`, `prepare_listener_guard.py`, `audit_source_poses.py`, `screen_connected_route.py`, `test_runtime_v3.py`, with `PYTHONDONTWRITEBYTECODE=1`. They run Python/source checks, not engines. The validation-wrapper patch snapshot is also pure Python and has only been AST-parsed.

V1/v2 are untouched and independently hash-checked. Historical generators/tests/reports are retained under `provenance/`; they describe those earlier drafts and are not the v3 test entry point. Re-run/seal any generated artifacts after a later rebase instead of claiming this pre-theatre manifest covers new bytes.
