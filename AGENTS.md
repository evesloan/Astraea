# Astraea production continuity

Use the existing Godot project and its current design contract. The ship is unfinished; preserve room identities, protected allocations, deck datums and working interactions. Catalogue presence counts do not establish completed rooms or final art acceptance.

Before production edits, inspect docs/CURRENT_STATUS.md, docs/AUTOMATED_BACKUPS.md and the current backup service status. Verify the watcher is running and independent retention has actually succeeded. A cloud reset may remove hooks and the watcher even when source has been restored. Re-arm it through the supported current Library workflow before continuing substantive edits. Do not store credentials or vendor modified transfer helpers.

Commit meaningful verified changes. The managed post-commit hook requests protection automatically. Check the resulting retention receipt; a commit and a local ZIP are not independent backups. Respect a blocked/uncertain upload state and investigate before further automatic writes. Preserve earlier checkpoints.

Use tools/validate.py for the full Godot check suite; focused --only runs are not full validation. Inspect actual in-engine views for architectural/visual changes. Preserve editable Blender sources alongside optimized runtime exports. See docs/WHOLE_SHIP_SECTION_COORDINATION.md for section-first planning and protected programme boundaries.

Focused validation now refreshes Godot imports before its requested check. A revised GLB can otherwise leave new marker lookups testing stale imported geometry. Treat any such failure as a real failed attempt, refresh imports, and rerun against the final source.
