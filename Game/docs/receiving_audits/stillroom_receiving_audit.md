# Stillroom read-only receiving audit

Audit date: 2026-10-09 UTC. Source only; no project builds, imports, or edits performed by this audit. Root owns installation.

## Result

No blocking static geometry clash was found for the corrected receiver. Use the outward 0.18 m mitre-buffered shell polygon and a 4 m-wide connector to D12_fore_route. The documented floor polygon follows shell centerlines and does not fully support the walls; its area label also repeats the rectangular allocation area. Installed physics, occupied body/cart/species tests, visual review, runtime light behavior, and structural load-path acceptance remain separate.

## Verified inputs

- Project: /workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4
- Package: /workspace/shared/Astraea_remaining_e_intake_20261009_0451/stillroom/03_stillroom
- All 84 entries in BYTE_SHA256_MANIFEST.json match both byte count and SHA-256.
- GLB SHA-256: 59e42624070aa9c4004ad6fb082cc90be998a9ccc25b6908468c50a981b6da97
- Placement is identity world XYZ metres; floor Y78; top Y83.64.
- Floor-owner snapshot: 303 original structural owners, 116 received owners, 2 Salon owners.

## Correct receiving polygons

All coordinates below are world XZ metres. Top Y78; standard receiving thickness 0.24 m gives underside Y77.76. No holes are required by the tested D12 protected voids.

The allocation [[8,-250],[54,-250],[54,-182],[8,-182]] has area 3128 m². The source FLOOR_PROPOSAL boundary has actual area 3050.96 m². The corrected structural receiver is that boundary buffered 0.18 m outward with mitre joins and intersected with the allocation; the intersection does not change it.

Recommended floor boundary, area 3090.143174841357 m²:

```json
[
  [
    8.02,
    -186.12544155877282
  ],
  [
    12.12544155877284,
    -182.01999999999998
  ],
  [
    49.87455844122716,
    -182.01999999999998
  ],
  [
    53.98,
    -186.12544155877282
  ],
  [
    53.98,
    -245.87455844122718
  ],
  [
    49.87455844122716,
    -249.98000000000002
  ],
  [
    12.12813046733221,
    -249.98000000000002
  ],
  [
    8.02,
    -246.0772760560344
  ]
]
```

Recommended explicit connector boundary, area 16.08 m²:

```json
[
  [
    4,
    -218
  ],
  [
    8.02,
    -218
  ],
  [
    8.02,
    -214
  ],
  [
    4,
    -214
  ]
]
```

- connection_to: D12_fore_route
- The connector touches the original fore route on X4 and the receiver on X8.02, each for a 4 m edge; no positive-area overlap.
- Do not author only the source-documented X8→8.2 threshold: the original floor ends at X4.
- Combined added area: 3106.223174841357 m².
- Portal clear opening is Z[-218,-214], 4 m wide and 3.2 m high; west shell opening is Z[-219,-213].
- Floor footprint covers 161 actual exported datum-contact nodes, comprising 174.474210425139 m² of unioned bottom-face contact area.
- The unbuffered centerline polygon misses 31.582377751588 m² of actual bottom contact across E_perimeter0–6, E_west_north, and E_west_south.
- The corrected floor covers every bottom-face contact within 0.00001 m tolerance, appropriate to observed float export error (<0.000005 m at relevant bounds).

## Owner and void checks

- Exact unioned triangles were used for each of the 421 retained floor owners, not AABB allocation rectangles.
- Corrected floor and connector: zero positive-area same-datum intersection against all owners.
- At thickness 0.24 m: zero positive-volume slab intersection against all owners.
- Zero area intersection with every protected D12 void.
- Source geometry minimum Y is 77.99999690055847, within float tolerance of Y78; no real below-datum protrusion.
- Cinema 2 D11_directory_03 has projected overlap with the southern edge but lies on floor Y69.5; it is not a same-datum floor conflict. This audit does not certify every installed D11 ceiling mesh.

## Route waypoints

All listed points are XZ at Y78. Actual exported triangles were clipped to the Y78.06–79.9 band. Buffered path checks found no positive-area source obstruction and no unsupported floor-sweep area on the union of retained Y78 floors plus the recommended receiver/connector. These are static geometric screens, not an occupied in-engine acceptance.

### arrival_main_lane

Radius: 0.65 m.

```json
[[8.6, -216], [11, -216], [11, -226], [16, -226], [16, -241], [16, -246.7], [34, -246.7], [34, -226]]
```

### care_cart

Radius: 1.7 m.

```json
[[8.6, -216], [11, -216], [11, -206], [16, -206], [16, -191], [14.5, -190.6]]
```

### stock_service_body

Radius: 0.65 m.

```json
[[16, -191], [16.3, -188.8], [16.3, -185.1], [14, -185.1]]
```

### receiving_entry_extension

Radius: 1.7 m.

```json
[[0, -216], [4, -216], [8.6, -216], [11, -216]]
```

## Source mesh and light checks

- 234 mesh nodes; 84,676 triangles; 10 embedded images; no external image URIs.
- All positions, normals, and UV components are finite. Every primitive has normals and TEXCOORD_0.
- Stored normal length range: 0.9999998808–1.0000001192.
- Four degenerate triangles (double-area <1e-10) are isolated to E_identity lettering. No receiver or floor-route failure results from this text artifact.
- No preview/QA floor is present in the delivered export.
- Export bounds: [[8.01999796811415, 77.99999690055847, -249.98000305891037], [53.98000326826066, 83.63999938964844, -182.01999530016425]]
- Twelve punctual point lights: six coves, four spine sources, care task, entry task. No GLB range fields; raw glTF intensity is 91310.37395068219 or 136965.5609260233. They must be normalized by the receiver instead of treated as ready runtime brightness/range.
- Root reports the shared receiving light adapter now supplies bounded 8 m range / 1.2 energy to these point emitters under the existing 8/32 manager. That reported integration was not executed or validated by this read-only audit.

## Quiet Grove upper interface

- Retained source plan SHA-256 matches the package interface: d0bf2e894aa2347ff50ea8580f0ff1d94c16754708732bb7ac94357f61a5775a.
- Reconstructed the 469 explicit mesh records and 11,489 oriented beam records from the retained source algorithm, covering all 11,958 parts.
- No reconstructed part AABB overlaps the Stillroom source volume Y78–83.64.
- Twenty upper guard AABBs graze the recommended floor in XZ; the lowest is StreetTerminalGuard_0_-250 at Y85.06. They are not physical clashes with the Stillroom. Avoid reporting an unconditional zero XZ overlap based only on the package’s empty overlap list.
- The nominal Y84 upper residential floor underside is Y83.76, leaving 0.12 m above the Stillroom roof wherever such a floor applies. This is a datum constraint, not evidence of an actual upper floor directly over every part of the room.
- No residential geometry, support policy, capacity, or identities should be changed. The audit is against the retained pinned plan; materially different live upper-house derivatives still need their own interface check.

## Reproducibility and scope

- Detailed machine-readable output: stillroom_receiving_geometry.json alongside this report.
- Scratch analysis scripts: audit_stillroom_static.py and finalize_stillroom_audit.py; they only read project/package sources and write scratch audit results.
- These results authorize no extra action; they inform root’s existing receiving work.
- No Blender/Godot invocation, build, import, or project mutation was performed by this audit.

Input floor/void file hashes:

```json
{
  "data/generated/structural_meshes.json": "e7cd0cc1c3892a99cf75f2dab4c852f3e1c1864a13b81f828e2a2f93cf239e92",
  "data/generated/received_structural_meshes.json": "e05fd27b14d97d5bdf37a6ac94bb80b1c009342d69ff90142579fe692af3a59b",
  "data/architecture/SALON_RECEIVING_FLOORS_CANDIDATE.json": "f2a04e22b2a085c6fb1c83f195031a43611402cc09eaa165ee278738fa9502dc",
  "data/spatial_layout.json": "75cc3e6259d89da873f5c2fa4fefa2e846427eeda3e5457561d785305a0471d2"
}
```
