# Independent bridge-platform source review

Status: PASS for architectural source geometry and contact continuity. No unresolved source-contact findings. Parent runtime floor compilation, integration and traversal acceptance remain required.

Source: `source/AST-CMD-003.blend`
SHA-256: `25b01464a01e7f86e97d6d79eefd2fbf8bd7ddf25d69694c3eb3ff494957a355`

## Independent method

Reopened the actual editable Blender file, read object world matrices and real mesh vertices, and independently reconstructed the convex plan prisms. Pair contacts use clipped polygon area and actual vertical overlap; finite face bearing is accepted, isolated point/edge touches are not. Float tolerance is 0.00002 m. The generated ledger was compared only afterward, with no mismatches.

## Results

- All 3,394 mesh pieces connect through physical contacts
- All 2,833 structural pieces have a complete contact chain to the four exact audited keel-pier envelopes, without using old-spine geometry, parent slab, ceiling or enclosure as a structural shortcut
- Four piers match X/Z centres (−29,−168), (29,−168), (−35.5,−86), (35.5,−86), envelopes 0.8 by 1.2 m and vertical −3.2..114 m; matched to the parent's existing 20 actual keel-contact rays
- All 54 hangers have positive-volume top contact with the new roof frame and positive-volume bottom contact with a floor support
- Bridge inner/outer edge girders, both bypass edges, grids, transverse roof frames, primary longitudinals, roof cantilevers and purlins form an independent connected load path
- All 26 main guard backing/toe/cap and corner-chain tests pass. All four mouths now have guard backing, toe and cap meeting X±4 exactly, supported shallow terminal shoes, and perpendicular backed returns to the actual floor edge. Four independently probed bypassable strips are now closed
- Fore gallery measured clear width 7.12000 m; port leg measured clear width 7.22000 m. Conservative 7 m standing-clear prisms and the full 6 by 6 m L-turn prism are unobstructed
- Both original X±4 spine mouths at Z−181/−173 remain open; whole Z−80..−74 fore apron is clear at standing height
- No deeper belowfloor structure intrudes X±4.1 in the D17 spine zone; no extra low supports occur outside the four audited piers
- Primary core public body volume, retained 109.85 m cover and clearance to Y111 remain untouched
- East return is directly roof-hung with positive contacts at both fore-gallery roof beams/hangers. Its shallow closure measures X3.74..4.18, Y106.265..106.49, Z−181..−173 and overlaps the retained slab envelope by 0.467997 m³, while remaining below the walk surface. No slit or standing-height spine intrusion
- All 20 fixture housings have positive seats, every lens contacts its housing, and actual downward source rays reach the parent floor without new-source obstruction
- No authored doors, semantic floor slabs, broad disguised slab-height panels, extra low support, or disconnected piece found

## Findings closed during review

1. Closed the initial wing-guard terminal gaps to the original spine
2. Added perpendicular backed returns at all four inboard guard ends so guests cannot sidestep into the strip behind the guards
3. Corrected the width declaration to the measured 7.12 m limiting hanger faces

## Evidence and limits

`independent_review_geometry.json` contains reopened actual meshes. `independent_review_contacts.json` contains support paths, assembly contacts, all hanger seats, guard tests, fixture checks, clearance queries, pier matches and measured widths. Reproducers are `independent_review_extract.py` and `independent_review_contacts.py`.

No Godot runs/imports, parent changes, existing assets, source/export/contract edits or backups were performed by this reviewer. Actual keel ray results are reused from the current parent audits; this review independently verifies the source matches those exact approved footprints. This is geometric construction continuity, not engineering certification. Source/export/material fidelity and actual parent runtime adoption remain separate gates.
