# AST-BOT-001 · Asymmetric small canopy specimen

Original script-assisted Blender catalogue work, 2 October 2026. This is a newly authored component, not restoration of the missing game, a room installation or a runtime acceptance claim. All three actual batch04 reference images were inspected before design. Their layered botanical structure and inhabited planting edges inform a smaller, open-trunk specimen; the atrium's giant tree scale is not copied.

## Deliverables

- `AST-BOT-001.blend`: 242 editable capped branch/root/petiole curve paths and 63 named leaf mesh groups. Original texture dependencies are packed. Branch points, taper radii, parent paths and leaf attachments remain explicit.
- `AST-BOT-001.glb`: four consolidated semantic material meshes/primitives, 7,096 triangles. Standard glTF Y-up conversion, applied unit scale, ordinary embedded base-color textures.
- `source/build_canopy.py`: deterministic original generator. Authorship is explicitly scripted; there is no literal hand-GUI modelling claim.
- `AST-BOT-001.manifest.json`: measured source dimensions, part identities, material roles and current hashes.
- `AST-BOT-001.collision_proposal.json`: seven narrow trunk capsules plus the short base segment, with numeric endpoints and radii. No canopy volume blocker.
- `qa/`: reloaded-source validation, binary GLB validation, support/leaf contacts, actual-import render evidence and labelled component proofs.

## Form and placement

Envelope is 2.393888 × 2.006192 × 2.692826 m (X/Y/Z). The asset pivot is the soil plane at (0,0,0), not the planter floor. Root flare caps and trunk base are on that datum, within Blender's approximately 5e-9 m floating-point evaluation noise. The lowest foliage is Z1.733910 m above soil.

At the supplied planter soil datum of Z0.390 m, the specimen reaches Z3.082826 m and the lowest leaf is Z2.123910 m. This is a component-placement proposal, not a real ceiling-fit claim. Place the stem toward one planter end and keep the seat approach open. The crown may overhang the planted opening; minor branches and thin leaves have a nonblocking collision proposal. Plant survival, horticultural volume, actor contact and engine collision require separate adoption checks.

There are seven unequal branch tiers and 21 directed terminal sprays, with 210 individually attached lanceolate leaves. The trunk is exposed below the canopy. Leaves use eight triangles each, with a raised midrib and downturned tip; six boundary edges per leaf are deliberate. Each leaf joins a short closed petiole, each petiole starts inside a supporting shoot, and every shoot connects to its branch. The source supports are independent closed solids that overlap at joins, not one boolean-unified watertight tree.

## Materials and topology

Roles are `botanical_bark`, `botanical_leaf_jade`, `botanical_leaf_sage`, and `botanical_leaf_olive`. All exported alpha modes are OPAQUE with alpha factor 1. Leaves are explicitly double-sided; bark is single-sided. There are no alpha cards, transparent foliage clouds or sphere leaf masses. Leaf UV U runs across the blade and V runs root to tip. Before role joining, evaluated meshes retain one normalized active `metric_material_uv` layer. Blender's coincident cap vertices are welded at 1e-6 m before export; the live source curve controls remain editable.

The validation reports distinguish intentionally open thin foliage from closed supports. Binary GLB checks cover dimensions, triangle count, finite data, normals/winding, nondegenerate triangles, noncollapsed UV area, role/primitive count, material alpha and byte-for-byte embedded texture references. The source check evaluates closed caps after coincident-vertex welding and checks actual curve-root positions against their named parent paths.

## Reproduction

From the catalogue root, run Blender 4.3.2 with `-b --threads 2 --python assets/botanical_canopy/source/build_canopy.py`.

Use `qa/check_and_render.py -- --preflight-only` for cheap source/contact and camera checks. Coordinate the shared render slot before the same script without the preflight argument. It renders only an imported final GLB with EEVEE_NEXT, no denoiser, two full 640×360 views and one deliberate branch detail crop. `standards/qa_frame.py` checks every full-frame camera. Then run `qa/label_evidence.py` for labelled evidence and `qa/validate_glb.py` for independent binary checks.

Lights, floor and cameras are QA helpers, excluded from the source asset and GLB. The generator reads shared botanical materials but does not alter them. Future game performance, instancing, shared runtime material mapping and collision acceptance remain untested.

## Compact-source rebuild readiness

Batch08 makes the generator create its own output directories before writing completion evidence. It can complete from source-only staging without a pre-existing review folder. Existing editable masters, exported geometry and texture bytes are unchanged; original generator provenance is retained in the checkpoint evidence.
