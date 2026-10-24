# Offline Windows launcher companion — frozen1091d34e test PCK

This small companion supplies a launch command and exact-byte checks. It includes **no Windows executable** and does not turn the test PCK into a validated Windows release. No download, installation, permission change or engine/source import is performed.

Restore the twelve transport parts using their unchanged RESTORE_PACKAGE.py into a new directory. Put these launcher files alongside the decoded Astraea-1091d34e.pck. Reuse the original official Godot4.6.3 Windows editor from your retained older archive if available; do not use an older exported Astraea game EXE. The original engine receipt identifies172409864bytes and SHA256ef90e929ba1a6a4322860285d97f40f4aa349c90329a91b0e8b55b8df0f4cb00. The launcher verifies both engine and PCK before invoking anything.

With Python3.9+ (also used by the transport restorer), run:

```
python LAUNCH_ASTRAEA.py --engine "C:\existing archive\engine\Godot_v4.6.3-stable_win64.exe" --check-only
python LAUNCH_ASTRAEA.py --engine "C:\existing archive\engine\Godot_v4.6.3-stable_win64.exe"
```

Alternatively, place the exact existing engine under `engine` beside the launcher and double-click Launch-Astraea.cmd when the Windows Python launcher is installed. Existing engine/source directories remain untouched. No automatic copying or search of unrelated directories occurs. The command invokes the official editor's `--main-pack` entry, so it does not need a whole project reimport. The package supplies Enter the ship, Resume, Settings and Quit and waits for real runtime readiness.

Controls: WASD/mouse, RMB focus, E interact, M directory, F10 pause, Esc pointer release, F3 internal resolution, F4 effects, F11 fullscreen. Settings persistence is in the package. The editor source matching this PCK is1091d34e; later Tidal court-finish source is separate. Earlier Windows walking crashes, this package's native Windows run, full gameplay and target60FPS remain unaccepted. This companion has source-level refusal/path checks; it has not been executed on Windows in this cloud environment.
