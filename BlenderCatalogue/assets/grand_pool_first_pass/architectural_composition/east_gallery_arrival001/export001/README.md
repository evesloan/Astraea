# East-gallery derivatives: source-equivalence complete

Four existing source002 GLBs are retained byte-for-byte: 76 meshes, 85 nodes,
9,990 triangles. Source parent families remain AST-AQU-016, AST-RES-001 and
AST-LIB-010. Four runtime botanical models are reused later; no botanical
geometry or new floor owner is exported here.

The authoritative success is qa/transform_audit001/FOUR_EXPORT_EQUIVALENCE.json.
The full display report and bulky source snapshots are losslessly gzip-packed;
FILE_MANIFEST.json records compressed and original byte counts/SHA-256 values.
Every manifest source field is the original provenance path, not a portable
execution path. Tooling and its original absolute input paths are preserved for
audit; do not blindly rerun an archived wrapper after relocation.

## Preserved attempts and actual result

- source001 stopped during display snapshot at a blanket no-modifier check. No
  export ran. Its scripts, partial snapshots and failed logs are preserved.
- source002 correctly snapshots the retained static BEVEL/WEIGHTED_NORMAL stacks
  on 25 display meshes, copies actual evaluated geometry and clears modifiers
  on export copies to avoid double application. All four GLBs were exported.
- The first source002 checker passed the first three assets, then rejected the
  display child origin under an overstrict per-axis float32 roundtrip rule. The
  failure and successful first-three reports are preserved without modification.
- A separate offline audit proves all 26 display-child raw translations exactly
  from saved matrices and Blender 4.3.2 cofactor inverse, float32-product/double-sum
  matrix arithmetic, and near-zero canonicalization. A one-ULP mutation fails.
  Strict root and other-node checks remain unchanged. No re-export or GLB edit.
- All four now pass complete source triangle/topology/cyclic-winding, UV, material,
  packed-image and normal checks. Display source-local coordinate deviation is
  zero, maximum world deviation 12.211625 micrometres (existing ceiling 50), and
  maximum normal deviation 8.995e-8 (existing ceiling 2e-6).

Source .blend SHA-256: 9aa232ad30c515eabb128804b6d430ae2cfc3d76f93383a612165281620e6f05.
Its 127 source/evidence files were independently retained at remote commit
15f68cec578f1c054917f0540ac4789821889160, checkpoint 2026-10-06T20:37:09Z.
This export package still needs its own independent publication after copying.

## Native work remains separate

No native acceptance is claimed. Precision-critical imports must explicitly
disable attribute compression; native normals still use Godot 4.6.3 uint16
octahedral encoding. Render arrays and actual collider-grid semantics need
separate checks, together with physical mounts, soil contacts, cart/seat/media
approaches, old routes and ordinary in-game views.

The two actual light-reserve positions are exported with original placeholder
metadata. The retained optical proposal separately measures lens directions,
55-degree half-angle and a 5.2 m trial range. Its 700 W source preview is not
accepted native power. Native aim/power, hotspot/floor balance and natural
selection remain pending; at most two new lights and unchanged active 8 /
candidate 32 budgets apply.
