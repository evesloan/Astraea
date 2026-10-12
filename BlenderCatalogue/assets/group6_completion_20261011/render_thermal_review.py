"""Actual saved-source thermal courts; roof and optional water cutaway, never saved."""
from pathlib import Path
import json
renderer=Path(__file__).with_name('render_source.py').read_text()
exec(renderer[:renderer.index('records=[]')])
records=[]
roof=bpy.data.objects['AQD__opaque_roof'];roof.hide_render=True
cam.location=xyz((93,59,234));cam.rotation_euler=(xyz((80,46,217))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO';cam.data.ortho_scale=44
for name,drained in [('SOURCE_THERMAL_COURTS011',False),('SOURCE_THERMAL_ENTRY012',True)]:
    hidden=[roof.name]
    if drained:
        for o in s.objects:
            if o.type=='MESH' and o.get('kind')=='water_visual' and not o.hide_render:
                o.hide_render=True;hidden.append(o.name)
    s.render.filepath=str(P/(name+'.png'));bpy.ops.render.render(write_still=True)
    records.append({'name':name,'source':'AquaticCompletion_r013.blend','eye_xyz':[93,59,234],'target_xyz':[80,46,217],'orthographic_scale_m':44,'hidden_for_cutaway':hidden,'presentation':'Actual saved native, neutral Workbench source colors, roof cutaway; second view hides static water to expose real bank/bed/entry geometry. No game, fluid, wheelchair, species, engineering or final-art acceptance.','native_saved':False})
(P/'THERMAL_VIEW_RECEIPT.json').write_text(json.dumps(records,indent=2)+'\n')
