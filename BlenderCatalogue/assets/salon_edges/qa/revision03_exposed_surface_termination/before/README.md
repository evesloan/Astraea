# D09 salon edge junctions — new adjustable source components

AST-SAL-004 is an asymmetric low court edge with a 0.47 m walnut seat, deliberately shaped ivory fascia, three load piers, integral supported planting tray, and a small end perch. It is neither a generic BOT planter nor a free-standing tree monument. The existing AST-BOT-002 understory and AST-BOT-003 rosette appear only in labelled component QA and are not new designs or production dependencies.

AST-SAL-005 is a continuous substantial balcony edge-to-portal terminal with a useful 1.15 m walnut top, 0.16 m structural core, floor supports and native join faces. Its two infill fields are empty. It is not a completed safety barrier; pane/panel retention, host anchorage and compliance remain unresolved. No glass material or runtime glass shader is used.

AST-SAL-006 is a fixed two-faced service return. A finished guest side has framed vertical teal fields and a tactile ledge; its practical rear has four open shelf planes and a low work surface turning into a supported threshold edge. Lower shelf clear mouths exclude the actual corner support. There are no operating doors, hinges, slides, covers or implied removable panels.

## Authority and scope

These are original script-assisted source components, not recovered assets or installation in a rebuilt D09. The original game and final 825.8 m² guest polygon remain missing. All real public/service door clear spans, heights, leaf strokes, cassette depths and head interfaces are UNKNOWN. No theater dimensions have been borrowed. The historical D09_salon5 identity, arrival/service axis, X35..45 tram reserve and terrace relationship are preserved by the batch contract. Local suggested coordinates and the 4 m study strip are inspection hypotheses only.

All four actual salon reference images were inspected. The governing interpretation follows the later D09 composition contract: useful low planted edges, sheltered quiet bays at the documented 7.2×5.4×3.8 m maximum, purposeful service, and ivory structure/teal recess/walnut touch/champagne joints. The earlier tall-court scheme is not final evidence.

## Sources and rebuild

Run from the catalogue root with Blender 4.3.2:

    blender --background --threads 2 --python-exit-code 1 --python assets/salon_edges/source/build_salon_edges.py

The generator creates its output parent directories. Inputs are the original generator, both unchanged common/botanical material helpers, both material manifests, and every PNG opened by those helpers. The dependency manifest enumerates and hashes these actual reads, including unused roles. Production generation does not read QA scripts, plants, furniture, other salon components or renders.

Each source retains named semantic meshes, editable easing modifiers, ordinary Principled materials and packed images. Static GLBs consolidate evaluated mesh copies by material role with non-collapsed metric UVs. Explicit native marker nodes remain in every export. GLBs are actual portable exchange files, not source-render stand-ins.

## Coordinates, contacts and joins

Metres, source Blender +Z up, +X across, −Y guest front, floor Z0. Standard GLB conversion maps (x,y,z) to (x,z,−y). Actual native hierarchy transforms are authoritative. Manifests and marker_api.json pair both frames and distinguish physical contact faces from empty receivers and nonphysical origin/approach datums.

The compatible new-family profile uses 0.16 m structure, 0.022 m wood inset, 0.012 m reveal and 0.012 m arris. SAL004's left low shoulder is a real flat face at X−1.80/Y0.56..0.72/Z0.08..0.80. SAL005's terminal faces are X±1.40/Y0.16..0.32/Z0.08..1.10. For a SAL001 portal face centred at Y0.64, a +0.40 m local depth translation aligns SAL005's Y0.24 seam; the lead arrangement must also orient both pieces correctly. SAL006 offers a left lower-profile face and a separate right fixed service-return face. These interfaces do not define a real door mechanism.

Collision proposals use separate economical boxes/convex pieces. Seat knee spaces, actual service shelf compartments and unfilled guard fields remain open. They are not active engine collision, certified routes, accessible furniture or load-rated structure. Markers identify real supported surfaces; a receiver in open space is not relabelled as a contact.

## Evidence

QA reloads the actual .blend sources, independently parses native GLB geometry/UVs/normals, resolves marker transforms, compares source/export bounds and triangle counts, checks declared physical joins and finite use voids, and includes deliberately blocked collision controls. Camera bounds are preflighted with standards/qa_frame.py. Ordinary 640×360 images are actual imported-GLB views; necessary close detail crops are declared. Neutral lights, floor and botanical context are inspection aids, not runtime lighting, species fit or a lost host room.

The early joint/void findings and precise corrections are recorded under qa/revision01_joint_and_void. Every final capture binds the source and export hashes it inspected. This family still requires independent batch visual/spatial review, source-only restoration and durable batch backup before further categorical expansion.
