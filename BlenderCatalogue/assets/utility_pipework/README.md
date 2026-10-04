# ASTRAEA engineering utility pipework

Three original editable components, authored separately from the missing game. The technical blueprint and both staff corridor reference images were inspected for organized utility purpose and practical finishes. No reference pixels or original game geometry are included.

- AST-ENG-004: 0.800 m face-to-face straight, nominal 0.160 m bore / 0.200 m pipe OD
- AST-ENG-005: 90 degree elbow, 0.450 m centreline radius plus 0.120 m tangent at each end; outlet face centre (0.570, 0.570, 0) m
- AST-ENG-006: 0.650 m face-to-face manual valve, open bore inspection geometry; bolted shaped body, supported bonnet/yoke, exposed stem and named control wheel

Every module uses its inlet bare mating-face centre as source origin. Pipework has no fixed floor feet and can be rolled into horizontal, vertical or overhead routes. The inspection stand geometry exists only in the renderer. All dimensions are artistic modular proposals with no real operating rating.

## Shared interface and coordinates

`../../standards/utility_ports.py` is the common flange helper reused by the machine pair. `add_flange(name, face, outward, materials)` returns mesh objects and a complete source/exchange port record. Call `add_port_marker` once per flange and include the resulting named Empty in the GLB. Markers stay source-axis aligned; their explicit outward normal, not their local Z, defines the port direction.

The common interface has a nominal 0.160 m bore, 0.200 m pipe OD, 0.320 m flange OD, 0.035 m flange thickness and six 0.018 m holes on a 0.260 m bolt circle. Bare front faces coincide; the paired flange bodies occupy opposite sides of the seam. Captive decorative shanks and hex heads remain behind the mating plane. A 48-segment annular profile has a minimum bore polygon diameter of approximately 0.159657 m. This tessellation is shared exactly by all family connections.

Blender source is Z-up. GLB exchange is Y-up with `(x,y,z) → (x,z,−y)`. `port_and_seam_api.json` gives both-frame positions, normals, whole assembly transforms and seam centres. Actual `PORT_INLET`, `PORT_OUTLET` and `VALVE_CONTROL_WHEEL` nodes retain explicit frame metadata. The wheel’s source +Z axis is GLB +Y; there is no unqualified axis string or valve-travel simulation.

## Source, export and evidence

Run Blender in background with `source/build_utility_pipework.py` to rebuild the three `.blend` files and role-consolidated GLBs. Keep the catalogue-relative standards and staff materials dependencies. The source retains named editable components and casework modifiers; GLBs consolidate static material roles while keeping the named wheel hierarchy. All staff textures are packed unchanged.

`qa/validate_glb.py` independently parses actual GLB chunks, accessors and node transforms. It checks finite triangles, normals, UVs and exact shared texture pixels. `qa/check_native_motion.py` tests an exported wheel vertex rotated about its actual node pivot and rejects the deliberately unconverted source-axis control. `qa/check_helper.py` tests axis/diagonal inputs, invalid-vector rejection, closed helper meshes and like-for-like 96/48 segment costs. `qa/check_source_contacts.py` checks the yoke toes against finished cover faces and its tips below the bridge top.

Final renders come only from re-imported GLBs. `qa/camera_preflight.json` verifies full silhouettes before EEVEE_NEXT rendering; targeted details explicitly permit crops. `qa/review_media_manifest.json` names inspected 640×360 standing views and detail/assembly images. No denoiser is used.

The proposed collider is the final triangle shell, preserving the real open bores and separated moving wheel; an enclosing convex hull would close the openings and is unsuitable. Receiving-engine collision tolerances, interaction mapping, actor usability, actual room fit, physical operation and target-PC performance remain pending.
