"""Selected original fixtures only; correct rib intersections in new sources."""
from pathlib import Path
import bpy, json, hashlib
from mathutils import Matrix, Vector

P=Path(__file__).resolve().parents[1]
ROOT=P.parents[2]
recovery={r['programme_key']:r for r in json.loads((P/'qa/VENUE_SOURCE_RECOVERY.json').read_text())['rows']}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def bounds(obj):
    p=[obj.matrix_world@Vector(v) for v in obj.bound_box]
    return [min(v.z for v in p),max(v.z for v in p)]
def data_pin(obj):
    return hashlib.sha256(json.dumps({'vertices':[list(v.co) for v in obj.data.vertices],
        'faces':[list(p.vertices) for p in obj.data.polygons],
        'uvs':[[list(v.uv) for v in layer.data] for layer in obj.data.uv_layers],
        'materials':[m.name if m else None for m in obj.data.materials]},sort_keys=True).encode()).hexdigest()
def export(path):
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',export_yup=True,
        export_texcoords=True,export_materials='EXPORT',export_extras=True)
rows=[]
for key in ['D09_directory_02','D09_directory_07','D09_directory_09']:
    original=P/recovery[key]['native']['recovered_path'];before=sha(original)
    bpy.ops.wm.open_mainfile(filepath=str(original))
    changes=[];selected=set()
    for i in range(4):
        name=f'Room_{i}_39'
        rod=bpy.data.objects[name+'_suspension'];housing=bpy.data.objects[name+'_housing'];lens=bpy.data.objects[name+'_lens']
        rib=bpy.data.objects[f'Rib_{i}_3']
        selected.update([rod,housing,lens])
        original_pins={o.name:data_pin(o) for o in [rod,housing,lens]}
        rod_before=bounds(rod);housing_before=bounds(housing);lens_before=bounds(lens)
        rib_bottom=bounds(rib)[0]
        drop=housing_before[1]-(rib_bottom-.03)
        assert .35<drop<.45,(key,name,drop)
        for o in [housing,lens]:o.matrix_world=Matrix.Translation((0,0,-drop))@o.matrix_world
        height=rod_before[1]-rod_before[0]
        scale=Matrix.Diagonal((1,1,(height+drop)/height,1))
        rod.matrix_world=Matrix.Translation((0,0,rod_before[1]))@scale@Matrix.Translation((0,0,-rod_before[1]))@rod.matrix_world
        bpy.context.view_layer.update()
        assert bounds(housing)[1]<=rib_bottom-.0299
        assert abs(bounds(rod)[1]-rod_before[1])<.00002
        assert bounds(rod)[0]<bounds(housing)[1] and bounds(rod)[0]>bounds(housing)[0]
        assert all(data_pin(o)==original_pins[o.name] for o in [rod,housing,lens])
        changes.append({'fixture':name,'drop_m':drop,'beam':rib.name,'beam_bottom_m':rib_bottom,
            'original_mesh_data_pins':original_pins,'mesh_vertices_faces_uv_materials_unchanged':True,
            'housing_before':housing_before,'housing_after':bounds(housing),
            'lens_before':lens_before,'lens_after':bounds(lens),
            'suspension_before':rod_before,'suspension_after':bounds(rod),
            'ceiling_contact_upper_end_unchanged':True,'housing_to_beam_clearance_m':rib_bottom-bounds(housing)[1]})
    for obj in list(bpy.context.scene.objects):
        if obj not in selected:bpy.data.objects.remove(obj,do_unlink=True)
    for obj in selected:
        obj['origin_native_sha256']=before
        obj['revision']='group5_fixture_clearance_r001'
    bpy.data.orphans_purge(do_recursive=True)
    native=P/'source/venue_fixture_clearance'/(key+'_fixture_clearance_r001.blend')
    out=P/'exports/venue_fixture_clearance'/(key+'_fixture_clearance_r001.glb')
    native.parent.mkdir(exist_ok=True);out.parent.mkdir(exist_ok=True)
    assert not native.exists() and not out.exists(),'Never overwrite a saved revision'
    bpy.ops.wm.save_as_mainfile(filepath=str(native))
    export(out)
    export_sha=sha(out);saved_sha=sha(native)
    bpy.ops.wm.open_mainfile(filepath=str(native))
    repeat=Path('/tmp')/(key+'_fixture_clearance_repeat.glb')
    export(repeat)
    assert sha(repeat)==export_sha
    assert sha(native)==saved_sha and sha(original)==before
    rows.append({'programme_key':key,'original_native':str(original.relative_to(ROOT)),'original_native_sha256':before,
        'native':str(native.relative_to(ROOT)),'native_sha256':saved_sha,'export':str(out.relative_to(ROOT)),
        'export_sha256':export_sha,'runtime_model_path':'res://assets/models/group5/venue_fixture_clearance/'+out.name,
        'source_meshes':12,'replaced_runtime_meshes':12,'fixtures':changes,
        'fresh_native_repeat_export_byte_identical':True,'original_native_unchanged':True,
        'scope':'Four complete original fixture assemblies below existing ribs;housing/lens rigid drops,suspension lower extension with unchanged ceiling top;all unselected originals preserved'})
(P/'docs/VENUE_FIXTURE_CLEARANCE.json').write_text(json.dumps({'status':'PASS','rows':rows,'sources':3,
    'fixture_assemblies':12,'source_meshes':36,'original_native_and_runtime_files_immutable':True,
    'scope':'Explicit selected derivative fixtures;not replacement provenance for original models,engineering sizing or whole-venue acceptance'},indent=2)+'\n')
print('GROUP5_VENUE_FIXTURE_CLEARANCE_PASS',len(rows),36)
