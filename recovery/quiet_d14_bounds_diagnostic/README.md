# Quiet D14 bounds evidence — diagnostic only, not a fix

Cloud retained-import/direct-GLB checks match all three immutable receipt bounds. Receipt first-two bounds equal exact original GLB POSITION bounds. The third is the prior QuietD15 replacement named PATCH_lobby_wall_staff_white_paint_y11. Therefore compression or a cross-platform renderer difference is not yet proven. No tolerance, receipt, geometry or import policy changed.

On the laptop, while no editor/import/game process is running, execute the supplied probe against the already imported frozen project:

```powershell
& 'C:\path\Godot_v4.6.3-stable_win64_console.exe' --headless --path 'C:\path\Astraea-f94cc1c8\Game' --script 'C:\path\probe.gd' -- 'C:\path\quiet-d14-laptop-bounds.json'
```

Use a new output filename. This loads only two already-imported model scenes and examines the three relevant meshes, including the prior D15 patch. It does not instantiate the ship, invoke editor import, launch a game or alter project files. It records expected/actual bounds, vertex bounds, source and import-config hashes, compressed-surface counts, triangles and duplicate/material-assignment bounds. Return that JSON. If all bounds pass, the remaining failure is in the installed predecessor chain and requires capturing the actual failing owner's identity/bounds at the original guard during the next owned launch; do not infer that the error is fixed.

The initial cloud probe used the original third-wall name instead of the preceding replacement name and stopped at its lookup assertion; the corrected source lookup completed. This lookup correction was diagnostic only.
