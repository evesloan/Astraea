"""Reload final editable sources, inspect evaluated support/contact and UV data."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1]
report=[]
def bounds(ob):
    dg=bpy.context.evaluated_depsgraph_get();e=ob.evaluated_get(dg);me=e.to_mesh();p=[ob.matrix_world@v.co for v in me.vertices];e.to_mesh_clear()
    return {'min_m':[min(v[i] for v in p) for i in range(3)],'max_m':[max(v[i] for v in p) for i in range(3)]}
for src in sorted((BASE/'source').glob('AST-*.blend')):
    bpy.ops.wm.open_mainfile(filepath=str(src));mesh=[o for o in bpy.data.objects if o.type=='MESH'];bb={o.name:bounds(o) for o in mesh};lo=[min(b['min_m'][i] for b in bb.values()) for i in range(3)];hi=[max(b['max_m'][i] for b in bb.values()) for i in range(3)];rec=json.loads((BASE/f'{src.stem}.manifest.json').read_text());checks={}
    checks['source_matches_manifest_bounds']=all(abs(a-b)<1e-6 for a,b in zip(lo+hi,rec['bounds_blender_z_up']['min_m']+rec['bounds_blender_z_up']['max_m']))
    checks['all_semantic_parts_have_uv']=all(o.data.uv_layers.active and o.data.uv_layers.active.name=='metric_material_uv' for o in mesh)
    checks['all_objects_identity_scale']=all(all(abs(k-1)<1e-6 for k in o.scale) for o in mesh)
    checks['no_light_objects']=not any(o.type=='LIGHT' for o in bpy.data.objects)
    checks['top_anchor_plane_zero']=abs(hi[2])<1e-6
    checks['example_headroom_at_least_2_65']=3.3+lo[2]>=2.65
    contact={}
    if src.stem!='AST-STF-006':
        for index in(1,2):
            beam=bb[f'support_{index}_formed_crossbeam'];rail=bb['formed_left_return_lip_rail'];nut=bb[f'support_{index}_-1_beam_retaining_nut']
            contact[f'beam_{index}_to_rail_z_gap_m']=rail['min_m'][2]-beam['max_m'][2];contact[f'nut_{index}_to_beam_z_gap_m']=beam['min_m'][2]-nut['max_m'][2]
        checks['beams_touch_rails']=all(abs(v)<1e-6 for k,v in contact.items() if 'to_rail' in k)
        checks['nuts_touch_beams']=all(abs(v)<1e-6 for k,v in contact.items() if 'to_beam' in k)
        checks['all_rungs_support_cable_bases']=all(abs(b['max_m'][2]-(-.388))<1e-6 for n,b in bb.items() if n.startswith('ladder_rung'))
    else:
        for index in(1,2):
            drop=bb[f'fixture_mount_{index}_folded_drop'];plate=bb[f'fixture_mount_{index}_ceiling_plate'];saddle=bb[f'fixture_mount_{index}_housing_saddle'];body=bb['formed_enamel_channel_with_return_lips']
            contact[f'drop_{index}_ceiling_plate_overlap_m']=drop['max_m'][2]-plate['min_m'][2];contact[f'drop_{index}_saddle_overlap_m']=saddle['max_m'][2]-drop['min_m'][2];contact[f'saddle_{index}_housing_overlap_m']=body['max_m'][2]-saddle['min_m'][2]
        checks['mounts_form_continuous_path']=all(v>=-1e-6 for v in contact.values())
        lens=bb['continuous_opal_prismatic_lens'];guard=[b['max_m'][2] for n,b in bb.items() if n.startswith('lens_guard_longitudinal')];contact['lens_to_bottom_guard_vertical_gap_m']=lens['min_m'][2]-max(guard)
        checks['bottom_guard_clears_lens']=contact['lens_to_bottom_guard_vertical_gap_m']>.03
    report.append({'asset':src.stem,'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'bounds':{'min_m':lo,'max_m':hi},'checks':checks,'contact_measurements':contact,'named_semantic_parts':len(mesh),'non_destructive_modifiers':sum(len(o.modifiers) for o in mesh),'passed':all(checks.values()),'part_bounds':bb})
(BASE/'qa/source_reload_checks.json').write_text(json.dumps({'method':'Blender reload each final compressed source; evaluate modifiers; inspect named part bounds','assets':report,'all_passed':all(r['passed'] for r in report)},indent=2)+'\n');print([(r['asset'],r['passed'],r['checks']) for r in report])
