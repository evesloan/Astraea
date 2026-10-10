from pathlib import Path
import json
W=Path(__file__).resolve().parent
refined=json.load(open(W/'PLAN.json'))
assert refined['aquatic_circulation_refinement']['structural_parts_unchanged']
assert refined['all_twenty_allocations_unchanged']==json.load(open(W/'attempt04_connected_aquatic_rim_route/PLAN.json'))['all_twenty_allocations_unchanged']
assert [r['source_index']for r in refined['rooms']]==[976,988]
print('REFINED_PLAN_RETAINED; use PLAN.json as exact authoring input, not the superseded initial generator')
