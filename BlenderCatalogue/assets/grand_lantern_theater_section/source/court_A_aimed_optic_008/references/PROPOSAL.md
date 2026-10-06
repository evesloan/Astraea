# Court A local-light refinement 006

Scratch-only source screen; no engine, import, live patch or shared writes.

## Measured candidate

FP 2_D 11_BANK_0 at (-69.5,73.75,-138.3): aim (0,-0.6427876097,-0.7660444431), 40° below horizontal toward−Z. Retain 75° fullcone,7.9 m range,0.8 energy and warm color. Prefer this over 45° or a 90° cone for a diagnostic.

## Exact receiver screen

| Receiver | Range m | Current off-axis° | 40° candidate off-axis° | Clear/in-cone current → candidate |
|---|---:|---:|---:|---:|
| Front crown broadleaf centroids | 4.81–6.10 | 0.52–23.63 | 5.83–24.58 | 584/722 → 584/722 |
| Main counter top | 3.58–4.02 | 28.26–38.40 | 13.46–25.27 | 9/14 → 13/14 |
| Lower writing stone top | 3.82–4.21 | 31.51–41.85 | 16.31–26.89 | 4/14 → 11/14 |
| Usher mark front | 4.03–4.10 | 41.42–41.75 | 26.63–27.29 | 0/2 → 2/2 |
| Reception printed programme | 3.60–3.72 | 33.61–36.42 | 18.85–22.38 | 132/132 → 132/132 |
| Original wall programme | 7.18–7.34 | 13.43–22.63 | 28.37–36.42 | 120/132 → 120/132 |
| Side-table programmes | 4.47–4.68 | 53.18–60.93 | 44.97–48.95 | 0/264 → 0/264 |

All 1,440 authored crown broadleaf triangle centroids were tested. Front band is native z≥−143.1, the crown stem plane; full rear-band results are preserved too. Programme grids use 66 barycentric samples per source triangle, including perimeter and shared-edge duplicates; these counts are not area fractions. Complete newCourt source triangles 44,906 plus retained CourtA architectural triangles 1,536 were segment-tested. Prototype triangles use exact native_matrix transforms. Fixture subset 120 triangles.

## Physical fixture gate

The physical opal panel is horizontal, normal(0,−1,0). No visible tilted optic, reflector or louver is present. Proposed axis is 50° off that normal. Both current and 40° axes escape the real opening; this proves geometric escape, not that the visible lamp supports an asymmetrically aimed spotlight. Metadata-only re-aim is not a passed strict optic-alignment gate.

65,536 uniformly spaced cone-rim azimuths: current 75° cone 66.1819% escape;40°/75°87.7670%;45°/75°100%. Fractions describe cone-boundary directions, not beam energy. Current rim has upward rays reaching the lens;40° rim has a shallow sector hitting the hollow frame.

Wall programme top-center(-69.5,73.265,-145.46499634) hits the frame at 0.250575 m. Its centroid clears. Twelve of 132 retained face-grid samples are lip-blocked. A single clear center ray cannot certify the face.

If strict visible axis alignment is required, source-author a visible, physically attached directional optic with emitting normal(0,−0.6427876097,−0.7660444431), and verify its fit and actual beam escape before adoption. Do not rotate the existing wide flat lens into its shallow fixed housing without new geometry/contact analysis. No such source revision is included here.

## Interpretation and next step

Counter improvement is plausible because its samples move well inside the existing cone. Plant coverage is retained, not proven brighter: representative crown leaf goes 4.67°→11.56° off-axis. Original wall programme moves toward beam edge and may dim;45° clips 60/132 wall samples, so 40° is preferable. Fullcone 90° is not needed for these central receivers and does not solve side tables.

After authorized engine boundary, run the separately prepared unsaved nativeA/B at fixed cameras, exposure, active source roster, materials and all unmodified light settings. Review front-crown layer separation, main/low writing top, counter programmes, original wall sign and warm ceiling rhythm separately. This native trial is a lighting diagnostic until visible-optic gate is resolved. No world ambient, hidden fill, range inflation or 8-shadow/32-candidate changes.

## Evidence

SOURCE_RECEIVER_SCREEN.json contains every exact triangle/barycentric point, normal, range, current/candidate angle, inside-cone result and first blocker. CANDIDATE_PROPOSAL.json contains representative source points and exact candidate fields. screen_receivers.py reproduces the geometric screen without engines. Input hashes checked against receipts and checked unchanged after reading.
