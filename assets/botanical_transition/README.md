# AST-BOT-010 — Raised planted-seat end transition

One original script-assisted editable Blender design, expanding the established botanical edge. It preserves the unchanged AST-BOT-004 start profile and its nominal 2 mm construction joint, keeps a useful full-depth timber sitting ribbon, and raises a real enclosed planting cell behind it. The three supplied botanical/court reference images were inspected as composition guidance; no reference pixels or missing ship geometry were copied.

Source: `source/AST-BOT-010.blend`. Native export: `exports/AST-BOT-010.glb`. Generator: `source/build_botanical_transition.py` with local `profile_helpers.py`. All 28 named semantic mesh parts remain editable, with eased arris and weighted-normal modifiers. Native export consolidates evaluated copies into five material-role meshes, retaining 18 actual source/contact/root/mating datum nodes. Current geometry is 1,806 triangles. Opaque ordinary Principled materials and original packed shared textures are unchanged.

## Settled section and uses

Metres; source X follows the edge, Y points rearward, Z points up. Native GLB maps source `(x,y,z)` to `(x,z,-y)`. Origin is nominal start seam at floor datum; real start faces are at X0.001. The intended relative join places this component at X2.4 after AST-BOT-004. All dimensional figures describe component geometry, without assigning a host location.

- Physical overall span: X0.001–1.799, Y−0.490–approximately1.03657, Z0–0.830
- Sitting surface: Z0.470, underside0.415, Y−0.490–−0.020, useful length1.798. Three floor-to-seat bracket/shoe paths are centered at X0.220,0.900,1.580; two real timber bearing rails remain below the three ribbons
- Lower soil: rectangle X0.001–0.560, Y0.150–0.880; topZ0.390, baseZ0.105, depth0.285
- Upper soil: rectangle X0.680–1.680, Y0.150–0.880; topZ0.790, baseZ0.365, depth0.425. The real base occupies Z0.335–0.365, supported by two floor-bearing piers at X0.730–0.830 and1.520–1.620, Y0.220–0.810
- Riser wall: X0.560–0.680. Closed terminal stone wall: X1.680–1.796. Coping and timber finish atX1.799, creating a real3mm terminal finish reveal rather than exposed coincident material faces
- The front and rear retaining walls rise over X0.300–0.680. Upper coping reachesZ0.830. The front raised coping begins atY+0.030, preserving the sitting ribbon and its above-seat clear space
- Proposed AST-BOT-008 root: `(1.100,0.690,0.790)`, within a0.400×0.350 root reservation. Rear coping is root-relativeY0.164–0.347, with top+0.040m. Trailing geometry belongs on the rear side. AST-BOT-007 and009 roots use the existing straight planter context, rather than crowding all three root types into this cell
- Proposed front approach: Y−1.690–−0.490. The unplanted rear maintenance approach begins beyondY1.080; the assembled trailing specimen occupies part of that region, so its final stance must move beyond the measured foliage sweep and retain flanking access. These are finite geometric reservations, not actor/path certification

## Geometry and exchange evidence

`qa/source_reload_checks.json` reopens the actual source, measures every source part, verifies18 real/datum markers, explicit bearing witnesses, all-part floor connectivity and full finite volume grids/rays. It preserves two useful under-seat bays, the opening above both soil levels, a chamber under the upper base, front/rear approaches and the above-seat ribbon volume.

`qa/native_surface_checks.json` resolves real GLB hierarchy/transforms and physical triangles. The actual start profile matches the unchanged004 end by material; maximum sampled profile difference is below0.000001m and the measured nominal2mm join is approximately2.00007mm. `qa/glb_validation.json` checks actual geometry/normal winding, finite and non-collapsed UVs, original embedded texture pixels and source/native bounds. Marker origins and directions are distinguished from physical surfaces.

`qa/finish_plane_screen.json` has zero terminal cross-material same-facing axial overlaps. Remaining candidates are the inherited start profile within its intended construction joint and buried timber/bracket bearing contacts; the screen is advisory, not a global sloped-surface proof.

## Collision limits

There are25 numeric compound proposals, split by real structural purpose and profile changes. They preserve entire lower/upper soil cavities, seated clearance, the two under-seat bays, under-upper-base chamber and front/rear approaches. Soil volumes and thin finish/trim layers are deliberately not collision solids.

The largest observed finite inflation is19.543mm in the independent35mm-grid sample; the author’s finite sample measured15.4mm. Sampled front/rear surface undercoverage peaks0.254/0.301mm; continuous clipping also found nonzero uncovered front/rear surface area0.000154/0.060630m², so complete collision coverage is not claimed. These are different sampling scopes, not analytic global bounds or adopted physics. `qa/collision_volume_checks.json` tests complete convex-hull/box intersection using linear-program feasibility; `qa/collision_overreach.json` records author vertices, face/edge samples and9×9×9 interior lattices against actual evaluated mesh surfaces. Profile splitting corrected a rear cavity incursion and reduced avoidable flared-support inflation from55.1mm.

## Images and reproducibility

Actual imported-GLB standing, seated, rear maintenance and soil/riser detail views use Eevee at64 samples. `qa/render_evidence.json` binds them to exact source/export hashes and camera settings. The source/export are checked unchanged across captures. `qa/revision01_before_terminal_finish/` preserves the prior source/export and render snapshot. Its native seam detail remains valid only for the unchanged seam region; it is not relabelled as a full final-export render.

`dependency_manifest.json` names all inputs needed for a clean generator run, including every shared role loaded by the helpers, even unused output roles. The independent fresh source-only rebuild passed using20 seeds, no unexpected catalogue reads, a byte-identical GLB and equal actual editable/evaluated source signatures; `qa/independent_source_only_rebuild.json` contains the exact r04 receipt. Source/native corner checks explicitly account for3 evaluated polygons that receive dominant-plane projection during export. No existing catalogue sources or materials are changed.

No host room/deck fit, structural load, irrigation, plant species suitability, actor/rig fit, wind, LOD, engine collision, target-PC performance or runtime integration is certified.
