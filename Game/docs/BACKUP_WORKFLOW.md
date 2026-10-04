# Recoverable production checkpoints

1. Commit a meaningful tested change in the Godot source tree. Local Git alone is not disaster recovery.
2. Run `python3 tools/checkpoint_source.py --output /path/outside/project/checkpoint.zip --restore-check`. An optional `--since <verified ancestor>` reduces bundled history; all ordinary source files are still included. The tool refuses dirty source, existing destination files and unsupported tracked symlinks.
3. Check the receipt, the manifest hashes and the clean-restore log. The ordinary ZIP contains the full tracked source, a Git history bundle and usage instructions. Editable Blender sources and original design archives are separate packages.
4. Retain the ZIP through the supported Library upload workflow. Record the returned artifact ID and successful metadata result. This is independent of the current workspace, but is not proof that Workshop received it.
5. Copy to Workshop through a supported path and compare the file's SHA-256 to the receipt. Preserve previous checkpoints. If transfer is blocked, request the user's download into Workshop Downloads, then verify and file the copy after it arrives.

The receipt deliberately initializes independent retention and Workshop verification to false. Do not silently treat packaging, upload or remote availability as equivalent. Never package authentication directories, build caches, imported engine caches or another project's work. Only committed tracked source is selected.

The latest known Workshop verification remains the initial Godot baseline. Checkpoints10 and11 and the Blender22–24 additions are retained independently; the user has been asked to download checkpoint10 and the Blender additions. Do not issue another download request merely because a newer internal checkpoint exists.
