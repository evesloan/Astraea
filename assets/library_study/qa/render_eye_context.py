"""Two ordinary eye-height contexts; imports final GLBs, no source edits."""
import sys,json,hashlib
from pathlib import Path
import bpy
QA=Path(__file__).resolve().parent
sys.path.insert(0,str(QA))
from render_and_audit import ROOT,BASE,import_glb,studio,render

views=[{'catalogue_id':'AST-LIB-STUDY-01','file':'01_shared_standing_eye_1650mm_640.png','camera_position_m':[3.45,-4.5,1.650],'target_m':[0,0,.600],'lens_mm':42,'camera_height_m':1.650,'camera_label':'Standing-height camera, Z1.650m'},
       {'catalogue_id':'AST-LIB-STUDY-02','file':'02_single_seated_eye_1190mm_640.png','camera_position_m':[2.50,-3.65,1.190],'target_m':[-.10,-.10,.650],'lens_mm':42,'camera_height_m':1.190,'camera_label':'Seated-height camera, Z1.190m'}]
api={r['catalogue_id']:r for r in json.loads((ROOT/'integration_api.json').read_text())}
chair=BASE/'assets/furniture/AST-FUR-002_day_reading_chair.glb'
for v in views:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    glb=next(ROOT.glob(v['catalogue_id']+'_*.glb'));import_glb(glb,prefix=v['catalogue_id']);cam=studio()
    for i,c in enumerate(api[v['catalogue_id']]['approach']['candidate_chairs']):
        import_glb(chair,c['origin_m'],c['rotation_z_degrees'],'QA_reused_chair_'+str(i))
    render(cam,v['file'],v['camera_position_m'],v['target_m'],(640,360),v['lens_mm'])
    v['study_glb_sha256']=hashlib.sha256(glb.read_bytes()).hexdigest();v['chair_glb_sha256']=hashlib.sha256(chair.read_bytes()).hexdigest()
    v['scope']='Blender component evidence from actual imported final GLBs. Camera height is measured, no actor/species-fit acceptance.'
(QA/'eye_context_camera_records.json').write_text(json.dumps(views,indent=2))
print('EYE_HEIGHT_CONTEXTS_COMPLETE',flush=True)
