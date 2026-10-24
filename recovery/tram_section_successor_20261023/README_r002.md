# Tram central section r002 — authored, not admitted

The original tram source, lower lift/pit/stairs, protected slabs, room/capacity IDs,
all five station identities and production admission flags are unchanged. r001 is
independently retained at `41b4bc0883d3f7e2a0216ffc08563db5082835d2`. r002 is a
separate section/bridge candidate, not a selected route or playable scenic ride.

## Physical scope

The 270.630218 m central interval now routes from `(-5.6,-85.3)` through radius
4 m tangent corners near `(-5.6,-78)`, `(44.5,-78)`, `(44.5,78)`, `(-5.6,78)` to
`(-5.6,92)`. Original route points outside that interval and the four other station
docking locations remain. Rail head Y55.74, soffit Y55.55 and boarding Y56.1 stay.
The protected lower band remains Y52.55–56.55, 4 m wide; the upper running band
remains 4 m wide and Y56.1–60.1. No lower headroom reduction, raised slab or hull
cut is proposed.

348 authored parts cover complete guideway ribbons, central receiving members,
the fore boarding apron, replacement edge guards and portal. There are 74 actual
bearing footprints across 41 receiving records. Short overhead arms, maximum
1.5 m reach, connect drops outside the running band to existing D10 apron/terrace
owners. Header/arm undersides are Y60.18, above the full Y60.1 running ceiling;
pads meet the existing Y60.76 slab underside. This establishes geometric bearing
contact, not structural load capacity. South pads use their full 0.42×0.75 m
footprints on the existing D09 owners. No duplicate supporting floor was added.

The new apron butts against the original CENTRAL floor at Z−75, across
X−6.570065119…−3.251441743. The original lift housing, pit, cabin IDs, stair
flights, upper return and floor stay. The old north-end guard opening and obsolete
east boarding portal require named replacements; the old east opening is closed.

## Actual curved body and bridge bearing

The body is fitted by its unchanged 3 m kingpin chord, not snapped to a route
point or forced straight. CENTRAL cursor is 388.515586048 m; body position is
`(-3.185106399,56.1,-78.648574102)`, yaw `1.129009860` rad. The body chord midpoint
is 0.292626557 m inward of the sampled rail center. Rear/front bogie rail cursors
are 386.977888437/390.053283659 m, with relative yaw ±0.384464830 rad at the stop.
The full pose table contains 10,180 rows. Maximum sampled bogie yaw is
0.384783235 rad; maximum lateral slide is below 8e−9 m. These are source fit
results, not moving-wheel/joint acceptance. The retained .20 m slide limit remains.

Bridge hinge origin is `(-4.250841579,56.1,-76.395266383)`, with the same yaw as
the actual body. The required deck reach is 1.385219150 m; the retained reach
1.092592593 m is too short by 0.292626557 m. The successor extends only the moving
deck/ribs between X0.08 and the old deck end. Fixed receivers, hinge and four
knuckles are byte-equivalent; the final receiving tongue translates unchanged.
All Y/Z vertices, 2.18 m usable width, mesh identities, topology, UVs, materials
and embedded source image bytes are preserved. No whole-pivot X scaling occurs.

## Completed focused evidence

`TRIANGLE_GATE_r002.json`: 162,184 retained source triangles checked in the bounded
core/atrium/eight-bearing/CENTRAL station/stair/retained receiver context; 11,736
candidate triangles; zero capsule intersections. Triangles are clipped at the
actual Y bands and tested as projected polygons against the full route capsule;
this is not the earlier vertex-only screen. Later installed district details
are not included, so this result is not whole-ship clearance.

`SOURCE_VALIDATION_r002.json`: 535 source checks passed, including exact input
pins, outward/nondegenerate solid winding, all 74 full actual pad footprints,
fixed/knuckle vertex/normal/UV/index bytes, unchanged bridge topology and
15-frame/.005 m/.001 rad docking criteria. `EXPORT_RECEIPT.json` identifies the
two directly authored runtime GLBs and their exact hashes. No engine or Blender
was run by this worker.

## Sole-engine-owner handoff

Run the native recipe once in a new background process, into a new filename:

```sh
blender --background --python recovery/tram_section_successor_20261023/build_native.py -- --output recovery/tram_section_successor_20261023/native_r002/Tram_Section_r002.blend
```

This creates a named editable derived .blend from the exact authored runtime
mesh/material bytes; it does not overwrite or replace the original native
construction history. Inputs and existing outputs are protected against overwrite.
The .blend has **not yet been generated** at this handoff.

Focused Godot check (source workspace; no import, build, export or full ship):

```sh
godot --headless --path /workspace/Astraea-recovered-e6274e77-20261021/Game --script res://tram_section_successor_20261023/check_connected.gd
```

Use the already selected Godot executable. The check loads the new GLB bytes
directly, creates only the candidate plus retained CENTRAL/stair contacts,
tests unchanged 4 m cylinders and floor continuity from the upper stair return
through the original platform/new apron/deployed bridge into the actual rotated
source024 body. It creates no motor, cart, passenger or operating controller.
It has **not been executed** at this handoff. Root should preserve its actual
result separately, including any failure; do not infer a pass from source tests.

## Exact future production boundary — not implemented here

1. Keep the original source files and configurations. In a named assembly
   successor, replace the three source016 continuous meshes with the three new
   route ribbons, and source017 `M003_Site_*`, `M003_UnderwebGirder_*` and
   `M003_SouthFoot_*` with the corresponding new central receivers. Retain all
   other core/station receivers. Rebuild the affected grouped contacts so removed
   visual geometry does not leave invisible old collisions.
2. In source014 replace only `V2_Central_NorthEnd_infill`,
   `V2_Central_NorthEnd_rail`, the two `V2__CENTRAL__Boarding_Post_*` and
   `V2__CENTRAL__Boarding_Header`. Preserve all other source014 members. Add the
   new apron, side/north guards and old-portal closure. Source018 stays unchanged.
3. Rebind only CENTRAL's source025 fixed barrier receivers and its existing
   bridge/gate identity to the new hinge transform. Fixed receiver reorientation
   and floor-bearing checks are still needed. Use the new bridge GLB for CENTRAL
   only. Its occupancy query must expand from the old 1.24 m length to cover the
   complete longer panel/tongue; never shorten it or reduce the 2.22 m query width.
4. A named boarding-safety successor must evaluate the measured body pose/yaw at
   every stop, retaining 15 stationary frames, .005 m and .001 rad tolerances.
   The old code's `st.yaw == 0` choice of PORT/STARBOARD is invalid for this curved
   station: CENTRAL must retain explicit **PORT** door identity. Do not open the
   STARBOARD door because the station yaw is nonzero. Original phase/occupancy,
   gate, bridge, loaded-cart and admission checks remain required.
5. Bind the named travel-plan successor to these pose knots and unchanged physical
   wheel/bogie interfaces. Do not teleport or override the persistent passenger
   or cart. The old production startup pose remains untouched; after acceptance,
   only initial placement of a newly created empty candidate may use the new dock.

Still required before selection/admission: full source-body swept envelope and
later installed neighbor contacts, apron access/headroom and fixed barrier
receiving, actual gate/bridge sequence and curved dock behavior, native/material
visual inspection, the existing caster/joint hold, moving-passenger ride and
repeated-route performance evidence. The original missing October20 intro director
source remains missing. Neither source fit counts nor this static connection
fixture establish frame rate, full gameplay or scenic visual acceptance.
