# Cap-supported west inspection fixture candidate

This is a small, unadopted AST-ENG-008 source derivative. It reuses the retained north inspection mount, housing and lens, rotates their placement, and adds a real stem bearing against the existing containment cap. The frozen saved source contains four meshes, 48 triangles and one marker, with no light object.

Source: source/AST-ENG-008_west_inspection_fixture.blend
Export: exports/AST-ENG-008_west_inspection_fixture.glb

The independent reopen/export check preserves the reused local geometry, material graphs and UVs. The four contact interfaces meet, the full 70 mm square stem footprint contacts the cap, and the established triangle/prism helper finds no retained obstruction. Source-to-export world-transform rounding has a maximum 0.0912 mm residual; UVs and texture pixels match exactly. See qa/INDEPENDENT_QA_SUMMARY.md and the named final receipts.

The geometric trial intent is marker (25.55, 9.5, -432), emitter 0.08 m below, range 4 m and angular radius 32 degrees. Energy is not approved. All 49 sampled rays reach only the central 0.65 m-radius nose disc, sampled through radius 0.59 m. This does not establish whole-endcap coverage. Future acceptance must show visible focal machinery through the retained glazing, rather than a bright flat disc, and real standing/seated guest-view source selection under the unchanged eight-active/32-candidate limits.

No Game file, old source, original fixture, pressure glass, registry, shared light profile or selector was changed. This folder is source retention only. Native import, energy, actual source selection and visual acceptance remain pending.

The first builder attempt stopped on a mutable Blender library-request list. The corrected builder uses an immutable name tuple and a fresh request list. The initial diagnostic also had a syntax error. Both stopped before creating a source/export and are retained as failed evidence. A separate new UV edge-length QA threshold was unnecessarily tight; its measured 0.031 mm residual is diagnostic, not an asset requirement. Neither geometry nor UVs was changed to satisfy it. The first pure obstacle-screen result is superseded by the established Query.prism_hits result.
