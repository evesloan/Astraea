# Focused release probe entry correction r002

This separate correction preserves eb11381c and its repair payload unchanged. It replaces ONLY the focused probe PCK and its startup instructions. Use the original repair archive's verified installer and source payload if/when application is approved. Do not use its obsolete --main-pack/--script probe invocation.

## Laptop preparation and execution — approval pending

In a NEW isolated directory, place `release-operations-probe.pck` from this archive beside a byte-identical COPY of the existing laptop release executable, named `release-operations-probe.exe`. Verify the copied EXE's SHA256 equals the original's; do not rebuild, modify or replace the original EXE. Retain any required runtime DLLs through the laptop owner's established setup. The original external ship PCK stays untouched.

After approval, run from that isolated directory (absolute baseline/overlay paths; no engine path/script override):

```powershell
.\release-operations-probe.exe --headless -- --baseline="C:\absolute\existing\Astraea-WIP.pck" --overlay="C:\absolute\isolated\release-operations-probe.pck" --mode=operations
```

The configured main scene runs the probe as a Node on the engine's normal SceneTree. User arguments after `--` are consumed by the probe. It mounts the baseline, the baseline's embedded exact-source pack, then its own repair overlay. Run approved modes sequentially: operations, chain, d17, d17-raw; each must log debug=false and failures=0, exit 0, and have no script errors. Negative-glb and negative-config must exit 2 with ASTRAEA_RELEASE_GUARD. Never pass --allow-editor=1 to a laptop release acceptance run. No full ship launch is performed by this probe.

## Exact scope

All 79 repair payload files are byte-identical to the previous probe. Only project startup configuration, main-scene resource and the fixture's SceneTree-to-Node entry adapter changed. Test operations and checks are otherwise identical. Previous repair files and previous PCK remain preserved. The archive contains no executable.

Official Godot 4.6.3 main/main.cpp: lines 1704–1733 gate --main-pack; 3926–3937 clear script/game/main-loop overrides in builds without OVERRIDE_PATH_ENABLED; 3938 onward selects application/run/main_scene. Lines 1949–1958 describe matching executable/PCK names. Source: https://github.com/godotengine/godot/blob/4.6.3-stable/main/main.cpp

## Validation limits

A byte-identical Linux editor copy, named release-operations-probe beside this PCK, was invoked without --main-pack, --path or --script. It found the configured scene and correctly refused editor acceptance (exit 3). A separate explicit editor-preflight operations run tested the Node adapter. These are packaging/editor checks, NOT Windows release proof. No laptop action, repair application, release execution, full build or full ship launch has occurred for r002. Those laptop actions remain pending user approval.
