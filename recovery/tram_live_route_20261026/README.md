# Selected aquatic ship: moving route remains blocked

Baseline cc1867017f969856ae2ef24b5faa6641df6970bf, actual Windows Godot 4.6.3 / Compatibility / 1920x1080 player camera. Run003 reached installed contact sweep, physical boarding and moving-route stages. No completed outbound/return result. The monitor stopped its own process on engine errors at 04:55:03 UTC (185.36 seconds after start), not on the RAM floor. No other game was terminated.

First error: Element limit reached, core/templates/rid_owner.h:132, during group2_completion/package.gd:18 load, through source_dispatch.ensure and received_homes residency._attach_visible_room. Null allocation and GLES3 mesh errors follow. Buffered log streams do not identify the exact first failing key or RID owner. The error count is not a live allocation count. Do not raise limits or infer GPU OOM.

Peak private14.254 GiB / resident12.152 GiB; minimum available RAM5.319 GiB. Last route sample:162 active received rooms,43578 active mesh nodes,38916 cached detached mesh nodes,632 deferred rooms,262871 resources,567001 nodes,79476 draw calls and7001414 primitives. Sampling process time0.718342s and physics0.091863s are single samples, not frame median/p95. No reliable route FPS result was finalized. Raw logs and external resource samples are preserved in run003.

The five nearby load sources 788/812/824/836/818 contain6620 mesh definitions but424 exact geometry payload groups across files. Retained source vertices/index/attribute bytes, layouts and primitive semantics were compared without tolerances; material assignments deliberately kept separate. Within each file,1252 geometry-plus-material-index groups remain, so arbitrary whole-mesh deduplication would change material ownership. This is evidence for investigating exact geometry/shadow sharing, not an implemented optimization or proof of the exhausted RID owner.

The focused check_shadow_representation.gd attempted to inspect one imported source without constructing a ship. Its initial invocation returned no result; a subsequent captured invocation produced signal11 with no useful native symbols and no result JSON. Both are finished; no process remains. Preserve shadow_stdout.log/shadow_stderr.log. Do not treat this as a successful ownership measurement or repeat unchanged. No production sharing patch has been applied.

The existing screenshot was pixel-inspected: a dark, obstructed cabin view, not useful wide architectural/guest-space acceptance. No separate render was launched.

Grand Arrivals architectural choice remains pending the owner's answer. No Arrivals geometry, rail, lift, baggage or capacity interpretation authored. Selected aquatic physical circulation remains previously passed; whole moving tram, loaded cart/capacity, guest-space visual completion, all-group completion and matching Windows release remain separate open gates. Existing Windows package has not been rebuilt.
