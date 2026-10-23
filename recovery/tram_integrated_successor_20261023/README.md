# Tram section and repeated-passenger-route source package

This is a compact prepared source package, not an implemented scenic ride. The original integrated tram remains physically and operationally held. No production geometry, vehicle/passenger pose, collision mask, admission flag, room policy, motor, existing test or protected datum changed. No engine/import/build/export or publication was launched by this helper. The integration owner alone ran the bounded protocol check.

## Physical section result

`SECTION_OPTIONS.json` is reproduced by `python section_options.py`. It reads the retained section interface, actual D10 bearing identities and current source024 car GLB. Its source arithmetic is not an engine clearance result.

- Protected D09 test volume: Y52.55–56.55. Current soffit55.55, rail55.74 and boarding56.10 leave only3.05m above the D09 floor52.5.
- With10mm separation, clearing that unchanged lower test requires +1.01m: soffit56.56, rail56.75 and boarding57.11.
- Keeping the recorded upper4m running band then requires top61.11, which exceeds the actual D10 receiving underside60.76 by0.35m. Raising the original header with the rails makes its top61.51,0.75m too high. Removing a web or shaving a support cannot resolve both bands.
- The exact car GLB roof is2.869999886m above its local floor, so that raised car would top out59.98. Keeping the old header60.18 would leave0.20m above the body but only3.07m above boarding. This is explicitly **not selected** because it reduces the recorded upper4m clearance.
- A straight lateral separation needs at least3.75m before margin:2m reservation radius plus1.75m web half-width. This is only a geometric lower bound, not a verified corridor. Shoes, curvature, body swing, platforms/lifts and receiving owners need coordinated redesign. The governing six-point bypass remains protected, and the earlier alternative screen explicitly did not certify a replacement or complete adjacent receiving volume.

The next physical gate is a complete legal section/receiving design that preserves both criteria and occupied neighbours. No further permission is presumed merely for design work, but no compliant corridor is established by the retained bounded evidence. The original north physical dock(-5.6,56.1,-241) and directory catchmentZ-216 remain distinct. Existing cart caster/joint admission is also still held. Do not enable movement based on this package.

## Prepared route observer

`route_profile.gd` is an opt-in Node attached to the actual existing ship after runtime_ready. It uses only the retained operating controls and single loaded actuator, and requires the original passenger to have physically boarded. It never positions/reparents the passenger, changes their physics, changes a camera, invokes apply_pose, changes admission, or creates another motor.

The route is CENTRAL → AFT_MIDSHIP → CENTRAL → FORE_MIDSHIP → CENTRAL, repeated twice by default. This crosses the retained central bypass and both adjacent promenade approaches; it does not claim a complete terminal-to-terminal scenic tour or proven amenity sightlines. It waits the safety controller's existing15 stationary frames before querying each physical dock, and waits12seconds at docks/final return so the existing8-second residency grace can expire. The current real assembly must return BLOCKED at configuration because its admission flags are false.

Once the physical integration gates genuinely pass, the sole engine owner can attach this script to a new Node in the existing scene and call:

```
observer.configure(actual_ship, unique_jsonl_path, exact_source_revision, 2, false, Vector2i(1920,1080))
```

The actual internal viewport must match the requested size. It records the current camera transform/FOV rather than inventing a view or locking the player. Use the same real boarding stance, camera, settings and route for comparisons. Cancellation stops observation and future departure requests; it leaves the existing motor's current target and all normal controls intact. It does not terminate the game. The profile has a30-minute ceiling and refuses output overwrite.

Frame records contain real-clock intervals, built-in process/physics monitors, visible/shadow submissions, primitive counts, nodes/resources, static memory and exact car/passenger/camera state. Once per second it records the existing received/private/contact manager counters and exact entered/departed room identities. There is no repeated whole-tree scan or unbounded in-memory sample array. Observer overhead is recorded. JSONL is flushed each second so an interruption retains prior evidence.

Optional viewport CPU/GPU timing uses documented Godot4.6 RenderingServer methods. It is off by default and requires exclusive ownership of that viewport's measurement switch; enabling it does not imply valid GPU measurements. CPU render excludes script/physics time; zero GPU time is unavailable, not free. OS static allocation and Resource counts are not process RSS/private RAM or allocator-specific live RID counts. Keep external memory/crash records and built-in script profiling alongside this stream.

Official API reference: https://docs.godotengine.org/en/4.6/classes/class_renderingserver.html#class-renderingserver-method-viewport-get-measured-render-time-cpu

`summarize.py existing.jsonl --output unique-summary.json` produces per-cycle/leg/phase median,p95,p99 and settled CENTRAL resource deltas. No causal performance win,60FPS claim, repeated-route plateau or crash fix is inferred automatically. Camera/content/source/settings traces must agree before an A/B comparison. Target-hardware acceptance cannot come from cloud software rendering.

## Validation and boundary

-12 production preimages match independently retained47dbba2b. All four route destinations remain in the original safe source cursor range. Static checks confirm no actor/car/admission override and correct stationary-witness ordering.
- Root ran `check_protocol.gd` once: PASS8 protocol checks. The check uses synthetic empty ownership nodes only. It verifies parseability and fail-closed admission logic, not moving-vehicle, passenger, collision, visual or performance behavior.
- The section calculator initially rejected mixed D09/D10 receiver rows and transformed non-mesh markers. The final version explicitly selects named D10 receivers and checks geometry-bearing GLB nodes/ancestors. No source input changed to satisfy it.
- No full tram run, build, renderer capture or new geometry was performed. Missing unpublished October20 tram-intro source is not recovered or patched by this new observer.

`PACKAGE_MANIFEST.json` hashes every file except itself. Preserve this prepared boundary; root owns adoption/publication and engine checks. The previous clearance review remains unchanged.
