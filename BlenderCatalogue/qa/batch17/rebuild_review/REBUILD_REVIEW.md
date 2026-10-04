# Batch17 independent source reconstruction

PASS for the frozen four-design sources and all actual exports. This review performs no rendering or production writes.

| Family | Original inputs | Editable sources | Identical GLBs | Identical art PNGs | Equal generated JSON |
|---|---:|---:|---:|---:|---:|
| housekeeping_equipment | 13 | 2 | 6 | 2 | 7 |
| housekeeping_handling | 13 | 2 | 2 | 4 | 7 |

Each fresh stage initially contains exactly the declared original generator/artwork/helper/material inputs. No existing new blend, GLB, generated artwork, body proxy, author QA file or reviewer report is seeded. Original graphics regenerate from encoded original glyphs. Python catalogue-open attempts and actual native Blender image bytes at each source save are recorded; external Python artwork children are instrumented when present. No out-of-stage catalogue read was observed. This is not a complete OS syscall trace; Blender, Python, Pillow and their system resources are execution-environment dependencies.

All actual GLBs are byte-identical, including states, native node transforms, mesh data, UVs, normals, materials, extras and embedded images. Editable sources agree for evaluated triangles/material assignment, mesh topology/UV/normals, modifiers, drivers, shape keys, hierarchy/transforms, properties, complete used material node graphs and packed image records including their reference paths. Source-container binary hashes may differ; generated JSON normalizes only each source_sha256 value already bound to the independently read source pair. No geometry, interface, hash of an export, artwork value, timing field or source semantic property is normalized.

Body selection is explicitly documented as a separate reviewer second stage. Its generated inputs are the already rebuilt detailed collision JSON and selection names recovered from author keep flags in the rebuilt editable sources. The selector is run twice; exact shape dictionaries, ownership, voids and motion records are preserved. The generated selection config and generated detailed geometry are never labelled original production inputs. Literal subset preservation adds no hull or intrusion at any owner pose; omitted detail stays omitted. Physical adequacy and omitted-distance measurements belong to the separate geometry review.

- housekeeping_equipment: AST-HSK-001 77 detailed → 55 retained (22 omitted); AST-HSK-002 61 detailed → 61 retained (0 omitted)
- housekeeping_handling: AST-HSK-003 25 detailed → 23 retained (2 omitted); AST-HSK-004 51 detailed → 33 retained (18 omitted)

Earlier attempts are retained. Handling r01 stopped because of a reviewer audit helper naming collision, after successful generation; corrected subsequent independent runs passed. Any later superseded attempts remain in their own stage and receipt. No engine adoption, host room or species fit, mechanical/operational acceptance, runtime performance or render acceptance is claimed here.

See FINAL_REBUILD_RECEIPT.json for exact input/source/export/JSON/artwork/stage2 bindings and per-family receipts for all individual source and output pairs.
