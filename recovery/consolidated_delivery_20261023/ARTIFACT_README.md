# Astraea integrated test package — 1091d34e

This package contains the complete selected construction source at 1091d34e914ad9c36f7ff487ed72e4d959a96886, including the launcher, main menu, settings, retained ship chain, Tidal D14 architecture and isolated private-contact single-pass repair. It is an unfinished test artifact, not accepted gameplay or a proven walking-crash fix.

## Restore without overwriting an existing build

Keep every .partNNN file, TRANSFER_MANIFEST.json and RESTORE_PACKAGE.py together. With Python 3.9+, run:

```text
python RESTORE_PACKAGE.py --verify-only
python RESTORE_PACKAGE.py --output Astraea-1091d34e-isolated
```

The utility verifies each part, the complete ZIP and decoded PCK. It refuses an existing output directory and creates no redundant joined ZIP. Allow 7,314,424,115 bytes for the decoded PCK, in addition to the downloaded parts.

## Runtime and controls

No Windows executable is included: the cloud does not have the official Windows export template, and its template metadata request was denied. This is not a standalone Windows release. Use the official Godot 4.6.3.stable.official.7d41c59c4 editor for your platform to open the PCK with `--main-pack Astraea-1091d34e.pck`; editor tools permit that option. An exported release runner may disable command-line path overrides, so do not assume the same invocation works with an older game EXE. A complete verified Windows assembly and actual native launch remain outstanding. No installation, credential or permission change is performed by this handoff.

The selected main presents Enter the ship, Resume, Settings and Quit. Movement remains gated on actual runtime readiness. Controls: WASD, mouse look, RMB focus, E interaction, M directory, F10 pause menu, Esc release pointer; F3 render resolution, F4 retro display effects, F11 fullscreen. Settings include internal resolution, effects, fullscreen, master volume and frame limit.

## Matching editable source

Private repository: https://github.com/evesloan/Astraea/tree/1091d34e914ad9c36f7ff487ed72e4d959a96886
Branch: construction/group1-tidal-d15-20261010. Preserve existing work and use this exact revision for comparison. Run PREPARE_EDITOR.py then PREPARE_EDITOR.py --check-only before opening Game/project.godot. SOURCE_MAP.md documents runtime hierarchy, native Blender ownership, master design and held experiments. Blender native sources remain in BlenderCatalogue and retained package directories; do not enable automatic .blend import.

## Verified and unfinished

The existing full project imported with exit 0 and no logged warnings/errors; import metadata remained byte-identical. The PCK passed all 17,571 exact source contracts, 13 Royalty pins, ten required Group 5 scene loads, nested-pack digest and selected-main checks. Its full ship was not instantiated by those checks. The private contact fixture preserved geometry/materials/collisions over three load/release cycles while eliminating the discarded first contact build. This is not target-hardware FPS evidence.

All eight groups and final architecture/material/visual acceptance remain unfinished. Queue, staged activation, prewarm and D04 batching experiments are not adopted. The walking crash and sustained 60 FPS remain open. Tram motion remains held by the D09/D10 clearance conflict. StarAtlas r002's externally retained 114-part candidate is not included because consumer materialization was denied; existing Star Atlas living construction is retained. The unpublished October 20 08:49 UTC WIP/tram intro source has not been recovered. Comparison-held Sequoia has not been adopted.

Final export-log review found ten editor dialog-ownership errors despite exit0; packaged-byte checks passed, but full exported-runtime acceptance remains open. See `recovery/consolidated_delivery_20261023/EXPORT_DIAGNOSTICS.json` and `LATE_VALIDATION_NOTES.md`.
