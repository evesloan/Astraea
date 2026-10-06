"""Engine-free negative controls: mount, route, aperture and preservation fail closed."""
import copy,json,tempfile,unittest
from pathlib import Path
from check_wayfinding import screen,HERE
from wayfinding_geometry import dump,local_box

class SourceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.original=json.loads((HERE/'wayfinding_contract.json').read_text())
    def run_candidate(self,d):
        with tempfile.TemporaryDirectory(prefix='pool-sign-contract-') as root:
            p=Path(root)/'contract.json';dump(p,d);return screen(p)
    def test_unchanged_contract_passes(self):self.assertTrue(self.run_candidate(self.original)['pass'])
    def test_hash_change_fails_closed(self):
        d=copy.deepcopy(self.original);d['pins'][0]['sha256']='0'*64
        self.assertFalse(self.run_candidate(d)['pass'])
    def test_disconnected_mount_fails_closed(self):
        d=copy.deepcopy(self.original);s=d['signs'][0];s['components']=[c for c in s['components'] if not c['name'].startswith('FixedPad')]
        r=self.run_candidate(d);self.assertFalse(r['pass']);self.assertTrue(any('connected_mount' in a['check'] for a in r['issues']))
    def test_reversed_arrow_fails_closed(self):
        d=copy.deepcopy(self.original);s=next(s for s in d['signs'] if s['id']=='ramp_lower');s['arrow']['unit_arrow_uv']=[-1,0]
        r=self.run_candidate(d);self.assertFalse(r['pass']);self.assertTrue(any('route_arrow' in a['check'] for a in r['issues']))
    def test_aperture_intrusion_fails_closed(self):
        d=copy.deepcopy(self.original);s=d['signs'][0];c=next(c for c in s['components'] if c['name']=='MapFrame')
        c['local_bounds_uvd'][0][1]=-1.0;c['world_bounds_xyz']=local_box(s,c['local_bounds_uvd'])
        r=self.run_candidate(d);self.assertFalse(r['pass']);self.assertTrue(any('clear_volumes' in a['check'] for a in r['issues']))
    def test_unapproved_mounting_compromise_fails_closed(self):
        d=copy.deepcopy(self.original);d['unresolved_mounting_compromises']=['Test only']
        self.assertFalse(self.run_candidate(d)['pass'])

if __name__=='__main__':unittest.main(verbosity=2)
