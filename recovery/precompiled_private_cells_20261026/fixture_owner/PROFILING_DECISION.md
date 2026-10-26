# Performance decision after run025

Goal1080p60 requires16.67ms/frame, not merely a draw-count reduction. Current603-frame wall median241.349ms/p95639.764ms fails. Run019254.440ms was only a17-frame pre-error window; run017237.077ms is a complete603-frame sample with residency/activation differences. Neither comparison establishes a repeatable FPS gain. No further cohort compilation is justified yet.

Measured: natural private batching engages, correct197-fixture owner and release lifecycle; short20m route passes. Counters: roughly49k finaldraws/5.54millionprimitives and over500knodes. These counters do not prove CPU versus GPU limitation. Old precompiled-bank fixture increased primitives; track geometry/GPU work, not just draws. Old2026-10-23 script/GPU results are historical, not current attribution; detailedGPUprofile suffered timestamp capacity errors.

Next one bounded fixed-camera current-ship attribution: original real Central boarding and same1920x1080Compatibility view,24-frame warmup,96samples of built-in viewport renderCPU/GPU/setup timers and process/physics monitors, plus --profiling script self/total timings. No full-tree scan or render-owner exclusion in sample loop. Record changing node/resource counts and mark unstable residency. Profiling/editor overhead is explicit; nested/asynchronously sampled categories must not be added or subtracted. No --gpu-profile detailed timestamp flood.

Decision gate: identify dominant category/owner before a production approximation or more compilation. Proposed change must preserve functional route collision, identities, editable originals and required views, show visual comparison for approximations, meaningful repeatable uninstrumented frame-time/tail benefit beyond variation, safe resource release/reactivation and no RID errors. Rollback remains selected aquatic baseline plus protected prior memory fixes; all experimental integration stays opt-in. Whole-route/loaded-cart/visual/Windows acceptance remains open.

RID errors at833/857 indicate where loading met pressure, not uniquely faulty assets. All-Resource count is not allocator-specific live count; freeRAM does not disprove a RID ceiling. Current short route has no RID error but is not whole-route proof. Distinguish retained ownership from growing leaks across release/return.

References: https://docs.godotengine.org/en/4.6/tutorials/scripting/debug/debugger_panel.html#visual-profiler ; https://docs.godotengine.org/en/4.6/classes/class_multimesh.html ; https://docs.godotengine.org/en/4.6/tutorials/performance/using_servers.html#rids
