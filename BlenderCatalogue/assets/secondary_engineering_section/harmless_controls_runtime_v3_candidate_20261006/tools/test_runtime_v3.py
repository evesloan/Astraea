#!/usr/bin/env python3
"""Pure draft checks. No engine/imports; model checks do not prove audio playback."""
from pathlib import Path
import ast,copy,difflib,hashlib,json,math,re,unittest
R=Path(__file__).resolve().parents[1];V2=R.parent/'engineering-harmless-controls-labels-v2-20261006';GAME=Path('/workspace/shared/astraea-godot-production-20261003')
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
D=load(R/'data/ENGINEERING_CALIBRATION_DRAFT.json');B=load(V2/'data/ENGINEERING_CALIBRATION_DRAFT.json');P=load(R/'reports/runtime_v3_preflight.json')

class LeaseModel:
    """Small independent arithmetic witness, never runtime evidence."""
    def __init__(self,hz=60):self.hz=hz;self.until=[-1]*4;self.last=-10**6;self.starts=[]
    def play(self,frame,duration=.42):
        if (frame-self.last)/self.hz<.08:return False
        for i in range(4):
            if frame<self.until[i]:continue
            self.until[i]=frame+math.ceil(duration*self.hz)+1;self.last=frame;self.starts.append((frame,i));return True
        return False
    def stop(self):self.until=[-1]*4

class RuntimeDraftTests(unittest.TestCase):
    def test_frozen_v2_and_originals_untouched(self):
        receipt=load(R/'provenance/labels_v2_bundle_hashes.json')
        for p,h in receipt['files'].items():self.assertEqual(sha(V2/p),h,p)
        original=load(R/'provenance/original_bundle_hashes.json');v1=R.parent/'engineering-harmless-controls'
        for p,h in original['files'].items():self.assertEqual(sha(v1/p),h,p)

    def test_all_120_source_labels_and_effects_unchanged(self):
        self.assertEqual(D['controls'],B['controls']);self.assertEqual(len(D['controls']),120)
        self.assertEqual(D['audio'],B['audio']);self.assertEqual(D['cake'],B['cake']);self.assertFalse(D['cake']['enabled']);self.assertFalse(D['adoption_gate_accepted'])
        for p in (V2/'audio').glob('*.wav'):self.assertEqual(sha(R/'audio'/p.name),sha(p))
        self.assertEqual((R/'data/LOCAL_EFFECT_ALLOWLIST_V1.json').read_bytes(),(V2/'data/LOCAL_EFFECT_ALLOWLIST_V1.json').read_bytes())
        self.assertEqual((R/'data/SUNCORP_LABELS_V2.json').read_bytes(),(V2/'data/SUNCORP_LABELS_V2.json').read_bytes())

    def test_exact_separate_listener_and_cell_additions(self):
        proof=load(R/'docs/ENGINEERING_CONTROLS_LISTENER_ADOPTION_DRAFT.json')
        text=(R/'integration/presentation.listener_candidate.gd').read_text();line=proof['exact_added_line']
        self.assertEqual(line,'\tworld_view.audio_listener_enable_3d = true\n');self.assertEqual(text.count(line),1)
        self.assertEqual(hashlib.sha256(text.encode()).hexdigest(),proof['candidate_sha256'])
        self.assertEqual(hashlib.sha256(text.replace(line,'').encode()).hexdigest(),proof['predecessor_sha256'])
        self.assertEqual(proof['predecessor_sha256'],proof['original_section_predecessor_sha256']);self.assertFalse(proof['adoption_approved'])
        cell=(R/'integration/secondary_engineering_cell.controls_candidate.gd').read_text();addition='\tload("res://scripts/engineering_calibration_builder.gd").build(wrapper,visual,ship)\n'
        self.assertEqual(cell.count(addition),1)
        self.assertEqual(hashlib.sha256(cell.replace(addition,'').encode()).hexdigest(),P['base_pins']['scripts/secondary_engineering_cell.gd'])
        guard=(R/'tests/engineering_controls_listener_successor.gd').read_text()
        self.assertIn(sha(R/'docs/ENGINEERING_CONTROLS_LISTENER_ADOPTION_DRAFT.json'),guard)
        self.assertIn('restored.sha256_text()',guard);self.assertIn('section_successor.historical_sha256',guard)
        self.assertFalse(any(p.name=='secondary_engineering_additive_guard.gd' for p in R.rglob('*.gd')))

    def test_listener_binding_is_exact_deferred_and_fail_closed(self):
        bank=(R/'scripts/engineering_calibration_bank.gd').read_text();audio=(R/'scripts/engineering_calibration_audio.gd').read_text();builder=(R/'scripts/engineering_calibration_builder.gd').read_text()
        self.assertEqual(builder.count('bank.call_deferred("bind_original_player_after_build", ship)'),1)
        for token in ['listener_bind_attempts == 1','ShipSpace/PersistentActors/Player','not listener_ready or not audio_owner.listener_contract_holds()']:self.assertIn(token,bank)
        for token in ['viewport.audio_listener_enable_3d','listener_camera.get_viewport() != viewport','viewport.get_camera_3d() != listener_camera','voice.get_world_3d() != listener_camera.get_world_3d()']:self.assertIn(token,audio)
        self.assertNotIn('create_timer(',audio+bank)

    def test_audio_leases_four_cap_and_spacing_model(self):
        for hz in (30,60,120):
            model=LeaseModel(hz);spacing=math.ceil(.08*hz)
            for i in range(4):
                self.assertTrue(model.play(i*spacing));self.assertFalse(model.play(i*spacing))
            self.assertFalse(model.play(4*spacing));self.assertEqual(len({v for _,v in model.starts}),4)
            for a,b in zip(model.starts,model.starts[1:]):self.assertGreaterEqual((b[0]-a[0])/hz,.08)
            model.stop();self.assertFalse(model.play(model.last))
            self.assertTrue(model.play(model.last+spacing))
        audio=(R/'scripts/engineering_calibration_audio.gd').read_text()
        for token in ['MAX_START_HISTORY := 64','frame < _lease_until_frame[index] or voice.playing','voice.max_polyphony = 1','_start_cooldown_s := .08','start_history.pop_front()']:self.assertIn(token,audio)

    def test_no_runtime_room_scans_live_systems_or_new_lights(self):
        text='\n'.join(p.read_text() for p in (R/'scripts').glob('*.gd'))
        for token in ['func _process(', 'func _physics_process(', 'func _input(', 'func _unhandled_input(', 'Light3D.new(', 'HTTPRequest.new(', 'AudioServer.set_bus', 'FileAccess.WRITE', 'request_floor(', 'gate.interact(', 'randi(', 'set_shader_parameter(']:self.assertNotIn(token,text)
        self.assertIn('actor != manager.original_actor',text)
        self.assertIn('actuator.transform = _home_local',text)
        self.assertIn('actuator.set_surface_override_material(_pulse_surface, _original_surface_override)',text)
        self.assertIn('_original_surface_override = actuator.get_surface_override_material(_pulse_surface)',text)

    def test_connected_actual_world_test_is_not_pose_teleports(self):
        route=load(R/'data/ENGINEERING_CONTROLS_WALK_ROUTE_V3.json');test=(R/'tests/validate_engineering_calibration.gd').read_text()
        self.assertEqual(route['allowed_diagnostic_arrivals'],1)
        self.assertEqual(len(route['segments']),10);self.assertEqual(len({x['panel'] for x in route['segments']}),10)
        self.assertEqual({x['panel'] for x in route['segments']},{x['panel'] for x in D['controls']})
        self.assertEqual(test.count('ship.arrive_at('),1)
        self.assertNotIn('actor.global_position =',test);self.assertNotIn('actor.set_physics_process(',test);self.assertNotIn('actor.move_and_slide(',test)
        self.assertIn('ship.add_child(blocker)',test);self.assertNotIn('root.add_child(blocker)',test)
        self.assertIn('blocker.get_world_3d() == actor.get_world_3d()',test)
        self.assertIn('for waypoint in segment.waypoints_xyz:',test)
        self.assertIn('cached roster',test)

    def test_engine_test_covers_requested_negatives_and_rest(self):
        t=(R/'tests/validate_engineering_calibration.gd').read_text()
        for token in ['identity_and_listener_census','source_target_box_overlap_pairs','Original capsule resized or offset','source-pivot formula','Second cycle failed to restore NULL override','cache_real_system_states','original_2_5m_range','four_audio_voice_cap_and_80ms','escape_cancel_null_material_restore','Original current camera','Original RMB/E']:
            # Camera wording is represented by its explicit topology assertion.
            if token=='Original current camera': self.assertIn('main.world_view.get_camera_3d() == actor.camera',t)
            else:self.assertIn(token,t)
        self.assertIn('actual_engine_checks',json.dumps(D));self.assertEqual(D['runtime_prerequisites']['actual_engine_checks'],'UNRUN')
        self.assertIn('"human_listening_accepted":false',t)

    def test_python_syntax_and_validation_wrapper_are_additive(self):
        for p in (R/'tools').glob('*.py'):ast.parse(p.read_text(),str(p))
        p=R/'integration/validate.controls_candidate.py';ast.parse(p.read_text(),str(p))
        text=p.read_text();self.assertIn("frame_budget='40000'",text);self.assertIn("1200 if label=='engineering_controls' else",text)
        self.assertIn("commands.sort(key=lambda entry: entry[0] != 'import')",text)

    def test_precise_targets_no_overlap(self):
        controls=D['controls']
        for i,a in enumerate(controls):
            self.assertEqual(a['target_radius_m'],.018)
            for b in controls[i+1:]:self.assertGreater(math.dist(a['target_center_xyz'],b['target_center_xyz']),.037)
        builder=(R/'scripts/engineering_calibration_builder.gd').read_text()
        for token in ['validate_precise_target_data','Overlapping/ambiguous source targets rejected','Unapproved local effect mapping','Cake remains disabled and reserved']:self.assertIn(token,builder)

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(RuntimeDraftTests))
    report={'status':'PASS_PURE_RUNTIME_DRAFT_CHECKS' if result.wasSuccessful() else 'FAIL','tests_run':result.testsRun,
        'failures':len(result.failures),'errors':len(result.errors),'godot_executed':False,'gdscript_parsed':False,'imports_performed':False,
        'actual_world_routes':'UNRUN','actual_audio_listener_and_playback':'UNRUN','human_listening':'UNRUN','scope':'Pure contract/byte-preservation/Python/algorithm witnesses only. No game/runtime claim.'}
    (R/'reports/runtime_v3_pure_tests.json').write_text(json.dumps(report,indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
