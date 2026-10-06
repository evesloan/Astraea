#!/usr/bin/env python3
"""Build a scratch-only, source-pinned calibration contract and original PCM cues.
Never imports/runs an engine and never changes the game or retained source.
"""
from pathlib import Path
import collections, hashlib, json, math, random, struct, wave
from glb_geometry import glb

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/secondary_engineering_section/workbay_section_gate_v2_candidate_20261006')
GAME = Path('/workspace/shared/astraea-godot-production-20261003')
RADIUS = .018

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def emit(path, data): path.write_text(json.dumps(data, indent=2, sort_keys=True)+'\n')

def make_audio():
    rate = 24000
    recipes = {'mechanical_click': .085, 'relay_double': .18, 'soft_hum': .42, 'courtesy_chirp': .22}
    records = {}
    for name, duration in recipes.items():
        rng = random.Random(6721)
        samples = []
        for i in range(round(rate * duration)):
            t = i/rate
            noise = rng.uniform(-1, 1)
            if name == 'mechanical_click':
                sample = .095*(noise*.62+math.sin(2*math.pi*1350*t)*.38)*math.exp(-85*t)
            elif name == 'relay_double':
                sample = 0
                for delay in (0, .065):
                    tt = t-delay
                    if tt >= 0: sample += .075*(noise*.5+math.sin(2*math.pi*960*tt)*.5)*math.exp(-95*tt)
            elif name == 'soft_hum':
                env = math.sin(math.pi*t/duration)**2
                sample = .052*env*(math.sin(2*math.pi*120*t)+.25*math.sin(2*math.pi*240*t))
            else:
                env = math.sin(math.pi*t/duration)**2
                phase = 2*math.pi*(660*t+180*t*t/(2*duration))
                sample = .055*env*(math.sin(phase)+.15*math.sin(2*phase))
            # Two-ms boundary fades; no hard discontinuity, clipping or looping.
            sample *= min(1, t/.002, (duration-t)/.003)
            samples.append(max(-32767, min(32767, round(sample*32767))))
        samples[0] = samples[-1] = 0
        path = ROOT/'audio'/f'{name}.wav'
        with wave.open(str(path), 'wb') as f:
            f.setnchannels(1); f.setsampwidth(2); f.setframerate(rate)
            f.writeframes(struct.pack('<'+'h'*len(samples), *samples))
        peak = max(abs(x) for x in samples)/32767
        rms = math.sqrt(sum((x/32767)**2 for x in samples)/len(samples))
        assert peak <= .12 and duration <= .42 and abs(sum(samples)/len(samples)/32767) < .005
        records[name] = {'file': f'audio/{name}.wav', 'sha256': sha(path), 'sample_rate': rate,
                         'channels': 1, 'pcm_bits': 16, 'duration_s': duration, 'peak_linear': peak,
                         'rms_linear': rms, 'loop': False, 'origin': 'Original procedural synthesis, tools/build_candidate.py',
                         'listening_accepted': False, 'in_engine_verified': False}
    emit(ROOT/'reports/audio_build.json', records)
    return records

def main():
    manifest_path=SOURCE/'source/calibration_control_manifest.json'
    contract_path=SOURCE/'source/runtime_contract.final_source.json'
    source=json.loads(manifest_path.read_text()); contract=json.loads(contract_path.read_text())
    model=SOURCE/'exports'/contract['model_file']; g=glb(model)
    assert g['sha256']==contract['model_sha256']=='6896d757c5a248d0fcf37a2ae7a197de24566a3fec3f80ce80cdc12186e34368'
    assert sha(SOURCE/contract['source_blend'])==contract['source_sha256']
    assert sha(GAME/'assets/models'/contract['model_file'])==g['sha256']
    nodes={x['name']: x for x in g['nodes']}; assert len(nodes)==len(g['nodes'])
    controls=[]; ids=set(); source_box_overlaps=[]
    profiles={
        'momentary_travel': ('travel_return','mechanical_click',False),
        'meter_step_return': ('detent_return','relay_double',False),
        'local_led_sequence': ('face_pulse','soft_hum',True),
        'latch_click': ('press_return','mechanical_click',False),
        'phase_courtesy_check_and_chime': ('courtesy_local_pulse','courtesy_chirp',True),
        'bounded_cake_candidate': ('reserved_cake_no_effect','mechanical_click',False),
    }
    for row in source['controls']:
        r=dict(row); identity=r['id']; assert identity not in ids; ids.add(identity)
        marker=nodes[r['source_marker']]; actuator=nodes[r['actuator_mesh_name']]
        assert marker['extras']['control_id']==actuator['extras']['control_id']==identity
        assert marker['extras']['normal_xyz']==r['target_normal_xyz']
        assert math.dist(marker['world_matrix'][:3,3],r['target_center_xyz'])<.0001
        assert actuator['extras']['collision_contract']=='actuator_no_body_contact'
        for k in ('pivot_xyz','travel_axis_xyz','travel_type','travel_limits','travel_units'):
            assert actuator['extras'][k]==r[k], (identity,k)
        assert all(v>=RADIUS for v in r['target_half_extent_m'])
        assert math.isclose(math.dist([0,0,0],r['travel_axis_xyz']),1)
        assert r['travel_limits'][0]<=0<=r['travel_limits'][1]
        assert math.dist(r['proposed_eye_xyz'],r['target_center_xyz'])<2.5
        assert abs(r['proposed_eye_xyz'][1]-r['proposed_approach_xyz'][1]-1.65)<1e-9
        profile,cue,pulse=profiles[r['effect_candidate']]
        materials=contract['groups'][r['actuator_mesh_name']]['materials']
        pulse_material=next((m for m in ('ASTRAEA_staff_label','ASTRAEA_staff_cable_blue','ASTRAEA_staff_white_paint','ASTRAEA_staff_cable_red') if m in materials),'')
        assert not pulse or pulse_material
        # All motion is displacement FROM the imported rest transform. Source limits
        # contain zero; no load-time posing or reparenting is permitted.
        endpoint=r['travel_limits'][0] if r['travel_type']=='translation' else r['travel_limits'][1]
        r.update({
            'runtime_profile':profile, 'cue_id':cue, 'target_shape':'sphere', 'target_radius_m':RADIUS,
            'target_shape_reason':'Precise sphere inside source proposal envelope; original 90 mm boxes overlap for 16 adjacent pairs.',
            'motion_endpoint':endpoint, 'return_to_exact_imported_rest':True,
            'pulse_material_name':pulse_material if pulse else '', 'pulse_energy_max':.22,
            'pulse_color_rgb':[.48,.82,1.0], 'duration_s':.68 if profile=='detent_return' else .52,
            'cooldown_s':.9, 'label':f'E · Calibration {r["panel"].replace("_", " ")} {identity.rsplit("_",1)[1]}',
            'scope_label':'Local calibration only', 'cake_effect_id_reserved':'bounded_cake_candidate' if profile=='reserved_cake_no_effect' else '',
            'source_actuator_parts_are_blender_only':True,
            'runtime_mesh_original_transform_rows':actuator['world_matrix'].tolist(),
            'runtime_materials':materials,
        })
        controls.append(r)
    assert len(controls)==120
    for i,a in enumerate(controls):
        for b in controls[i+1:]:
            separation=math.dist(a['target_center_xyz'],b['target_center_xyz'])
            assert separation>2*RADIUS+.001
            if all(abs(a['target_center_xyz'][j]-b['target_center_xyz'][j])<a['target_half_extent_m'][j]+b['target_half_extent_m'][j] for j in range(3)):
                source_box_overlaps.append([a['id'],b['id']])
    assert len(source_box_overlaps)==16
    counts=dict(collections.Counter(r['bay'] for r in controls)); assert counts=={'CONTROL':72,'WORKBAY':48}
    pins={str(p.relative_to(GAME)):sha(p) for p in [GAME/'scripts'/n for n in ('player.gd','fixture_switch.gd','physics_tether.gd','service_door.gd','engineering_cell_gate.gd','engineering_cell_gate_target.gd','secondary_engineering_cell.gd','lighting_budget.gd')]}
    audio=make_audio()
    data={
        'schema':'astraea.engineering-calibration.scratch-draft.v1', 'status':'SCRATCH DRAFT, engine and listening acceptance required',
        'adoption_gate_accepted':False, 'catalogue_id':contract['catalogue_id'], 'model_file':contract['model_file'],
        'model_sha256':g['sha256'], 'source_manifest_sha256':sha(manifest_path), 'source_contract_sha256':sha(contract_path),
        'source_blend_sha256':contract['source_sha256'], 'retained_runtime_pins':pins,
        'control_count':120, 'counts_by_bay':counts, 'max_active_controls':4,
        'audio':{'max_voices':4,'global_start_cooldown_s':.08,'volume_db':-12,'max_distance_m':6,'unit_size_m':.8,'cues':audio},
        'source_target_box_overlap_pairs':source_box_overlaps,
        'cake':{'reserved_effect_id':'bounded_cake_candidate','enabled':False,'spawn_budget':0,'probability':0},
        'scope':{'only_local_actuator_transform_and_duplicated_material':True,'no_dynamic_lights':True,'no_global_state_writes':True,'no_frame_room_scans':True,'no_live_systems':True},
        'controls':controls,
    }
    emit(ROOT/'data/ENGINEERING_CALIBRATION_DRAFT.json',data)
    emit(ROOT/'reports/build_candidate.json', {'status':'PASS_SOURCE_BUILD_ONLY','count':len(controls),'counts_by_bay':counts,
          'source_box_overlaps':len(source_box_overlaps),'runtime_sphere_overlap_count':0,
          'model_sha256':g['sha256'],'source_manifest_sha256':sha(manifest_path),'retained_runtime_pins':pins,
          'godot_executed':False,'imports_performed':False,'game_writes':False,'audio_listening_accepted':False})
    print('Built 120 source-pinned controls, precise non-overlapping targets and four original draft audio cues. No engine run or Game write.')
if __name__=='__main__': main()
