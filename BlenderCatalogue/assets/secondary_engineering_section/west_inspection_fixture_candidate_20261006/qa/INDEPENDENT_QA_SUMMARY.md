# Independent source-only fixture QA

PASS. Four physical meshes, 48 triangles and one datum marker were reopened from the saved Blender file. No light object exists. The three reused north-fixture donors retain exactly the same local mesh topology, UVs and material graphs. The explicit cap stem retains the donor material.

The actual GLB contains the same 48 oriented object/material triangles, zero missing or extra triangles, exact source-to-export loop UVs, identical texture pixels and matching PBR values. World-position agreement is within 0.1 mm (largest export/source float-transform residual: 0.0912 mm).

Actual authored horizontal faces have zero vertical gap at all four interfaces: opal/housing, housing/mount, mount/stem and stem/containment cap. The full nominal 70 mm square stem footprint bears on the retained cap underside at Y10.48. This is geometric contact evidence, not structural certification.

No retained triangles intrude into any of the four conservative fixture volumes. Screening includes all four currently installed AST-ENG-008 GLBs, including the current cell signage and sectional gate. The existing Query.prism_hits helper independently confirms zero intrusions and handles axis-aligned triangles as well as sloped triangles. Use ESTABLISHED_PRISM_SCREEN.json for the authoritative volume-screen result and INDEPENDENT_EXPORT_CONTACT_RAYS_002.json for the combined evidence; the first combined report is superseded for its broad-phase implementation.

All 49 rays from the actual exported marker/emitter hit the intended nose disc first, within the trial cone and range; the central emitter exit is clear over its first 10 cm. These samples cover radii 0, 0.2, 0.4 and 0.59 m on the physical 0.65 m central disc. They do not verify coverage of the larger 1.73 m profiled endcap or prove visual quality.

The initial 20-micrometre UV-derived edge-length gate was an added QA assumption, not an asset requirement. Its 0.031 mm residual is a float32 world-mapping diagnostic. The failed script/log and one corrected reopen remain retained. Neither source geometry nor UVs changed to satisfy it. Exact donor data and exact source/export UV equality are the meaningful preservation checks.

Evidence: INDEPENDENT_REOPEN.json; reopened_source.npz; SOURCE_MATERIALS.json; INDEPENDENT_EXPORT_CONTACT_RAYS_002.json. All retained inputs and the candidate blend/GLB remained unchanged. No Game edit, import, rendering, source registry adoption, energy approval or native eight-active/32-candidate selection test occurred. Desired future visual acceptance remains visible focal machinery, including the full cap silhouette and ordinary guest/seated views, rather than merely a bright central disc.
