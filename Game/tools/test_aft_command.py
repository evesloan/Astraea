import copy,json,unittest
from pathlib import Path
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from author_aft_command import floor_extension,OWNER
ROOT=Path(__file__).resolve().parents[1]
class AftCommandFloorTests(unittest.TestCase):
    def setUp(self):
        self.original=json.loads((ROOT/'data/spatial_layout.json').read_text())
        self.original['regions']=[r for r in self.original['regions'] if r.get('authoring_owner')!=OWNER]
    def test_preserves_every_existing_region_and_void(self):
        before=copy.deepcopy(self.original);new=floor_extension(self.original)
        self.assertEqual(before,self.original)
        self.assertEqual([r for r in new['regions'] if r.get('authoring_owner')!=OWNER],before['regions'])
        self.assertEqual(new['voids'],before['voids'])
    def test_exact_missing_area_and_two_components(self):
        rows=[r for r in floor_extension(self.original)['regions'] if r.get('authoring_owner')==OWNER]
        self.assertEqual(len(rows),2)
        union=unary_union([Polygon(r['boundary']) for r in rows])
        self.assertAlmostEqual(union.area,1408)
        self.assertAlmostEqual(union.intersection(box(-4,80,4,102)).area,0)
    def test_idempotent(self):
        first=floor_extension(self.original);self.assertEqual(first,floor_extension(first))
    def test_changed_existing_substrate_rejected(self):
        altered=copy.deepcopy(self.original)
        altered['regions'].append({'id':'unexpected','deck':'D18','boundary':[[10,82],[12,82],[12,84],[10,84]]})
        with self.assertRaises(AssertionError):floor_extension(altered)
    def test_protected_opening_rejected(self):
        altered=copy.deepcopy(self.original)
        altered['voids'].append({'id':'unexpected_opening','decks':['D18'],'boundary':[[10,82],[12,82],[12,84],[10,84]]})
        with self.assertRaises(AssertionError):floor_extension(altered)
    def test_public_cross_street_is_existing_substrate(self):
        existing=unary_union([Polygon(r['boundary'],r.get('holes',[])) for r in self.original['regions'] if r['deck']=='D18'])
        belt=box(-48,60,48,66)
        self.assertAlmostEqual(belt.area,576)
        self.assertAlmostEqual(belt.difference(existing).area,0)
if __name__=='__main__':unittest.main()
