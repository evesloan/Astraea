# Tidal refinement and exact Group1 adoption — r008

The r005 picture was improved construction but failed the requested room-quality bar. R008 preserves that revision and corrects the same room: the northern bath and its existing central recovery/entry bay. It adds no new aquatic programme, capacity, occupied-water system or room family elsewhere. The selected source is `BlenderCatalogue/assets/group6_completion_20261011/tidal_room/TidalNorthRoom_r008.blend`; selected runtime is `Game/assets/models/Group6TidalNorthRoom_r008.glb`.

## Actual changes and evidence

The broad rear black strip is resolved by a real internal arched threshold joined to the retained vault and a roofed central entry foyer. Its southern boundary is a framed receiving view into the unrefined southern basin, not a substituted exterior backdrop. Curved ribs and fitted shoes make the ceiling junctions visible. The added floor piers are replaced by overhead hangers contacting the actual retained sloping vault members. Original vaults, walls and hull remain untouched.

The old central pavilion is replaced by a wall-connected upholstered alcove in its original bench footprint; the two recovery bays share a continuous cove. No extra decorative props are added. Slim satin-metal ramp grips and visibly glazed gallery guards preserve actual contact and the turning opening while revealing the seating. Transparent guard meshes transmit light and do not cast opaque shadows; their faithful source colliders remain. Every opaque member keeps its shadow/contact rules.

The source exporter now selects the authored UV layer for every new mesh. Cube primitives had kept their default UVs ahead of the authored layer, stretching material patterns into bands. Meter-aligned paving, finer basin mosaic, sage ceramic recesses, ivory masonry and timber now have deliberate scale. Water normals are weaker and combine oblique ripples; lower reflection intensity, angle-dependent transparency and visible basin lining provide quieter surface/depth cues. Original water boundary/height and ground contact are unchanged; this is visual water, not swimming/fluid operation.

Fixture output is reduced rather than changing exposure/ambient/budget. Two uplight lenses and their receivers move off the opaque pendant stems. Fresh saved-native origin tests reject a source inside any closed opaque authored housing/stem. Eight local sources remain; original ambient0.2, GL Compatibility, shared eight-shadow/32-candidate selector and original controller remain.

`NATIVE_PROOF008.json` passes preservation of all424 context meshes/nine packed resources, authored UV selection, real vault-hanger/cove/guard contacts, threshold/roof joins, parked-transfer clearance, all eight emitter origins outside opaque geometry, ceiling bound and byte-identical fresh export. `TIDAL_NORTH_ROOM_LOCAL010.json` passes22 original-player route/entry/recovery legs with3,149 continuous samples, maximum frame displacement0.05788m and minimumY43.99936; no traversal position/velocity writes. `THERMAL_ADOPTION_LOCAL002.json` passes the actual retained Group1 registration, occlusion and residency APIs in the isolated two-room/four-floor context: four predecessor lights preserved,34 new sources registered exactly once, inactive successor bindings off, eight active shadows at most, and automatic local reflection after source admission. This is not a combined-ship build or hardware result.

Both ordinary-height views in `tidal_north_room009` were inspected at default640×360 and clear1920×1080. The wide camera is exactly the r005 camera; circulation/geometry and lighting were changed instead of choosing a flattering view. The dry view shows the former pavilion as recovery seating beneath the joined cove. The southern unfinished context remains visible through its truthful framed interface. Software-renderer shadow/material balance still requires combined-scene review; no final visual-quality acceptance is claimed. Library picture identity/version and exact bytes are recorded in TIDAL_R008_LIBRARY.json.

## Current retained Group1 state and one-line hook

Read-only source review covers `construction/group1-tidal-d15-20261010` at47eb8359caa5531e04122b6e56292f8c44d4281a, refreshed to a036eb484537f721e943dcd7d49f644728ef0cce. The newer ship root adds synthesis-plant calls; the relevant thermal bootstrap, registry, entry/support dependencies, source-room exports, compiler floors, light budget and residency are unchanged. GROUP1_RETENTION_READBACK.json contains exact blob/hash comparisons. Unpublished Group1 WIP is not inferred.

That retained root already installs the annex successor, thermal entriesr003 and supportsr004. Its deferred `received_sections_bootstrap.gd` registers support lights after the existing ship budget is configured. Recovery and the new room are retained source, with no installation calls there. Therefore **do not add another entry/support loop or move the old root/configuration back into place**.

Copy only the exact runtime files in GROUP1_THERMAL_RUNTIME_FILES.json. It excludes shared roots, controllers, registries, prior rejected room exports and historical evidence. Retain the selected editable native and source/proof separately from the runtime installation. Apply GROUP1_TIDAL_ADOPTION.patch to the current bootstrap; its one added line follows the existing support registration loop and precedes static occlusion/residency:

```gdscript
load("res://scripts/group6_completion/thermal_integration.gd").finish(ship)
```

The patch was checked against the exact retained bootstrap without editing Group1's workspace. The source-owned helper:

1. Requires the existing entry/support roots; never rebuilds or registers their four sources again.
2. Installs recoveryr004 for both actual thermal rooms, then R008 only in D08_directory_02. Recovery preflights its exact support/export pins; the new room preflights the recovery pin and affected original bounds.
3. Uses the current registry for only newly created roots. Existing bindings are enabled because that inspected root has no old-lens thermal binding call. If newer unpublished work adds such bindings, reconcile before applying; do not register duplicates.
4. Disables replaced Tidal bay1/bay2 tasks and original bath_light3/bath_light4 bindings. These are the northern and central fittings; bath_light2 stays unchanged. Hidden predecessor visuals retain their original nodes/transforms/IDs but have no old StaticContact. The existing occlusion installer skips hidden meshes and shader glass, so this call must precede occlusion/residency setup.
5. Arms one source-owned, bounded reflection callback. It remains inert outside the local room/altitude and until the shared registry contains all eight room sources and admits at least one. It then enables one interior reflection capture after the unchanged budget and stops processing. No new player hook is needed.

Refresh changed imports once, then restart the combined scene. Do not hot-swap or stack revisions on a live Group6ThermalRecovery/Group6TidalNorthRoom, re-register cached sources, reuse stale occluders/residency witnesses or copy this branch's old ship root. The cached reflection/room nodes remain with normal residency; changing selected source/materials requires a fresh scene. Group1 remains sole combined writer/build owner.

## Concrete receiving choice and remaining holds

Recommended construction choice: accept the exact local roof/cove/frame interfaces within D08_directory_02, then use the default `finish(ship)`. New footprint is X27.65..50.7/Z-437..-403.95; new roof stays below51.55, with retained D09 underside52.26. Recovery cove underside48.35; arched wet thresholds clear below47.4..47.95; southern dry cove exit head starts47.15. Gallery/return surfaces and X45 dry route retain their tested source alignment. Hangers meet original vault members; source proof rejects intersections with retained parked transfer stations. Current Group1 source-room/floor pins match, but its sole combined build must still check any newer neighbouring work and actual room optical selection.

If a current combined receiving conflict prevents that acceptance, call `finish(ship,false)` to install only Mineral recovery and leave Tidal entries/support as they are. This deliberately leaves the northern correction uninstalled; it does not expose the known rejected Tidal recovery canopy as a fallback. Resolve the named roof/contact conflict before enabling R008, rather than cutting original/shared geometry or silently changing datums.

Steel sizing/load capacity, consolidated enclosure/pressure continuity, broad species/chair/assistance, recovery occupation, thermal/gravity, swimming, avatar buoyancy, AFK mount/dismount/pause/save, slide/occupied-hoist operation and target hardware remain held. Existing annex/service/50m/cascade interfaces keep their recorded scope; no new occupied-water features were introduced. Group6 is not accepted as a whole, and this room family is not propagated elsewhere.

Failed attempts remain immutable: r005 rejected view; r006 authored-UV/lighting visual hold; r007 uplight-origin containment hold; initial adoption-harness type-inference parse error. Their technical passes are not final visual acceptance. R008 and the corrected adoption harness have clean engine/script logs; ordinary V-Sync/software-renderer limitations remain recorded.
