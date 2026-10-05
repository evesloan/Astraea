import copy
import unittest

from plan_d17_connected_platform import digest, plan


class FloorPlannerTests(unittest.TestCase):
    def setUp(self):
        self.layout = {'regions': [{'id': 'old', 'deck': 'D17', 'boundary': [[0,0],[3,0],[3,14],[0,14]], 'holes': [], 'priority': 65}], 'voids': []}
        self.contract = {'floor_regions': [{'id': 'apron', 'floor_y': 102, 'thickness': .24, 'boundary': [[0,13.2],[3,13.2],[3,25.5],[0,25.5]]}]}
        self.levels = {'D17': 102, 'D18': 106.5}

    def run_plan(self, layout=None, contract=None, expected=None):
        source = self.layout if layout is None else layout
        return plan(source, self.contract if contract is None else contract, self.levels,
                    digest(source) if expected is None else expected)

    def test_existing_seam_not_duplicated(self):
        result, report = self.run_plan()
        self.assertAlmostEqual(report['existing_floor_overlap_m2'], 2.4)
        self.assertAlmostEqual(report['new_floor_m2'], 34.5)
        self.assertEqual(result['regions'][0], self.layout['regions'][0])

    def test_overlapping_proposed_strips_union(self):
        c = copy.deepcopy(self.contract)
        c['floor_regions'].append({'id': 'cross', 'floor_y': 102, 'thickness': .24, 'boundary': [[0,22.5],[15.5,22.5],[15.5,25.5],[0,25.5]]})
        _, report = self.run_plan(contract=c)
        self.assertAlmostEqual(report['candidate_overlap_removed_m2'], 9)
        self.assertAlmostEqual(report['new_floor_m2'], 72)

    def test_protected_void_is_preserved(self):
        self.layout['voids'] = [{'id': 'opening', 'decks': ['D17'], 'boundary': [[1,20],[2,20],[2,22],[1,22]]}]
        result, report = self.run_plan()
        self.assertAlmostEqual(report['new_floor_m2'], 32.5)
        self.assertEqual(result['voids'], self.layout['voids'])
        self.assertEqual(len(result['regions'][-1]['holes']), 1)

    def test_absolute_elevation_ownership(self):
        self.layout['regions'][0].update(deck='D18', offset_y=-4.5)
        _, report = self.run_plan()
        self.assertAlmostEqual(report['new_floor_m2'], 34.5)

    def test_changed_substrate_rejected(self):
        original = digest(self.layout)
        self.layout['regions'][0]['boundary'][2][1] = 15
        with self.assertRaises(AssertionError):
            self.run_plan(expected=original)

    def test_input_not_mutated(self):
        before = copy.deepcopy(self.layout)
        self.run_plan()
        self.assertEqual(before, self.layout)

    def test_repeated_planning_is_idempotent(self):
        first, _ = self.run_plan()
        second, _ = self.run_plan(layout=first, expected=digest(self.layout))
        self.assertEqual(first, second)

    def test_existing_compiler_id_collision_rejected(self):
        self.layout['regions'][0]['id'] = 'D17_connected_house_floor_00'
        with self.assertRaises(AssertionError):
            self.run_plan()

    def test_wrong_datum_or_slab_rejected(self):
        for key, value in [('floor_y', 106.5), ('thickness', .5)]:
            c = copy.deepcopy(self.contract)
            c['floor_regions'][0][key] = value
            with self.assertRaises(AssertionError):
                self.run_plan(contract=c)


if __name__ == '__main__':
    unittest.main()
