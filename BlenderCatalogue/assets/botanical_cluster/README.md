# Botanical cluster expansion — AST-BOT-007 / 008 / 009

Three original script-assisted editable Blender designs for a proposed planted commons edge. The actual diorama and both residential-court reference images were inspected. The forms use intentional pleated fans, unequal rearward trailing stems, and a three-clump upright flowering rhythm. Existing designs and shared material artwork are unchanged.

| ID | Authored form | Actual source envelope, metres | Triangles | Static export mesh / primitive count |
|---|---|---|---:|---:|
| AST-BOT-007 | Three joined stems carrying nine folded fans | X −1.093951…1.189906; Y −0.804781…0.913285; Z 0…2.529818 | 1,130 | 4 / 4 |
| AST-BOT-008 | Five unequal rearward arches from a rooted crown | X −0.376961…0.410513; Y −0.080840…0.887478; Z −0.570972…0.253770 | 1,256 | 4 / 4 |
| AST-BOT-009 | Three independently rooted clumps, six flowering uprights | X −0.511402…0.484828; Y −0.250591…0.233850; Z 0…1.127064 | 2,448 | 5 / 5 |

Source files are `source/AST-BOT-xxx.blend`; exchange files are `exports/AST-BOT-xxx.glb`. The source retains every named stem, fan, blade, collar, pedicel, calyx and petal as editable meshes. Runtime copies consolidate by material role; there is no individual-leaf animation. These counts do not establish engine or target-PC performance.

## Coordinates and root fit

All quantities are metres. Source X is right, Y rearward, Z up, with front −Y. Native GLB maps `(x,y,z)` to `(x,z,−y)`: native +Y is up and native −Z is the trailing rear direction. Origins are soil-plane datums. Root/contact empties are exported and verified through actual native node transforms. Foliage extremities are not contact markers.

- 007 actual root contact diameter is 0.340 m. Its proposed root reservation is a 0.440 m diameter footprint, fitting a 0.730 m strip. Proposed spatial soil depth is 0.260 m, within AST-BOT-004's 0.285 m modeled depth. Lowest actual fan foliage is Z1.230 m; this is a crown measurement, not universal headroom. Roots below soil are not modeled.
- 008 actual soil contact is the ten-sided crown within X ±0.085 m and Y ±0.080840 m. Reserved root rectangle is 0.360×0.290 m. Proposed spatial soil depth is 0.200 m. Negative Z is intentional on its rearward tails. No pot or rail support is invented.
- 009 has three real soil-contact collars at (−0.250, −0.015), (0, 0.025), (0.250, −0.010) m. Each has 0.070 m contact radius and 0.090 m reserved radius, inside the overall 0.800×0.350 m root reservation. Each clump has a complete geometry support path to its own soil contact. No above-soil connector spans the clumps. Proposed spatial soil depth is 0.240 m.

Reservations and depths are component placement proposals only. No horticultural, species, biological, irrigation or load suitability is claimed.

## Rear coping clearance

For the proposed placement of 008 in 010 at source translation (1.100, 0.690, 0.790) m, the rear coping band is local Y0.164…0.347 m, top Z0.040 m above the soil. Every actual plant triangle, including leaves, is clipped to that band: minimum plant Z is 0.167600 m, giving at least 0.127600 m vertical separation from the coping top in that slab. The actual transition-mesh test is separately hash-bound in `qa/trailing_transition_clearance.json`; future component changes need rebinding. This is a relative component arrangement and assigns no ship coordinates.

## Materials and geometry

Existing `materials/botanical` roles remain unchanged. All textures are opaque RGB images, with no alpha cards. Leaves and petals are genuinely folded open surfaces using the library's opaque two-sided roles; bark supports are closed. There are no enclosing foliage collision meshes. Fine leaves, flowers and petioles are non-colliding.

Collision proposals contain 11 local crown/trunk segment hulls for 007, 2 small crown hulls for 008 and 6 small collar segments for 009. These preserve the space between stems and clumps. Finite sampled hull overreach is at most 0.000174 m on 007 and zero in the sampled sets for 008/009. This is a finite source approximation measurement, not a global Hausdorff bound or runtime collision behavior claim. Whole-triangle clipping verifies the declared empty side/front probe boxes.

## Rebuild and checks

Run the generator with Blender 4.3.2:

    blender --background --threads 2 --python-exit-code 1 --python source/build_botanical_cluster.py

A fresh source-only stage contains exactly the original generator, `standards/botanical_materials.py`, the botanical material manifest and all six loaded material images, including the unused soil role. It starts without outputs or QA inputs. It reproduces all three final GLBs byte-for-byte, including geometry, material textures and markers. Source container bytes can differ by save path/session; reproducibility is also bound to editable names, geometry bounds, joins and marker records. See `dependency_manifest.json` and `qa/source_only_rebuild_receipt.json`.

Author checks reload the actual .blend files and verify all supported part chains, closed-solid topology, positive volume, root surface normals, real UVs and packed material graphs. An independent binary GLB parser checks finite geometry, winding, normals, noncollapsed UV area, actual native bounds and embedded PNG pixels. `qa/source_native_geometry.json` compares every source/export triangle by material, transformed position and UV; raw vertex discrepancy is below 1e−6 m, UV discrepancy below 1e−6 and normal discrepancy below the explicit 2e−4 export-quantization tolerance.

The final source/imported PNGs and `qa/render_evidence.json` bind exact frozen hashes and cameras. `qa/pre_consolidation` retains the earlier full-semantic exports, source/imported pictures and the superseded 009 connector source. The failed initial crown-camera preflight is retained separately; it failed before any render because the conservative bounds clipped the bottom edge. No source geometry changed for camera correction.

All images are Blender Eevee component inspection aids. Ordinary seated/standing outlook and rear maintenance context are assessed in the batch's joined arrangement, rather than inferred from isolated product views. Game, actor, host, structural load, irrigation, wind, LOD and target-PC acceptance remain pending.
