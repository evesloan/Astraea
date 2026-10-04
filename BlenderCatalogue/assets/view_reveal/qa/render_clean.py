"""Rerender component evidence with bounded clean raster lighting. No asset edits."""
import bpy, sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'source'))
import build_reveal as build
engine='BLENDER_EEVEE_NEXT'

def setup():
    s=bpy.context.scene;s.render.engine=engine
    if hasattr(s,'eevee'):s.eevee.taa_render_samples=128
    s.render.image_settings.file_format='PNG';s.render.resolution_percentage=100

if '--only-joins' in sys.argv:
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'qa/joins_editable.blend'));setup()
    for o in bpy.data.objects:
        if o.get('module')=='sill':o.location.z=.7
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'qa/joins_editable.blend'),compress=True)
    build.render('join_exploded_1280.png',(4.7,-7,3.6),(0,0,1.7),res=(1280,960),ortho=5.7)
    print('CLEAN_JOINS_COMPLETE');quit()
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'source/AST-VR-01-ASSEMBLY.blend'));setup()
build.render('neutral_640.png',(4.3,-6.8,3.35),(0,0,1.65),ortho=6.8)
if '--test-only' in sys.argv:quit()
build.render('standing_640.png',(0,-5.25,1.65),(0,0,1.65),lens=30)
build.render('seated_640.png',(.45,-5.25,1.15),(.1,0,1.45),lens=30)
build.render('detail_1280.png',(3.6,-4.1,3.6),(.75,-.03,2.25),res=(1280,960),ortho=2.05)
for o in bpy.data.objects:
    if o.type=='CAMERA' and o.name=='QA_ONLY_saved_camera':o.data.ortho_scale=6.8
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source/AST-VR-01-ASSEMBLY.blend'),compress=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'qa/joins_editable.blend'));setup()
for o in bpy.data.objects:
    if o.get('module')=='sill':o.location.z=.7
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'qa/joins_editable.blend'),compress=True)
build.render('join_exploded_1280.png',(4.7,-7,3.6),(0,0,1.7),res=(1280,960),ortho=5.7)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'qa/terminal_editable.blend'));setup()
build.render('terminal_closed_1280.png',(3.3,-3.8,2.6),(.85,0,1.33),res=(1280,960),ortho=1.35)
build.render('terminal_rear_1280.png',(3.3,3.4,2.5),(1.11,0,1.34),res=(1280,960),ortho=.9)
print('CLEAN_RENDERS_COMPLETE')
