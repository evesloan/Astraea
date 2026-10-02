# Aquatic towel-use components

Two original editable designs for Batch14. These are component proposals for the existing D08 aquatic programme, not a restored room, ship, engine implementation or new allocation. All prior assets and shared finishes were left untouched.

| Catalogue ID | Component | Source dimensions, X × Y × Z | Evaluated triangles | Native meshes |
|---|---|---|---:|---:|
| AST-AQU-007 | Protected dry towel and supply niche | 1.340 × 0.620 × 1.820 m | 6,900 | 6 |
| AST-AQU-008 | Guarded used-towel return with rolling receiver | 1.004 × 0.746 × 1.220 m, closed | 5,388 | 8 |

The withdrawn AST-AQU-008 export is a state of the same design. Integrated folded towels, lettering, wheel attachments and collision/export derivatives add no designs.

## Use and form

AST-AQU-007 uses an authored, rounded ivory U-section with a warm clay recess. Two useful open shelves protect dry stock behind the hood, while the original stacked-cloth symbol and DRY relief distinguish retrieval without relying on colour. Ten supported textile folds are original integrated stock. Restocking uses the same front loading openings. The opaque back carries a small bounded inspection/service face; it is not an invented room connection or rear loading door.

AST-AQU-008 is lower and has a guarded mouth, shaped downward receiving floor and fixed opaque baffle. RETURN, a downward arrow and a folded-cloth symbol identify the receiving role. A genuinely open-top container has a lowered front rim to clear the fixed chute, higher side/rear walls, a real open handle gap and four floor-contact wheels. Its complete assembly translates source +Y by 0.92 m through the rear service face. The full stroke remains on floor Z0; actual rolling, mechanical loads and handling are unimplemented.

Dry retrieval and used return must stay separate in any host placement. The proposed rear withdrawal reserve is X −0.385..0.385 / Y −0.290..1.305 / Z 0..0.730 m. Rear service staging is X −0.620..0.620 / Y 0.390..1.820 / Z 0..1.000 m. These are component-relative proposals, not actor or route certifications.

## Reference and programme scope

Both actual reference images were inspected: the warm waterpark and the public amenities blueprint. Rounded ivory structure, clay recesses and restrained teal informed the new forms; no pixels or clinical cabinet geometry were copied. The current portable D08 handoff governs the older illustrative blueprint.

D08_bath6 dry changing and D08_service9 towels/care are distinct historical allocations, not adjoining or back-to-back rooms. No fixture route, new changing slot, occupancy, capacity, door aperture, local headroom, plumbing or six-species fit is supplied by these components. The historical Universal room title is not physical compatibility evidence.

## Files and reproducibility

- `source/AST-AQU-007.blend` and `source/AST-AQU-008.blend` preserve 41 and 35 editable named semantic parts, respectively
- `source/build_towel_use.py` rebuilds the family with Blender4.3.2 from the 20 inputs enumerated in `dependency_manifest.json`
- `exports/AST-AQU-007.glb`, `AST-AQU-008.glb` and `AST-AQU-008_withdrawn.glb` are actual evaluated native exports
- Per-asset manifests contain measured bounds, material roles, useful clear volumes, physical contacts, reference/provenance and limits
- Per-asset collision JSON uses purposeful structural profiles instead of enclosing either useful cavity in a whole-object hull

The sources keep semantic objects; export copies consolidate static parts by shared material. Only the actual moving bin has a separate hierarchy. Every physical marker names a real source part. The nonphysical receiving-mouth proposal is labelled separately; approach directions are not asserted as surface normals. Metres and source X/Y/Z are explicit; native GLB maps (X,Y,Z) to (X,Z,−Y). Moving marker records describe the closed source pose, with the parent transform supplying the exported state.

All common/aquatic materials and textures are unchanged, packed in source and embedded in GLB. Metric UVs are normalized and reprojected on evaluated copies. Original relief markings use editable geometry. No external asset, texture or font download was used.

## Checked scope

- Actual evaluated source parts all have measured support paths to floor contacts. Letter backs physically intersect their supporting panels; wheel treads have real flat Z0 faces
- Native transformed triangles, normals, UVs, materials, embedded texture pixels, bounds and source correspondence pass. No degenerate triangles or collapsed UVs remain
- All declared clear boxes are checked as complete volumes, with boundary intersection and solid-containment checks plus positive controls
- Every moving part's complete 0..0.92m swept convex enclosure clears all fixed native triangles, including handle and wheels. The deliberately wrong lateral-position control collides
- A continuous 50mm geometric corridor through the dogleg into the closed bin passes. This is an empty-space witness, not evidence that a real towel deforms, passes through, fits or can be collected
- Finite ordinary eye samples at1.20 and1.65m check rays crossing the guest mouth toward rear service samples in both states. Those rays are blocked; clear mouth and rear-service controls remain open. Rays over the complete housing are outside this bounded mouth-to-service claim, so this is not a privacy wall
- Collision proposals preserve the useful openings, continuous throat and removal sweep. Rounded plinth/floor profiles and shelf stops avoid unnecessary overfill. Small hems, lettering/service details and wheel axle brackets are deliberately noncolliding attachments. Analytic wheel-cylinder proposals overreach the polygon floor contact by0.961mm; this is documented and not an engine adoption
- The final source-only rebuild started in an empty catalogue with only the20 declared input files, no QA, new blends or pre-existing exports. It reproduced all three GLBs and both collision proposal JSONs byte-identically

Evidence lives in `qa/glb_validation.json`, `actual_native_interfaces.json`, `collision_proposal_checks.json`, `source_only_rebuild.json`, source support/contacts reports and the independent Batch14 review. Earlier failed/superseded records remain retained.

## Imported pixel evidence

Five fresh views show the final actual GLBs: three640×360 views at1.65m camera height (dry retrieval, guarded return and withdrawn rear), plus two960×720 detail crops. `qa/render_evidence.json` records exact cameras and captured source/export hashes; `review_media_manifest.json` binds the executed script, raw images and unchanged visual-input verification.

A collision-only generator/proposal amendment happened during capture. No `.blend`, GLB or executed render script changed; the capture receipt covers those unchanged visual inputs. Previous proposal/generator records remain under `qa/revision03_before_collision_refinement` and the first source-only stage. The amended generator then passed a second fresh rebuild against the current records. No recapture is implied by that metadata-only difference.

No engine scene, working water, laundry, hygiene process, real material compatibility, species ergonomics, structural certification, animation physics or target-PC performance is claimed.
