# D05 clinical architecture components

Two original editable components for Astraea's existing forward triage/medical programme. Script-assisted Blender 4.3.2 source, metres, X width / Y depth / Z up, front −Y. This is a fictional ship component kit. No active clinical system, clinical advice, compatibility chemistry, patient capacity or host-room reconstruction is implied.

- **AST-MED-001** is a 2.74 × 0.80 × 2.36 m freestanding arrival return with a controllable opaque privacy field. Its source retains the separate fixed return, feet, posts, exposed rod, annular sleeves, hangers, screen, grip and raised legends. SCREEN_TRANSLATION has editable linear poses at frame 1 (closed) and frame 117 (open), travelling 1.16 m toward source −X. The open GLB is a state derivative of this design. The screen nests in a separate parallel plane in front of the return; it does not create a door or assume a host opening.
- **AST-MED-002** is a 1.60 × 0.76 × 1.64 m shaped clinical wash/supply bay. A continuous recessed bowl and flat dry landing are supported on actual bearing lands. The right tower and lower shelf have real front-access retrieval volumes. Two actual receiver crossbars support the removable service cover. The cover, stout tap and physically distinct rear water, drain and control caps are static, unimplemented interfaces. No fluid, medicine, powered behavior or sterility claim is included.

The native GLB basis is (source x, source z, −source y), and the floor placement origin is (0,0,0). Both-frame points, physical normals, poses and approach proposals are recorded separately in the per-asset manifests and marker_api.json. Physical sleeve/handle witnesses lie on actual faceted surfaces, not abstract radial vectors. Native node transforms are checked against the source, including the open state.

The care language uses the new shared blue-green resin and neutral brushed metal with existing ivory enamel and dark rubber. Two local original 256 px textures supply muted opaque privacy sage and dark lettering ink. Named semantic roles remain separate. Original shape geometry communicates the bowl, dry storage, privacy pull and service cover; CARE / QUIET / PRIVACY / CLEAN / SERVICE legends are original raised lettering with actual backing contact. These words describe fictional organization and affordance only.

## Rebuild and inspection

From the catalogue root:

1. python assets/clinical_architecture/source/make_clinical_textures.py
2. blender --background --threads 2 --python-exit-code 1 --python assets/clinical_architecture/source/build_clinical_architecture.py
3. blender --background --threads 1 --python-exit-code 1 --python assets/clinical_architecture/qa/check_sources.py
4. python assets/clinical_architecture/qa/validate_glb.py

The fresh source-only rebuild runner and receipt live in qa. It stages authoring scripts, existing shared source maps and the new shared care pixel generator; it does not seed itself with a new .blend, GLB, local texture or QA result. The generated GLBs, pixel textures and interface/collision files reproduce byte-for-byte. The shared material helpers open all eight original maps and all three new care maps, including unused roles, so every loaded dependency is disclosed.

Final captures import the actual GLBs. Ordinary eye-height images and higher detail images are labelled separately, with exact source/export/script/image hashes and camera settings in qa/render_evidence.json. The neutral floor, lights and cameras are inspection aids only. No source file is saved by the render script.

## Bounded evidence and remaining work

Eight finite privacy rays, at two proposed eye heights with modest oblique variations, strike the closed field and clear the open field. Two negative controls clear the top and right edge in both states. privacy_test_field.json gives every source/native eye and target; it is not a claim about a whole room. The sleeve/rod section has a small positive design clearance; no gravity, bearings, locks, damping or load capacity has been solved. The source poses and native state transforms are geometry proposals, not implemented controls.

Motion is checked over 117 source poses and independently through continuous sweep separation and invariant sleeve/rod sections. Actual useful voids, physical support contacts, faceted witness normals and exposed axial/canted material layers are checked before final render. Collision files contain 15 structural compounds for 001 and 37 for 002, with finite profile-overreach sampling rather than a claimed exhaustive bound. The largest observed approximation is about 63 mm at the basin-wall hulls; the section-split cheek proposals are about 31 mm at the broader independent sample, and the privacy pull compound about 30 mm. These are recorded in qa/collision_approximation_receipt.json; they preserve the declared bowl, shelves, approach and open-state field. No collision is installed in the unavailable original game.

The supplied D05 medical panel is programme/material guidance, and its illustrative bed counts are not adopted. Previous public/staff references guide readable approaches and supported service forms; neither supplies a finished room. Actual room polygons, doors, headroom, floor load paths, service feeds, species fit and actor/cart clearances remain unknown. Components add no rooms, beds, patients or population.

Final current visual counts are 2,442 evaluated triangles for 001 and 3,164 for 002. The open screen derivative shares the 001 design count. All 41 wash semantic mesh parts have checked support paths to the two contact shoes; this is geometric adjacency, without a force or fastener calculation. Exact current media execution and dependency bindings are in qa/media_execution_receipt.json and qa/final_execution_bindings.json.
