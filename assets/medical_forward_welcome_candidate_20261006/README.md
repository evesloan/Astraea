# D05 forward waiting and support source candidate

6 October 2026. **Uninstalled Blender source work. No finished room, clinical operation, species fit or runtime acceptance is claimed.**

## Current handoff

- Editable complete source assembly: `source/D05_forward_welcome_006.blend`
- New architecture only: `exports/D05_forward_welcome_architecture_006.glb`
- Source/instance/receiver/fixture record: `qa/SOURCE_MANIFEST_006.json`
- Exact receiving/floor proposal with every current old owner/void record retained verbatim: `qa/RECEIVING_FLOOR_PROPOSAL.json`
- Current source-view receipt: `qa/RENDER_RECEIPT_006_waiting_entry.json`
- Empty-volume source check: `qa/LOADED_SOURCE_FIT_006.json`
- Native export check: `qa/NATIVE_EXPORT_006.json`
- Dependencies and preserved input hashes: `qa/DEPENDENCY_MANIFEST.json`

The assembly keeps `D05_directory_01_local_waiting_and_escort_01` and `D05_directory_01_local_diagnostic_support_01`, their 224 m² gross allocation, the six clinical fit targets and the existing operational clean/soiled crossing decision. It does not add a catalogue identity, destination, patient or berth.

The room now has two scalloped seating pockets, a ceiling fitted to their outline, a welcome ledge tied to a swept wall receiver and canopy, a screened connection to diagnostic support, and a rhythm of deep faceted admission portals. The admission connection includes a recessed wayfinding frame and a visible left-turn direction at its end. Diagnostic support has usable stock depth, a work edge and a closed service receiver. Original quiet ivory, sage weave and sand textures complement the retained palette.

## Retained components

Four clinical designs remain intact: AST-MED-001 privacy return, AST-MED-002 wash/supply bay, AST-MED-003 neutral support platform and AST-MED-004 supply trolley. Six AST-LND-002 waiting units and two AST-GST-002 sconces are reused. The twelve instances remain separately identified in the source manifest. Their original files and Catalogue entries were not changed. The support platform is not an adopted bed, and the trolley's visual wheels do not establish dynamics.

The `.blend` contains the editable architectural pieces and retained-source instances. The new GLB intentionally contains only the new architecture and its marker data. Instantiate the retained designs separately using the source manifest; do not import the whole assembly as another unique design count.

## Coordinates and receiving ownership

Source is Blender metres, X right, Y depth, Z up. World mapping is:

`world XYZ = (source X − 28, source Z + 21, −source Y − 446)`

Standard GLB conversion is already Y-up. Place the new architecture GLB at world `(-28,21,-446)` with no extra basis conversion.

The exact proposed new floor union is 350.72 m²: the 224 m² paired allocation, 126 m² admission connection and 0.72 m² missing core threshold. This is unbuilt support, not floor credit. The proposal preserves all original region and void records, plus their canonical hashes and order. Future integration should verify those exact records and identify only the named new union; it must not assume an old global owner count.

The uninstalled core aperture concerns only `CORE_OuterWall_04_-1` and `CORE_WallDado_04_-1` in the retained forward-core derivative. Its clear world bounds are X−7.88…−7.635, Y21…23.4, Z−433.8…−430.2. The missing floor connector is X−8…−7.8 over the same Z extent. The core and all existing floor owners remain untouched. Door leaves, pockets, operational controls, clinical transfer and the D05 staff-lift/service network remain parent-owned later work.

There is **no production floor slab in the source or export**. A QA-only floor and fixture-bound light objects are added in memory for source images, then discarded without saving. They illustrate the proposed receiving relationship. The source stores actual fixture housings/receivers and their proposed light exits, not engine lighting acceptance. General clear roof geometry is at least 4.2 m above D05; the admission lens underside is 4.185 m. Entry aperture reservation stays 2.4 m high.

## Evidence and revision history

- Draft001 remains intact, including its three early source views. The furnishings/palette were coherent, but the enclosure and admission read too much as rectangular corridors.
- The room-scale revision introduced the scalloped plan, fitted ceiling, integrated welcome ledge and deep admission portals. Its reviewed waiting image is `renders/003_waiting_entry_source_only.png`.
- A bounded source check caught an admission pier intruding into the proposed core entry. It was moved outside the opening; the failed003 result remains preserved. The waiting and admission composition did not undergo another broad redesign.
- A native export check found zero-area font and overly wide thin-part bevel triangles in005. The final generator bounds bevel size to member thickness and cleans the raised lettering's editable mesh. Native006 has finite geometry, valid index ranges, textured UV presence and zero zero-area triangles. Prior005 evidence remains preserved.
- The final empty-volume screen tests actual evaluated Blender triangles against three 3.6 m clear planning prisms: admission, waiting and core entry. It is not a capsule, loaded-cart, door-sweep, species or navigation certificate.

The source views use ordinary 1.65 m cameras. They are Blender images, not the Game renderer, CRT, a freehand walkthrough or target-GPU evidence. All local inspection lights correspond to named modeled lenses/sconces. The broad clinical fit targets remain unbuilt targets, not accepted operational capacity.

## Remaining guarded steps

Parent review and independent retention precede any adoption. Structural receiving/load paths, actual floor/compiler integration, full door mechanics, internal clean-service handoffs, staff transport, species/body contacts and the privacy approach still require their own checks. Floor finish/lighting treatment and the diagnostic-support composition remain open to normal in-game review. No Game, Catalogue, core, registry, backup service or credentials were modified by this package.

The parent-requested reviewed003 waiting view was uploaded as **Astraea Medical Waiting - Uninstalled Blender Source Draft.png**, Library ID `libfile_912946ca55fc8191b3ba78d64a10907d`. It remains an explicitly labelled early source draft. Its upload receipt is `qa/LIBRARY_WAITING_DRAFT.json`.

Rebuild only in a coordinated source slot: Blender 4.3.2, `--background --threads 2 --python-exit-code 1 --python source/build_forward_welcome.py -- NEW_RUN`. The generator refuses to overwrite an existing source/export run. `source/make_materials.py NEW_DIRECTORY` reproduces the three original textures without overwriting this package. Keep prior drafts and failure evidence.
