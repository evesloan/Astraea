# Spatial screen provenance

The nominal screen is copied unchanged from the independent R3 spatial author. It checks proposed component boxes, transforms and declared context extents, not the final authored meshes, physical mounting or original host fit. This earlier nominal-only phase is superseded by the final source-bound screen described below.

Original: /workspace/scratch/375c2e438292/district-layout-audit/landing-kit-review/batch11_nominal_screen.json
SHA256: 0e1401c8bda86a673f2975aeb567f5075962abcf5b27436384a2722ff4339539

Final r03 source-bound screen: `batch11_frozen_export_screen.json`, SHA256 bdd9e92efe37f3eb659924f7e1c845a5495e55c0fca2dd732d38f0ab92b79375. Reproducer copied unchanged as `screen_exported_landing.py`. It checks all six actual GLBs and 7,716 triangles against proposed component envelopes and empty-plan zones, verifies all 21 freeze-bound files before/after and agrees with imported bounds within 0.000015m. Original host geometry, floor/support, headroom, moving doors, actor/cart fit, material/contact quality and visual acceptance remain separate.

Copied checker SHA256: c5227d602a14ebd3c18ea9581994dfb89f361229b508a83ebfab3584e45d241d. The copy is byte-identical to the final checker supplied by the spatial author.
