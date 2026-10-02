# Staff overhead service components

Three original, editable component designs for batch03. The authored shape language follows the two supplied staff-corridor photographs (supported exposed services, ordinary formed housings) and shared-staff-room reference (plain practical finishes). No reference image pixels are embedded. Nothing is installed in the missing original game.

- **AST-STF-004 — supported straight service run:** 1.2 m nominal pitch; two lipped metal side rails, five folded rungs, two ordered conduits and three separated subdued cables, two paired suspension assemblies, exterior rail splices and hollow conduit union sleeves
- **AST-STF-005 — matching quarter-turn junction:** R0.60 m centreline, tangent entry along +X and exit along +Y, continuous organized services, matching seam profiles, two paired suspension assemblies
- **AST-STF-006 — guarded utility light housing:** 1.12 m formed channel within a 1.2 m pitch, closed end caps and gaskets, twin-bay reflector, opaque opal lens, clips, wire guard, two rigid ceiling drops, saddles and locking pins. It has no runtime light object, no emissive material and no electrical function

## Mounting and joins

Metres, Blender Z up. Every source uses ceiling mounting plane **local Z0**, with hanging geometry below it. The straight entry seam is X0 and exit is X1.2. The turn entry is (0,0,0), exit (0.6,0.6,0); rotate the next straight +90 degrees around Z. The fixture long axis is +X and its origin is the start of a nominal 1.2 m pitch. Standard GLB export converts to Y up.

Bodies end 1 mm short of each seam, leaving 2 mm between two adjacent bodies. The preceding module’s rail collars and hollow conduit sleeves extend 35 mm past its exit seam to surround the next module. Splice bolts and pad/support intersections are intentional construction connections. Exposed cable ends retain the 2 mm geometric seam. There is no utility continuity or structural load claim. See `mounting_api.json` and `qa/join_checks.json` for directions and measured cap checks.

**The lowest service geometry is Z −0.442 m, at the suspension rod ends. The lowest fixture geometry is Z −0.6075 m, at the guard.** To retain at least 2.65 m below the existing fixture requires a ceiling mounting datum of at least **3.2575 m**. The demonstrated 3.30 m placement yields 2.6925 m below the guard. It does not establish real ship headroom and is not automatically suitable for a lower crew corridor. The inspection arrangement leaves an open body/cart-width example; it does not reproduce the narrow photographs or create a room.

Named rods/drop meshes and generator dimensions can be edited. There is no single validated hanger-length parameter and no shorter installation has been checked. Any change needs renewed bounds, support and clearance checks. Ceiling anchors and segmented collision envelopes are proposals for later integration; their substrate, fasteners, capacities and physics are unverified.

## Files and editability

`source/AST-STF-00*.blend` contains named semantic parts, real metric UVs, packed shared staff textures and retained bevel/weighted-normal modifiers where useful. `source/build_staff_overhead.py` is the reproducible script-assisted authoring source. `exports/` holds static material-role-consolidated GLBs, retaining role metadata and embedded original textures. UV-layer names are normalized before joining, with nonzero planar cap UVs. No guest materials or earlier assets were modified.

The generator depends on `../../standards/staff_materials.py` and `../../materials/staff/`. The final sources and GLBs are independently usable with packed images; the generator reads the shared helper. Every source/export is below 0.4 MB, comfortably below the 8 MB per-file limit. `.blend1` autosave backups are excluded. The manifest and dependency records state exact hashes, materials, bounds, origins and dependencies.

## Verification and evidence

- `qa/glb_validation.json`: independent binary glTF accessor validation; finite geometry, normal/winding checks, real UV area, embedded staff texture pixel matches and per-role mesh counts
- `qa/source_reload_checks.json`: every final source reloaded and evaluated; exact support contact, source bounds, real UV layer, retained editability, no light objects, rod/anchor extents, lens/guard clearance
- `qa/join_checks.json`: actual exported cap vertices at both mating seam planes and tangent placement records
- `qa/camera_preflight.json`: conservative framing check, complete silhouette and fixture views
- `qa/render_evidence.json`: exact imported GLB hashes, cameras, dimensions and QA-only lighting scope
- `qa/*_labelled.png`: complete assembly silhouette, 640×360 ordinary eye-height view, close seam, fixture construction detail, and a normal-height joined staff-service-bay component arrangement

The shared service-bay evidence reuses frozen AST-STF-001/002/003 wall/corner/terminal GLBs and the closed AST-STF-007 cabinet. It adds no authored design. The cabinet is 20 mm clear of the back wall/bumper and 295 mm beyond the end of a marked 1.8 m-wide, 2.65 m-long open QA aisle; the side wall clears that aisle by 130 mm. A wire outline declares the sample Z3.30 m mounting datum. The actual imported bounds, file hashes and placements are in `qa/render_evidence.json`; this arrangement is not a complete room or route, and cabinet-open access/cart turning remain outside its claim.

Render path is Blender 4.3.2 Eevee, 48 samples, QA exposure −1.3 stops, without OpenImageDenoise. Image labels are added outside untouched render pixels. All evidence is component QA, not original room, route, game, actor, electrical, structural or target-computer performance acceptance.

Rebuild with Blender from the generator, then run `qa/validate_glb.py` with ordinary Python, `qa/inspect_sources.py` with one-thread Blender, `qa/check_join_records.py` with Python, and `qa/finalize_records.py` with Python. Preflight cameras with `qa/render_imported.py -- --preflight` before the bounded imported-GLB render pass. Run `qa/label_qa.py` after rendering.
