# Group7 continuation r002: terminal wings and maintained upper routes

This is a separate, constructed source slice authorized by root after acceptance of the bounded first delivery at `e6abd8100af7c56587dcf7dfb6eb85450dbcd1fe`. Every first-delivery file and its manifest remain unchanged. This slice does not establish completion of Group7 or final-art acceptance. Runtime model/effort is not exposed.

## Constructed sources

`source/natives/G7C2_Fore_Terminal_r002.blend` and `G7C2_Aft_Terminal_r002.blend` retain individually editable semantic parts, materials, packed retained textures, four source door-family instances and four attached light sources. Two compact architectural GLBs preserve geometry by material/contact role. Four additional GLBs are closed door **previews** for source review; they must be dropped when root instantiates the retained operating family.

All exports are world-coordinate Y-up, origin `(0,0,0)`, rotation zero, unit scale. Blender source uses `(x,-z,y)`. No Game script, shared catalogue, host branch or retained source was changed. The G7C2 names are source namespaces; root owns adopted stable IDs and catalogue registration.

The fore roof has 2,603.622 m² of architectural slab; the aft roof has 1,691.315 m². Each has two 3 m wide, 2 m long bridge plates totaling 12 m². Roof slab top is Y69.5 and underside Y69.2. Bridge underside is Y69.28. Ribs and notch receivers are actual constructed parts. Lower facade/seal parts rise from the first-delivery frame top at Y61 to the stepped roof. Upper head and neck walls rise from Y69.5 to Y106.5.

The retained D10–D18 fore/aft routes really extend to Z±530. The low wing roof therefore has an open notch X±6 and extends behind the route end at absolute Z530.7. Neck faces are at X±6.8 and Z±531.5. The currently constructed skin is 0.18 m with receiver members between normal depths 0.18 and 0.40 m. A 0.8 m overall reserved envelope was used in planning, not falsely claimed as a fully built wall thickness. At Z±510 the headwalls step to the locally authored upper terminal widths: fore 70.92 to65 m and aft54.175 to49 m from Y69.5 to106.5. These are local design knots, not adoption of the old global taper guides.

## Floor and connector adoption

`TERMINAL_PLAN_R002.json` records exact new roof and bridge polygons and four retained-route receivers. These source slabs already exist physically. Root may add their planning/coverage records but must **not** generate a second physical slab over them. All retained floors stay owned by their existing builders. The bridge plates abut each exact D11 route edge X±4, Z±517.5±1.5, Y69.5. Root owns connector collars at those retained boundaries.

Each roof maintenance bay has actual guards, a cut in its newly owned neck side and a retained AST-STF-008 closed source preview at `(±6.8,69.5,±517.5)`. Placement/yaw, original family hash and controller dependency are supplied in `TERMINAL_DELIVERY_R002.json` and `qa/door_input_receipt.json`. The original 2.4×2.54 m framed aperture remains; clear between existing handles is2.168 m. Root instantiates the original family with `Game/scripts/service_door.gd`, preserving hinge identities, permissions, focus and interaction. The door sweep faces the roof bay. No operating door or route/cart acceptance is claimed here.

Four source hardware/lens/downlight placements are built at `(±7.15,72.28,±517.5)`. Each points down, proposes range3.5 m and25° half-angle. The emitting point is below its lens. Runtime lights are not included in the compact exports: root registers the supplied positions and values through its existing lighting budget and controller. Diagnostic daylight in the views is separate from these sources.

Root should add collisions for the `solid_skin`, `solid_frame`, `solid_guard` and `solid_roof` export categories through its established asset pipeline. `visual_lens` is visual only. Doors receive their existing family/controller collision handling. No swimming, ride physics, whole-engine run or pressure/load certification is part of this source construction.

## Retained inputs and rebuild

The parent package retains the full governing master inputs, sources and materials at pins `77a745750169a8ee853e71785f82fd2862bdaba5` and `9d6f8518f9ddbe5892711ca4eb4849a46fbd32be`. The Group2 boundary snapshot at9311 is coordination evidence, not silent replacement of the Game pin. Original overview/engineering pixels and the full whole-ship section coordination were reopened for this slice. The four door native/export/manifest/controller inputs are copied with exact pin hashes inside this slice; no new input fetch was needed. Do not run the first delivery's hash or publication script for this continuation, as that would alter its preserved manifest.

Use the supplied Python3 environment with `AstraeaTools/pythondeps` (NumPy and Shapely) and Blender5.1.2. Scripts deliberately refer to those verified MousyLaptop runtimes; moving hosts requires changing those paths in this slice only. From the project root:

1. Run `continuation_r002/source/check_retained_batch.py` using Python.
2. Run `materialize_door_inputs.py` and `prepare_terminal_plan.py` using Python. The materializer rejects conflicting existing bytes.
3. Run Blender background with two threads and `--python continuation_r002/source/build_terminal_slice.py`.
4. Run Python `check_terminal_exports.py` against final exports.
5. Run Blender background with two threads and `--python continuation_r002/source/render_terminal_views.py`; inspect the six actual PNGs.
6. Recheck retention. Run Python `publish_r002.py <phase>` only with the already authorized Git connection. It stages this subtree only, preserves all first-delivery blobs, checks raw commit bytes, uses a non-force push to the existing handoff branch, and verifies the remote commit.

The script paths above are relative to `external_packages/group7_hull_atrium_20261009`. Rebuilding changes this slice's own generated sources and receipts; it never writes the first delivered source batch. Native backup files and local publication internals are excluded from the resource manifest. No duplicate watch/publisher service is created.

## Remaining coordination

The upper route opening has **no new roof cap**. D18 is an occupied retained route atY106.5; root must resolve its actual roof/headroom rather than silently cover it at106.5 or cut its floors. Root also owns the neighboring general-body seam boundaries atZ±510, final collar/asset/floor adoption, service controllers and light registration. House/private window and lift interfaces remain unchanged and open for their owners. No second skin was placed on the tight retained crown roofs. Other upper-body walls outside this bounded terminal slice remain separate construction work.

Verification receipts distinguish the bounded sources, floor checks, source/export equivalence and Blender import smoke check from engine, movement/cart, pressure, material-performance and final visual acceptance. Root performs integrated checks and final adoption.
