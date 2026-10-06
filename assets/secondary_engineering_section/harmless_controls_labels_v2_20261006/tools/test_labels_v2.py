#!/usr/bin/env python3
"""Label/effect separation and source-preservation checks, without any engine."""
from pathlib import Path
import copy, hashlib, json, re, unittest
from apply_labels_v2 import DISPLAY_FIELDS, EFFECT_FIELDS, MAPPING, NEW_LABEL_FUNCTION, OLD_LABEL_FUNCTION, REVISION
ROOT=Path(__file__).resolve().parents[1];OLD=ROOT.parent/'engineering-harmless-controls'
def load(path):return json.loads(path.read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
BASE=load(OLD/'data/ENGINEERING_CALIBRATION_DRAFT.json')
DATA=load(ROOT/'data/ENGINEERING_CALIBRATION_DRAFT.json')
LABELS=load(ROOT/'data/SUNCORP_LABELS_V2.json')
ALLOW=load(ROOT/'data/LOCAL_EFFECT_ALLOWLIST_V1.json')

def validate(data):
    assert len(data['controls'])==120
    assert data['display_revision']==REVISION
    old_by_id={r['id']:r for r in BASE['controls']};new_by_id={r['id']:r for r in data['controls']}
    assert set(old_by_id)==set(new_by_id) and len(new_by_id)==120
    for identity,r in new_by_id.items():
        old=old_by_id[identity]
        for field,value in old.items():
            if field!='label':assert r[field]==value,(identity,field)
        assert set(r)-set(old)==DISPLAY_FIELDS-{'label'}
        assert r['label_identity']==r['status_identity']==identity
        assert r['display_revision']==REVISION and r['label_brand']=='SunCorp'
        assert r['label'].startswith('E · ') and not r['faux_status'].startswith('E · ')
        assert len(r['label'])<=44 and 3<len(r['faux_status'])<=40
        assert not re.search(r'\b(gate|door|airlock|lift|transport|teleport|damage|kill|punishment|calibration|fake|harmless|simulation)\b|local test',r['label']+' '+r['faux_status'],re.I)
        m=MAPPING[r['effect_candidate']]
        assert r['runtime_profile']==m['runtime_profile'] and r['cue_id']==m['cue_id']
        assert bool(r['pulse_material_name'])==m['pulse']
        assert {k:r[k] for k in EFFECT_FIELDS}==ALLOW['effect_mapping_by_id'][identity]
    assert len({r['label'] for r in data['controls']})==len({r['faux_status'] for r in data['controls']})==120
    for key,value in BASE.items():
        if key!='controls':assert data[key]==value,key
    assert set(data)-set(BASE)=={'display_revision'}
    assert data['cake']=={'reserved_effect_id':'bounded_cake_candidate','enabled':False,'spawn_budget':0,'probability':0}
    assert not data['adoption_gate_accepted']

class LabelTests(unittest.TestCase):
    def test_all_120_label_and_status_identities(self):
        validate(DATA)
        self.assertEqual(len(LABELS['rows']),120)
        indexed={r['id']:r for r in LABELS['rows']}
        for r in DATA['controls']:
            label=indexed[r['id']]
            self.assertEqual((r['label'],r['faux_status'],r['panel_theme']),(label['reticle_prompt'],label['faux_status'],label['theme']))
        self.assertEqual(len({r['panel'] for r in LABELS['rows']}),10)

    def test_original_bundle_and_unchanged_runtime_audio(self):
        receipt=load(ROOT/'provenance/original_bundle_hashes.json')
        for path,digest in receipt['files'].items():self.assertEqual(sha(OLD/path),digest,path)
        for name in ('engineering_calibration_builder.gd','engineering_calibration_bank.gd','engineering_calibration_audio.gd'):
            self.assertEqual((ROOT/'scripts'/name).read_bytes(),(OLD/'scripts'/name).read_bytes(),name)
        for old in (OLD/'audio').glob('*.wav'):self.assertEqual(sha(ROOT/'audio'/old.name),sha(old))
        expected=(OLD/'scripts/engineering_calibration_control.gd').read_text().replace(OLD_LABEL_FUNCTION,NEW_LABEL_FUNCTION)
        self.assertEqual((ROOT/'scripts/engineering_calibration_control.gd').read_text(),expected)

    def test_exact_source_fields_and_effect_mapping(self):
        source=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/secondary_engineering_section/workbay_section_gate_v2_candidate_20261006/source/calibration_control_manifest.json')
        self.assertEqual(sha(source),DATA['source_manifest_sha256'])
        source_rows={r['id']:r for r in load(source)['controls']}
        for row in DATA['controls']:
            for field,value in source_rows[row['id']].items():self.assertEqual(row[field],value,(row['id'],field))
        self.assertEqual(ALLOW['source_candidate_mapping'],MAPPING)
        self.assertEqual(len(ALLOW['effect_mapping_by_id']),120)
        self.assertEqual(ALLOW['caps'],{'active_controls':4,'audio_voices':4,'audio_global_cooldown_s':.08,'per_control_cooldown_s':.9,'audio_volume_db':-12,'audio_max_distance_m':6,'pulse_energy_max':.22})

    def test_rejects_effect_escalation_and_geometry_changes(self):
        for field,value in [('runtime_profile','open_airlock'),('cue_id','unbounded_loop'),('motion_endpoint',180),('target_radius_m',1),('pivot_xyz',[0,0,0]),('duration_s',900),('pulse_energy_max',5)]:
            broken=copy.deepcopy(DATA);broken['controls'][0][field]=value
            with self.assertRaises(AssertionError,msg=field):validate(broken)
        broken=copy.deepcopy(DATA);broken['cake']['enabled']=True
        with self.assertRaises(AssertionError):validate(broken)

    def test_rejects_id_aliasing_and_transport_prompt_collision(self):
        for field,value in [('label_identity','OTHER_ID'),('status_identity','OTHER_ID'),('label','E · Open service cell gate'),('faux_status','Lift moving')]:
            broken=copy.deepcopy(DATA);broken['controls'][0][field]=value
            with self.assertRaises(AssertionError,msg=field):validate(broken)
        broken=copy.deepcopy(DATA);broken['controls'][1]['faux_status']=broken['controls'][0]['faux_status']
        with self.assertRaises(AssertionError):validate(broken)

    def test_stable_labels_independent_of_source_order(self):
        reversed_data=copy.deepcopy(DATA);reversed_data['controls'].reverse();validate(reversed_data)
        by_id={r['id']:r for r in DATA['controls']}
        expected={'ENG2_CONTROL_C1L_01':'E · Condensate Bypass','ENG2_CONTROL_C2L_02':'E · Auxiliary Phase Trim',
                  'ENG2_CONTROL_C3R_01':'E · Reserve Coil Isolation','ENG2_WORKBAY_MORALE_01':'E · Executive Climate Override',
                  'ENG2_WORKBAY_MORALE_12':'E · Executive Morale Override'}
        for identity,label in expected.items():self.assertEqual(by_id[identity]['label'],label)
        self.assertEqual(by_id['ENG2_WORKBAY_MORALE_12']['faux_status'],'Request filed in triplicate')
        self.assertEqual(by_id['ENG2_WORKBAY_MORALE_12']['runtime_profile'],'reserved_cake_no_effect')

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(LabelTests))
    report={'status':'PASS_LABELS_AND_BOUNDED_EFFECT_PRESERVATION' if result.wasSuccessful() else 'FAIL',
        'revision':REVISION,'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
        'labels':120,'statuses':120,'source_fields_unchanged':True,'original_bundle_unchanged':True,
        'gdscript_parsed':False,'godot_executed':False,'imports_performed':False}
    (ROOT/'reports/label_revision_tests.json').write_text(json.dumps(report,indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
