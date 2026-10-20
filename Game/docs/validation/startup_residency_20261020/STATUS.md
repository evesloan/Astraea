# Startup residency repair WIP — not a repaired release

Original runtime scripts, original scenes, source GLBs, design gates and D04 original builders are unchanged. No default main-scene hook has been changed.

127 source-preserving exact visual/contact derivatives are prepared: seven audited laundry/night-table/crew sources and120 D04 private room sources. All pass independent exact transformed-contact byte comparisons, visual triangle counts and relevant imported light/glass ancestry checks. Laundry, night-table and a representative private room pass49 physics-ray comparisons and ten exact-contact load/free cycles with stable memory and unchanged visual/light identities. Full geometry remains visually resident; opaque contacts load/free by full cell AABB. Transparent contacts retain mesh/material ancestry for unchanged lighting visibility tests.

Two guarded whole-ship candidate runs still FAILED to reach readiness within5GiB RSS. Seven-model candidate stopped at5128MiB after botanical pair;127-model candidate stopped at5168MiB after Sunset. Both had zero engine/assertion errors. This is partial allocation reduction, NOT a complete startup repair.

An additive staged ship/bootstrap/presentation successor has since been added and parses successfully, but has not run yet. Bootstrap waits for an explicit construction_finished signal, original deferred builders are preserved in original order until bootstrap completion, gameplay remains paused until explicit runtime_ready, and loading progress remains visible. Original Node.ready is not treated as complete construction. New scenes are candidate-only.

Next: staged bounded diagnosis/readiness, extend appropriate exact residency at measured bottlenecks, offscreen source/baked pixel comparison, complete ready/region transition evidence, then parent retention/export. Do not publish as a repaired build before that evidence exists.

Rejected first laundry save used broken bundled material references; failure logs and hashes retained, disposable rejected outputs removed after valid r002 successor verification. Original source remains intact. First r002 attempts failed on invalid grow_enabled and nullable indices; these logs remain and final corrected outputs have clean checks.
