# SunCorp control labels v2

**Revision:** `suncorp_control_labels_v2_20261006`

A versioned, display-only successor to the harmless-control scratch candidate. All 120 source IDs now have deliberate panel-themed SunCorp labels and brief matching faux status text. The existing reticle displays the label while idle and the row's status during its existing 0.52–0.68 second effect. No new UI, timer, source geometry or gameplay system is added.

**Scratch only. Not integrated or engine-parsed. No Game writes, imports, engine execution or commits.** The adoption flag stays false; actual-engine, listening, graphical and aggregate acceptance remain unrun.

## Review entry points

- `LABEL_REVIEW.md`: all 120 ID → label → status pairs, grouped by the authored machinery theme.
- `data/SUNCORP_LABELS_V2.json`: machine-readable stable label/status map and source-theme evidence.
- `data/LOCAL_EFFECT_ALLOWLIST_V1.json`: exact existing six-profile mapping, all 120 per-ID motion/audio/material bindings, resource caps and disabled cake reservation.
- `data/ENGINEERING_CALIBRATION_DRAFT.json`: complete source-pinned v2 candidate contract.
- `scripts/engineering_calibration_control.gd`: the only changed runtime script. The change is exactly `get_interaction_label()`: return the row's `faux_status` while busy, otherwise its `label`.
- `tests/validate_engineering_calibration.gd`: original-main-scene QA draft, now additionally asserting each exact idle prompt, busy status and prompt restoration. Still unrun.
- `QA_PLAN.md`: actual-engine acceptance plan with the revised display requirements.
- `reports/label_revision_tests.json`: six passing new label/effect-preservation tests, including negative mutation cases.
- `RETENTION_ALLOWLIST.json`: exact scratch source/payload hashes for copying this new revision into a new watched catalogue directory after parent review. It authorizes no Game application or old-bundle overwrite.

## Authored themes and examples

The six CONTROL wings follow their existing station crowns: pressure balance, phase courtesy and relay verification. The WORKBAY rows follow the bench oscilloscope, morale cabinet and the two remote transducer/relay panels. Names are individually authored and addressed by source ID, with no random word bank or generated reassignment when row order changes.

- `ENG2_CONTROL_C1L_01`: **Condensate Bypass** → “Bypass seated”
- `ENG2_CONTROL_C2L_02`: **Auxiliary Phase Trim** → “Phase offset aligned”
- `ENG2_CONTROL_C3R_01`: **Reserve Coil Isolation** → “Reserve coil state registered”
- `ENG2_WORKBAY_MORALE_01`: **Executive Climate Override** → “Preferred temperature noted”
- `ENG2_WORKBAY_MORALE_12`: **Executive Morale Override** → “Request filed in triplicate”

The last is the restrained humorous oddity. Its existing reserved cake identifier remains disabled with zero probability and zero spawn budget; it still only presses/returns/clicks.

The visible strings do not universally say “Calibration” or “local test.” Internal source IDs, provenance, safety metadata and code names keep their original identity. Real gate/door/lift/transport words and actionable open/close prompts are reserved for the real functioning controls. The current real gate remains “E · Open service cell gate” / “E · Close service cell gate,” unchanged.

This revision does **not** alter source pigment artwork. The frozen source still contains markings such as “BENCH TESTER / STATIC,” “MORALE CALIBRATION” and “CONTACT TEST / LOCAL.” The reticle update does not remove those world-space decals; a later artwork revision would need separate source review.

## Exact scope and invariants

- All 120 original IDs, source markers, ACT meshes, original transforms, proposed poses, floor owners, axes, pivots, source travel limits and collision/target sizes are unchanged.
- Only each row's existing `label` is replaced. Six display-only row fields are added: `faux_status`, `display_revision`, `label_identity`, `status_identity`, `panel_theme`, `label_brand`. A top-level `display_revision` is added.
- Every existing runtime effect/motion/audio/material field is byte/value-equivalent to the prior contract. Labels and statuses never dispatch effects.
- The runtime script difference is confined to the existing three-line label accessor. The builder, bank and audio-owner scripts are byte-identical to v1; all four WAV files are byte-identical.
- The same original 2.5 m first-hit RMB/E interaction, 18 mm source-marker spheres, source-axis/pivot motion, exact rest return, per-control cooldown, four active effects and four spatial voices remain.
- There are no reactor, security, airlock, real gate, lift, transport, damage, punishment, networking, persistence or cake effects. Believable fictional labels do not connect the controls to such systems.
- The source-only 120-pose screen still passes, and the six original pure tests plus six v2 tests pass. These are not Godot parsing or physics evidence.

## Preservation and reproduction

The original bundle at `../engineering-harmless-controls` is untouched. `provenance/original_bundle_hashes.json` pins every original file, and the new tests verify those hashes. Historical v1 documents and manifest are copied under `provenance/`; their former universal-label guidance is superseded by this README and the current QA plan, not retroactively edited in the original bundle.

The label-only generator is `tools/apply_labels_v2.py`. It reads the immutable original contract/script, authors the v2 display fields and exact label accessor, and leaves all mechanics/audio bindings intact. Run it with `PYTHONDONTWRITEBYTECODE=1`, followed by `tools/audit_source_poses.py`, `tools/test_candidate.py`, and `tools/test_labels_v2.py` in this revision. The inherited `tools/build_candidate.py` remains v1 provenance and would regenerate old labels; if it is used for a full candidate rebuild, apply the v2 label generator immediately afterwards before testing or review. Do not run either tool in the original bundle.

Review and retain the new versioned tree without overwriting the original. Integration remains the separate parent-controlled step described in `provenance/v1_README.md`, with its **old visible-label guidance superseded** by this revision. Complete the current architectural/physics gate first, then parse and exercise the candidate in the existing engine. Do not relax any prior physical or source-preservation test to accommodate this label pass.
