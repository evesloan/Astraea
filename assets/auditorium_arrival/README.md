# Auditorium arrival fittings

Two original, unplaced Batch16 components for the historical D11 cultural programme. The original ship is absent. These files add no room, door, capacity, current show schedule, row placement, or verified foyer/workshop connection.

## Authored pieces

- **AST-CUL-001 — Acoustic programme wing and removable cultural cassette.** A shallow asymmetrical walnut frame rises from a rounded stone plinth. Its crowned upper profile and real returned edges enclose an original *A Thousand Small Worlds* programme study. The reverse has a navy fibre service cassette and a backed amber textile insert. The navy/amber materials express absorptive design intent; no acoustic performance is measured. The rear panel, edge returns, bosses, grip and its own markers belong to one real removable root. Access means withdrawal along source +Y, with hand support and release/tool procedure still unverified.
- **AST-CUL-002 — Curved usher counter with lower writing wing and programme storage.** The swept public shell supports two shaped stone working levels, an original usher mark and a restrained amber inset. The open staff side has a useful programme cubby and shallow tray drawer. Its complete tray, side/back walls, fascia, long runners, bosses, pull and markers move together. Fixed bearing overlap remains 0.150 m at the proposed access pose. These are supported geometric configurations, not a functional ticketing or drawer mechanism.

## Measurements and economy

| ID | Closed width × depth × height | Evaluated triangles | Editable semantic meshes | Export material/ownership groups | Collision proposals |
|---|---|---:|---:|---:|---:|
| AST-CUL-001 | 1.200 × 0.640 × 2.300 m | 332 | 19 | 8 | 24 |
| AST-CUL-002 | 1.510 × 0.780 × 1.065 m | 592 | 32 | 7 | 32 |

Source XYZ is metres, Z-up, with public front −Y and service +Y. Both pivots are floor (0,0,0). Actual native GLB mapping is (X,Z,−Y), with its node hierarchy authoritative. The dimensional limits describe closed components. Rear removal moves 0.320 m and expands AST-CUL-001 overall depth to 0.825 m. Drawer travel is 0.280 m and expands AST-CUL-002 overall depth to 1.024 m. External staff/service approach proposals remain separate empty volumes.

## Editable source and poses

Open `source/AST-CUL-001.blend` or `source/AST-CUL-002.blend`. Deliberately named meshes retain distinct timber frame, material returns, work surfaces, stow floors, supports, bearing parts and artwork. There are no QA floor/cameras/lights in production sources. `REAR_SERVICE_PANEL` and `USHER_DRAWER` are true ownership roots, saved at their closed translation of zero. Their explicit source/native translation axes and access distances are custom properties. Set only the root's source Y translation to the recorded distance to inspect an access pose.

Primary exports are `exports/AST-CUL-001.glb` and `exports/AST-CUL-002.glb`; `_access.glb` derivatives retain the same design and hierarchy. Moving derivatives do not count as extra designs. Evaluated export copies consolidate by real material and moving ownership. Original semantic sources remain unjoined.

## Production inputs and rebuild

Run from the catalogue root:

`blender --background --threads 2 --python-exit-code 1 --python assets/auditorium_arrival/source/build_auditorium_arrival.py`

Twenty precise inputs are listed in `dependency_manifest.json`: the new generator; original graphic script, font/license and two source PNGs; the unchanged common and new auditorium helpers/manifests; and all ten loaded shared texture roles, including unused roles packed into native sources. The generator reads only these source paths anchored to its own staged catalogue root; it does not read QA, an existing .blend, GLB, or earlier generated manifest.

Original graphics can be regenerated with `python3 assets/auditorium_arrival/source/draw_programme.py`. Unmodified DejaVuSans is bundled with the full distribution notice in `source/fonts/`; artwork is authored anew, with no pixels from the architectural references. Its abstract orrery uses twelve distinct worlds and no invented current showtimes. The graphic PNGs are source inputs to Blender, rather than renders of another asset.

The isolated rebuild starts with no .blends or GLBs and reproduces both artwork PNGs, all four GLBs byte-for-byte, and marker/collision JSON exactly. See `qa/source_only_rebuild.json`. An attempted syscall trace was blocked by container ptrace policy; the receipt makes no syscall completeness claim. Reviewer-only clean staging independently reproduced the outputs before capture.

## Evidence and boundaries

- `qa/source_checks.json`: evaluated source physical-marker distances, actual normal directions and named contact witnesses
- `qa/glb_validation.json`: raw native GLB finite triangles, UV areas, winding/unit normals, transforms, embedded PNG pixel equality, counts and bounds
- `qa/native_marker_checks.json`: actual node hierarchy, source/native triangle signatures and physical/proposal marker transforms/normals in closed and access states
- `marker_api.json`, per-asset manifests and `collision_proposals.json`: explicit frames, real owners, useful voids, complete translations and structural collision proposals with zero omitted visual parts
- Independent Batch16 reports under the catalogue's `qa/batch16`: complete convex/SAT/LP useful-void and continuous-access tests, zero-area-contact distinction, collision coverage, support graph, full-orientation finish checks and capture clearance
- `qa/camera_preflight.json` and `qa/render_evidence.json`: actual imported ordinary-height 640 × 360 pictures, exact cameras and source/export/image hashes

All failed/superseded source and evidence revisions remain under `qa/revision*`. The source-only stage directories are evidence, not production inputs. The four views use a separate neutral inspection floor and lights; they are not game geometry or room arrangement.

No source or export demonstrates real host mounting, stability, loads, structural fixing, door/pocket or cart clearance, audience flows, six-species reach/fit, acoustic/photometric performance, a runtime mechanism, engine budget, or user visual acceptance. Those remain explicit later gates in the restored original host.
