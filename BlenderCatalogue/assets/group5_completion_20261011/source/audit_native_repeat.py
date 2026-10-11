"""Fresh saved-native exports compared byte-for-byte with live selected GLBs."""
from pathlib import Path
import bpy,json,hashlib
P=Path(__file__).resolve().parents[1];OUT=Path('/tmp/group5-repeat-exports');OUT.mkdir(exist_ok=True)
components=json.loads((P/'docs/COMPONENTS.json').read_text())
names=[Path(r['native']).stem for r in components]+[r['variant'] for r in json.loads((P/'docs/WAYFINDING_VARIANTS.json').read_text())]
names.append('retail_door_control_r001')
records=[]
for name in names:
    native=P/'source'/(name+'.blend');original=P/'exports'/(name+'.glb')
    before=hashlib.sha256(native.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(native))
    out=OUT/(name+'.glb')
    bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_texcoords=True,export_materials='EXPORT',export_extras=name.startswith('retail_') and 'control' not in name)
    source_materials=[]
    for m in bpy.data.materials:
        if not m.use_nodes:continue
        for n in m.node_tree.nodes:
            if n.type=='TEX_IMAGE' and n.image:
                source_materials.append({'material':m.name,'image':n.image.name,'packed':n.image.packed_file is not None,'packed_sha256':hashlib.sha256(n.image.packed_file.data).hexdigest() if n.image.packed_file else None})
    h=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
    records.append({'native':str(native.relative_to(P)),'native_sha256':before,'native_unchanged':h(native)==before,'export_sha256':h(original),'repeat_sha256':h(out),'byte_identical_repeat':h(out)==h(original),'mesh_count':sum(o.type=='MESH' for o in bpy.context.scene.objects),'packed_original_materials':source_materials})
receipt={'status':'PASS' if all(r['native_unchanged'] and r['byte_identical_repeat'] for r in records) else 'HOLD','selected_natives':records,'blender':bpy.app.version_string,'source_and_runtime_frame':'metre Blender XYZ Z-up -> GLB Y-up','scope':'selected new group5 saved native/exports and packed material evidence; originals never resaved'}
(P/'qa/NATIVE_REPEAT_EXPORT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('GROUP5_NATIVE_REPEAT',receipt['status'],len(records))
