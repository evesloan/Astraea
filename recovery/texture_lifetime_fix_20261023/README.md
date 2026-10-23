# Texture interner resource-lifetime fix

Source-only successor for the repaired eb11381c delivery payload. Frozen deliverable and all earlier revisions remain unchanged. This does NOT establish that the user's walking crash is fixed.

## Proven source defect and bounded repair

The original exact_texture_intern.gd holds strong Texture2D references in both canonical[key] and textures[id].shared. Its pruning removes expired original lookup/material references but never prunes canonical. Consequently a unique texture survives after the last live material/room owner releases it. This is retained resource ownership, not merely an expired weak-reference key.

The successor uses weak references in BOTH cache locations, resolves them before reuse, re-interns when a shared target has expired, and prunes dead canonical/lookup entries. Active materials remain strong resource owners. Complete pixel hash, texture class, dimensions, format, mipmaps and alpha checks are unchanged. No resizing, visual detail loss, material value changes, geometry changes, renderer switch or residency rewrite.

Focused Godot4.6.3 test: original keeps the texture and one canonical/lookup entry after last owner release; successor releases it and leaves zero entries. Live material ownership and identical-payload sharing remain valid. Different pixel payloads remain distinct. One hundred churn cycles leave no entries. This was an isolated resource test, not a full ship launch or FPS benchmark. Actual user's crash causality and target performance remain unproven.

## Apply through the sole laptop owner

`python apply.py --repo PATH` verifies every preimage and payload; `--apply` backs up originals under `.astraea-delivery-backups/texture-lifetime-20261023`, refuses mismatches and verifies results. It launches nothing. PATCH.json supplies both file hashes. The source manifest adds the interner's exact bytes so the existing export mechanism carries this successor into a rebuilt artifact. No transitive current-source pin refers to the previous interner hash; historical archives remain untouched.

Coordinate the exact immutable patched boundary with the laptop owner after preserving user crash logs. Do not run a competing cloud build/import. Compare loaded rooms, live/cache texture resources, memory and activation durations along the same walking route. Lower cache ownership alone does not prove playable60FPS or resolve native-crash causality.

## Other lifecycle findings — not silently changed

- Private/D04 details free their detail node, clear entry.detail and prune weak collision entries after visibility/proximity holds expire; no detached detail cache is held by those managers. Their visibility and refresh paths can load multiple entries synchronously without a shared activation-time budget.
- Ordinary deferred_home_visual.release frees the visual. Retained Group2 source_dispatch.release detaches and caches the visual to preserve controllers/state. Room nodes themselves are retained by the received-room manager. This intentional bounded retention must not be mistaken for all ordinary interiors leaking.
- Received-room deferred visibility attachment does not recheck current screen visibility, unlike private detail loading; stale callbacks can reattach until the next hidden grace expires. No callback fix is bundled with this texture patch.
- Detached rooms leave the live SceneTree; lighting_budget skips out-of-tree lights. Ranking still scans the registered sources every0.2s. Persistent public architecture/controllers remain active by design; no offscreen behavior has been removed.
- Exact contact residency frees bodies or clears shape references. Static contact and adopted-contact caches are weak. Exact contact verified hashes are a path/bool table. Texture pending mesh references are weak and flushed every process frame after readiness, so that queue is not a demonstrated permanent texture owner.
- No measured memory trajectory, user crash stack or cause is inferred from these code findings. Laptop evidence remains the authority for reproduction.
