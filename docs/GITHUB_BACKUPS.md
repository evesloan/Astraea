# GitHub checkpoint protection

Destination: private https://github.com/evesloan/Astraea

## Layout and evidence
- main contains Game/, BlenderCatalogue/ and DesignArchive/; the latter preserves313 retained design/reference files
- source/godot and source/blender preserve the separate original production histories
- CHECKPOINT.json records source heads, changed-work status and per-file SHA-256 hashes for each managed production tree
- The initial clean network clone matched8473 files; three historical Blender editor autosaves are excluded from main but retained in the original source history
- Files are source checkpoints, not release builds or proof of final quality

## Routine
The publisher checks local state every15 seconds. A changed source commit is eligible immediately; changed uncommitted work is eligible every15 minutes. Unchanged work creates no commit. Source is copied into a separate mirror, checked for stability and hashed before publication. Workspaces are never reset, cleaned or rewritten by the publisher.

Before each push, the destination identity and private visibility are checked. Main must still equal the last verified remote commit. Main and source-history branches are pushed atomically without force. The returned remote main SHA must match the intended checkpoint. Transport uncertainty is resolved by reading the remote before any retry; a mismatch, unexpected remote edit, credential-like file, oversized file or genuine failure stops publication and records a blocker. Normal concurrent source edits defer to a later stable pass.

Authentication is outside the project and all backup scopes. No credentials belong in source, archives or CHECKPOINT.json. No paid storage or LFS subscription has been enabled. Files over95MiB stop publication for a storage review rather than being silently omitted. Repository growth must be reviewed before large future asset batches.

## Recovery and limits
Clone the private repository into an empty directory, verify CHECKPOINT.json file hashes, then open Game/project.godot with the pinned engine. BlenderCatalogue contains editable sources. To retain separate histories, use source/godot and source/blender branches and overlay any explicitly marked WIP snapshot. DesignArchive includes historical documents whose implementation claims must not be mistaken for the current rebuild.

Cloud reset can remove the running publisher and its sign-in. Remote checkpoints survive independently; credentials must be re-established through an approved sign-in. An hourly independent read-only check looks for confirmed protection failures. Inactivity or an old-but-current checkpoint alone is not failure.

Older Library checkpoints remain retained. Automatic Workshop copies remain unverified. Do not claim zero-loss guarantees, perpetual execution or hardware performance validation.

## Publisher lifetime and reviewed recovery
A single publisher is now hosted in a named foreground terminal on the cloud desktop, following the existing graphical-review runner's lifetime pattern. Its lock and fresh heartbeat must still be checked; an open terminal or stale healthy receipt is not evidence of current protection. Never start another publisher while the lock is owned.

If a publisher has exited, first compare private destination identity, remote main, clean mirror HEAD and any pending upload. A bounded invocation of the same publisher is a permitted recovery path only after confirming no writer remains and resolving the recorded blocker. Do not reset a blocked state merely to retry. Unknown or divergent upload outcomes still stop publication.

New launches from this revision record the checking-remote stage and classify external command failures without retaining raw stderr or command arguments. Ten publisher unit tests cover the existing safety checks plus sanitized authentication/transport diagnostics. This does not change credentials, repository permissions, retention cadence or the no-force-push policy. Long-running operation remains subject to actual verification and cloud-session availability.
