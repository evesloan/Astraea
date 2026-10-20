# R064 Parcel Room: saved assembly workflow

## Open and edit

Open `res://docs/manual_editor_handoff_20261020/ParcelRoom_R064_Authored.tscn` in Godot4.6.3 Compatibility. Select the root and press F. The root is `SHOP_D09_S72_A080`; stable room ID R064 is retained. The scene is section-local; its production placement is `(72,52.5,80)` and belongs to the production room wrapper, not twice in the geometry.

The saved scene contains 298 owned children, including the original 11 shell/fitout mesh nodes, their exact policy-derived contacts, the actual one-region compiled structural slab with two render cells, three complete source-backed door assemblies, six source control pods, and three source light nodes. It contains no player, whole-ship controller or unrelated district. The scene is **not installed** in production.

Use `ManualAdditions` for new construction. Saved mesh nodes are explicit, and their resources are embedded in this authored successor rather than automatically recreated from GLBs at startup. Geometry changes therefore belong to this scene; reimporting the original GLB does not automatically update or overwrite them. Any intentional upstream source update requires a reviewed successor merge. Preserve the original source and its new authoring lineage.

- Floors: `Floor_SourceWorldFrame` compensates for production world-coordinate slab vertices and UVs. Its offset is `(-72,-52.5,-80)`. The actual top is at local Y0. Keep this transform while editing the saved slab; do not apply the offset a second time. The production shared structural floor remains untouched.
- Doors: `PublicDoors`, `WorkBayDoors`, `StockStreetDoors` retain their original physical IDs. Four named moving bodies per door and the source control meshes are saved, not regenerated. A bundled saved-node controller, authored from `saved_retail_slider.gd`, inherits the original interaction/obstruction/movement code but binds these existing bodies in `_ready()`. The converter bundles its source into the saved scene: editing the template `.gd` later does not change the already-saved built-in controller. Deliberately replace/edit that built-in controller if a future reviewed revision needs it. Its inheritance still references the preserved original `scripts/group5_retail_slider.gd`. Do not rename moving-body nodes or change their local motion origin casually: original movement writes their X displacement.
- Lights: three original source specifications are saved, with visibility/shadows disabled, exactly as before source-budget registration. In the editor, temporary preview lighting is fine; do not mistake always-on authoring lights for an adopted runtime budget. Before adoption the existing source manager must register them once.
- Changes to a colliding mesh do not automatically remake its embedded collision. Update its exact collision and the successor manifest together. Do not leave stale contacts, old bounds or occlusion after remodeling.
- `assemble_parcel_room.gd` is an offline one-time converter, not an editor tool or startup script. It refuses to overwrite the authored scene. Do not delete the scene simply to rerun this generator over manual work.

`persistence_probe_test_only.tscn` is evidence only: a copy with one temporary added BoxMesh. It is not the authoring entry and must never be installed alongside it. The check demonstrated save/reopen persistence, identical existing node paths/types, all three IDs, and no duplicated door geometry on reload. This is not a user travel or whole-ship performance test.

## Runtime ownership contract: proposed, not installed

The current live room is constructed by `shopping_promenade_adoption.gd`, then `group5_completion.gd`, then registered by `received_room_residency.gd`; its visuals are loaded/freed by `deferred_home_visual.gd`. No part of that chain was changed here.

Before admitting this authored successor:

1. Pin the original construction contract, shell/fitout/floor GLBs, door/control GLBs, original slider script and compiled floor builder. Retain those original guards and files unchanged. Pin the authored scene, adapter and all local resources separately.
2. Choose one ownership plan. Recommended: keep the original persistent wrapper/door/light identities; replace only its immutable shell/fitout with an authored immutable child scene, and move manually authored door/light changes through explicit persistent-child bindings. The full assembled authoring scene is a preview of both layers, not itself the unloadable visual payload.
3. Export an exact `immutable.tscn` from the saved authority with only SourceGeometry/approved static additions, plus successor bounds/mesh count/contact policy/occlusion/partition receipts. The already-owned floor stays with its original structural owner unless a separate explicit floor successor is admitted. Never duplicate the slab.
4. Bind the three saved door assemblies to their existing exact physical IDs instead of also calling the old door generator. Persistent state must survive residency detach/re-entry. Keep mutable door state out of the freed immutable subtree. Admit authored door geometry by an explicit exact successor gate; do not silently reuse stale source contacts.
5. Select the old or new immutable payload for this one room before bounds/residency snapshots, never both. Register the original source lights once. Preserve all other177 chunk counts/address semantics and the existing15 proven identity joins.
6. Check save/reopen; edited geometry plus updated collision; door sweep/obstruction and existing controls; local floor support; repeated visual unload/reload; retained open/closed door truth; bounds and source-light budget. Then perform an ordinary single-room approach/exit in the installed world. This should be focused receiving, not an exhaustive shipwide test campaign.

The adapter still needs the startup owner's review because new derived private-shell/contact artifacts must follow the exact new authoring hash. If this scene is edited, stale derived data must fail clearly rather than silently replacing the user's edits or weakening predecessor gates.
