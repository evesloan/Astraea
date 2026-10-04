# Crew personal fittings — two original designs

AST-CRW-003 is a modest open personal storage unit, 0.640 m wide × 0.531 m deep including its pull × 1.380 m high. Two open lined shelves remain useful, with complete front retrieval volumes declared. The lower drawer is genuinely hollow; its 0.500 × 0.368 × 0.206 m tested internal volume remains empty. A continuous 0.240 m withdrawal includes the front, inner base and walls, both runners, return pieces, pull and physical markers. The visible runners retain 0.155 m of supported overlapping bearing at full extension. This is authored geometric movement, not a functioning slide mechanism, control, item store, ownership system or load approval. Four individual soles reach the actual Z=0 plane. Its compact personal scale, open shelves and protected construction distinguish it from the earlier enclosed equipment cabinet.

AST-CRW-004 is a 0.340 × 0.260 × 0.360 m reading-light/shelf module relative to its rear mounting datum. Its shaped shield, returned arm, recessed opal diffuser, broad backplate and two side suspension brackets are physically supported. The small lined resting surface stays clear between the side brackets. All materials are unchanged staff roles, including the non-emitting opal material. The named emitter position, physical control face and suggested aim are interfaces only: no exported light, emission-based room illumination, live electrical control or photometric/glare claim.

The module rear Y=0 plane mounts at frame translation (−0.26, 2.14, 0.88) m with no rotation. Its four rear contact witnesses have +Y normals opposing the real AST-CRW-001 headboard −Y front. The backplate spans X±0.17 and Z−0.16..+0.18 relative to that datum. Four contact witnesses at (±0.11,0,±0.12) are physical surface witnesses, not fastener-hole centres. The lower visible washers are intentionally higher than the lower witnesses to terminate clear of the shelf. See `mount_contract.json` for source and native frames. No external host wall was invented.

Actual evaluated receiver geometry establishes 78 mm between shelf underside and pillow crown; the complete module stays 360 mm beyond the declared central rest-use prism along Y. That prism is preserved at X±0.40, Y0.30..1.52, Z0.565..1.10 in frame source coordinates. These are bounded component clearances, not approval of a sleeper's head motion, any of six species, load capacity or a real D03 room.

## Editable source and native states

- `source/AST-CRW-003.blend`: 29 editable semantic mesh parts, 2,892 evaluated triangles
- `exports/AST-CRW-003.glb` and `_open.glb`: one design in closed and fully open states, eight material-group meshes with one actual moving drawer root
- `source/AST-CRW-004.blend`: 16 editable semantic mesh parts, 1,540 evaluated triangles
- `exports/AST-CRW-004.glb`: six consolidated static material meshes
- `source/build_crew_personal.py`: original deterministic authored geometry; Blender 4.3.2, no generation credit, paid asset or copied reference texture

Units are metres. Source is XYZ with Z up/front −Y. Native GLB maps source (x,y,z) → (x,z,−y). Moving drawer grips and storage contact markers remain descendants of the actual `DRAWER_TRANSLATE` root in both native files. The export preserves metric active UVs, embedded staff texture pixels and editable source hierarchy separately. Source materials and all earlier designs are untouched.

## Evidence and limits

`qa/source_reload_checks.json` checks actual source surfaces, normals, joins, parent roots, packed images and editable parts. `qa/geometry_checks.json` checks every full useful box against every convex evaluated solid, complete continuous convex-part swept drawer volumes from the exact zero pose, all physical support connectivity and separate collision profiles. Positive controls distinguish true volume penetration from planar boundary contact. No undeclared solid overlaps remain in the authored final geometry.

`qa/glb_validation.json` parses actual native geometry, transforms, normals/winding, UV triangle area and embedded pixel identity. `qa/native_interface_checks.json` compares every evaluated source vertex against its actual native material group and all native physical marker contacts/normals in both drawer states. `qa/mount_and_clearance_checks.json` binds the actual receiver source hash to opposing contacts and whole-module bedding/use-region separation.

Collision remains a proposal: 25 storage compounds and 12 module profiles preserve the shelf mouths, drawer interior, grip gap and support spaces. Retained bevels and grouped sole shoulders are conservative approximations; the author screen records at most 5.34 mm sampled plane excess for local feet and 4 mm of deliberately grouped backplate/washer face infill for the module. This finite vertex/facet-centre check is not a global Hausdorff bound or runtime physics certification. Independent review may provide stronger measurements.

`qa/source_only_rebuild.json` starts with exactly twelve opened source inputs: this builder, the unchanged staff helper, its manifest, and all nine textures the helper loads. No existing blend, GLB, QA, reference or generated metadata enters the stage. All three GLBs and collision/marker/mount records rebuild byte-for-byte. The source-only ZIP is an input closure, not a substitute for the editable deliverables.

`qa/render_evidence.json` binds final imported-GLB images to precise input hashes, placements, camera height/lens and neutral inspection lamps. Context frame geometry is explicitly a QA receiver, not a recovered room or extra asset design. Camera preflight preserves the initial clipped framing separately. No room allocation, berth registration, roommate identity/story, species fit, electrical standard, engine rendering, live interaction, performance or original-game restoration is established.
