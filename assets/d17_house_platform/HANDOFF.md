# D17 house platform: verified interface stage, full platform held

## Delivered source subset

AST-RES-005 is a new, unadopted partial interface family: two deep open commons frames and two positive seated Royalty hull footings. It contains14 editable mesh parts,168 triangles, four interface markers and six spatial export batches. There are **zero walkable floors**, furnishings, new controls, room registrations or capacity additions in this source.

AST-COM-003 changes exactly four eligible old wall/wainscot meshes: `HC_ProfileWall_D17_-1_2`, `HC_Wainscot_D17_-1_2`, `HC_ProfileWall_D17_1_2`, `HC_Wainscot_D17_1_2`. Each original name remains on its left stub; four right stubs and two upper headers are added. All581 other original objects, including twelve markers, remain exact. Original material node defaults and packed texture hashes remain exact.184 surviving coplanar UV loops were checked against original affine mappings. The unchanged house floor contract is preserved.

Both portals have X78.5..81.5, Y102..104.82 clearance at Z±13.2. Frames occupy X78.22..81.78 and absolute Z12.75..13.65, seated wholly on existing D17 floor. Jambs reach104.82; headers reach105.06 below the retained105.35..106.05 shaped ceiling. Small metal fillets remain outside the clear aperture. There is no door leaf or controller.

The revised two Royalty footing interfaces occupy X107.6..108.4 and Z29..30.2 /49.8..51, moving the proposed column band outside retained crew allocations at X94..106. The former X100/Z50.4 full-height candidate intersected D03 crew-bank drawing420; geometric hull seating alone was insufficient. No crew allocation was moved.

Both new footings seat on actual retained HUL_LowerBand_00 polygon56, with bottomY approximately−0.90435..−0.80000 and flat top−0.45. Minimum positive thickness exceeds0.34999m. All162 source rays hit the same retained source polygon; maximum source plane/ray discrepancy is below1e−6m. Root runtime hull witnesses differ by at most0.000215590m; the new footing meshes have not been imported into Godot. All guest, crew, retail and historical programme allocation envelopes are clear at these two footprints. Full piers and superstructure still remain unbuilt.

Only the two footing objects changed from catalogue5366abf. All16 other interface objects and material/packed-texture fingerprints remain exact. COM003 is unchanged from that partial stage. See qa/footing_revision_preservation.json and qa/footing_allocation_check.json.

## Strict integration hold

**Do not copy the revised COM-003 export into Godot yet.** Its openings would lead toward unbuilt outer floors. Keep the currently accepted runtime export d2ebe0a3a980cb283a4dc8909d07609d112dcbca196d3edbbf7bf47f1fcc9125. The catalogue record retains this as runtime_adopted_export_sha256. The new catalogue design is also unadopted.

All16 floor polygons, thickness0.24, Y102, holes[] and low priority5 are in source/section_contract.json. They are mutually disjoint and disjoint from the retained D17 commons floor. Their2906.4m² is candidate area, not constructed floor. Every region is explicitly HELD. No upper floor polygon is invented: Royalty stair/shaft holes and support still need fitting. The revised standard candidate preserves five fore/four aft units in source-Z order, seven luxury replacements, all null historical stable IDs and16 canonical source indices. No runtime addresses are fabricated; ship total remains1000 units.

## Concrete unresolved members

- Fore court transfer at X84: Z−72 to−14 is58m without an accepted intermediate pier. Candidate X84/Z−48 intersects retained D13 residential street/arrival furniture; X84/Z−24 intersects Night Garden/commons. No long beam or cantilever has been authored
- Aft court transfer at X84: Z14 to61 is47m without an accepted intermediate pier. X84/Z24 intersects Night Garden. No protected owner has moved
- Commons outer aprons: X78.5..81.5, |Z|14 to25.5 need supported disjoint floor, edges/guards and joins to the guest branches before opening runtime portals
- Room floors: standard X63..76 and luxury X94..118 need rooted transverse overhead/edge members and hangers. They must fit the106.5 ordinary external roof, preserve D16 rooms and avoid obstructing entrances. Thin slabs alone are not accepted supports
- Royalty790: X94..118/Z29..51 retains its same-unit upper106.5 and roof≤112. The delivered footings do not solve its piers, transfer, upper floor, internal stair, existing-family private lift/gates, headroom or accessible landing route

Parent's eight-candidate evidence is copied unchanged to qa/parent_added_support_census.json. Survivors: X84/Z−72,+61 have flat keel contact; X100/Z−71.4,−48.6,+71.6 have sloped lower-hull contact. Existing X84/Z±82 and the original Royalty X100/Z29.6,50.4 were provisional candidates at that time; the delivered footings are now atX108. All eight added proposals avoided historical guest-envelope interiors, but only five cleared current actual non-hull contacts. No additional columns were built.

Additional parent evidence is preserved unchanged in qa/parent_support_alternatives_census.json. Clear except intended base: X62/Z−72,+61,+82 (flat keel), X100/Z±24 (sloped hull). Rejected: X62/Z−48 (twin suite/terrace); X62/Z±34 and X84/Z±34 (Night Garden, plus salon at X62/−34); X85.5/Z−48 (residential street/furniture). All avoid historical guest interiors; some rejected positions overlap historical programme envelopes. X62 lies outside the frozen X63..118 source boundary, so its census clearance is not permission to expand the house. No alternative geometry was authored.

## Minimal next bounded work

The later parent census has already rejected X84/Z±34 because they intersect Night Garden. Do not repeat those audits. First study whether the clear X100/Z±24 stations can support one bounded commons-to-wing junction within the existing house boundary and106.5 roof, then resolve transverse room supports with actual source geometry. Do not assume a24m cantilever to the standard edge. Fit one supported guest branch before imposing all16 floors. Near-hull X116 alternatives have not been audited.

Proposed guest envelopes in the contract are3m-wide lanes at X76..79 and91..94, with crosscourt connectors near Z±24. They are **not accepted routes**: the latter coincide with the failed support hypothesis. Private entries, service branch and future riser need actual cart/operator turns. No separate staff network is claimed. Royalty vertical interfaces must reuse established AST-CIR-003 cabin and AST-DOR-003 gate/controller families; none were changed or instantiated here.

## Verification and reproducibility

- qa/interface_verification.json: source preservation, positive-volume/manifold meshes, exact oriented source/export triangle/UV/material equality in raw glTF basis, and marker equality
- qa/seated_contact_verification.json: actual hull polygon contact,81-point grid per footing, unchanged hull hashes
- qa/floor_contract_verification.json: all16 held polygons and four existing-floor jamb seats
- qa/source_join_ledger.json: every authored part has a positive-area/volume rooted contact; this does not prove unbuilt platform supports
- qa/texture_byte_equality.json: exported texture bytes exactly match original catalogue material files

An initial comparison through Blender's glTF importer found389 COM UV differences caused by reverse-V float32 rounding. The final verifier compares raw exported V=float32(1−sourceV), avoiding this extra importer transform; equality passes exactly. No discrepancy was silently rounded away.

Rebuild with Blender4.3.2: source/build_d17_house_interfaces.py and ../starboard_house_upper/source/build_starboard_house_upper.py. Run both Blender QA scripts under qa/; run verify_floor_contract.py with the existing geometry-deps PYTHONPATH. The preservation verifier can recover its baseline into /tmp from catalogue commit3655b833f99048a109e30b3f5f39146afcc5b829, then verifies the baseline hash; it does not require a retained temporary file. Source contract includes original source hashes and complete master/reference review provenance.

No Godot source, tests, runtime export, engine, imports, captures, backup process, credentials, permissions or controller was changed or run. No physical loaded-cart, full16-unit circulation, species, occupancy, engineering-load, pressure, target-hardware or final-art acceptance is claimed. Parent owns integration, independent retention and later runtime tests.

## Allocation correction after the partial handoff

The earlier “survivor” lists referred to current static contacts and guest envelopes only. Later crew-bank comparison rejects full-height columns at X100/Z−71.4,−48.6,+71.6 (D03 drawings414,418,424) and the former Royalty X100/Z50.4 (drawing420). The revised delivered footings are at X108/Z29.6,50.4 and clear all historical guest, crew, retail and programme envelopes. No lower accommodation or address was moved.

Both embedded export textures still match the original catalogue PNG bytes. The footings are parameterized in footing_specs, verified against the actual source hull, and retain the prior sixteen non-footing objects exactly. COM003 remains held and unchanged from the partial stage. Full supported floors, piers, upper circulation and runtime adoption are still outstanding.

## Reproducible allocation regression

Run `python3 assets/d17_house_platform/qa/verify_allocation_footprints.py <Godot project root>` from the catalogue. This checks every configured footing footprint against all1000 guest,200 crew-bank,100 retail and161 programme envelopes and records exact input hashes. Four negative regressions require detection of the previously missed X100 crew-bank conflicts (drawings414,418,420,424). Current two X108 footprints pass. This conservative full-height plan screen is separate from actual mesh contacts, structural design and route acceptance; no new geometry was built in this QA addition.
