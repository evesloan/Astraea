# Verified Windows section source intake, 2026-10-07

SOURCE CANDIDATES ONLY. Six original compact source archives and their six freshly checked packed Blender/GLB pairs are retained here. The candidate is staged for root review; no receiving-engine adoption, new renders or Game change is implied.

The original six Library file IDs, archive byte counts and hashes are in retention_manifest.json and evidence/INTAKE_VERIFICATION.json. Original archives are unchanged. Every retained native/GLB is under 95 MiB; no mesh, texture or material simplification was performed. Packed native image bytes were explicitly decoded in fresh Blender reopen checks; the exported images/buffers are embedded and native external libraries are absent.

## How to reconstruct without duplicated dependency trees

1. Extract the chosen original_archives/*_SOURCE_REBUILD.zip into a NEW, separate staging workspace. Never unpack over this retention tree, a surviving work tree, Game or existing Catalogue assets.
2. In that new package, run its reviewed copy_dependencies.py against an exact retained Catalogue copy. dependency_map.json inside the archive gives each required Catalogue-relative file, byte count and SHA256. It refuses mismatched originals or existing targets. The source dependency inventory was verified against Catalogue HEAD ba17b5e24f70c663c6592d0d0bbe10a3367c6ed5; hashes, rather than HEAD alone, decide whether input bytes match. No copied dependency trees are duplicated here.
3. For WP02 only, replace source/build_section.py and source/review_section.py in the NEW workspace with source_overrides/WP02's reviewed files. FONT_EXPORT_FIX.diff and SUCCESSOR_SOURCE_PINS.json bind the exact minimal correction. Do not modify the original compact archive. All 52 authored signs must survive as actual exported mesh nodes.
4. Schedule Blender 4.3.2 source work with factory startup, auto-execution disabled, two threads and --python-exit-code 1. Run only the clean builder and reviewed validation entrypoints. Do not rerun WP04's workstation-specific stage_inputs.py, WP05's historical patch scripts or WP07's repair_preview_floor.py. See evidence/FIVE_PACKAGE_STATIC_REVIEW.md for the entrypoint map and limitations.
5. Re-run source geometry, fresh native reload with explicit packed-pixel decode, actual GLB vertex/resource checks, and independent source-image review. Historical native hashes may differ after a legitimate rebuild. No receiving adoption follows automatically.

The packages/ tree preserves the verified current native and GLB outputs, fresh receipts and useful receiving proposals. It intentionally lacks duplicated component/material input trees. Terminal receipts and historical records may contain original scratch paths as provenance; retention_manifest.json supplies the retained relative-path map. Generic audit scripts under evidence/review_tools retain the exact implementation used; their original workspace constraints must be consciously adapted before running them elsewhere.

## Important unresolved interfaces

- Long Library roof top is Y83.2000002. The current reviewed D13 slab underside is Y83.76, giving 0.56 m nominal clearance. Source-plan clearance does not establish roof/frame/downstream load capacity or approve receiving shoes. Off-grid descending supports remain excluded. WP06 arrival panel and care ceiling support/termination detail remains a material review gate.
- WP04 exports physical fixtures without native AREA lights; its 30 source AREA lights are supplied through the separate fixture lighting proposal for receiving adaptation. Runtime light budgets for the other sections remain open.
- Floors/slabs, parent-owned 4 m connectors, loaded-cart/capsule traversal, controls, body fit, performance and fresh visual review remain receiving gates.
- Preserve WP03's five prior-revision versus two final quiet/care image caveat, WP05's four pre-final-lettering views versus final service view, and WP07's diagnostic-only section image. These retained reviews are not new renders.

All source jobs represented here are terminal. WP07's initial added has_data check hit lazy image decoding; that small failed QA receipt/script and corrected successful explicit pixel audit are retained. No old render bulk is copied.
