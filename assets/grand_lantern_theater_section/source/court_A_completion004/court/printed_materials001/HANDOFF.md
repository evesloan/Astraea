# Court A printed materials, scratch preparation 001

Status: original artwork pixels reviewed; pure geometry, source-contact, material-recipe, schema and builder-syntax checks pass. The source successor has never been run in Blender. No source was saved, no engine was launched, nothing was exported or installed, and no scene/native/source-retention acceptance is claimed.

## Deliverables

- `SUNCORP_GRAND_LANTERN_PROGRAMME.svg` and `.png`: editable original 1250 × 990 art, exact 1.25 × 0.99 m display-plate aspect. Cream text on dark navy/teal, original ochre sun/orbit and clay curtain geometry.
- `SUNCORP_GRAND_LANTERN_COVER.svg` and `.png`: the same original composition with added lateral room, 1400 × 1000 for the exact 0.28 × 0.20 m programme covers. No stretched motif or type.
- `ART_RECEIPT.json`: image/vector pins and the verified retained fictional title, `details.programme` in the retained AST-CUL-001 manifest. `ART_VISUAL_REVIEW.json` records inspection of both PNGs through the image tool.
- `PRINTED_MATERIALS_CONTRACT.json`: nine closed 8-vertex/6-quad prisms, three per stack, plus the separately specified 5 mm display plate. Exactly 108 stack triangles; 12 plate triangles. No individual-page geometry.
- `PRINTED_MATERIALS_PURE_CHECK.json` and `PRINTED_MATERIALS_SCHEMA.json`: current pure validation with actual retained GLB triangle witnesses, hashes and explicit limitations.
- `build_court_A_source_printed_DRAFT.py`: full successor to the preserved original source adapter. `SOURCE_BUILDER_SUCCESSOR.diff` is its reviewable exact correction.
- `PARENT_GATE_FIELDS_REVIEW_ONLY.json`: data/pins for parent review, not an authorization gate. It deliberately leaves artwork-review acknowledgement false.
- `ARTIFACT_HASHES.json`: SHA-256 index of all authored deliverables and immutable-input pins.

## Art and geometry correction

In-world text is exactly SUNCORP CULTURE, GRAND LANTERN, A THOUSAND SMALL WORLDS, and EVENING PROGRAMME. The supplement replaces the old draft's PROGRAMME STUDY instruction; the original geometry contract itself is not edited. No WIP, invented performance time, admission price, copied logo/photo or reference art appears.

Each stack is bottom cover 1 mm, aggregate matte pages 20 mm, top cover 1 mm. Interfaces share exact contact planes without overlap/gaps. Both table-stack bottoms are Y70.16500002145767; reception is Y70.56500005722046. Each complete 0.056 m² bottom rectangle lies on actual hash-verified retained warm-stone top triangles at zero measured height error. The reception stack stays 0.31500000238418124 m to the right of the actual lower writing wing; the whole lower wing remains clear.

Each quad has explicit UV loops. Blank stock/pages use 0.25 m/tile metre-density mapping, including thin edge faces. The top covers use one complete, aspect-correct image, with image bottom toward public +Z and image top toward −Z, text-right toward +X. The framed plate uses one complete image on +Z only, image top toward +Y. No images are repeated across thin sides or backs. Three stacks use nine prisms total, not nine per stack.

The successor creates new matte paper and navy paper-stock Principled materials with roughness 0.92/0.88, metallic/coat/transmission/emission zero, reduced specular, and sRGB artwork. No retained cloth is renamed or reused as paper. It packs the two image files and checks the packed byte hashes, records material graphs, assigns materials per face, and includes all ten printed solids in closed-geometry validation.

## Parent-controlled next step

Use `python -B build_court_A_source_printed_DRAFT.py --inspect` for safe inspection. Reproduce pure checks with `python -B validate_printed_materials.py`. Artifact generation scripts are retained, but need not be rerun.

The successor reads the existing parent gate at `../PARENT_SOURCE_BUILD_GATE.json`. It retains all original static-checkpoint/source-job-slot/no-production and base-source-hash checks, plus pinned print-contract, pure-check, two-image and reviewed-art checks. It does not create or approve that gate. The proposed scratch output moves under this new folder: `authored_preview001/AST-CUL-005_arrival_court_A_004.blend`; it refuses existing output/report paths. The optional fuller mass stays under its original independent parent flag.

Before any source job, the parent must complete the static checkpoint, grant the actual source slot, review the artwork and adopt the pins. After an authorized build, independently reopen the new source, verify packed images/UVs/material graphs/contact bearings, and retain it before composing same-camera/seated/service review. Preserve old lights/exposure, old objects/plants/usher stations and all 2,200 chairs. Existing composed visual, source-retention, native collision and six-species gates remain pending. No export or installation is authorized by this preparation.

All writes for this task were confined to this new `printed_materials001` folder. Original source draft, input contracts and protected firstpass003 source hash remain unchanged.
