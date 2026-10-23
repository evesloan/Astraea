# Additive D04 optimization test successor

Requires exact frozen source with cumulative Quiet/Family patch retained at854dc6db. This is NOT a replacement Windows build. Baseline files and project main remain unchanged; candidate is OFF by default. The existing laptop owner must coordinate any launch.

Extract separately, then run `python apply.py --repo "ASTRAEA_REPOSITORY"` to preflight, and add `--apply` to install new files only. Existing different files or a mismatched baseline cause refusal before writing. No imports, launch or export is performed. Repeated application is a no-op.

See `Game/d04_surface_cells_20261023/README.md` for official research, implementation, measured scope, limitations and controlled comparison. Candidate entry is `res://d04_surface_cells_20261023/bootstrap.tscn`; enable only for an authorized test with `ASTRAEA_D04_SURFACE_CELLS=1`. `ASTRAEA_OCCLUSION=0` is the separate diagnostic control. Existing retained Godot4.6.3 opens this scene; no engine install or renderer switch.

Do not overwrite the frozen baseline binary, project settings or earlier fix backups. Original/native source revisions are untouched. Target-machine frame time, live lighting, streaming activation latency and memory acceptance remain open.
