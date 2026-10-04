# Backup transition to private GitHub

The current private GitHub publisher and recovery procedure are documented in GITHUB_BACKUPS.md. Inspect the active runtime receipt before deciding which watcher is operating. The Library process below remains a historical fallback until the GitHub watcher and clean retrieval have been verified; never run competing publishers against one mirror. Retained Library checkpoints are not deleted.

# Automated source protection

## Coverage
- A post-commit hook requests an independently retained checkpoint after a commit in either the Godot project or Blender catalogue
- A session-scoped watcher also snapshots changed work every15minutes, including eligible uncommitted source and newly authored assets
- Unchanged work is skipped. Both projects are checked independently
- Each portable snapshot has per-file hashes, a ZIP-integrity check and explicit committed/work-in-progress status
- The archive is considered retained only after the official Library upload workflow reports success and local identity metadata is applied for every part
- Earlier checkpoints are never automatically deleted

This bounds normal uncommitted-work exposure to roughly15minutes while the watcher and connection are healthy; a reset during an upload can leave the previous verified checkpoint as the recovery point. It does not promise zero loss, continuous execution after a cloud reset, or a functioning Workshop transfer.

## What is packaged
The Godot checkpoint contains the current portable production tree. The Blender checkpoint contains editable source, exports, materials, builders and production metadata. Historical catalogue QA/reference files remain in the independently retained Git baseline and design/reference archives; committed changes to them are preserved in the Git delta. Modified uncommitted QA files are included too. Engine caches, generated import caches, credentials and unrelated folders are excluded. Each snapshot records the retained history baseline; portable source can be used without restoring Git.

Source files are copied to a stable staging tree before archiving. If source changes while it is being staged, the attempt waits for another pass without uploading that snapshot. Upload failures or uncertain outcomes stop further automatic writes until the result is reviewed. No blind retries, no silent success, no credential creation or credentials saved in this repository.

## Session startup and recovery
1. Obtain the current official Library upload helper and companion files through its supported skill workflow into a private temporary directory; do not vendor or modify them
2. Run tools/backup/configure_session.py with the actual conversation workspace and fresh helper path. It uses the verified retained_baselines.json and refuses to overwrite an existing session configuration. Check both restored project roots and histories first
3. Run the backup unit tests, inspect the existing hooks, and install only the managed post-commit hooks. Existing unrelated hooks are preserved and reported
4. Run a real retention pass and inspect every returned file result before calling the service active
5. Start the watcher in a live foreground execution session or cloud desktop terminal, and verify its heartbeat advances across separate checks. A detached process from a one-shot command may be terminated when the command ends. Keep failure monitoring separate from the cloud process

The watcher and Git hooks are session machinery: a cloud reset can remove them. Restore source from the newest complete retained checkpoint, verify hashes/tests, then re-arm the watcher before production edits resume. Never infer that an old runner file proves a live process.

## Failure and recovery review
The runtime state and logs are outside the source trees. Status must distinguish packaging, uploading, waiting for stable source, healthy and blocked. Preserve any partially retained artifact IDs and do not re-upload an uncertain batch automatically. Resolve the outcome before clearing a blocked state. Local ZIP creation alone is not independent retention; Library retention is not Workshop verification.

Workshop remains a second backup layer. Its automatic transfer is presently blocked, so local copies need separate download/hash verification. A read-only periodic health check may report a stopped service, uncovered source or a partial checkpoint; it must not start competing writers or silently alter backup permissions.
