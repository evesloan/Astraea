# Isolated Uniforms D03 aft-core aperture candidate

PREPARATION ONLY. No production edits, publication, Godot imports, engine runs, rendering, collision disabling or source-room changes occurred.

The retained editable Blender source has exactly two source pieces replaced: CORE_OuterWall_02_1 and CORE_WallDado_02_1. All other 888 scene objects retain fingerprints covering geometry, transforms, polygon indices, UV layers, material assignments and object properties. Five closed cuboids provide the two full-height wall sides, supported central header, and two walnut dado sides. No new design ID is claimed.

The runtime successor preserves every byte of the original binary buffer, every original vertex attribute, all original nodes/materials/images/textures/samplers, and every retained triangle index in original order. Only the target wall and trim's twelve triangles each are removed from their batch index lists. The five source-exported cuboids are appended as distinct mesh nodes using original materials. Net triangle change is +36. Original unreferenced removed geometry remains in binary storage solely for exact inverse recovery and is not drawn or collidable.

Opening local Z is -2..2, world Z430..434; floor is Y12 and header underside Y14.64999961853 (float32 representation of14.65). Header thickness is1.61000061035m and spans the original4m opening between full-height wall segments. Cut affects only original ivory/walnut solids, X7.63500022888..7.88000011444. The solid-set difference is precisely these solids intersected with that aperture. No unrelated solid is removed; split-boundary coincident faces are internal and do not enter the clear opening. Floor and room geometry are untouched.

## Independent verification

Run: python verify_candidate.py

This is read-only and requires only Python/numpy, not Blender or Godot. It reconstructs original GLB bytes from inverse_original_header.bin plus the unchanged candidate binary prefix and checks the exact original SHA256. It checks original on-disk GLB/source hashes, successor hashes, retained index/attribute equality, original materials/nodes, all six correctly wound two-triangle faces of each replacement cuboid, and an exhaustive axis-aligned cell partition proving the revised solids equal original solids minus the portal void. SOURCE_PROOF.json records before/after888-object fingerprints from the single bounded Blender source job; it is not a claim that an independent second Blender load was run.

RUNTIME_PROOF.json and SOURCE_PROOF.json contain original/successor SHA256 hashes. prepare_source.py is the retained single-job editable-source authoring script. build_and_verify_runtime.py constructs the exact surgical runtime from the original and source-exported doorway_replacement_pieces.glb. Blender was run once, CPU2, one thread, bounded150seconds; its complete log is retained.

## Root-owned adoption gates

ADOPTION_CONTRACT.json and AFT_PUBLIC_CORE.candidate.json describe the one-field aft-only adapter. Preserve AST-CIR-005_spine_core.glb and its original editable source. Install the uniquely named derivative and change only AFT_PUBLIC_CORE enclosure_file. Never substitute globally or disable whole batches. No primary core/runtime source change is necessary.

Before opening this receiving interface, root must retain the package independently and confirm the existing D03 core support plus the0.2m×4m bridge to X8 and full room connector. Source room remains unchanged. Import and inspect actual meshes, preserve mesh-based triangle collision/occlusion, exercise body/0.85m cart sweeps, seam support/headroom, all unrelated core-instance regressions, complete regression and native graphical review. No gameplay, final-art or whole-ship acceptance is claimed.
