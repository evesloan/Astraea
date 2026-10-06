#!/usr/bin/env python3
"""Pure-source contract/unit checks only. Does not parse/execute GDScript."""
from pathlib import Path
import ast, hashlib, json, math, struct, unittest, wave
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
GAME=Path('/workspace/shared/astraea-godot-production-20261003')
D=json.loads((ROOT/'data/ENGINEERING_CALIBRATION_DRAFT.json').read_text())

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class CandidateTests(unittest.TestCase):
    def test_unique_source_identity_and_precision(self):
        self.assertEqual(len(D['controls']),120)
        for field in ('id','source_marker','actuator_mesh_name'):
            self.assertEqual(len({r[field] for r in D['controls']}),120)
        self.assertEqual(D['counts_by_bay'],{'CONTROL':72,'WORKBAY':48})
        for r in D['controls']:
            self.assertEqual(r['source_marker'],'TARGET_'+r['id'])
            self.assertEqual(r['actuator_mesh_name'],'ACT_'+r['id'])
            self.assertEqual(r['target_radius_m'],.018)
            self.assertTrue(all(v>=.018 for v in r['target_half_extent_m']))
        for i,a in enumerate(D['controls']):
            for b in D['controls'][i+1:]: self.assertGreater(math.dist(a['target_center_xyz'],b['target_center_xyz']),.037)
        self.assertEqual(len(D['source_target_box_overlap_pairs']),16)

    def test_movement_within_source_bounds_and_exact_return_recipe(self):
        for r in D['controls']:
            limits=r['travel_limits'];axis=np.array(r['travel_axis_xyz']);pivot=np.array(r['pivot_xyz']);home=np.array(r['runtime_mesh_original_transform_rows'])
            self.assertTrue(limits[0]<=0<=limits[1]);self.assertTrue(limits[0]<=r['motion_endpoint']<=limits[1])
            self.assertAlmostEqual(np.linalg.norm(axis),1)
            for alpha in np.linspace(0,1,101):
                value=r['motion_endpoint']*alpha
                self.assertTrue(limits[0]-1e-9<=value<=limits[1]+1e-9)
                if r['travel_type']=='rotation':
                    x,y,z=axis;theta=math.radians(value);K=np.array([[0,-z,y],[z,0,-x],[-y,x,0]])
                    rotation=np.eye(3)+math.sin(theta)*K+(1-math.cos(theta))*(K@K)
                    delta=np.eye(4);delta[:3,:3]=rotation;delta[:3,3]=pivot-rotation@pivot
                    self.assertTrue(np.allclose((delta@np.r_[pivot,1])[:3],pivot,atol=1e-10))
                else:
                    self.assertEqual(r['travel_units'],'metres');self.assertLessEqual(abs(value),.008+1e-12)
            # Exact home assignment, not numerical inverse accumulation, is required.
            control=(ROOT/'scripts/engineering_calibration_control.gd').read_text()
            self.assertIn('actuator.transform = _home_local',control)
            self.assertIn('delta * _home_source',control)

    def test_source_pose_screen_is_explicitly_not_runtime(self):
        p=json.loads((ROOT/'reports/source_pose_screen.json').read_text())
        self.assertEqual(p['status'],'SOURCE_POSE_SCREEN_PASS');self.assertEqual(p['failed_ids'],[])
        self.assertFalse(p['godot_executed']);self.assertFalse(p['actual_engine_accepted'])
        self.assertEqual(len(p['poses']),120)
        for row in p['poses']:
            self.assertTrue(row['within_original_2_5m_ray']);self.assertTrue(row['within_original_pitch_limit'])
            self.assertEqual(row['source_fixed_contact_occluders'],[]);self.assertEqual(row['source_capsule_penetrations'],[])

    def test_original_audio_pcm_and_budget(self):
        self.assertEqual(D['audio']['max_voices'],4);self.assertLessEqual(D['audio']['volume_db'],-12)
        for cue in D['audio']['cues'].values():
            path=ROOT/cue['file'];self.assertEqual(sha(path),cue['sha256'])
            with wave.open(str(path),'rb') as f:
                self.assertEqual((f.getnchannels(),f.getsampwidth(),f.getframerate()),(1,2,24000))
                count=f.getnframes();self.assertLessEqual(count/24000,.42)
                samples=struct.unpack('<'+'h'*count,f.readframes(count))
            self.assertEqual(samples[0],0);self.assertEqual(samples[-1],0)
            self.assertLessEqual(max(abs(v) for v in samples)/32767,.12)
            self.assertFalse(cue['listening_accepted']);self.assertFalse(cue['in_engine_verified'])

    def test_no_unapproved_runtime_or_live_system_hooks(self):
        self.assertFalse(D['adoption_gate_accepted']);self.assertFalse(D['cake']['enabled']);self.assertEqual(D['cake']['spawn_budget'],0)
        text='\n'.join(p.read_text() for p in (ROOT/'scripts').glob('*.gd'))
        for forbidden in ('func _process(', 'func _physics_process(', 'func _input(', 'func _unhandled_input(', 'OmniLight3D.new', 'SpotLight3D.new', 'DirectionalLight3D.new', 'HTTPRequest.new', 'FileAccess.WRITE', 'reparent(', 'create_timer(', 'randi(', 'AudioServer.set_bus', 'set_shader_parameter('):
            self.assertNotIn(forbidden,text)
        self.assertNotIn('gate.interact(',text)
        self.assertNotIn('desired_open =',text)
        for path,digest in D['retained_runtime_pins'].items():self.assertEqual(sha(GAME/path),digest,path)
        control=(ROOT/'scripts/engineering_calibration_control.gd').read_text()
        self.assertIn('actor.target_from_view() != self',control)
        self.assertIn('actor.get("interaction_target") != self',control)
        self.assertIn('actor.get("held_interaction")',control)
        self.assertIn('target_area.collision_layer = 2',control)
        self.assertIn('target_area.monitoring = false',control)

    def test_python_deliverables_parse(self):
        for path in (ROOT/'tools').glob('*.py'):ast.parse(path.read_text(),str(path))

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(CandidateTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    report={'status':'PASS_PURE_SOURCE_ONLY' if result.wasSuccessful() else 'FAIL', 'tests_run':result.testsRun,
            'failures':len(result.failures),'errors':len(result.errors),'gdscript_parsed':False,'godot_executed':False,
            'scope':'Python/source/PCM/static-policy checks only; runtime, imports, listening, visual and aggregate stages UNRUN.'}
    (ROOT/'reports/pure_tests.json').write_text(json.dumps(report,indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
