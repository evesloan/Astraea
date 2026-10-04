# Astraea library use components

Three new original, independently editable catalogue components. This package is a continuation of the backed-up catalogue, not a recovered or replacement ship. The four supplied library reference images informed useful forms, collection rhythm and restrained material treatment; none of their pixels or geometry were copied.

| ID | Component | Dimensions X/Y/Z, metres | Evaluated triangles |
|---|---|---:|---:|
| AST-LIB-008 | Housed study task fixture | 0.578 / 0.3244 / 0.490 | 2,138 |
| AST-LIB-009 | Low periodical browser | 1.200 / 0.535 / 1.2370 | 2,188 |
| AST-LIB-010 | Catalogue terminal stand | 0.722 / 0.5166 / 1.4141 | 2,964 |

The fixture has an open arched shell, bent reflector, source receiver and carrier, housed shallow opal diffuser, fixed represented rear service cover, low feed recess and physical rocker. No light source or emissive material is exported. Its contact shoe is separate from the wider upper foot. Actual exported shoe contact vertices lie on both existing study receiver plates within 0.00000002 m in the geometry check. Electrical function, light distribution and whole-fixture stability remain untested. Service covers are represented in the fixed geometry; there is no supplied removal trajectory or animation.

The browser has six distinct face-out placements across three original journal titles, with a 69 mm gap between neighboring covers. Sloped tiers keep the lower contact at about 0.69 m and upper contact at about 1.05 m; these are measurements, not an accessibility or alien-reach certification. The lower shelf is honestly labelled back-issue storage and remains empty, with two thin dividers and open bays. Each cover, bound board and page block is editable in the source. Runtime extraction or book selection is pending.

The terminal has a shaped, thick frame and recessed display, a back service body, three large physical keys and a separate selection dial. All four controls have explicit measured surface targets. Original screen art presents a catalogue and abstract collection index; it does not invent a ship plan. Search, index, back and selection behavior are not implemented. The fixed geometry retains a central knee/foot opening, with measured candidate standing and seated approach points that still need real-rig verification.

## Rebuild

From the catalogue root:

1. `python assets/library_use/source/make_use_art.py`
2. `blender --background --threads 2 --python-exit-code 1 --python assets/library_use/source/build_library_use.py`

The generator creates `source/`, `exports/`, `qa/` and `textures/` before writing. Python/Pillow and Blender 4.3.2 are required. No render, QA output or pre-existing new `.blend` or `.glb` is required. All actual shared inputs, including otherwise unused color maps loaded by the common material helper, are listed with explicit catalogue-root-relative paths and hashes in `dependency_manifest.json`. Original pixel lettering is encoded in `make_use_art.py`; no external font files are needed. Four existing book texture images are reused unchanged by explicit paths. Shared common materials were not edited.

## Coordinates and handoff

Metres, Blender Z up, source front −Y. GLB exchange uses `(x,y,z) → (x,z,−y)`, Y up and front +Z. Floor-origin pivots for the browser and terminal; the fixture uses its receiver contact plane at Z0. Every per-asset manifest has both coordinate frames for named physical surfaces, source receivers, controls, approaches and service workspace. The exported hierarchy includes the root, one static semantic-material mesh and all named annotation nodes. Export scale is applied. Editable semantic source objects and the actual static export have matching evaluated triangle counts and dimensions.

Separate collision proposals use thin independent pieces and preserve the hood cavity, browse approach, lower storage bays and terminal knee opening. They are proposals, not simulated or imported physics. No animation is invented for fixed furniture. Source covers remain separately editable objects, but the supplied static GLBs do not open them.

## Evidence

- `qa/glb_independent_validation.json`: independent actual GLB binary accessor, hierarchy, position, normal/winding, UV area, material-role, embedded-texture hash and marker-surface checks
- `qa/source_reload_import_audit.json`: every source reloaded in Blender and compared with actual imported export
- `qa/receiver_contact_validation.json`: actual exported lamp-foot contact vertices measured against both actual existing study GLBs
- `qa/RENDER_MANIFEST.json`: exact source/GLB/image hashes, camera positions, target, lens, sensor and resolution for imported-GLB views

QA floor, lights, camera positions and reused study table are inspection context only. No original room, Godot integration, ship lighting, crowd/species fit, physical behavior or target-hardware performance is claimed. Catalogue adoption and function remain pending until the original game is available.
