# Engineering calibration controls: reviewable scratch candidate

## Result and acceptance boundary

This bundle drafts harmless interactions for **all 120 source-authored controls**: 72 CONTROL, 48 WORKBAY, across ten panels. It adds no machinery, geometry or controls to the Game project. It preserves the original player, RMB/E dispatcher, 2.5 m first-hit ray, 1.65 m camera and 1.8 m capsule. It neither runs an engine nor refreshes imports nor commits anything.

**Not integrated, not engine-parsed, not visually accepted, and not listening-accepted.** The delivered contract deliberately has `adoption_gate_accepted: false`; its builder refuses to enable the draft until the accepting lane creates a reviewed integration revision. The preceding workbay geometry/physics gate must complete first.

### Findings that matter before integration

- The source manifest's proposed 90 mm target boxes overlap in **16 adjacent pairs**. This candidate uses an **18 mm-radius sphere at each exact source marker**, wholly inside its proposed envelope. The 120 spheres do not overlap. The original source envelopes and overlap pairs remain in the generated contract as provenance. No authored marker or mesh is moved to improve access.
- `actuator_parts` are Blender source pieces. The GLB merges each switch's tip/index into its one `ACT_…` mesh. The controller moves that entire mesh around the source pivot using the complete original transform. It does not search for missing tip/index children.
- There are no separate meter or LED nodes in this frozen export. `meter_step_return` is mapped to a clearly described actuator detent-return; `local_led_sequence` becomes a local face/index emission pulse. Neither is presented as an implemented meter needle or dedicated LED array.
- No existing sound facility/assets were found in the current Game scripts/scenes/assets. Four tiny **new original procedural PCM WAVs** are included, with deterministic source synthesis, measured raw levels and a four-voice spatial owner. These need actual listening and imported-runtime approval. The code never silently synthesizes missing sound at runtime.
- All 120 proposed poses pass a **new-GLB-only** triangle/capsule/ray screen at the original controller's dimensions. The screen excludes old-room geometry, compiled floors, old props and movable actors because they are not in this GLB. It is not full-scene Godot evidence.

## Files

- `data/ENGINEERING_CALIBRATION_DRAFT.json`: source-pinned 120-row contract, original markers/poses/pivots/limits, target refinement, feedback profile, material binding, audio provenance and protected runtime hashes.
- `scripts/engineering_calibration_builder.gd`: one-time validation/indexing of the already loaded source visual; creates one bank, 120 controls and one audio owner.
- `scripts/engineering_calibration_control.gd`: precise Area target, existing-dispatch verification, source-axis/pivot motion, exact rest restoration and per-actuator duplicate-material feedback.
- `scripts/engineering_calibration_bank.gd`: maximum four simultaneous local effects, no frame callback.
- `scripts/engineering_calibration_audio.gd`: one owner with four short one-shot spatial voices, 80 ms global start spacing, -12 dB gain, 6 m maximum distance, no loops or bus changes.
- `audio/*.wav`: mechanical click (85 ms), double relay (180 ms), soft hum (420 ms), courtesy chirp (220 ms). Mono 24 kHz 16-bit PCM; deterministic original synthesis; raw peaks below 0.12.
- `tests/validate_engineering_calibration.gd`: **unrun** original-main-scene QA draft, covering all 120 targets from the real player and explicit negative cases.
- `QA_PLAN.md`: actual-engine acceptance cases and gates beyond the focused script.
- `tools/build_candidate.py`: deterministic scratch-only data/audio generator. Writes only this bundle. Verifies retained source, model and current Game model hashes.
- `tools/audit_source_poses.py`: exact frozen-GLB triangle ray and capsule screen. No engine invocation.
- `tools/test_candidate.py`: pure Python/source/PCM checks; explicitly does not claim to parse GDScript.
- `tools/glb_geometry.py`: copied, inspected frozen-source GLB geometry helper, used read-only by the scratch tools.
- `reports/`: reproducible build, PCM, pose-screen and pure-test receipts.

## Interaction and safety contract

### Original dispatch, unchanged

The player holds RMB to focus and presses E. Its existing ray's first collider must be the precise Area under the relevant control; that control alone exposes `interact` and `get_interaction_label`. There is no panel-wide interactable collider or Area, click handler, proximity trigger, second ray-selection system or player modification.

On activation the control revalidates the existing actor target once, repeats the original first-hit ray once, requires empty hands/enabled gameplay, and requires the camera on the front side. It does not skip collisions or scan the room. Held carts/tools remain governed by the untouched original dispatch and physical tether.

All labels begin with calibration context and say "local test". The real gate's two buttons and existing labels/controllers remain separate and are not counted as calibration controls.

### Source movement and faithful rest

The source travel interval always contains zero. The neutral imported transform is preserved exactly at bind time; binding makes no pose adjustment. The motion endpoint is the source's positive rotation limit or negative push limit. That displacement is applied in **source-coordinate space** about the **source pivot/axis**, then mapped through the actual source visual transform. The whole imported mesh moves together, preserving its source mesh/material identity. After the finite effect or cancellation, its exact saved local transform is assigned back, avoiding accumulation drift.

Momentary-return, bounded detent-return, press-return and local pulse feedback finish in 0.52–0.68 seconds. Inputs while busy are ignored, with no queued replay. A 0.9-second per-control cooldown uses physics frames so fixed-step QA can exercise it without adding real-wall-clock sleeps. Up to four controls may run at once.

The source contract specifically makes actuators `actuator_no_body_contact`. This draft preserves that choice; it creates no actuator rigid body or moving contact collider. Collision clearance of the real player's pose is a separate QA requirement.

### Local visual/audio effects only

For the 31 face/courtesy pulse controls, only an explicitly named existing surface on that one ACT mesh is duplicated. Its material's color/roughness/textures remain unchanged; temporary emission is bounded at 0.22 and restored by reinstating the exact former override pointer. No shared material, shader, glass, room-light property, shadow selector, gate, reactor, security, lift, network or save-state API is modified. Other controls use movement and the selected short sound.

The audio owner uses four fixed `AudioStreamPlayer3D` nodes shared by the entire bank. It validates known cue names, raw file hashes, finite WAV duration and no-loop mode. If sound is missing or a slot/cooldown is unavailable, local mechanical feedback still completes and the sound start returns false, never a fabricated success. There are no 120 continuously active emitters.

The `bounded_cake_candidate` source identifier remains reserved for `ENG2_WORKBAY_MORALE_12`. That button performs only a harmless press-return/click. Cake enablement is false, probability zero and spawn budget zero. No random trigger, cake actor, inventory or dispenser is implemented in this pass.

## Proposed integration, for the accepting lane only

1. Complete and retain the existing new-cell geometry/physics gate, required backups and full-scene regression prerequisites. Do not use these draft interactions to conceal a blocked pose, gate or room contact.
2. Review this draft and parse/compile its GDScript only in the authorized testing lane. This author has not invoked an engine. Fix parser/type issues in the candidate first; do not call the current textual/source checks an engine pass.
3. Place the four scripts in the Game `scripts/` destination, the data contract in `data/architecture/`, the WAVs in `assets/audio/engineering_calibration/`, and the focused test in `tests/`, only when the parent accepts integration. Keep this scratch delivery unchanged as provenance; version any adopted revisions separately.
4. Import through the project's normal validation workflow. Verify the existing GLB remains losslessly imported with its exact retained hash, and inspect WAV import settings for unintended normalization/gain/looping.
5. Create a reviewed contract revision enabling `adoption_gate_accepted`. Preserve all protected controller hash pins. The current `secondary_engineering_cell.gd` hash is recorded as baseline provenance but is intentionally not enforced by the new builder, because the one integration call will change that file.
6. At the end of the existing `secondary_engineering_cell.gd` builder, after its source/collision/gate/light setup, call the new builder once with `(wrapper, visual)`. Use the already loaded visual. Do not reload or duplicate the source room, reparent the ACT meshes, change source contacts or replace the real gate controllers.
7. Before interaction, existing geometry/material/census tests must still pass in the rest state. During a local pulse the participating mesh intentionally has one temporary surface override; after it, the original-null override must be restored. Do not weaken existing material/source checks to accommodate a leak.
8. Execute `QA_PLAN.md`. Focused runtime success is not full-project validation, first-pass architecture acceptance, audio acceptance or target-device performance acceptance.

## Reproduction in scratch

From this bundle's parent workspace, run the Python scripts in order with `PYTHONDONTWRITEBYTECODE=1`: build candidate, audit source poses, then pure tests. They use already installed NumPy; no software installation or engine is needed. The builder pins the source GLB hash `6896d757c5a248d0fcf37a2ae7a197de24566a3fec3f80ce80cdc12186e34368` and refuses a different artifact.

The current receipts record 120 source binds, 16 rejected overlapping-box pairs, zero refined target overlap, 120 passing source-pose screens, four generated original WAVs, and six passing pure-source test groups. All actual engine, import, listening, graphical and aggregate stages remain **UNRUN**.
