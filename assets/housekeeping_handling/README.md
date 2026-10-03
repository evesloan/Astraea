# Housekeeping textile handling components · Batch17

Two original editable components extend the proposed D01 laundry workplace. They do not recover the missing game, furnish a whole room, establish a staff loop, or change the player cart.

- **AST-HSK-003**: 1.80 × 0.86 × 1.017 m textile sorting/folding workbench, 0.90 m worktop. A broad left CLEAN folding area and smaller right USED sorting area have real fixed separating/return edges, original legible markings, three anonymous folded textile forms and an open lower retrieval shelf. The labels identify handling intent; procedural and hygienic separation remain unassigned.
- **AST-HSK-004**: 0.792 × 0.735 × 1.077 m USED-only bulk-linen carrier. An open, deep faceted liner rests on a cradle within a supported hoop. The lowered front rail makes its bulk-transfer role distinct from AQU-008's removable towel receiver and HSP-006's service trolley. Four visible tread/axle/fork/bridge/stem assemblies and a retained rear handgrip have actual geometric contacts. This is a static proposed stance, not rolling, load or traction validation.

Source files are in `source/`, grouped native GLBs in `exports/`, records at the family root, and hash-bound inspection evidence in `qa/`. Semantic meshes and modifiers remain editable. Fixed export copies are grouped by material and graphic submaterial; no glyph creates a draw group. There are no moving-state derivatives.

## Original art and references

`textures/draw_handling_art.py` uses Python's standard library to reproduce two encoded-glyph identification graphics and two subtle weave textures. There is no external font, machine-font dependency or sampled reference pixel. The shared staff material helper and all its original input images are unchanged.

The actual blueprint and both staff-corridor photographs were inspected. The translation uses broad cool pale staff surfaces, metallic folded/retained edges, dark contact protection, regular exposed supports and restrained utilitarian detail. Blueprint logistics D03 maps to current D01; old printed quantities and the photographs' apparent passage widths are not equipment or room authority. The D01 housekeeping handoff and Batch17 contract preserve the separate laundry/depot allocations, unknown finished rooms and access contradiction.

## Coordinates and interfaces

Metres, source XYZ with +Z up and front −Y. Native GLB maps `(x,y,z)` to `(x,z,−y)`. Floor Z0 is the source origin; a centre datum may be empty and is not falsely labelled as a contact. `marker_api.json` distinguishes actual floor/work/load/grip/identification contacts, retained support joins, empty spaces and proposed approaches. Normals are actual faceted surface directions. Host floor, body, species, door, reach, carrier path, handling force and equipment quantities remain unknown.

The carrier's front is its lowered retrieval side, and its staff grip is rear +Y. The bench's right side is its USED region. A relative adjacency can place the carrier beside that region; it does not establish a corridor between the remote laundry and depot allocations.

## Collision roles

`collision_proposals.json` contains semantic convex reference shapes before edge easing plus an optional literal body subset authored at the same time. Bench: 25 precise reference shapes / 23 body shapes. Carrier: 51 / 33. The body subset retains all declared work, load, floor and grip surfaces and the real useful openings. Small labels, carrier straps, caster axles and fork detail remain in the precise reference and visible construction rather than adding every detail to the body candidate.

The omission distance report samples omitted vertices against retained actual surfaces; that distance is not material thickness or a complete Hausdorff bound. The liner wall thickness is nominally 8 mm in its designed XY offset, separately from optional-body detail omission. Static support is documented in the full editable/precise assembly; the optional body role is not a mechanical assembly or a game collider until adopted and checked. No new hull fills the liner or lower-shelf opening.

## Source-only reconstruction

Start with exactly the files in `dependency_manifest.json` under `source_only_inputs`, preserving their catalogue-relative paths. Run:

    blender --background --threads 1 --python-exit-code 1 --python assets/housekeeping_handling/source/build_handling.py

The builder regenerates original graphics and weave before creating source, native exports and interface/collision records. It never opens previous new `.blend`, GLB, renders, QA reports or generated local artwork as seeds. All nine images opened by the unchanged staff material helper are declared, including roles not used in the final designs. The optional body subset is generated in this same original-input build, with no later geometry simplification stage.

Useful focused QA commands are `qa/check_sources.py` through Blender, `qa/check_collision.py` through Python with NumPy/SciPy, and `qa/render_imported.py -- --preflight-only` through Blender. These scripts are verification tooling, not generator inputs. Full capture requires the lead's serialized render slot after independent cheap-check clearance.

All views use actual imported GLBs with a neutral QA floor, lights and camera, excluded from production. Source-only semantic reconstruction and native correspondence are independently reviewed at the batch level. Failed early finish/contact evidence remains under `qa/revision01_before_contact_finish/`; it does not describe the corrected final production.
