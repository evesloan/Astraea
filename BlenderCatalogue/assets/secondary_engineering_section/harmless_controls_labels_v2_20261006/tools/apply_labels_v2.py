#!/usr/bin/env python3
"""Versioned, deterministic display-only revision. Original bundle is read-only.
Never touches Game, imports assets, runs an engine, or changes effect bindings.
"""
from pathlib import Path
import copy, hashlib, json
ROOT=Path(__file__).resolve().parents[1]
ORIGINAL=ROOT.parent/'engineering-harmless-controls'
REVISION='suncorp_control_labels_v2_20261006'
# Deliberately authored per-panel lists, ordered by stable source ID. No RNG or
# label synthesis from an interchangeable word bank.
PANELS={
'C1L':('Pressure balance: condensate return', '''Condensate Bypass|Bypass seated
Return Pressure Trim|Return differential settled
Condensate Level Check|Collector level acknowledged
Drain Manifold Reset|Drain manifold reset complete
Return Loop Selector|Return circuit indexed
Collector Equalizer|Collector balance settled
Backflow Bias|Backflow bias within band
Drain Relay Acknowledge|Drain relay acknowledged
Return Header Isolation|Return header state registered
Collector Reference|Collector reference aligned
Return Pulse Monitor|Return pulse steady
Condensate Register|Condensate register updated'''),
'C1R':('Pressure balance: supply regulation', '''Supply Balance Enable|Supply balance latched
Regulator Fine Trim|Regulator reference centered
Header Pressure Check|Header reading retained
Balance Relay Reset|Balance relay reseated
Supply Reference Select|Supply reference selected
Differential Hold|Differential hold registered
Accumulator Bias|Accumulator bias settled
Pilot Relay Acknowledge|Pilot relay acknowledged
Supply Loop Isolation|Supply loop state retained
Equalizer Range|Equalizer range indexed
Regulator Response|Regulator response steady
Pressure Register|Pressure register updated'''),
'C2L':('Phase courtesy: auxiliary reference', '''Auxiliary Reference|Auxiliary reference latched
Auxiliary Phase Trim|Phase offset aligned
Reference Pulse Check|Reference pulse acknowledged
Phase Relay Reset|Phase relay reseated
Reference Channel Select|Reference channel indexed
Quadrature Hold|Quadrature hold accepted
Phase Comparator Bias|Comparator bias settled
Reference Latch Reset|Reference latch restored
Auxiliary Timing Loop|Auxiliary timing steady
Harmonic Range|Harmonic range selected
Phase Response Monitor|Phase response within band
Reference Register|Reference register updated'''),
'C2R':('Phase courtesy: coil timing and synchronization', '''Coil Reference Enable|Coil reference established
Synchronizer Fine Trim|Synchronizer trim settled
Coil Pulse Check|Coil pulse acknowledged
Timing Relay Reset|Timing relay reseated
Synchronization Source|Synchronization source indexed
Phase Hold Register|Phase hold value retained
Coil Impedance Bias|Coil impedance within band
Synchronization Acknowledge|Synchronization acknowledged
Standby Reference Loop|Standby reference steady
Courtesy Interval|Courtesy interval selected
Timing Response Monitor|Timing response settled
Phase Courtesy Request|Courtesy protocol satisfied'''),
'C3L':('Relay verification: contact routing', '''Relay Matrix Enable|Relay matrix latched
Contact Dwell Trim|Contact dwell aligned
Contact Continuity Check|Contact continuity registered
Relay Bank Reset|Relay bank reset complete
Verification Channel|Verification channel indexed
Contact Hold Register|Contact hold value retained
Relay Response Bias|Relay response within band
Contact Acknowledge|Contact sequence acknowledged
Matrix Return Path|Matrix return path registered
Contact Range Select|Contact range selected
Relay Pulse Monitor|Relay pulse steady
Verification Register|Verification register updated'''),
'C3R':('Relay verification: reserve coils', '''Reserve Coil Isolation|Reserve coil state registered
Reserve Coil Trim|Reserve winding bias settled
Winding Continuity Check|Winding continuity acknowledged
Reserve Relay Reset|Reserve relay reseated
Coil Bank Selector|Coil bank indexed
Reserve Contact Hold|Reserve contact value retained
Winding Response Bias|Winding response within band
Coil Relay Acknowledge|Coil relay acknowledged
Reserve Return Path|Reserve return state retained
Coil Range Select|Coil range selected
Reserve Pulse Monitor|Reserve pulse steady
Coil Service Register|Coil service register updated'''),
'SCOPE':('Bench oscilloscope: traces and signal references', '''Trace Hold|Trace hold latched
Timebase Fine Trim|Timebase reference aligned
Single Sweep|Sweep sample retained
Input Coupling|Input coupling selected
Trigger Level|Trigger level centered
Trace Zero|Trace baseline registered
Probe Attenuation|Probe ratio indexed
Reference Overlay|Reference overlay acknowledged
Trace Capture|Trace sample acknowledged
Channel Invert|Channel polarity registered
Sweep Synchronize|Sweep timing settled
Trace Register|Trace register updated'''),
'MORALE':('Morale cabinet: pantry and staff comfort', '''Executive Climate Override|Preferred temperature noted
Service Temperature Trim|Service temperature indexed
Tray Temperature Check|Tray temperature acknowledged
Portion Index|Portion reference selected
Beverage Ratio|Beverage ratio retained
Tray Reset|Tray register restored
Service Interval|Service interval indexed
Warming Reserve|Warming reserve acknowledged
Pantry Stock Check|Pantry stock entry retained
Service Chime Enable|Service chime setting registered
Comfort Response|Comfort response satisfactory
Executive Morale Override|Request filed in triplicate'''),
'TEST_RACK_REMOTE_L':('North remote left: return transducers', '''Transducer Reference|Transducer reference latched
Return Sensor Bias|Return sensor bias centered
Transducer Pulse Check|Transducer pulse acknowledged
Manifold Hold|Manifold hold registered
Sensor Range Trim|Sensor range aligned
Return Sensor Zero|Return sensor baseline retained
Manifold Response|Manifold response steady
Transducer Bank Select|Transducer bank indexed
Return Reference Link|Return reference link registered
Sensor Relay Reset|Sensor relay reseated
Manifold Range|Manifold range selected
Return Sample Hold|Return sample retained'''),
'TEST_RACK_REMOTE_R':('North remote right: relay cradle and cartridges', '''Cradle Load Trim|Cradle load reference aligned
Cartridge Continuity Check|Cartridge continuity retained
Relay Cradle Enable|Relay cradle state registered
Contact Spring Bias|Contact spring bias settled
Cartridge Seat Check|Cartridge seat acknowledged
Cradle Reference Hold|Cradle reference value retained
Cartridge Bank Select|Cartridge bank selected
Fuse Reference Link|Fuse reference link registered
Bench Relay Reset|Bench relay reseated
Cradle Range Select|Cradle range indexed
Cartridge Response|Cartridge response within band
Bench Service Register|Bench service register updated'''),
}
MAPPING={
 'momentary_travel':{'runtime_profile':'travel_return','cue_id':'mechanical_click','pulse':False},
 'meter_step_return':{'runtime_profile':'detent_return','cue_id':'relay_double','pulse':False},
 'local_led_sequence':{'runtime_profile':'face_pulse','cue_id':'soft_hum','pulse':True},
 'latch_click':{'runtime_profile':'press_return','cue_id':'mechanical_click','pulse':False},
 'phase_courtesy_check_and_chime':{'runtime_profile':'courtesy_local_pulse','cue_id':'courtesy_chirp','pulse':True},
 'bounded_cake_candidate':{'runtime_profile':'reserved_cake_no_effect','cue_id':'mechanical_click','pulse':False},
}
DISPLAY_FIELDS={'label','faux_status','display_revision','label_identity','status_identity','panel_theme','label_brand'}
EFFECT_FIELDS=('runtime_profile','cue_id','pulse_material_name','pulse_energy_max','pulse_color_rgb','duration_s','cooldown_s','motion_endpoint','travel_type','travel_limits','travel_axis_xyz','travel_units','pivot_xyz','target_radius_m','target_shape','cake_effect_id_reserved')
OLD_LABEL_FUNCTION='''func get_interaction_label() -> String:
\tif busy: return "Calibration test running"
\treturn str(record.label) + " · local test"
'''
NEW_LABEL_FUNCTION='''func get_interaction_label() -> String:
\tif busy: return str(record.faux_status)
\treturn str(record.label)
'''
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def emit(p,value):p.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
def original_guard():
    frozen=json.loads((ROOT/'provenance/original_bundle_hashes.json').read_text())
    for relative,digest in frozen['files'].items():assert sha(ORIGINAL/relative)==digest,relative
    return frozen

def main():
    baseline_guard=original_guard()
    baseline=json.loads((ORIGINAL/'data/ENGINEERING_CALIBRATION_DRAFT.json').read_text())
    revised=copy.deepcopy(baseline); revised['display_revision']=REVISION
    labels=[];count_by_panel={};allow_ids={}; panel_order=list(PANELS)
    for row in revised['controls']:
        panel=row['panel'];theme,body=PANELS[panel]
        pairs=[line.split('|') for line in body.splitlines()];assert len(pairs)==12
        count_by_panel[panel]=count_by_panel.get(panel,0)+1
        identity=row['id'];ordinal=int(identity.rsplit('_',1)[1])
        index=ordinal-(13 if panel=='TEST_RACK_REMOTE_R' else 1)
        assert 0<=index<12
        label,status=pairs[index]
        assert len(label)<=40 and len(status)<=40,(identity,label,status)
        row.update({'label':'E · '+label,'faux_status':status,'display_revision':REVISION,
                    'label_identity':identity,'status_identity':identity,'panel_theme':theme,'label_brand':'SunCorp'})
        expected=MAPPING[row['effect_candidate']]
        assert row['runtime_profile']==expected['runtime_profile'] and row['cue_id']==expected['cue_id']
        assert bool(row['pulse_material_name'])==expected['pulse']
        allow_ids[identity]={k:row[k] for k in EFFECT_FIELDS}
        labels.append({'id':identity,'bay':row['bay'],'panel':panel,'theme':theme,'label':label,
                       'reticle_prompt':row['label'],'faux_status':status,'source_marker':row['source_marker'],
                       'actuator_mesh_name':row['actuator_mesh_name'],'effect_candidate':row['effect_candidate'],
                       'runtime_profile':row['runtime_profile'],'cue_id':row['cue_id']})
    assert all(n==12 for n in count_by_panel.values()) and len(labels)==120
    assert len({x['label'] for x in labels})==len({x['faux_status'] for x in labels})==120
    for old,new in zip(baseline['controls'],revised['controls']):
        for k,v in old.items():
            if k!='label':assert new[k]==v,(old['id'],k)
    # Exactly the reticle accessor changes; all mechanics and audio bytes remain.
    old_script=(ORIGINAL/'scripts/engineering_calibration_control.gd').read_text()
    assert old_script.count(OLD_LABEL_FUNCTION)==1
    new_script=old_script.replace(OLD_LABEL_FUNCTION,NEW_LABEL_FUNCTION)
    (ROOT/'scripts/engineering_calibration_control.gd').write_text(new_script)
    for name in ('engineering_calibration_builder.gd','engineering_calibration_bank.gd','engineering_calibration_audio.gd'):
        assert (ROOT/'scripts'/name).read_bytes()==(ORIGINAL/'scripts'/name).read_bytes()
    for path in (ORIGINAL/'audio').glob('*.wav'):assert sha(ROOT/'audio'/path.name)==sha(path)
    emit(ROOT/'data/ENGINEERING_CALIBRATION_DRAFT.json',revised)
    emit(ROOT/'data/SUNCORP_LABELS_V2.json',{'revision':REVISION,'brand':'SunCorp','scope':'Existing reticle prompt and brief busy text only',
        'source_theme_evidence':{
          'CONTROL':'Authored crown sequence: 01 PRESSURE BALANCE; 02 PHASE COURTESY; 03 RELAY VERIFICATION. Left/right are deliberately related sub-panels.',
          'SCOPE':'BENCH_OSCILLOSCOPE with retained probe leads and printed trace.',
          'MORALE':'MORALE_CALIBRATION cabinet and retained receiving tray; reserved cake output remains disabled.',
          'TEST_RACK_REMOTE_L':'NorthRemote_L at x23.63, beside the return-transducer/relay zone.',
          'TEST_RACK_REMOTE_R':'NorthRemote_R at x25.39, beside the relay cradle/stock-cartridge zone.',
          'authored_layout_sha256':sha(ROOT.parent/'engineering-dense-bays/source/generate_dense_plan.py'),
          'north_revision_sha256':sha(ROOT.parent/'engineering-dense-bays/source/north_wall_revision.py'),
          'artwork_generator_sha256':sha(ROOT.parent/'engineering-dense-bays/source/draw_dense_graphics.py')},
        'panel_order':panel_order,'rows':labels})
    emit(ROOT/'data/LOCAL_EFFECT_ALLOWLIST_V1.json',{'revision':'local_effect_allowlist_v1_unchanged_by_labels_v2',
        'source_candidate_mapping':MAPPING,'effect_mapping_by_id':allow_ids,
        'caps':{'active_controls':4,'audio_voices':4,'audio_global_cooldown_s':.08,'per_control_cooldown_s':.9,
                'audio_volume_db':-12,'audio_max_distance_m':6,'pulse_energy_max':.22},
        'cake':baseline['cake'],'forbidden_live_effects':['reactor','security','airlock','gate','lift','transport','network','damage','punishment','persistent_save','cake_spawn'],
        'display_text_is_not_dispatch':'Only the existing runtime_profile and cue_id fields select existing local feedback; label/faux_status never select an effect.'})
    preview=['# SunCorp controls: authored label/status review','',f'Revision: {REVISION}. Every row retains its exact source identity and bounded local effect. No live systems or cake are enabled.','']
    for panel in panel_order:
        preview.extend(['## '+PANELS[panel][0],''])
        for r in labels:
            if r['panel']==panel:preview.append(f'- {r["id"]}: {r["label"]} → {r["faux_status"]}')
        preview.append('')
    (ROOT/'LABEL_REVIEW.md').write_text('\n'.join(preview))
    original_guard()
    emit(ROOT/'reports/label_revision_build.json',{'status':'PASS_DISPLAY_ONLY_BUILD','revision':REVISION,'controls':120,
        'unique_labels':120,'unique_statuses':120,'changed_runtime_function':'engineering_calibration_control.gd::get_interaction_label',
        'changed_original_row_fields':['label'],'added_display_row_fields':sorted(DISPLAY_FIELDS-{'label'}),
        'original_bundle_manifest_sha256':baseline_guard['source_manifest_sha256'],'original_bundle_unchanged':True,
        'source_controls_unchanged':True,'movement_and_effect_bindings_unchanged':True,'original_audio_bytes_unchanged':True,
        'game_writes':False,'godot_executed':False,'imports_performed':False,'actual_engine_accepted':False})
    print('Built deterministic 120-label/status SunCorp v2 revision; original bundle and effects unchanged.')
if __name__=='__main__':main()
