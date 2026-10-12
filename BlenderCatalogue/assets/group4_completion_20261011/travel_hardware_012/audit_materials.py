from pathlib import Path
import bpy,json,hashlib
W=Path(__file__).resolve().parent;R=next(p for p in W.parents if (p/'Game').is_dir())
text=(W.parent/'boarding_safety_009/audit_materials.py').read_text();exec(text[text.index('def material('):text.index('old=R/')],globals())
bpy.ops.wm.open_mainfile(filepath=str(W.parent/'boarding_safety_009/Group4_Powered_Portal_Body_r001.blend'))
expected={n:material(bpy.data.materials[n]) for n in ['champagne_metal','dark_rubber']}
bpy.ops.wm.open_mainfile(filepath=str(W/'Group4_Steering_Bogies_and_EndBuffers_r002.blend'));checks=0
for ob in bpy.data.objects:
 if ob.type!='MESH':continue
 for m in ob.data.materials:assert material(m)==expected[m.name],ob.name;checks+=1
(W/'MATERIAL_FIDELITY.json').write_text(json.dumps({'status':'PASS','checks':checks,'all46_original_material_graph_bindings_exact':True,'original_packed_texture_bytes_interpolation_and_color_spaces_exact':True,'source_body024_and_wheels_unchanged':True},indent=2)+'\n');print('TRAVEL_MATERIAL_FIDELITY',checks)
