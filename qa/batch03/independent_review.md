# Batch03 independent component review

Independent source, export, geometric-motion and final visual review passes for all seven new staff-only designs. No original ship was restored or altered. Backup upload and final delivery-archive verification remain the packaging owner’s step.

## Verified exported geometry

The final seven GLBs total 22,186 triangles. Independent byte parsing found finite geometry and normals, consistent winding, zero collapsed texture UV area, and no position-welded boundary edges. All embedded texture hashes match the original staff texture PNGs. Per-role static consolidation preserves semantic material identity; the cabinet keeps two leaf-role nodes and two handle-role nodes below its real hinge pivot. Final source and export hashes, dimensions, and triangle totals match their manifests.

All seven editable Blender sources reload at metre scale with named construction parts and retained modifiers. All 211 prior asset/material files remain byte-identical to backup commit 31aeee4c963a2894b490cbd3b80e1d4a41ce84d7.

## Joints, mounting and storage

Wall assets 001–003 have the declared 1.2 m bay, 0.3 m corner legs and 0.09 m terminal. Backing planes and floor Z0 agree with actual exports. Maximum straight-wall projection is 0.12 m. Closed bumper profiles match at both corner legs and the terminal on a 0.5 mm section grid; cove and top-return seam profiles are fully covered. The terminal visibly closes the bumper and formed foot.

Overhead assets 004–006 retain their explicit ceiling Z0 datum. Ten ceiling-anchor points lie on actual exported top faces. Crossbeam/rail contact probes and all 50 cable/conduit base-to-support probes pass. Both mating overhead profiles agree within 0.000000066 m after declared placements; the 2 mm body seam is intentionally spanned by external collars and hollow sleeves. Run minima are −0.442 m; fixture minimum is −0.607499957 m. At a 3.3 m mounting datum the lowest fixture geometry is 2.692500043 m; achieving 2.65 m requires at least a 3.257499957 m datum. These are component measurements, not acceptance of a real route or support load.

Cabinet 007 has a 0.94 m work surface, four grounded supports and four declared storage clear volumes. Independent triangle/AABB and separate collision-box tests find all four interiors empty. The overall left cavity envelope is correctly distinguished from the lower/upper clear volumes divided by its shelf. No whole-cabinet collision hull fills storage.

## Cabinet continuous geometric opening

The proof reads all 3,504 moving and 7,556 static triangles from the corrected final GLB, applies actual node transforms, and verifies that the moving nodes are exactly the hinge descendants. Deliberately intersecting leaf and handle controls detect 4 and 24 triangles, preventing empty-query acceptance.

From 0° to −105°, exact sinusoidal extrema over 420 quarter-degree intervals conservatively bound every moving triangle throughout each interval. All interval AABBs separate from static components except the intended hinge/pin vicinity; rotation-invariant triangle radial distances resolve those remaining pairs. Minimum bore/pin radial clearance is 0.443237 mm and strap/pin clearance is 3.000021 mm. Minimum moving Z is 0.202000007 m. The continuous swept bounds are [−1.055913782, −1.089630211, 0.202000007] to [−0.064369789, −0.284999996, 0.857999980] m. This proves only the component visual sweep; it does not accept a runtime controller, collision response, actor contact, room fit or gameplay.

## Reference and visual judgment

All three actual staff reference images were inspected and their hashes matched. The design direction correctly uses washable pale panels, discrete impact protection, organized exposed services with visible supports, ordinary guarded fixture construction and practical empty storage. It does not copy the photographed narrowness, crew allocation, grime, bright neon or guest timber. The formed edges, cove, replaceable guards, separate metal supports and folded cabinet distinguish useful construction from generic boxes.

All thirteen final labelled family images were pixel-inspected. Corrected cabinet pixels show the actual 105° opening and 65° intermediate pose. The renderer now asserts the pivot matrix before these frames; the invalid earlier closed-looking open evidence remains segregated as history. Overhead exposure −1.3 stops preserves legibility of zinc/paint and restrained cable colours.

The shared bay view is a full component silhouette from camera Z1.65 m with all seven designs. Actual exported placements independently reproduce 20 mm cabinet-back-to-bumper, 295 mm closed-cabinet-front-to-marked-aisle and 130 mm side clearance. All 11 placed component AABBs clear the marked 1.8 m × 2.65 m-high inspection prism; the lowest overhead geometry clears its top by 42.5 mm. This is the closed-cabinet arrangement only; opening the leaf into an eventual route is not accepted by this view. Full-frame camera preflights pass, while intentional construction and ordinary-height crops are separately described.

Final geometry review has no unresolved defect. All active reviewed files are individually below the decimal 8,000,000-byte limit. The exact reviewed-file inventory is `independent_reviewed_files.json`; it excludes interim history, caches, logs and duplicate raw render media, and does not certify an archive or durable upload created later. `independent_reviewed_assets_sha256.json` separately freezes the 26 source/export/material dependency files.
