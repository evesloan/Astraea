# Open Quiet Cocoon Rest Support

AST-RST-QC-001 is one original editable component. It is an open-front concave rest membrane suspended in a shaped ash frame, with a separate segmented teal acoustic hood and warm ivory inner lining. Exposed curved rails, individual tension ties, removable liner seams and grounded reaction struts explain how its parts meet. It is not a completed room or an ordinary mattress/bed with decorative trim.

## Files

- `AST-RST-QC-001.blend`: native Blender 4.3.2 source. Fixture collection contains 96 editable meshes, original simple materials, and named contact/approach datums. The separate studio collection is preview-only.
- `AST-RST-QC-001.glb`: fixture and datums only. No preview floor, camera or lights; no linked images or external assets.
- `build_quiet_cocoon.py`: deterministic mesh/material/export recipe. Run with `blender -b --python build_quiet_cocoon.py`; append `-- --no-render` to omit preview rendering. It reads the complete catalogue manifest and refuses another family's exact catalogue ID. It does not register the asset or change Game.
- `component_metadata.json`: measured bounds, coordinate contract, analytic support surface, contacts, proposed room reservation and approach volumes.
- `validate_component.py`: native closed-mesh checks under Blender, plus independent actual GLB node/triangle checks under Python with the installed NumPy. Run the Blender check first, then the Python check.
- `native_mesh_validation.json`, `validation_report.json`, `deterministic_rebuild_validation.json`: bounded receipts.
- `preview_front_threequarter.png`: inspected 900 × 800 component-only studio view, not an in-engine appearance acceptance image.
- `SHA256.json`: per-file hashes, excluding itself.

## Placement and contact

Metadata and GLB use metres with +X right, +Y up and the open front facing -Z. Floor origin is (0,0,0). This asset deliberately has native Blender front +Y, an explicit exception to the catalogue's normal -Y front. Standard export maps Blender (x,y,z) to GLB (x,z,-y). Do not rotate the GLB again merely to convert its coordinate basis.

Measured export bounds are X[-1.191443,1.191443], Y[0,2.351530], Z[-1.444595,1.511000]. Size is 2.382887 × 2.351530 × 2.955595 m (X/Y/Z), within the requested 2.4 × 2.4 × 3.2 m envelope.

The concave membrane center is Y=0.609688 m. Front transfer lip is Y=0.635 m at Z=-1.24. The support runs Z[-1.24,1.24], approximately 1.72 m across its widest point, with raised side edges and a gently raised back. Named surface datums are RestContact_Center, RestContact_Front, RestContact_Rear and Transfer_Lip. Their actual exported triangle contact errors are below 0.36 mm.

Reserve an additional 1.4 m-wide front floor approach, X[-0.7,0.7], Z[-2.54,-1.50], and preserve the clear internal front prism X[-0.67,0.67], Y[0.045,1.90], Z[-1.50,-1.27]. There is no front crossbar or footboard. The asset is a low-edge transfer rest fixture; the support occupies its interior, so this is not an upright walk-through volume. Room integration still must keep external clearance free of other furniture and choose/test actual collision geometry.

## Validation and limits

- 96 native closed manifold meshes; no degenerate faces; all signed volumes positive.
- 7,664 exported triangles; 125 material primitives; nine original simple asset materials.
- Actual GLB node hierarchy/positions match native reported bounds and contact datums.
- Both stated front approach volumes have zero exported triangle intersections.
- Regeneration produced byte-identical GLB output.
- Front three-quarter pixels were inspected for silhouette, open approach, curved support, seams and material hierarchy.

An initial width assertion caught a 2.423 m outer rib envelope; the authored rib section was narrowed and the final 2.383 m result passes. The first preview attempt hit this Blender build's unavailable denoiser; the successful final preview uses ordinary Cycles sampling without denoising.

No species is assigned. The fixture expresses a quiet-cocoon functional family; no exact biological envelope, pose compatibility, acoustic attenuation, real structural load rating or closed environmental simulation is claimed. No guest occupancy, berth ledger, room placement, Game import, full-game tests, hardware or final art acceptance was performed. No Game files, catalogue registration, backups or publication were changed. Existing sources were preserved.

The chapter 6 and 8 source blocks and current application overlays were consulted. The intimate resort reference was reopened for warm wood/ivory/teal hierarchy only; the fixture silhouette and materials are newly authored. No asset service, download, subscription or engine change was used.
