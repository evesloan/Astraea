# D05 clinical support furnishings

Two original script-assisted editable Blender 4.3.2 designs for the distributed fictional D05 care programme. They add no rooms, beds, patients, treatment behavior or population. This is component production, not the recovered game or a clinical device specification.

| Design | Source XYZ proposed envelope | Source parts / evaluated triangles | Collision proposal |
|---|---|---|---|
| AST-MED-003 neutral modular examination-support platform | 1.18 × 2.20 × 0.75 m | 21 / 1,740 | 13 profile-following convex components |
| AST-MED-004 closed-supply and retrieval clinical trolley | 0.70 × 0.92 × 1.07 m | 48 / 4,688 | 30 profile-following convex components |

These dimensions are adjustable proposals, smaller than the requested maxima. They do not establish fit in an original room, body fit or safe loading. The fixed platform is symmetric along its length and has no anatomical head/foot default. The default source contains no motion, powered lift, tilt or dynamics.

## What physically exists

The platform has a clipped support deck, three equal removable pad modules whose central flat contact surfaces are at source Z0.75, two splayed trestles with four floor shoes, an underdeck tie, and two recessed attachment rails on real bearing lands. The source contains separate pad objects so they can be removed or replaced in later authoring. No attachment is supplied. The rail markers identify real outward mounting faces, not a coupling standard, treatment accessory, Mindo port or validated species interface. Four floor markers and each pad plateau have real boundary/normal witnesses. Broad central and side spaces under the deck remain open.

The trolley has four fixed visual wheel/fork/axle/stem assemblies, a separate lower open retrieval shelf, two closed lift-off supply cases supported by a middle shelf, a raised-rim staging surface, and a swept rear push hoop. The two cases are original integrated parts of this one design, with unspecified contents. There are no medicines, dosage labels, bins for waste, cleaning tools or player-cart implementation. The pull handles have real open midpoint finger spaces. Wheel pivots are bearing-centre datums inside the assembly; they are not exposed contact surfaces. The actual hand contacts lie on deliberately flat grip facets.

## Interfaces and coordinates

Metres, source X width / Y depth / Z up, front −Y, local floor origin. Native GLB mapping is (x,y,z) → (x,z,−y). Both source and exchange records appear in the per-asset manifests, marker_api.json and collision_proposals.json. The actual exported hierarchy is authoritative. Physical pad/rail/floor/grip/staging contacts, physical bearing centres, and nonphysical staff/transfer/inspection approach proposals have separate kinds. Joins distinguish opposing boundary bearings from buried structural/axle overlap and the angled push-support end. No visual component is a proposed approach marker.

Body dimensions, species posture, support load, transfer method, treatment position, aquatic/Baelin dry support, chemistry, hand fit, sterility, floor anchoring and host aisle clearance remain unverified. A Koblin is not assumed to be a child; no human anatomy or synthetic-person hardware has been imposed. The source does not allocate family waiting or relocate the aft waiting programme.

Finite independent profile sampling measured up to 23.5 mm external excess around a grouped trestle/sole and 20 mm around a grouped caster support. Those are sampled measurements, not certified global bounds. The meaningful underdeck, retrieval, staging and grip openings remain excluded from the proposals. The detailed per-shape measurements are retained in qa/collision_approximation_receipt.json.

## Source and materials

source/build_clinical_support.py authors the designs from semantic parts. Bevel/normal modifiers remain editable in the saved .blend files. Export uses evaluated copies consolidated by material role, preserving source editability. Evaluated active UVs are normalized and collapsed bevel UVs are reprojected. Ordinary embedded color PNGs and Principled materials remain portable. Metal texture V follows each major member's longest local axis. Existing shared ivory, rubber and warm stone are unchanged; new shared care pad, resin and neutral metal roles coordinate this batch. No light or camera lives in the production assets.

The actual D05 panel in references/engineering/technical_reference.png was inspected, along with the public amenities sheet and the prior staff services corridor. They guide calm care/staff support, clear circulation and readable joints. Printed old capacities, neighboring deck numbers, and illustrative beds were not adopted. The current Batch12 contract, coordinate/environment/profile standards and Batch11 craft findings govern this work.

The small provisional local contact texture was superseded before review renders by the coordinated shared care roles. Its unused tile and log are retained only as historical evidence under qa/provisional_texture_unused. They are not production dependencies or current materials.

## Reproduction and evidence

Run Blender with `--background --threads 2 --python-exit-code 1 --python source/build_clinical_support.py` from any directory. dependency_manifest.json names and hashes every external file read by the builder, including all loaded unused shared-material roles. qa/rebuild_source_only.py stages only those inputs before the build. No pre-existing new blend, GLB, texture, manifest or QA output is an input. The receipt records its initial file listing, commands, runner/checker hashes, exit statuses and byte-identical GLB comparison. Checker scripts are introduced only after authoring completes. The retained staging tree is evidence, not a third design.

qa/check_sources.py reloads actual editable sources and checks physical markers, real joints, packed maps and sample-ray voids. Those ray checks are limited; independent Batch12 review also tests whole declared boxes against actual source/native triangles and collision hulls. The first review found the trolley's sloped push support entered a corner of a proposed staging-air box; the declaration now ends at Y+0.30 and retains a useful 0.57 × 0.64 m rectangle. Source geometry was retained. qa/validate_glb.py independently parses actual GLB chunks, accessors and node transforms, verifies winding/normals, noncollapsed UVs and embedded texture pixels. Native geometry/marker and exact-box/profile review is under the lead's qa/batch12/independent_* receipts.

qa/render_imported.py uses actual imported GLBs in a neutral ordinary-height Blender inspection stage. Framing failures before images are preserved separately. Production hashes are captured before/after successful views. The floor, lights and cameras are QA aids and do not establish host geometry, Godot appearance or performance. Final pixels must be inspected before acceptance.

No files were uploaded, implemented in the game or promoted to a catalogue by this author. Independent review, parent integration, actual restore verification and durable delivery remain lead gates.
