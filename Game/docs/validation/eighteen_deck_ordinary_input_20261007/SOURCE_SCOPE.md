# Eighteen-deck ordinary-input acceptance candidate

2026-10-07. ISOLATED, UNRUN. No engine launched; no Game files changed.

## Handoff

Root may review and adopt `validate_eighteen_deck_ordinary_input.gd` as a new test at `Game/tests/validate_eighteen_deck_ordinary_input.gd`, then schedule Godot through the existing fixed60 validation runner. Do not replace an old test or interpret this source review as a passing runtime result. The test writes only `artifacts/eighteen_deck_ordinary_input.json`. Its exact runner registration is deliberately left to root. Protect/retain input source per repository instructions before adoption. Keep failed receipts before any retry.

## What it establishes if it passes

- Starts from actual normal salon spawn (63,52.5,-20.5), no relocation fixture.
- Follows the reversed retained salon route, then east atrium perimeter and central-core bypass.
- Operates D09 landing call and every cabin destination using actual focused RMB/E rays.
- Walks out of the cabin at every one of 18 canonical floors, reaches the north spine, traverses the core's starboard bypass to Z−80, returns and physically reboards.
- Walks all seventeen central switchbacks down and up with the player's normal W-input physics, then returns by lift to D09 and walks back to default spawn.
- No position/velocity writes, `arrive_at`, direct `request_floor`, `move_and_slide`, `toggle_grab`, collision disable, or replacement geometry. View orientation alone is set for steering/aiming, as in the existing theater ordinary-input test.
- Samples real support and motion continuity every fixed60 frame, rejects fall/recovery jumps, checks normal player physics stays active and all lift gates remain shut during movement. Logs compact half-second support traces and milestone coverage.
- Verifies selected controller/contract/compiled-floor/test hashes unchanged across execution. Root should additionally freeze the full current source/import set using its established runner: this test's selected pins do not attest every visual/runtime asset.

This is bounded central-spine acceptance, not all destinations, every public/staff core, cart handling, tram, visual finish, species ergonomics, freehand comfort or GPU performance. It does not construct missing sections.

## Source evidence and exact gap

- `scripts/ship.gd` builds central `PRIMARY_ATRIUM_CORE`, forward −432, fore-midship −272, aft-midship +272, aft +432 cores, and aft-crown D17/D18 link at Z119.
- Central uses all eighteen datums and seventeen switchbacks; outlying cores stop at D17; aft crown gives another physical D17/D18 route. Shared `commons_lift.gd` is a real moving AnimatableBody3D with independent landing gates, bounded acceleration and interlocks, not transport teleportation.
- `validate_primary_core_stairs.gd` continuously moves the real capsule up/down, but disables normal player physics and directly uses inherited `move_and_slide`. Its bypass phase repositions once per deck.
- `audit_ship_backbone.gd` queries static capsule/support samples, rather than moving a player continuously.
- `validate_primary_core_lift.gd` inherits real RMB/E selection and physical cart carry from `validate_commons_lift.gd`, but begins already in the cabin. `validate_primary_core_boarding.gd` uses real W/S entry/exit yet directly invokes cart grab and lift request. Existing evidence is valuable; preserve it.
- `tests/validate_salon.gd` records the salon mouth route. `tests/validate_theater_stair_walk.gd` supplies the existing ordinary W-input steering/deceleration pattern reused here. New default-spawn connector and stitched landing loop remain runtime-unverified and may expose actual blockages. Failures must be investigated, never solved with teleporting or suppressing collisions.

## Remaining physical connections

- Tram is unimplemented runtime. The D09 bounded reservation is a planning hold only; it explicitly records conflicts with full axial alignment, station supports and boarding transfer still missing. Existing ±216 transit catchments differ from ±272 public cores by 56 m. Do not rewrite working lift/stair cores for a speculative tram.
- Fore/aft/midship core lateral walls are closed unless an actual documented receiving connection exists. Mere adjacent directory allocations are not entrances.
- D07 Movement Studio source portal at (8,35.5,−456) can receive via existing `D07_fore_route` rectangle X±4 / Z−530…−445 plus a new X4…8 branch, avoiding the forward core. This was sent to the section-map worker.
- Theater static shell and internal D11–D13 foyer stairs are distinct from its still-unaccepted local operating lift and external upper/staff interfaces. Source-only theater operating-door scripts must not be mistaken for instantiated systems.

## Authority / protected ownership

Datums from `data/design_contract.json`: 0,6,12,16.5,21,27,35.5,44,52.5,61,69.5,78,84,88.5,93,97.5,102,106.5 m. No alterations permitted by this candidate. `PRIMARY_ATRIUM_CORE.json` owns the enclosure, shaft, switchbacks and floors; compiler-owned floors, the theater, botanical openings, salon, and all live Team Lounge/botanical work remain untouched. Historical master implementation claims are superseded by `MASTER_CURRENT_APPLICATION.json` and inspected source, while master chapters4/5/7/28/32 govern spatial/travel acceptance.

## Bounded test operation

160,000 simulated frames maximum and 30-minute wall watchdog. These are failure limits, not expected durations or performance claims. At a failure the script emits a FAILED receipt with phase, support trace and last completed milestones, and exits nonzero. It never broadens routes or alters gameplay. Root owns engine execution and subsequent diagnosis/adoption.
