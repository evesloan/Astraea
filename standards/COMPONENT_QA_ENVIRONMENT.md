# Verified component inspection environment

Blender 4.3.2 is installed. The current build does not provide OpenImageDenoise; do not enable it in a fresh Cycles job and repeat that known failure. Headless `BLENDER_EEVEE_NEXT` works for the component inspection views. Use a bounded 32–128 sample pass and inspect the pixels for noise; this is not the game's renderer.

Typical process invocation is `blender --background --threads 4 --python <inspection-script>`. Keep heavyweight render jobs sequential. Brief one-thread source reload checks can run separately because they do not render or save. Some successful Eevee runs print initial EGL/cache warnings; require actual exit status, expected image files and source hashes before deciding whether a job failed or succeeded.

Render the imported GLB at least once for each final source/export change. Source `.blend` renders cannot reveal all export defects. Store source/GLB hashes and exact camera settings with evidence. A small material or metadata correction should not automatically trigger every unchanged view again; retain earlier evidence with its exact source scope and add only the needed comparison.

QA floor, lights, proxy bodies and camera arrangements are inspection aids only. Never report them as game geometry, actor rigs, physical behavior or target-PC performance. Keep normal-height views separate from high three-quarter/detail views. The original game uses its own Godot Compatibility and low-resolution pipeline, which is not currently available for integration checks.
