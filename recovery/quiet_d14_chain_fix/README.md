# Quiet / Family delivery chain correction — unfinished ship

Cumulative successor to the incomplete QuietD14 composed fix. Frozen source remains f94cc1c8fde5e310bfae3ebd045272f67de66089. Do not change the frozen checkout revision or discard either earlier delivery backup.

The first fix composed the real Quiet Grove specialty guard and D14 staff opening correctly, but omitted six downstream exact script/receipt pins. This package closes their transitive dependencies together: Quiet D13/D16, Family D13–D16, and Family specialty's D14 receipt provenance. Twenty-two pin links change. All non-pin receipt fields, geometry, room/rest identities, capacities, bounds and 0.0002 guard tolerance remain unchanged relative to the first fix. Historical documentation pins are preserved as history.

## Apply to the existing isolated laptop repository

Close Godot first. Extract this archive to a separate directory. From that directory run:

```
python apply.py --repo "PATH_TO_ASTRAEA_REPOSITORY"
python apply.py --repo "PATH_TO_ASTRAEA_REPOSITORY" --apply
```

The first command preflights without writing. The installer accepts only exact frozen baseline or exact first-fix bytes (or already-final bytes), validates every payload before any write, refuses unknown local changes, and backs up replaced bytes under `.astraea-delivery-backups/quiet-d14-chain/`. Existing `.astraea-delivery-backups/quiet-d14-composed/` is preserved. It neither imports nor launches Godot. Reapplying is a verified no-op.

Payload: 11 files total; the already-first-fixed laptop changes only 8 (six receipts, Family guard provenance and source-contract manifest). QuietD14 script, composition helper and geometry JSON are byte-identical to the first fix. PATCH.json records every allowed input and output hash. Source contracts: 17,488 → 17,495, adding seven exact receipt/provenance entries; every prior contract remains unchanged. Against original frozen source the composition JSON is the eighth addition to 17,487. Keep the earlier exact .import/embedded-PNG supplement installed.

## Verified scope

Godot 4.6.3.stable.official.7d41c59c4, bounded actual-resource startup-order fixture: actual Quiet17/30 adapters, QuietD15 → D14 → D13 → D16, Family original adoption, FamilyD13 → D14 → D15 → D16, then actual Family47 successor adapter. All completed; 47 Quiet and 47 Family specialty entries, 82 ordinary Family homes retained. Composed guard collision faces equal final visual mesh faces. No positive-fixture script errors. Unrelated ship systems omitted deliberately.

Eight deliberate negative tests rejected before mutation: corrupted QuietD14 predecessor pin in each of the six dependent builders, wrong composition-owner transform, and wrong preimage mesh. The eight assertions in negative_guards.log are expected test evidence, not successful-startup errors. All 157 source-pin edges in the eight receiving receipts and all 17,495 source-contract files were checked against exact overlay/base bytes. Installer tested against baseline, first fix, idempotent repeat, and unknown-survivor refusal with no partial writes.

This is a focused delivery correction, not another full-ship test. Coordinate the next laptop run with its existing owner; do not start a concurrent launch. Windows startup after this cumulative patch, export, whole-ship performance, full gameplay and final visual acceptance remain unverified. No density/FPS acceptance can be inferred from the earlier run that omitted failed receiving work.
