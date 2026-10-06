# Actual-engine acceptance plan: engineering calibration controls

**Status: every engine, import, listening and graphical case below is UNRUN.** Pure-source receipts are useful preflight only. Parent lane must finish its current section physics gate before enabling this draft. Keep the engine/controller already in use; no engine switch, no original-controller patch, no raised camera, no resized capsule, no widened global ray.

## Gate 0: retained baseline and parser/import

- Verify independent backup success and current source/runtime retention receipts before any authorized Game edit.
- Record the exact engine version, platform, fixed-step versus real-time mode, source GLB hash, newly adopted script/data/WAV hashes, and main-scene revision. Preserve original player, service-door, real cell-gate, fixture-switch, tether and light-selector hash pins.
- Parse all four new scripts and the focused test. Treat warnings-as-errors according to the project's existing policy. No such parse has happened in this bundle.
- Refresh imports using the existing validation wrapper. Confirm the source GLB import remains lossless/current. Verify the new WAVs import as finite one-shot streams, without normalization, unexpected amplification or loop markers. Source WAVs' raw peaks are below 0.12; imported/perceived loudness still needs checking.
- Leave `adoption_gate_accepted` false until the parent explicitly accepts the integration revision. Then stage the one existing-room builder call. Confirm one bank, exactly 120 controls/Areas, no new ACT meshes, no cloned room, no actuator body contacts, no new lights, one audio owner and exactly four voice nodes.

## Gate 1: exact identity/rest preservation

- Run the existing section source/collision/material census before any calibration interaction and again after all effects settle. The 153 mesh groups, 120 ACT meshes, ten glass contacts, gate leaf, exact triangle counts, source identities and source bounds remain unchanged at rest.
- Enumerate all 120 IDs: 72 CONTROL, 48 WORKBAY. Match each exact marker, ACT mesh, original source transform and material order; no duplicate IDs, name-prefix accidental binding or missing tip/index error.
- Verify each Area is a radius-0.018 sphere at the precise source target, on layer 2, mask 0, monitoring/monitorable false. Confirm no broad parent Area and no overlapping calibration targets. Separately verify the two real gate targets remain exactly as before.

## Gate 2: all 120 original-player poses and RMB/E

Execute the provided `tests/validate_engineering_calibration.gd` in the integrated real main scene. It contains ten explicitly declared panel arrivals and ordinary W movement within each panel. It does not claim a continuous whole-room ingress route.

For every control:

1. Use its source-proposed foot location, keep player physics enabled, allow real settling and verify the actual compiled floor owner. Verify original radius 0.3, height 1.8, capsule center y0.9 and eye y1.65. Check the real standing envelope against all physical machinery/walls, not just this GLB. Record the actual settled feet/eye, pitch and range; no alternative elevated/widened pose may silently replace the proposal.
2. Aim at the source marker within the original ±1.35 rad pitch. The original `target_from_view()` must yield the intended control. Independently record that the very first collider is exactly this control's Area, within the original 2.5 m ray. A node ancestor or another neighbor is failure.
3. E without RMB must do nothing. RMB+E must activate once. E auto-repeat and rapid repeated E during the effect must not queue/restart duplicate effects.
4. Observe a nonzero authored actuator motion. Sample complete ACT mesh transforms and compare against the source-axis/pivot formula throughout travel; no overshoot beyond the source limit, geometric scaling, detached index/tip or initial jump. The supplied focused draft checks visible motion and exact restoration; add per-frame transform-envelope samples before acceptance.
5. After the finite effect, exact original local transform and original per-surface override pointers must be restored. Record protected real gate state unchanged. The focused test waits 65 additional physics frames, longer than the effect and cooldown.

If a pose fails in the real scene, record the exact first collider or capsule obstruction and the original proposed/actual pose. Route it to architecture/source review. Do not fix it with a giant hitbox, camera offset, collision exclusions, console teleport during an ordinary segment or an edited original controller.

## Gate 3: target boundaries and interrupted interaction

The focused script includes E-without-RMB, E echo/repeat and an opaque foreground blocker case. The additional cases below still need actual-engine implementation/execution and recorded results:

- Nearest-neighbor seams: each of the 16 formerly overlapping box pairs, plus horizontal neighbors, aimed at midpoint and edges. No wrong neighbor activates. Small target spheres should remain usable from normal standing focus, without aim assist or expanded ray.
- Exact range boundary: approach naturally from beyond 2.5 m and within it; only the existing ray determines reach. Test both frontal and oblique angles. Capture actual first-hit distance rather than measuring to the marker center alone.
- Opaque cabinet, glass proxy, closed real gate and held prop in the ray: no activation through the intervening collider. Clear blocker and verify normal control returns. The supplied temporary-box fixture is a first-hit mechanism check, not proof for these real objects.
- Backside/side approach wherever physically reachable: solid structure/first hit and front-normal guard prevent back activation. Never move the real capsule through the cabinet to manufacture a test position.
- Hold a real cleaning bottle/cart through the original tether, look toward a calibration control and press E: the existing release behavior wins. The control count stays unchanged. Then empty-handed interaction resumes normally.
- Press Escape during the effect, release/reacquire RMB, alt-tab/focus recovery and scene-tree pause/resume. No extra activation, stuck state or permanent pose/material remains. Existing gameplay-disable semantics are preserved.
- Cancel/reload/unload the section mid-effect and with all four slots busy. Active tweens are killed, surviving meshes restored exactly and voices stopped. Reopening yields source rest state, with no persistence claim.
- 100 complete cycles of each kind, plus the two guarded controls. Verify exact rest transform/material pointers on every cycle, finite resource counts and no drift, queued actions or steadily rising memory.

## Gate 4: local visual and audio quality

- Inspect in the actual rendered engine from source-proposed standing poses in CONTROL and WORKBAY, at original normal and RMB FOV. Capture representative toggle, rotary, selector, blue push, guarded courtesy and reserved morale control before/during/after. No unrelated cabinet, room, glass or shared material may pulse.
- Face/index pulse is explicitly local emissive feedback. Confirm restrained output under existing lighting and no glare/flicker/undesired bloom. There is no actual separate LED or meter needle in this source; do not claim one.
- Compare the pre/post whole-scene dynamic-light count and profiles. Calibration adds zero lights and changes no shared shader or light-selector file. The original light selector can naturally select different existing fixtures as the player walks; do not confuse this with calibration side effects.
- Listen to all four ORIGINAL scratch WAVs, first isolated and then in the actual room at close range, normal 1.1 m use, 3 m and beyond 6 m. Use a modest listening level. Check clicks are not startling/harsh, hum is short and gentle, relay tail ends cleanly, chirp has no unwanted voice-like content, no clipping/DC pops, and sound position follows the source control rather than the listener.
- Missing/unimported/incorrect-hash audio must report unavailable and remain silent while mechanical/visual interaction works. A dropped voice start under cap/cooldown must not be reported as audible. Do not call this a sound acceptance pass just because `.play()` was invoked or the waveform is numerically bounded.
- Rapidly operate at least five controls: maximum four simultaneous local animations and four audio voices, no unbounded event queue or loops. The 80 ms shared spacing and 0.9-second per-control cooldown must hold. Check imported-stream audio behavior in a real-time run, separate from accelerated fixed-step physics tests.

## Gate 5: no consequential systems and cake reserved

- For all 120 controls snapshot/check real gate desired/open state, service-door state, lift state, reactor/gameplay values, access flags, network activity, save data and active-object counts. The draft exposes no such effects; actual scene hookups must not introduce them.
- Verify HUD wording clearly identifies local calibration and does not mimic real gate-open controls. Source gate buttons still operate only the real gate through their original script.
- Trigger `ENG2_CONTROL_C2R_12` (courtesy) repeatedly: only the local press/pulse/chirp. No phase/reactor/security action.
- Trigger `ENG2_WORKBAY_MORALE_12` repeatedly and at reload: harmless press/click only. `bounded_cake_candidate` stays reserved, disabled, zero probability, zero spawn budget. There is no cake/dispenser implementation to test or claim yet.

## Gate 6: regression, performance and acceptance record

- Rerun existing engineering-cell, access, essentials, cart/tool, fixture-switch, service-door and lighting checks against the FINAL adopted code. Existing geometry/material checks run at rest; leaks must be fixed, not exempted.
- Run the project's full `tools/validate.py` aggregate after focused checks. Report focused/aggregate/graphical/listening outcomes separately, including failed attempts and never-run stages.
- Capture actual target-hardware idle and four-active-control frame/resource behavior. Verify no per-frame whole-room scans, runaway tween/material allocations or 120 active sound sources. Fixed-step test execution timing is not FPS or input-latency acceptance.
- Retain the final contract/script/audio hashes, source pins, per-ID pose/first-hit records, transform-envelope samples, negative-case records, listening decisions and screenshots/video. Keep the preceding geometry gate and this control gate distinct. Only then enable first-pass interaction acceptance; source/architecture overall quality remains separately judged.
