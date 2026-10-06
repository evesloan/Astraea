# Workbay recessed service-cell integration contract

Source proposal only. Current Game remains untouched. The user approved the improved spatial direction; source, floor, door, physics, light and runtime gates remain separate.

## Models and ownership

- Family: AST-ENG-008 / secondary_engineering_section, new dense_bays_section derivative
- New section GLB includes the120source-bound calibration actuators plus the compatible equipment placement and new section, all at identity world transform
- Do NOT instantiate the unadopted dense_bays equipment GLB beside the section GLB; that would duplicate its contents
- Preserve original AST-ENG-008 section/context and already-adopted essentials. They are referenced in the .blend study but excluded from the new section export
- All preview compiler-floor meshes are excluded from the section GLB. Floor changes below must go through the real floor owner
- Fixed new glass uses the unchanged bridge_pressure_glass graph on one visible sheet. Each pane has an exported26mm contact-proxy bound; instantiate its actual thin BoxShape, not a whole-enclosure convex hull. The maintained door opening must remain open in static contact

## Real floor change

Named existing owner: D02_secondary_engineering_floor, upperY6, thickness0.24.

Cut the exact XZ rectangle X21.9..27.1/Z−406.6..−403.65 out of that owner's upper polygon. The current slab cannot remain invisibly over the lower cell. Preserve all other floor regions/owners and the uncut part of this floor. Lower slab is Y5.55, thickness0.24, underside5.31. Assign an explicit new compiler-owned lower-cell floor record. Keep the D01 Cold provisions architecture reservation clear to that underside; absence of present room geometry is not permission to forget future programme headroom.

Existing east3.6m turn square remains X28.2..31.8/Z−406.8..−403.2 atY6. North/south service strips and other protected prisms remain unchanged. The nominal south bench-body gap is1.65m; the real drawer-pull clearance is1.53m. North projecting machinery leaves approximately1.69m. These are staff operating approaches, not a3.6m loaded-cart loop.

## Stair and maintenance access

Three150mm risers lead down from west through a real1.2m gate:
- Door clearZ range−405.10..−403.90
- Descent zone X21.90..22.80; first two upper tread meshes atY5.85/Y5.70, followed by the actual lower floorY5.55
- Lower landing X22.80..24.00/Z−405.10..−403.90
- Upper approach X20.70..21.90 atY6
- Machinery skid X23.85..25.85/Z−406.25..−405.50; service face is south, reached from that landing. No route behind the machinery is claimed

player.gd has no special step-up implementation. Use the existing Grand Pool source-bound visual-stair/flight-contact convention, without altering player.gd. Proposed flight-contact upper quad is(21.9,6,−405.1),(21.9,6,−403.9),(22.8,5.55,−403.9),(22.8,5.55,−405.1), with bounded thickness and named visual-only treads. Actual ascent/descent, end seams, foot support and under-tread contact must be tested; the source study does not certify them.

Cart stays on the upper route. A portable-tool shelf is outside the cell near X27.2..28.08/Z−407.03..−406.52. Validate a real parked cart/operator envelope, ordinary pickup/carry through the west approach/steps and safe return using existing held-object controls. Do not claim cart descent or an implemented cleaning task merely from this layout.

## Source-bound gate fitting

Stable ID: D02_secondary_engineering_workbay_cell_gate.
- Canonical closed-rest pivot: (21.8675,6,−404.5)
- Source moving node: LEAF_WORKBAY_CELL
- Opening travel: world(0,0,−1.22), into the north horizontal pocket
- Closed complete leaf/frame bounds: X21.84..21.895/Y6.03..8.44/Z−405.12..−403.88
- Original visual study posed this open. The installable source/export stores closed rest; the diagnostic render opens it explicitly
- Two fixed, source-marked controls: TARGET_CELL_GATE_OUTSIDE and TARGET_CELL_GATE_INSIDE. They operate the actual gate, are not counted among the120harmless calibration candidates, and require first-hit area/shape proof on both sides

Existing guest_entry_door.gd is NOT a drop-in fit: it asserts only the1.56/2.36m paired catalogue profiles. Do not scale one silently. Add a narrowly source-bound single-leaf fitting subclass using service_door.gd's existing state, obstruction and pause/physics lifecycle, with this exact visual node, travel and contact extent. Override fitting setup, pose and bounded swept-volume query locally. Keep old profiles, their dimensions and all existing door behavior unchanged. Give this gate an honest service description; SunCorp restriction is architectural identity until an actual access-rule owner is approved.

## Lighting and panes

The early new glass boxes were26mm thick with a double-sided alpha0.28 material, causing two transparent-surface crossings per pane. New visual sheets remove that extra surface while retaining the exact material/profile and separate physical thickness. No old glass or shared shader edit is included.

Actual supported proposals include cell and threshold task housings, capped structural yokes and retained north/bench sources. Runtime settings are a bounded local trial, not a source-render watts mapping. Preserve the original8active-source/32candidate selector. Prove new emitter exits, actual intended receivers, selection during upper/lower movement, shadow behavior and no through-wall illumination before adoption.

## Required gates before claiming usable installation

1. Independent source/export triangles, UV/materials, all120IDs, changed contact/port ownership, source markers and explicit preview/context exclusions
2. Independent retention and exact new-only source copy; old assets remain hash-pinned
3. Bounded named Game preimages/allowlist: floor-owner revision, new lower owner, section instance, local gate fitting, source-bound contact data and focused tests only
4. Actual compiler floor topology, all original unchanged floor regions, lower/D01 reservation and cap support
5. Original controller: upper arrival, west gate, down/up three-step path, lower service face, safe recovery and no unsupported seam
6. Actual gate opening/closing/blocked travel from both sides, held-object priority, repeated inputs and no collision through pane/pocket
7. Upper cart parking, portable-tool carry and return; no loaded cart stair claim
8. Relevant existing engineering/door/lighting/floor regressions, normal processed/clear-world original-eye and threshold views, then fresh aggregate validation as parent schedules

No Game import, code write, floor mutation or adoption was performed by the source worker.
