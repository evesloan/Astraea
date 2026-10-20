# Astraea: practical manual-editor handoff

Prepared 20 October 2026. This is an authoring audit and safe starting workflow, not a claim that the whole ship is an editable assembled Godot scene. No production scene, bootstrap, asset, import setting, or export was changed for this handoff. A bounded one-room conversion and saved-scene/reopen check were performed; no full import or whole-ship engine run was performed by this handoff task. Use the project's existing Godot **4.6.3 Compatibility** configuration; this work does not authorize an engine switch.


## Native-source acquisition update, 20 October 08:22 UTC

The initial presence/recovery audit below is preserved as a dated baseline. Since that audit, all27 targeted native files have been acquired or found already present and verified against the retained SHA256 manifest. Together they total39,374,038bytes. Twenty-five source/family manifests and35 narrowly justified source/material dependencies were also verified; the complete87-file retention set totals40,147,113bytes. No surviving file was overwritten.

Twenty-one native/live-export pairs now have an explicit source manifest matching both hashes. Six native files are hash-verified but their exact binding receipt/new roundtrip remains unconfirmed. Three older botanical-understory dependency hashes differ from later shared versions; those conflicts were recorded, not overwritten. No Blender opening/version-compatibility check or new roundtrip was run, and grouped tram sources and broad suite-native coverage remain incomplete.

Read `NATIVE_ACQUISITION_RECEIPT.json` for the exact evidence and limitations, `NATIVE_ACQUISITION_FILES.json` for the87 verified retained paths, and `NATIVE_DEPENDENCY_PLAN.json` for the historical conflicts. These update earlier statements that these27 files had not yet been acquired; they do not turn the whole ship into a complete editor-authored handoff.

## The important distinction

The ship has substantial retained construction, but most assembly currently occurs in code. `scenes/main.tscn` loads presentation; `scenes/ship.tscn` contains the world skeleton; `scripts/ship.gd::_ready()` and `scripts/received_sections_bootstrap.gd` build the districts, fittings, controls and contacts. Opening `ship.tscn` does **not** expose that full assembled world for ordinary editor manipulation. Looking at the running Remote tree is inspection, not a durable authoring workflow.

There are 177 shopping chunk scenes and 10 Group5 revision scenes in the surveyed `scenes` directories. These are useful editor-visible shell/fitout instances, not fully assembled rooms: floors, doors, lights, gameplay and residency are often added elsewhere. Individual GLBs can be inspected/instanced, but they are imported scene resources, not their native Blender construction history.

## Start construction safely today

**Preferred assembled entry:** open `res://docs/manual_editor_handoff_20261020/ParcelRoom_R064_Authored.tscn` and follow [PARCEL_ROOM_WORKFLOW.md](PARCEL_ROOM_WORKFLOW.md). This now includes the actual floor, all three source door assemblies and three source lights, with298 saved children and preserved identities. Save/reopen and manual-added-mesh persistence passed without regenerating duplicate geometry. It remains a separate, uninstalled successor. The earlier shell-only teaching example below is retained for comparison, not the main handoff.

### Earlier minimal reference example

1. Open `Game/project.godot` with the existing pinned engine. Do not press Run Project merely to edit a section.
2. Open `res://docs/manual_editor_handoff_20261020/parcel_room_editor.tscn`. It instances the existing R064 / Parcel Room shell and fitout at **section-local origin**, alongside a separate saved `manual_additions.tscn`. This is a small reference workspace, not a replacement for production.
3. Open `manual_additions.tscn` directly to add ordinary named Node3D/MeshInstance3D/Marker3D children. Save and reopen it. Your additions are normal saved scene data, not generated in `_ready()`. Use descriptive stable names. Nothing in this example runs code or generates contacts.
4. The reference shell's actual production placement is `(72, 52.5, 80)` metres. Do not bake that placement into local children and also apply it to the room wrapper. Keep scale one. Astraea uses X port/starboard, bow toward -Z, and its existing floor-origin deck datums.
5. Keep the imported reference intact. To remodel its mesh, locate the corresponding native Blender source and create a named successor export. To customize an imported scene in Godot, create a separate inherited scene or instance overrides; do not edit `.godot/imported` or overwrite the original source. Imported subresources require separate local/external resources for edits. Ordinary added nodes belong in the user-owned scene.
6. This example has **no structural floor, collision, lighting rig, player, production hook or gameplay controllers**. It demonstrates saved authoring and references only. Do not treat its appearance or F6 run as a room acceptance test, and do not insert it alongside the existing production room because that would duplicate geometry.
7. Before installing a meaningful changed room, use the migration contract below. A small local editor preview and affected collision/door/streaming checks are sufficient for the next construction increment; do not make whole-ship exhaustive testing a precondition for every edit.

## What can erase or reject an edit

- Runtime-only child/property changes are not saved back to scene files. `ship.model()` uses `add_child()` without scene ownership and is not an editor authoring tool. Packing a running tree casually can omit unowned nodes, duplicate global systems, freeze transient state and lose source-instance relationships.
- `deferred_home_visual.gd::release()` frees `ResidentAuthoredInterior`; `ensure()` recreates it from the configured PackedScene/path. Unsaved edits inside that live subtree disappear. The room root and doors can be retained independently.
- `shopping_promenade_adoption.gd` verifies layer hashes and sets visual mesh count, bounds and collision policy. Adding a mesh to the production deferred scene without a successor contract can fail count/policy assertions or leave old bounds/occlusion.
- `received_sections.gd` verifies model hashes from `received_sections.json`. Secondary engineering also verifies exact part names, triangle/material expectations and contacts. Other receiving guards preserve predecessor script/source hashes. A direct replacement is not a supported bypass.
- Generated scene/data outputs and imported-resource caches are not a safe location for handwritten changes. A builder/reimport can replace them. Save manual work in a separately owned authored scene with a manifest; generators must not target that location.
- Startup optimization candidates are **derived artifacts**, not authoring authority. Their exact contact/shell partition receipts belong to their recorded source. Never feed edited geometry through stale precomputed contacts or remove a guard to make it load.

## Migration to genuinely assembled editor authoring

The needed next deliverable is a **section-by-section authoring scene with a single runtime adapter**, not one giant frozen ship bake.

For each section, record its exact existing receiver, source contracts, programme/persistent IDs, placement transform, protected allocations and shared interfaces. Preserve original files as immutable predecessors. Create a new authoring directory containing:

- `section.tscn`: saved complete local assembly with original source instances, explicitly authored additions, static floor/ceiling/trim, source-driven light nodes, interaction anchors and collision ownership. Keep dynamic door/lift/player state out of the immutable geometry layer.
- Separate reusable scenes/resources for new manually edited parts. The editor scene is the authority for these; a build script must not regenerate over it.
- `source_binding.json`: predecessor source hashes, successor scene/resource hashes, retained semantic names, original IDs and transform, and explicit ownership of every changed part. No synthetic extra room/berth IDs.
- A derived manifest for mesh count, local bounds, collision policy, occluders and startup partitions generated **from that exact successor**. Store contact provenance and preserve all original guards. New authority is admitted by a separate exact successor gate, not by updating old evidence to pretend the predecessor never changed.
- A narrow adapter that selects either the existing builder or the admitted authored section, never both. Register the same stable room wrapper with residency before bounds/occlusion snapshots; preserve original persistent controllers and state. User-authored immutable details must reload from the saved successor scene. Persistent switches/doors belong outside the freed visual subtree or need explicit state restore keyed by their existing IDs.

Begin with a single small shop/room, prove save/reopen, one source reimport, unload/reload, the affected doorway and floor support, then use the same contract for adjacent sections. Only then expand to atrium/engineering/large districts. A manual edit should cause a clear stale-derived-manifest diagnostic until its exact successor artifacts are rebuilt; it must not silently load old geometry or bypass original hashes.

The current example intentionally does **not** install this adapter: there is ongoing startup ownership work, and arbitrary replacement of the shared bootstrap would break integration boundaries. The above is the concrete integration work still required for the broad handoff.

## Where the user's named work lives

These are exact source entry points, not claims of editor-ready or accepted operation:

| Work | Current construction hook / authority | Editor status and remaining limitation |
|---|---|---|
| Atrium and public cores | `scripts/ship.gd` calls `atrium_lighting.gd`, `atrium_garden.gd`, `primary_atrium_core.gd` with its core contracts, and `atrium_gallery_receiving.gd`; source models include `AST-ATR-001.glb` and its botanical successor | Runtime assembly. No complete standalone authored atrium scene established in this audit. Preserve multi-deck datums, botanical guard and core source contracts when migrating. |
| Visible fusion cores and arrivals | `scripts/arrivals_fusion.gd`, called by `ship.gd`; `AST-ARR-002.glb` at `(-31,0,-432)`, `AST-ENG-007.glb` instances mounted at authored gallery markers | Source exhibits are included by the builder. This is not operating reactor acceptance. Room lighting, contacts and exhibit transforms cannot be recovered simply by dropping one GLB at zero. |
| Reworked tram | `scripts/group4_integrated_receiving.gd::before_budget/after_budget`, the seven `GROUP4_*` candidate contracts, exact-pit successor guard and the source024 body | Installed construction/source controls have explicit operational holds: original-cart impulse and protected D09 transit criteria remain unresolved. No standalone complete tram authoring scene established here; preserve owned vehicle/controller identities. |
| Hundreds of suites/homes | `night_garden_rooms.gd`, `star_atlas_rooms.gd`, Tidal/Quiet/Family/Sunset room builders, specialty builders, `received_homes_20261015`, and their exact per-room contracts | Large existing source-backed inventory, much deferred. A registered allocation is not a fully fitted home. Current D15 and Royalty candidates are newer work, not part of the old Windows package. Use the master gap assessment and each current successor receipt, not file counts. |
| Secondary engineering and switches | `secondary_engineering_section.gd` -> `secondary_engineering_essentials.gd` / `secondary_engineering_cell.gd`; `SECONDARY_ENGINEERING_RUNTIME.json`, `SECONDARY_ENGINEERING_CELL_RUNTIME.json` and model pins | Existing named source parts are protected, including explicit material/contact checks. This audit does not establish a count of functional switches or claim all controls operate. Native mesh fixtures, interaction wiring and persistent system behavior must be distinguished. |

`RECEIVER_EDITOR_INDEX.csv` inventories **all 226** previously mapped direct receiver calls, their current exact line locations, contracts and named roots. All 226 expressions were found in current source. It is static call evidence; it does not prove execution of every branch, resolve dynamic asset paths, or declare all historical work integrated. The associated full 18-deck master assessment is retained alongside this guide, explicitly as a dated baseline.

## Complete-source accounting, not just the executable

Three different deliverables must not be conflated:

1. **Packaged Windows build:** the existing `BUILD_INFO.json` identifies runtime checkpoint `5acf0c2a` and packaging revision `470dbde`. It states Windows launch, main startup and visual acceptance were not accepted. A PCK is a runtime delivery, not a complete editable-source archive. Later D15/Royalty/startup work is not automatically included in that older package.
2. **Current staging source:** includes later additive work and the project scripts/data/models. This survey found 66 native `.blend` files in the staging BlenderCatalogue and 11 under Game/source_derivatives. Presence is not proof each is the newest corresponding source or readable by the installed Blender. The known cascade newer-format source cannot be represented as editable in Blender4.3.2 just because its bytes are retained.
3. **Retained source/history:** the supplied acquisition manifest is much broader than staging. Presence comparison found 31,207 recorded Game paths present and 4,292 absent; 11 recorded BlenderCatalogue paths present and 21,835 absent. New staged paths can exist outside that older manifest. These are inventory-path counts, **not completion or loss percentages**. Most of a historical catalogue being absent from a selective runtime staging tree means a comprehensive native-source handoff still needs a separate source bundle and mapping.

`RETAINED_NOT_IN_STAGING.csv` records every absent manifest path and retained SHA256 for targeted source recovery. It is a recovery index, not a claim those paths were in the Windows build or that all are needed at runtime. `COVERAGE_SUMMARY.json` states the comparison scope. No blanket file-hash revalidation, remote archive extraction or new source recovery occurred in this handoff.

For each section finally delivered, require one row joining **retained native source -> current export -> runtime hook -> assembled editor scene -> explicit omitted/held scope**. If native source is not acquired, mark it missing from the handoff, do not substitute a GLB and call it native. Historical variants and QA failures should be retained separately, not blindly installed as extra rooms.

## Official Godot guidance

- [Godot 4.6 import configuration and inherited scenes](https://docs.godotengine.org/en/4.6/tutorials/assets_pipeline/importing_3d_scenes/import_configuration.html): keep custom scene work separate from source imports; inherited scenes add nodes/overrides but do not allow deleting base nodes or directly editing inherited subresources.
- [Godot 4.6 Node ownership](https://docs.godotengine.org/en/4.6/classes/class_node.html#class-node-property-owner): scene ownership controls which children are stored when packing. This is why a runtime hierarchy is not automatically a saved editable scene.

These sources were consulted for this handoff. Project-specific constraints above come from the actual local sources and retained integration evidence, not from assumptions about generic Godot projects.

## Smallest complete handoff bundle and acquisition order

Deliver a source bundle separately from the Windows executable:

1. Current Game source and required runtime assets, preserving the exact working project/import settings. Include every final worker delta and its receipt; do not claim the existing older PCK contains these changes. Keep uninstalled startup/D15/Royalty candidates visibly labelled as such until their actual receiving hooks are admitted.
2. The **current native sources** for the exports in that Game bundle, with materials/textures, source builders and per-export source binding. Recover missing native assets into new staging locations from verified retained GitHub blobs; compare the recorded SHA256 before admitting them. Do not overwrite surviving native files. Source size is a storage-planning concern, not a permission denial.
3. The new authored section scenes and ownership contracts as they are migrated, including the current prototype, plus a per-section assembly/editor index. A directory of GLBs alone is not this layer.
4. A compact historical provenance index and retained commit links for predecessor variants, rejected QA and alternatives. Do not bulk-copy all historical variants or install them as new content. The original retained data remains preserved.

Absent-path triage is deliberately conservative. `ABSENT_CATEGORY_TOTALS.json` gives **known-byte lower bounds**, because cached tree metadata is incomplete:

- Native-source candidates requiring current-export joins: 1,242 paths; 2,393,741,831 known bytes; 230 sizes unknown.
- Evidence/reference/alternative paths: 11,382; 1,182,424,996 known bytes; 327 unknown.
- Export/asset candidates to deduplicate: 2,775; 1,968,925,139 known bytes; 428 unknown.
- Source scripts/manifests/other review: 10,658; 1,653,574,499 known bytes; 1,375 unknown.
- Existing safety-excluded paths: 70; 33,604,391 known bytes. These are explicitly marked **do not acquire**. They are not a required handoff backlog.

Path categories do not establish that an asset is current or superseded. Do not use these totals as an archive size estimate or download queue. `NATIVE_SOURCE_RECOVERY_CANDIDATES.csv` is the narrower exact-path/hash inventory for targeted joins. Acquire the native source of the next section being edited first, along with its dependencies. The supported route is the authenticated GitHub connector's file/blob retrieval at the retained source revision, followed by exact SHA256 verification. That initial audit did not perform acquisition; subsequent verified recovery is recorded below.

Historical pre-acquisition examples (these four have since been recovered; see the r002 coverage update below):

| Retained native source | SHA256 | Known bytes |
|---|---|---:|
| `BlenderCatalogue/assets/atrium_guard_network/source/AST-ATR-001.blend` | `ec5b30be2a4e991255ed088bfb2dbbf7c3683952858002cff545ec6307ddcecc` | 31,452,800 |
| `BlenderCatalogue/assets/arrivals_fusion/source/AST-ARR-002.blend` | `c32d578aab696e3c2faffac2f8a575f327d9ab67e584ab2697e9a1cea5bf43d1` | 3,767,404 |
| `BlenderCatalogue/assets/fusion_exhibit/source/AST-ENG-007.blend` | `adce75fee1e6e8d6e5c2de6d304e3334c47ee7a642360cac93107796e5b4390a` | 1,269,152 |
| `BlenderCatalogue/assets/secondary_engineering_access_interfaces/source/AST-ENG-008_receiving_shoulders.blend` | `d6dc26696f22ca30568ae6dad3ab97a249d97c81fced9dccafbd3a8ec30ad4da` | 1,736,332 |

These names match active model uses, but the exact native-to-current-export roundtrip/manifest still needs confirmation before remodeling. In particular, original atrium source is only one ancestor of the later botanical adjustments; preserve and acquire the applicable successor too. The tram's several source families and engineering workbay variants require their specific live contracts, not selection by filename similarity.

## New construction entry: Royalty790 upper candidate

A more substantial assembled editing example is now available from the current construction work:

- Open `res://royalty_790_completion_20261020/Royalty790_UpperCandidate.tscn`.
- Select `UpperGallery/RG_UpperGalleryFloor` and press **F** to frame it.
- Its 426 explicit named meshes are grouped under RetainedArchitecture, UpperGallery, FittedStair, PitlessReceiver, Fixtures and SupportingFrame. This is saved editor scene content, not a hidden `_ready()` builder.
- Native counterpart: `royalty_790_completion_20261020/source/ROYALTY790_upper_candidate_r002.blend`. Keep the scene at identity/zero-origin and follow the adjacent README for the compiler-owned lower slab exclusion.
- It is a **bounded successor** to AST-RES-006, not an extra suite. Do not instance it over the existing suite, or instance both its editor reference cabin and runtime package.

The construction owner reports saved-scene/reload checks passed, with dummy-renderer resource-cleanup warnings on exit. This handoff audit verified the entry and native files exist, but did not independently rerun the engine. The runtime package remains held pending the documented neighbor/admission/operation checks; it is not installed by this handoff and is not evidence the entire ship is editor-ready. This is newly authored upper construction, not a recovered historical completed upper.


## Current native-export joins

`NAMED_EXEMPLAR_EXPORT_JOINS.csv` records52 current-file hashes across atrium, arrivals/fusion, engineering and tram contract references. Matching retained exports are byte-identical by SHA256. `TARGETED_NATIVE_ACQUISITION.json` proposes27 exact retained native paths/hashes for the straightforward family/stem joins. This was the initial planning state. The r002 update below supersedes acquisition/binding status; native roundtrip validation remains unperformed. These indexes are targeted preparation, not proof every historical contribution is already editable.

The assembled Parcel Room now has a pixel-reviewed graphical preview, `PARCEL_ROOM_SAVED_SCENE_PREVIEW.png`, and exact predecessor lineage in `ASSEMBLED_SOURCE_LINEAGE.json`. See `VISUAL_REVIEW.md` for preview-only lighting and environment warnings. Production runtime adoption remains proposed, not done.


## Verified current-source recovery, r002

`CURRENT_NATIVE_HANDOFF_LEDGER_R002.json` and `R002_SOURCE_COVERAGE.md` record 209 exact verified files (367,064,423 bytes), including 93 native Blender files (358,365,959 bytes): 92 selected current natives and one historical precursor dependency. All 27 initially targeted native/export bindings are now supported by explicit receipts. The six current house families contribute 48 native prototypes spanning 498 allocation rows, plus their two door source families. Allocation rows are not a claim of 498 completed or accepted suites. Grouped tram recovery includes its current geometry, boarding, travel, controls and station-information sources and the selected direct generator dependencies.

Recovered Blender sources are editable source assets, not saved assembled Godot scenes. Generator portability, external resource completeness and fresh native/export roundtrips remain untested. Historical botanical dependency conflicts are preserved rather than overwritten. See the ledger for exact scope and open limitations. A further 58 received-section native counterparts were absent from the baseline manifest; recovery from their exact retained source archives is underway separately, not counted as complete in r002.

### Current tram arrival component

`res://scenes/tram_arrival_intro_20261020/OpeningTramDirector.tscn` is a separate editable component with cursor, speed, standing, dwell and itinerary settings. It is disabled and not installed by this handoff. Read `docs/tram_arrival_intro_20261020/IMPLEMENTATION.md` and its contract before integration. It is intended for the real ship, not a duplicate standalone route; actual-main admission and guideway clearance work remain separate.


### Separately recovered, not integrated

The recovery inventory also contains the distinct Sequoia Atrium package (native Blender and GLB, a 96-suite static layout) and Luxury Suites + Painterly Garden v03 (64 asset families, 128 LOD GLBs and source payload, no native Blender file claimed). These are isolated alternatives, not proof that another 96 suites or these assets are installed in Astraea. Do not copy their project/controller files into the live game or run their installer. Canonical placement, room identity mapping, duplication review and integration are still required. Their provenance and hash receipts are maintained in the separate recovery inventory.
