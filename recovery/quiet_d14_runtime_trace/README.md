# Quiet D14 runtime trace — diagnostic only

Frozen baseline f94cc1c8 remains unchanged. This package adds one read-only logging call immediately before the original bounds assertion and appends its helper. Every original executable statement, receipt, tolerance and source/import policy is preserved. This is not a defect fix. No launch is authorized or performed by this package.

Target: `Game/scripts/quiet_d14_receiving_20261016/package.gd`. PATCH.json supplies exact before/after SHA-256; PATCH.diff is reviewable. Original bytes are supplied as package.gd.before.

With no game/editor/import active, stage the additive diagnostic folder separately from the frozen checkout, then:

```powershell
python apply.py --repo "C:\path\Astraea-f94cc1c8"
python apply.py --repo "C:\path\Astraea-f94cc1c8" --apply
```

Only the named file changes; an exact original sidecar is retained. Unknown target or backup bytes are refused. Repeating apply is harmless. Use --restore to return to the supplied exact baseline. Neither command launches Godot. Do not edit the frozen SOURCE_CONTRACTS manifest. Await the parent's next-run authorization; collect stdout lines beginning QUIET_D14_RUNTIME_BOUNDS with the assertion log from that single owned run. Assertion line numbers move because logging was inserted, but assertion text is unchanged.

The captured record includes actual owner/node paths and IDs, mesh identity/resource path/class, global/local transform, custom and measured bounds/deltas, surface formats, triangles/faces SHA-256, metadata, all matching mesh paths, contact identities, D15 original-mesh metadata, current receipt row/hash and engine version. It prints each reached row before checking its bounds.

## Source ordering evidence, not a proven cause

Selected Star Atlas main inherits the consolidated construction pipeline. At consolidated ship lines362–364, quiet_grove_adoption invokes the specialty/bank/court hooks. The QuietGrove17 adapter explicitly removes predecessor guard nodes and installs named successors; its RECEIVING_BUILD lists QG_Batch_38 (972 retained triangles plus two new segments) and QG_Batch_43 (384 retained triangles). These names overlap the later D14 receipt, whose original counts are984/456. At425 QuietD15 builds and substitutes the clinical lobby wall; at428 QuietD14 expects that wall's D15 replacement. QuietD13 and QuietD16 run afterward. This ordering requires observation of the actual selected owner, not a speculative compression or tolerance change.

Both cloud and laptop isolated original-resource checks matched all three expected AABBs, including after laptop duplication/material assignment. They do not prove installed predecessor-chain equivalence. Final diagnosis remains open until the actual guard record is collected.
