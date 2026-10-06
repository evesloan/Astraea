# Revised full media reopen checker

Ready in scratch; not executed in Blender. The installed source and original verifier remain byte-identical.

`reopen_media_qa_actual_image.py` is the full original checker with a bounded image-probe correction. `GATE_PATCH.diff` shows every change. `STATIC_PATCH_QA.json` records the static review and replay against the direct saved-source diagnostic.

The direct diagnostic reproduced the cause: first display ray index 1 targets a planned corner slightly outside the actual float32 image edge. All 120 paired actual-UV casts reached the correct image. Maximum planned-to-actual displacement is 13.682 μm, below the unchanged 50 μm contract.

The revised checker derives all five points from actual evaluated image UV triangles (four corners and centre), keeps all six original eye poses per display, and checks every actual point against its planned rectangle and reservation with the existing tolerance. Planned points only verify correspondence and displacement; they never define a replacement ray.

It then runs the full original self-occlusion, retained architecture, installed51/planned48, staged finish, and complete vegetation-reservation checks against these actual points. Every pre-existing support, bearing, material, packed-image, metric-UV and handedness helper is AST-identical. The existing intersector and every ray/occlusion tolerance expression are unchanged. No source rebuild, material edit or tolerance relaxation is needed.

## Parent-coordinated full reopen command

    blender --background --threads 2 --python-exit-code 1 --python /workspace/scratch/375c2e438292/pool-media-reopen-revision-20261006/reopen_media_qa_actual_image.py -- --media-root=/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_pool_first_pass/comfort_greenery/media --report=/workspace/scratch/375c2e438292/pool-media-reopen-revision-20261006/INDEPENDENT_REOPEN_QA_ACTUAL_IMAGE_001.json

The same command is saved in `RUN_COMMAND.txt`.

The checker requires explicit media/report paths and refuses to overwrite a report. It reads the original family source for material ground truth, then the saved candidate. It writes only the new report location and verifies the installed source and original verifier hashes remain unchanged. This patch has not replaced the installed verifier and does not authorize exports or claim visual acceptance.
