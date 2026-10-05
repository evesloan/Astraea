import copy,json,unittest,tempfile,subprocess,shutil,os
from pathlib import Path
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from author_bridge_platform import plan_floors,OWNER
R=Path(__file__).resolve().parents[1]
class BridgePlatformPlan(unittest.TestCase):
    def setUp(self):
        self.layout=json.loads((R/'data/spatial_layout.json').read_text())
        self.layout['regions']=[r for r in self.layout['regions'] if r.get('authoring_owner')!=OWNER]
        self.brief=json.loads((R/'data/architecture/BRIDGE_PLATFORM_CONSTRUCTION.json').read_text())
    def test_preserves_existing_owners_and_voids(self):
        before=copy.deepcopy(self.layout);result=plan_floors(self.layout,self.brief)
        self.assertEqual(self.layout,before)
        self.assertEqual([r for r in result['regions'] if r.get('authoring_owner')!=OWNER],before['regions'])
        self.assertEqual(result['voids'],before['voids'])
    def test_three_components_and_net_areas(self):
        rows=[r for r in plan_floors(self.layout,self.brief)['regions'] if r.get('authoring_owner')==OWNER]
        self.assertEqual(len(rows),3)
        self.assertEqual(sorted(round(Polygon(r['boundary']).area,6) for r in rows),[1096,1692,1692])
        self.assertAlmostEqual(unary_union([Polygon(r['boundary']) for r in rows]).area,4480)
    def test_existing_spine_never_duplicated(self):
        rows=[r for r in plan_floors(self.layout,self.brief)['regions'] if r.get('authoring_owner')==OWNER]
        for r in rows:self.assertAlmostEqual(Polygon(r['boundary']).intersection(box(-4,-530,4,-80)).area,0)
    def test_infill_never_supersedes_existing_owner(self):
        result=plan_floors(self.layout,self.brief)
        old=[r for r in self.layout['regions'] if r['deck']=='D18' and abs(r.get('offset_y',0))<1e-6]
        added=[r for r in result['regions'] if r.get('authoring_owner')==OWNER]
        for new in added:
            for existing in old:self.assertLessEqual(new['priority'],existing.get('priority',0))
    def test_compilation_preserves_every_existing_region(self):
        # A source-record comparison cannot detect GEOS-induced retriangulation.
        with tempfile.TemporaryDirectory(prefix='astraea-infill-') as temp:
            root=Path(temp)
            for folder in ['tools','data/generated','docs']:(root/folder).mkdir(parents=True,exist_ok=True)
            shutil.copy2(R/'tools/compile_layout.py',root/'tools/compile_layout.py')
            shutil.copy2(R/'data/design_contract.json',root/'data/design_contract.json')
            def compile_rows(layout):
                (root/'data/spatial_layout.json').write_text(json.dumps(layout))
                subprocess.run(['python3',str(root/'tools/compile_layout.py')],env=os.environ,check=True,capture_output=True,text=True)
                return {r['id']:r for r in json.loads((root/'data/generated/structural_meshes.json').read_text())['regions']}
            before=compile_rows(self.layout)
            after=compile_rows(plan_floors(self.layout,self.brief))
            self.assertTrue(before)
            self.assertEqual({key:after[key] for key in before},before)
    def test_idempotent(self):
        first=plan_floors(self.layout,self.brief);self.assertEqual(first,plan_floors(first,self.brief))
    def test_changed_substrate_rejected(self):
        self.layout['regions'].append({'id':'unexpected_bridge_floor','deck':'D18','boundary':[[-22,-152],[-20,-152],[-20,-150],[-22,-150]]})
        with self.assertRaises(AssertionError):plan_floors(self.layout,self.brief)
    def test_protected_void_rejected(self):
        self.layout['voids'].append({'id':'unexpected_bridge_void','decks':['D18'],'boundary':[[-22,-152],[-20,-152],[-20,-150],[-22,-150]]})
        with self.assertRaises(AssertionError):plan_floors(self.layout,self.brief)
if __name__=='__main__':unittest.main()
