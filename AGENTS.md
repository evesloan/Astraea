# Astraea production continuity

Use the existing Godot project and its current design contract. The ship is unfinished; preserve room identities, protected allocations, deck datums and working interactions. Catalogue presence counts do not establish completed rooms or final art acceptance.

Before production edits, inspect docs/CURRENT_STATUS.md, docs/AUTOMATED_BACKUPS.md and docs/GITHUB_BACKUPS.md and the current backup service status. Verify the watcher is running and independent retention has actually succeeded. A cloud reset may remove hooks and the watcher even when source has been restored. Re-arm it through the supported current Library workflow before continuing substantive edits. Do not store credentials or vendor modified transfer helpers.

Commit meaningful verified changes. The GitHub watcher observes new commits every15seconds and changed WIP every15minutes. Check the resulting retention receipt; a commit and a local ZIP are not independent backups. Respect a blocked/uncertain upload state and investigate before further automatic writes. Preserve earlier checkpoints.

Use tools/validate.py for the full Godot check suite; focused --only runs are not full validation. Inspect actual in-engine views for architectural/visual changes. Preserve editable Blender sources alongside optimized runtime exports. See docs/WHOLE_SHIP_SECTION_COORDINATION.md for section-first planning and protected programme boundaries.

Focused validation now refreshes Godot imports before its requested check. A revised GLB can otherwise leave new marker lookups testing stale imported geometry. Treat any such failure as a real failed attempt, refresh imports, and rerun against the final source.

The authoritative version0.3 master is retained under docs/master_source. Consult MASTER_CURRENT_APPLICATION.json and the relevant complete chapter blocks in MASTER_FULL_CONTENT_INDEX.json before system/district work; the original DOCX and all33 chapters remain governing context. Its October1 implementation claims are historical. Latest species, luxury/admission, shared-room, controls and grand-arrivals decisions are explicit overlays, not reasons to discard the rest of the document. Reopen the relevant reference images for each architecture/material/lighting pass; an image being archived is not proof it was used in review.
