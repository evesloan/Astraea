"""Actual saved-source care bay and annex; documented cutaway, never saved."""
from pathlib import Path
import json,sys
renderer=Path(__file__).with_name('render_source.py').read_text().replace('AquaticCompletion_r013.blend','AquaticCompletion_r015.blend')
exec(renderer[:renderer.index('records=[]')])
records=[]
views=[('SOURCE_AQUATIC_WIDE015',(120,96,279),(78,46,216),88,False),('SOURCE_WATER_CARE016',(90,55,218),(97.6,46.7,210.7),21,True)]
if '--detail-only' in sys.argv:views=views[1:]
for name,eye,target,scale,detail in views:
    hidden=[]
    for o in s.objects:
        hide=o.type=='MESH' and o.name.startswith('AQD__') and any(t in o.name for t in ['opaque_roof','enclosure_','threshold_','east_boundary_','west_portal_header','portal_canopy'])
        if detail and o.name in ['AQ6__continuous_launch_gallery','AQ6__water_care_ceiling','AQ6__water_care_south_wall']:hide=True
        if hide and not o.hide_render:o.hide_render=True;hidden.append(o)
    cam.location=xyz(eye);cam.rotation_euler=(xyz(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=scale
    s.render.filepath=str(P/(name+'.png'));bpy.ops.render.render(write_still=True)
    records.append({'name':name,'source':'AquaticCompletion_r015.blend','eye_xyz':eye,'target_xyz':target,'orthographic_scale_m':scale,'hidden_for_cutaway':[o.name for o in hidden],'presentation':'Actual native source and exact registered gate reference; neutral Workbench geometry/base colors. Detail removes roof/gallery/near bay wall to expose hardware. No game-light/texture/flow/filter/species/engineering/final-art acceptance.','native_saved':False})
    for o in hidden:o.hide_render=False
(P/('WATER_CARE_DETAIL016_RECEIPT.json' if '--detail-only' in sys.argv else 'WATER_CARE_VIEW_RECEIPT.json')).write_text(json.dumps(records,indent=2)+'\n')
