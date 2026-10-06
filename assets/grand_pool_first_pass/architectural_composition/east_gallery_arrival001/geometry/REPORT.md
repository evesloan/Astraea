# Opposite/east pool architecture: retained geometry and bounded proposal

Read-only/scratch study, 6 October 2026. No Blender, Godot, imports or production writes. All coordinates are Godot world XYZ metres. Proposed free volumes below are not authored geometry or approved runtime work.

## Immediate design result

1. The large pale mass at the right of the installed long view is the local lift enclosure, not an ornamental pier. Pure ray witnesses from the exact recorded camera hit GP_LocalLiftRear at pixel (1280,550), and GP_LocalLiftSide.001 at (1600,600). Both are in runtime node GPM_CELL_-1_-21_5_ASTRAEA_ivory_enamel_concave_static_surface. Do not carve it, treat it as an empty wall, or edit that mixed batch directly.
2. The useful upper bay is behind the dry gallery circuit, against the actual east wall: X−11.2..−8.2, Z−454..−445, Y52.5..57.8. Its full 27 m² footprint is on the retained gallery floor, with no positive-volume source/finish/prop/sign AABB or retained route/view conflicts in the screen. Two asymmetric use/seating pockets can fit inside that one volume. Leave the intervening X−14.4..−11.2 apron clear for approaches.
3. The proposed overlook pockets X−17.6..−14.0 are rejected. They occupy the protected dry loop X−17.8..−14.4. Glass-adjacent seating plus knee/standing room is not spare space.
4. Do not repeat the upper bay at Y46.2: the ramp and low arrival/approach exclusions consume that footprint. An optional separate lower service/rest pocket is X−9.0..−8.2, Z−427.5..−424.0, Y46.2..49.1. Its 2.8 m² footprint is fully floor-backed, but its tight east-stair relationship makes furniture/occupied use provisional; do not claim a new accessible 2.4 m passage there.

## Exact shaft hosts and additive limits

| Retained source identity | Actual retained bounds (rounded to 0.001 m) | Ownership |
|---|---|---|
| GP_LocalLiftRear | X−17.52..−17.36; Y45.96..55.60; Z−414.44..−410.36 | AST-CIR-004, assembled within AST-AQU-016 |
| GP_LocalLiftSide | X−17.52..−13.24; Y45.96..55.60; Z−414.60..−414.44 | Same |
| GP_LocalLiftSide.001 | X−17.52..−13.24; Y45.96..55.60; Z−410.36..−410.20 | Same |
| GP_LocalLiftCap | X−17.52..−13.24; Y55.60..55.74; Z−414.60..−410.20 | Same |

- Lower west landmark/reveal: X−17.90..−17.52, Z−414.32..−410.48, Y46.20..51.00. The external host face is X−17.52, normal (−1,0,0). A recess here is a cavity between new forward framing and the intact wall. Maximum proposed projection is 0.38 m. Any shelf/door/stock operation needs its own occupied-reach check.
- Upper west continuation: X−17.70..−17.52, same Z, Y51.00..55.60. Y51 is a design transition, not an existing obstruction. This thinner continuation can meet the retained cap underside and give the two levels one identity. It is wall-mounted over the existing gallery void: no balcony, shelf or new floor.
- Camera-facing/aft return: X−17.30..−13.55, Z−410.20..−410.00, Y46.20..51.00. Host GP_LocalLiftSide.001 face Z−410.20, normal (0,0,+1). Stop before the gate side. No upper-return claim is made here.
- Both lower faces can carry real supported wayfinding. Keep the existing lower gate-side “Orchard Market” sign at X−13.102..−12.971, Y49.16..49.67, Z−413.1..−411.7 and its view intact. Do not imply the lift opens west; its doors remain east-facing.

The source contact graph connects the rear through side/pit/cap and compiler slabs to retained keel support. Use the existing host; no new deep support system is necessary. Exact direct contacts and root paths are in RETAINED_SUPPORT_PATHS.json. These are retained geometric contacts, not load certification.

## East room and gallery hosts

- GP_EastWall/GP_EastWall.001: X−8.20..−8.00, Y44..52.26, respectively Z−466..−435 and Z−429..−398. The wall is interrupted by the real public portal at Z−435..−429. It is not a continuous pool-edge wall.
- GP_EastWall.002/.003: same X/Z ranges at Y52.50..60.76. Upper bay host is .002; lower optional pocket host is .001. The internal mounting face is X−8.20 with normal (−1,0,0).
- GP_GalleryFasciaBody_2: X−18.24..−17.76, Y51.08..52.26, Z−458..−428. GP_GalleryFasciaLowerReturn_2: X−18.36..−17.64, Y50.95..51.12, same Z. These actual solids may inform a separately fitted canopy/edge profile. The Y52.5 glazing is not an opaque host. Do not continue that band blindly through the local wet-link detour or across doors.
- Retained GP_UpperPier_3: X−13.412..−11.588, Y52.5..60.76, Z−441.64..−439.36. GP_UpperPier_4: X−10.0765..−8.4235, Y52.5..60.76, Z−459.14..−456.86. Keep both visible/unmodified. GP_SculptedPier_5 near the camera is X−13.416..−11.184, Y46.2..52.26, Z−405.768..−404.032; it is distinct from the large shaft.

## Hard preservation boundaries

- Pool clear water: X−40..−22, Z−457..−407, Y46.05; wet deck Y46.20. Preserve shell/pan/coping/drains and footprint.
- Continuous east wet strip: conservatively reserve X−21.05..−18.12, Z−457.7..−406.3, Y46.2..49.2. This 2.93 m strip derives from actual drain/guard extents and is not a new route certification. Shaft proposals stay east of it.
- Dry gallery Y52.50: east loop X−17.8..−14.4; fore belt Z−464.8..−461.4; aft belt Z−402.6..−399.2; local bypass X−10.85..−8.45, Z−427.9..−410.2. Preserve the adopted closed-door cross-link at Z−429.5.
- Upper environmental glass: main east plane X−18.05..−17.95, Z−458..−428, Y52.5..60.76; local-link east plane X−11.15..−11.05, Z−428..−406.9, same Y. Transverse door-side/transom glass is at Z−428 and −406.9, X−18..−11.1. No blind cladding across any of these.
- Stair: gross X−17.5..−11.1, Z−425.5..−415.7, levels46.2/49.35/52.5. Preserve flights, guards, supports, 2.6 m flight clearances and 2 m return. Preserve the exact nonconvex joined upper opening and compiler-owned upper landing X−14..−11.1/Z−425.5..−423.5.
- Whole shaft X−17.52..−13.24/Z−414.6..−410.2/Y45.96..55.74 stays intact. Cabin top at highest stop55.44 has only0.16 m to cap underside55.60. East sills/gates/buttons/approaches are excluded. The source’s fixed sill is X−13.59..−13.50; gate centre X−13.48.
- Upper doors: full 5.16 m cassettes X−17.13..−11.97, Y52.5..55.16, at Z−428±0.13 and −406.9±0.13. Protect full pockets/leaf travel, not just2.4 m openings. Keep threshold signs and their saved view rays.
- D08 dry arrival stays Y44, ramp1:12 stays in X−18..−10.5/Z−464.9..−446.3, with retained landings/guards. Public portals retain Z−435..−429 and clear Y44..47.2 /52.5..55.7.
- Existing floor ownership is unchanged. No slab/void alterations, occupied D10 addition aboveY61, or new intrusion belowY43.76 intoD07.

## Evidence and limits

- INPUT_HASHES.json pins the actual source blend/export/contract, installed GLB/contracts/scripts/import record/cache, retained snapshots/contact/route evidence, and installed image/caption. The source blend/export/contract match AST-AQU-016.manifest.json; installed GLB is byte-identical to source export and source/runtime contracts are equal.
- RETAINED_PART_BOUNDS.json maps all562 source parts to installed GLB triangles;132 installed batches,8,432 triangles, zero unassigned triangles, maximum source vertex delta0.00001511 m.300 triangle records have multiple possible part owners at shared/coincident vertex sets; the two image identity witnesses are unique. This is vertex/triangle-set correspondence, not a fresh full topology/UV or native geometry equivalence proof.
- The retained native installed image/caption supplies the exact supported eye (−20.5,47.85,−405), forward vector and72° field of view. LONG_VIEW_IDENTITY_RAYS.json independently traces actual GLB shell triangles. Other installed assets/transparency are not ray-traced; no new engine render or native-array extraction was run.
- ADDITIVE_RESERVATIONS.json contains numeric boxes and actual screening results. Every listed candidate has zero positive-volume retained source/finish/furnishing/wayfinding box hits and no tested protected-route/view-segment hits. The two floor-backed candidates have exact retained-triangle coverage. This screen bounds source authoring; detailed joints, new-new contacts, load assumptions, knee/stance/door use, controller/cart motion and in-ship appearance remain later checks.
- REJECTED_CANDIDATES.json preserves the two rejected concepts so they cannot reappear as assumed spare space. PROTECTED_RESERVATIONS.json and FLOOR_POLYGONS.json carry machine-readable no-fill routes, voids, glass, gates, signs and exact floor geometry.
