# Other five retained Windows section packages: static execution review

2026-10-07 UTC. Source-only safety/readiness screen; no engine runs in this review. Original archive/extracted builders remain unchanged. Full source pins/imports/file-affecting call inventory: FIVE_PACKAGE_STATIC_SAFETY_RECEIPT.json.

## Result and order

Proposed next isolated reconstruction order: WP07 Listening Salon, WP03 Cloud Conservatory, WP04 Botanical Nursery, WP05 Moonfruit, then WP02 Sports Care after its signage export fix. WP07 is the smallest dependency closure and a complete D12 candidate; WP03 has both native and actual-vertex export checks. This is scheduling advice, not permission to run unscheduled jobs or adopt geometry. All runs use Blender 4.3.2 --factory-startup --disable-autoexec -t 2 --python-exit-code 1, no render arguments.

All five clean builders have package-relative reads/writes and no subprocess/network/exec/eval. Their only nonstandard imports are bpy/mathutils/bmesh and WP05's reviewed package-local signage_spec.py. Blender scene deletion is only in the fresh isolated process. Output names are overwritten by design; never run in an existing work tree. WP03/04/05/07 assume an initial World, so factory startup rather than an empty factory scene is appropriate. Native save can precede a later failing bounds assertion; terminal exit and actual checks must decide success, never output existence alone.

154 restored dependency rows across these five packages independently rehashed with exact byte/hash matches (167 including WP06). Embedded pre-build hash gates also pass: WP02 8, WP03 12, WP04 27 actual asset rows, WP05 10. WP07 lacks a pre-build hash gate but its 11 staged inputs were verified and its verifier rechecks both furniture sources. Material filename references inspected are confined to the package and resolve. Successful reconstruction/native packed-image inspection is still needed for transitive image closure outside WP06.

| Package | Restored rows / bytes | Clean entrypoint | Follow-up checks | Material caveat |
|---|---:|---|---|---|
| WP07 | 11 / 1,915,963 | source/build_listening_salon.py | plain Python source/verify_package.py, plus independent native reload/packed images | verifier writes manifest before final assertion; inspect checks. Builder's optional section render does not restore hidden geometry for a later view; use separate reviewed render_review.py when rendering is assigned |
| WP03 | 20 / 4,036,449 | source/build_conservatory.py | Blender tests/check_native.py; Python tests/check_export.py (imports reviewed tests/glb_reader.py) | source/GLB already use world coordinates; placement [0,0,0], never add another offset |
| WP04 | 25 / 3,328,112 | source/build_nursery.py | Blender tests/reload_and_export_check.py; add exact GLB resource/mesh check | zero exported punctual lights is intentional: AREA source lights delivered as docs/fixture_lighting_proposal.json for receiver adaptation. Reload check ignores file images without has_data; independently check for missing/unpacked images |
| WP05 | 50 / 7,315,206 | source/build_moonfruit.py plus source/signage_spec.py | Python tests/check_source.py, plus independent native reload and actual GLB resource/vertex checks | existing check_source is source-record/AABB validation, not actual GLB validation or live movement. Do not substitute historical diagnostic forecasts |
| WP02 | 48 / 7,263,334 | source/build_section.py | Blender source/review_section.py | BLOCKER: authored FONT signs are omitted by export selection and by native QA. A minimal isolated successor must preserve editable native text, convert/export signs and explicitly assert every authored sign is present as a GLB mesh |

## Excluded entrypoints

- WP04 source/stage_inputs.py is a historical, workstation-relative intake helper. It reads old sibling BlenderCatalogue/Game/local_delivery paths and overwrites isolated intake files. Do not run; the verified common bootstrap has replaced it.
- WP05 source/patch_preview_only.py, patch_review.py and patch_sign_contrast.py are retained history, not clean reconstruction steps. Corrections are already in build_moonfruit.py and signage_spec.py. Do not replay them.
- WP07 source/repair_preview_floor.py is a one-time historical native patch whose old-location assertion is unsuitable for a corrected clean build. Do not run it.
- WP05 tests/diagnose_routes.py and forecast_clearance_fix.py use dynamic exec of an edited local checker. They do not import external code but are diagnostics/hypotheticals, not acceptance tests and not required for reconstruction. Exclude them from the clean pipeline.
- Copied material generator scripts are not imported by any clean section builder. Do not rerun them over hash-verified material inputs.

## Review provenance that must survive reconstruction

WP03: only final quiet/care images bind to historical final native 6120fa3a… and GLB bf1e8461…. Arrival/grove/activity/mounts/quiet_garden are retained PRIOR-revision images tied to prior native c944fe10… through recorded chronology. Main-hall enclosure/islands/supports/coffers/main lighting/exposure/cameras were unchanged by that correction, but all seven seat-planter flower/root/contact placements and local quiet/care fixtures changed. Do not claim all geometry/lighting was unchanged or all views are final-source renders.

WP05: service image is the final ivory-lettering revision. Arrival/activity/booth/quiet predate only the final text-material correction; geometry/lighting/layout did not change. Those are accepted historical source views, not new-build images. Historical native patch scripts are not required rebuild steps.

WP07: SOURCE_ONLY_section.png is diagnostic cutaway only. It is not an ordinary-eye-height acceptance view. Preview-floor correction changed source preview backing and did not change delivered GLB geometry.

All root_review records and embedded historical receipts remain provenance only until fresh outputs and actual pixels have been inspected. No floor ownership, external 4 m connector, collision/traversal, controls, body fit, runtime lighting or engine adoption has been established here.
