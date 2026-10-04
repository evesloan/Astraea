# Fast current-project validation

Run `python3 tools/validate.py` for the full current suite. Run `python3 tools/validate.py --only arrivals_fusion` for that focused check plus import refresh. A focused pass never substitutes for the full suite.

Headless simulation checks use Godot's supported `--fixed-fps 60` option. It disables real-time synchronization while preserving the established60Hz physics timestep and time scale1. Assertions, input fixtures, motion/contact queries, frame budgets and error rejection remain unchanged. Baseline validation checks the physics rate and time scale explicitly.

Use `--realtime` to retain the previous wall-clock synchronized mode, for example `python3 tools/validate.py --only arrivals_fusion --realtime`. Graphical captures and target-machine play checks are separate and retain their existing timing. Faster headless assertions do not establish graphics performance, real input latency or visual acceptance.

The runner retains full check records and per-check wall times in `artifacts/validation_<selection>_<mode>.json`, with the existing latest-result file preserved for compatibility. Console output ends with a compact summary instead of repeating the complete result array.

## Paired observation
On4 October2026, the same arrivals traversal/screening test passed in53.657seconds with real-time synchronization and3.9753seconds with fixed60 simulated time. The full29-check fixed60 run passed in52.9847seconds including import. This is one observation on the cloud CPU, not a statistical or target-GPU benchmark. See VALIDATION_CLOCK_COMPARISON.json for source hashes and scope.
