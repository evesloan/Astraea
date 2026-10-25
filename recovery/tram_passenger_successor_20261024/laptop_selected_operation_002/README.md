# Selected tram operation 002 — allocation safety stop

Tested source: `7182a3676a245a9c3a860881f7f54dd59e081ba5`, retained official Godot 4.6.3, Windows Compatibility, 1920x1080 internal resolution. No production admission flags were enabled. The test's temporary boarding/motion permissions were confined to its process.

The corrected test waited for fully open station and vehicle gates. The selected world reached boarding, onboard secure and moving-route stages. It did not complete the outbound/return acceptance. The monitor stopped its own process on engine errors at 22:21:26 UTC; no engine remained running on the subsequent CIM check. This was a controlled forced stop, not proof of OOM or a native crash. Peak private memory was 14.036 GiB; resident 11.926 GiB; minimum available RAM 5.984 GiB.

First error: `Element limit reached`, `_allocate_rid (./core/templates/rid_owner.h:132)`. GDScript context is `group2_completion/package.gd:18` (loading a retained GLB), called by `received_homes_20261015/source_dispatch.gd:13`, `residency.gd:88`, `_process:81`. The stderr contains 444 allocation-limit errors, 444 null-memory errors, 1,628 null-mesh errors and 147 own-shadow-mesh errors. The latter errors follow allocation failure; they do not establish independent geometry defects.

Eight route samples are preserved in EVIDENCE.json. From first to last, active received rooms rose 80→161, resources 234,085→261,732, draw calls 36,916→79,334 and nodes 555,679→597,031. Private interiors reached 69 loads/11 releases/58 residents. At the last sample, received rooms had 42,254 reported active meshes and 98 pending visible activations. Statistics named cached_detached_meshes count node inventory, not proven live mesh resources. The preceding lease correction releases detached source meshes; it does not bound the simultaneously visible working set.

The last printed loads include 812,824,836,788,818. Most of these individual retained GLBs contain 1,324 meshes. Separate stdout/stderr buffering prevents assigning the first allocator failure to one exact key; 824 is a correlation, not a proven first failing source. Total Resource count is not an exact per-owner RID count. The generic allocator backtrace does not identify the exhausted owner. Do not increase limits, suppress errors, or delete required rooms to pass.

No result.json was produced. Frame intervals accumulated in the test process were not flushed before the stop; therefore no median/p95 or completed return/settling result is available. No 60 FPS claim. Raw logs and external samples are unchanged and individually hashed in EVIDENCE.json.

`central_aboard_actual.png` is an actual player-camera capture from this run, inspected at 1920x1080. Heavy pale vertical framing and narrow dark teal apertures dominate the view. Some surrounding atrium is visible, but this is not a useful wide grand-space view and does not pass scenic acceptance. It is evidence of the current view obstruction, not concept art.

Next resource work must reduce exact live source representation cost, preserving all authored geometry/materials, contacts, controllers and persistent IDs; validate focused equivalence before another warranted full run. No unchanged rerun or new export was started after this stop.
