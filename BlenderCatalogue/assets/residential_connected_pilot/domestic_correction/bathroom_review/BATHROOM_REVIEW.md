# Residential bathroom enclosure review

Status: source-only correction ready for a fresh prototype build. Game adoption stays held. No Blender or Godot job, import, shared Catalogue/Game edit, commit, or upload was performed.

Update 2026-10-06 22:07 UTC: the parent-applied actual court_domestic_r007 exports now pass the direct exported-geometry, privacy and offline sweep screen for their three named units. See R007_ACTUAL_EXPORT_REVIEW.md and R007_ACTUAL_EXPORT_VERIFICATION.json. The original analytic evidence below remains distinct; no runtime acceptance is implied.

## Result

The retained prototypes contain a real bathroom volume, actual toilet/vanity/shower geometry, and the separate opaque AST-DOR-001 door component in their source assemblies. They are not just doorway markers. However, the enclosure is not yet clean enough to accept: a 40 mm front corner slit and an exposed 30 mm door-head seam must close. The minimal correction adds two fixed pieces to the prototype shell, with no replacement door asset and no new controller.

The actual retained GLB bytes were decoded, including full node transforms and triangles, for all 17 production_r005 shells and the reused door/fixtures. The door export equals CurrentGame AST-DOR-001.glb byte-for-byte. The focused defects exist in all 17 shells. Finite offline tests below pass with the proposed two-piece geometry; they are not Godot operation/visual acceptance.

## Design references reviewed

See REFERENCE_INSPECTION.md for direct full-chapter inspection of master chapters 6, 21 and 32, the current application overlay, actual intimate/premium reference pixels, and three retained source views. It records specific observations and their effect on each decision. This inspection was completed after the initial audit and before any source build or adoption; the proposed fix has been re-reviewed against it.

## Exact geometry, Blender source coordinates in metres

Source axes: +X right, +Y inward, +Z up. Runtime exchange is (x, y, z) -> (x, z, -y). All A/B/C standard/family prototypes inherit the same bathroom region.

- Left enclosure is the existing suite side wall, with inner main face x=-3.44. Floor is the existing suite slab, top z=0.
- Front enclosure is the existing left entry jamb, x=-3.50 to -0.80, y=0.03 to 0.21, z=0 to 2.95.
- Inner forward partition has x=-0.76 to -0.64, y=0.12 to 2.35, z=0 to 2.60.
- Its corner does not reach the front jamb: x=-0.80 to -0.76 is a 40 mm open slit. The common entry header caps this at z=2.55; the slit is not a valid privacy detail. A closed suite entry leaf can conceal it in some views, so test with the suite entry open.
- Inner rear partition runs y=3.45 to 4.00 with the same thickness and height. Return wall y=3.94 to 4.06 closes toward the left wall. The return/inner corner has overlap; the left edge meets the side wall.
- Door rough opening is y=2.35 to 3.45: width 1.10 m, header underside z=2.25.
- Bathroom ceiling is x=-3.44 to -0.70, y=0.16 to 4.00, z=2.60 to 2.74. It meets the side wall and overlaps the front, inner and return walls. No ceiling gap was found. The higher main suite ceiling is not relied on for bathroom enclosure.

## AST-DOR-001 fitting and operating convention

The door placement is source (-0.70, 2.90, 0), yaw +PI/2. DATUM_bath_entry is (-0.65, 2.90, 0), an approach point 50 mm toward the dry side; it is not the correct door origin. Keep those meanings separate. The proposed helper adds DATUM_bath_door at the actual door center without moving any existing datum.

The fixed frame occupies x=-0.775 to -0.625, y=2.31 to 3.49, z=0 to 2.28. Its 1.18 m overall width overlaps the rough opening by 40 mm at each end. Frame top overlaps shell header by 30 mm. Frame's inner width is 1.08 m. The actual opaque leaf's planar solid is 1.026 m wide, 2.125 m high, 50 mm thick; contact dimensions and hinge match the retained manifest. Door hinge source (-0.528, 0.085, 0) maps to suite (-0.785, 2.372, 0).

The closed leaf top is z=2.15 while fixed frame header begins at z=2.18: a 30 mm straight sightline exists above the leaf. Top bevels add triangular sight gaps near the jambs. Existing side stops already mask the main side clearances.

A 25 mm floor undercut is intentional and remains. The leaf is chamfered at the lower corners; this is a practical privacy enclosure, not an airtight/watertight volume or species-fit claim. No sill/threshold is added across the walk path.

The existing guest_privacy_door.gd extends service_door.gd and preserves HINGE_LEFT, MovingPrivacyLeaf, the leaf contact, two handle contacts, shared RMB/E targeting, motion and occupied-swing inhibition. Default runtime state is open. Source assembly currently shows the closed authored pose; an assembly render or shell marker cannot prove operation. For new prototypes, a real separate AST-DOR-001 must be instantiated through the same existing script. Do not bake the leaf into the shell or detail_props.

The offline inflated 0–90 degree sweep covers x=-1.82535 to -0.70550, y=2.29250 to 3.41235, z=0.023 to 2.152. No retained fixture lies inside that sweep. At the fully open handle height, remaining passage is approximately 0.99 m, less than the 1.10 m rough opening. Runtime capsule/cart tests must use the real open leaf and handles.

Existing adapter nuance: its occupied-swing query transforms to source x=[-1.88,-0.62], y=[2.32,3.48], z=[0,2.30]. The fully open protruding handle contact reaches y about 2.2945, 25.5 mm beyond the query at one edge (27.5 mm with the offline inflation). This is not a demonstrated runtime collision failure, but the current broad occupied-swing test does not prove the grazing-handle case. Include that edge in dynamic obstruction tests; do not silently widen or replace the shared controller during this source-only task.

## Fixtures

Actual GLB bounds after marker placement:

- Vanity: x=-3.430 to -2.890, y=2.555 to 3.645, z=0.340 to 2.165. Standing datum (-2.490, 3.100, 0). The wall-hung height is intentional. Mirror/wall trim approach the decorative wainscot very closely, so do not demand zero AABB overlap at wall mount contacts.
- Toilet: x=-3.100 to -2.500, y=0.287 to 1.270, z=0 to 0.908. Standing datum (-2.800, 1.850, 0).
- Shower: x=-2.003 to -0.760, y=0.180 to 1.630, z=0 to 2.120. Standing datum (-1.380, 1.055, 0.020). The tray reaches 30 mm into the front-wall footprint at floor level, making a closed seam, and meets the inner wall at x=-0.76. Do not misclassify these intended tray/wall contacts as furniture spacing failure. The glass screen is not the bathroom's privacy barrier.

No water, flushing, mirror reflection, lid operation, locking, save persistence, or species-specific fixture use is added or claimed.

## Minimal source correction

Files in this directory:

- bathroom_enclosure_patch.py: one additive helper using the existing template primitives. It writes nothing itself and checks required objects and duplicate invocation.
- build_family_bathroom_only.patch: four narrow integration edits against the audited retained generator. Place the helper beside source/build_family.py, import and invoke it after template execution, use the dedicated door datum for the unchanged placement, and record the enclosure contract in the source receipt. This patch has not been applied to the parent/shared generator.

New fixed source solids:

1. SUI_BathEntryCornerClosure: x=[-0.84,-0.70], y=[0.12,0.24], z=[0,2.60], ivory_enamel. It overlaps both existing corner walls, stays behind the sliding entry panels, and extends no farther into the dry path than the existing partition.
2. SUI_BathDoorHeadStop: x=[-0.755,-0.735], y=[2.36,3.44], z=[2.10,2.25], warm_walnut. It joins the existing side-stop language, masks the exposed head gap and top chamfers, and retains 5 mm nominal separation from the opaque closed leaf plane. Its lowest edge is deliberately 2.10, not 2.13: the latter can leave small triangular chamfer leaks.

Original installed rooms 13017/13041, their IDs, AST-SUI-001/002 source/exports, all input templates, AST-DOR-001 source/export, and every Game controller remain unchanged. Apply only to fresh candidate prototypes. Existing build_family already refuses preserve_installed rows.

## Executed offline checks

- Complete GLB transform/triangle decode of 17 shells; retained door matches CurrentGame SHA-256.
- 11 targeted corner/head probes per prototype: 10 unblocked before (one high corner probe is capped by the entry header), zero after the analytic patch.
- 9,735 sampled front/inner/outer/return/ceiling boundary rays on a representative shell: 21 unblocked before, zero after.
- 11,376 dense 5 mm door-head/chamfer probes: 1,220 unblocked before, zero after.
- 8,640 finite dry-room/street eye-to-bath occupied-volume sightlines: 7 unblocked before, zero after.
- 301 distinct angles, 3 controller collision boxes, 2 mm conservative inflation: 903 exact triangle/OBB tests after broad-phase filtering, no intersection with retained shell/frame/fixtures or either added piece.
- Source helper and patched generator text parse successfully as Python. No bpy execution.

These are finite offline screens. The proposed geometry was represented analytically, not re-exported from Blender. The actual next-revision exported triangles must pass again before any adoption decision.

## Required prototype acceptance gate

1. Parent-authorized source slot only: incorporate the two pieces in fresh A/B/C standard and family prototypes (including both family berth signatures). Keep retained originals byte-identical. Export normal shell separately from door/components. Verify hashes and recoverable retention before later adoption.
2. Re-decode final exports. Require the new source solids and dedicated marker; one exact HINGE_LEFT in the separate door export; all 17 corresponding bathroom marker coordinates unchanged except the new marker; fixed asset hashes and fixture placements unchanged. Re-run the finite boundary/head/occupied-sightline suites on actual new triangles with zero unblocked results, keeping the documented 25 mm floor undercut outside the acceptance rays.
3. Re-run the 301-angle/903-contact offline screen against final exported shell and fixture triangles. No nonintentional intersection, at least 3 mm residual nominal head-stop clearance after the 2 mm inflation. Check suite entry sliding leaf motion too: the new corner piece starts y=0.12, well behind the moving entry panels near y=-0.05, but test the actual export.
4. Parent-authorized isolated Godot gate later: instance each distinct corrected prototype through guest_privacy_door.gd, with the existing shared interaction controller. Refresh imports before tests. Validate exactly one AST-DOR-001 and one moving privacy leaf per suite, stable unique bath-door identity, and no duplicated baked/static leaf.
5. Execute at least a close/open/close cycle with >=300 checked physics samples, comparing actual moving contact shapes to fixed architecture/fixtures at every frame. Test exact handle/leaf targeting from both sides, RMB+E operation, unfocused-E rejection, repeated E, mid-motion reverse, CharacterBody/RigidBody occupied-sweep inhibition, and recovery after obstruction clears. Include an actor/rigid body grazing the protruding open handle just outside the adapter query boundary (source y about 2.2945–2.32), not only an actor centered in the sweep. Verify a visible closed pose is also collidable; pass-through markers do not pass.
6. With the suite entry open and bathroom door closed, repeat physics privacy rays at the corner, header, side jambs, return and ceiling. For 8,640 sightlines, shell/opaque door must block them; a toilet, shower glass, or hidden debug wall is not accepted as privacy. With the bathroom door open, the intended doorway must be traversable rather than still blocked by a stale baked collision.
7. Walk the existing player capsule from salon into bathroom to all three standing datums and back. Measure actual doorway clearance at handles, head and foot heights. Test shared cart only if cart access is a required supported profile; report actual fit without claiming all species fit. Confirm head stop is above the usable clear headroom and no threshold trip edge was introduced.
8. Capture ordinary non-cutaway in-engine views: dry-side closed bathroom, dry-side open bathroom, inside showing toilet/vanity/shower and enclosing walls/ceiling, entry-open corner sightline, and high-eye door-head detail. A top cutaway deliberately hiding SUI_BathCeiling is diagnostic only. Do not use it as visible enclosure evidence.
9. Re-run original installed13017/13041 identity/hash preservation and their existing wash/privacy-door regressions unchanged. Then run the applicable complete Game validation suite after any eventual authorized adoption. Focused source checks do not establish whole-Game acceptance.

Relevant retained sources: inputs/build_residential_suite.py lines 70–76 and 128–132; inputs/build_twin_retreat_suite.py has the same bathroom primitives; source/build_family.py lines 178–182; guest_privacy_door/source/build_guest_privacy_door.py lines 38–57 and manifest; Game scripts/guest_privacy_door.gd, service_door.gd, residential_suite.gd lines 53–62; tests/validate_privacy_door.gd and validate_guest_wash.gd. The existing tests explicitly select Suite13017BathDoor / first matching fixtures, so their historical pass cannot certify every future batch unit.
