"""Export the actual shared assembly book layer missing from shell/furniture maps."""
from pathlib import Path
import bpy,json,hashlib,os
ROOT=Path(__file__).resolve().parents[1];rows=[];revision=os.environ.get('ASTRAEA_PRODUCTION_REVISION','production_r004')
for source in sorted((ROOT/'outputs'/revision).glob('*/assembly.blend')):
    before=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source));dest=source.parent/'detail_props.glb';assert not dest.exists()
    bpy.ops.object.select_all(action='DESELECT');selected=[]
    for ob in bpy.context.scene.objects:
        if ob.type=='MESH' and ob.name.startswith(('SUI_DeskBook_','SUI_TableBook_')):ob.select_set(True);selected.append(ob.name)
    assert 5<=len(selected)<=7
    bpy.ops.export_scene.gltf(filepath=str(dest),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
    assert hashlib.sha256(source.read_bytes()).hexdigest()==before
    rows.append({'prototype':source.parent.name,'source_sha256':before,'parts':selected,'detail_glb_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'source_unchanged':True})
(ROOT/'qa/DETAIL_PROP_EXPORT_RECEIPT.json').write_text(json.dumps({'status':'ACTUAL_ASSEMBLY_DETAIL_LAYER_EXPORTED','prototypes':rows,'scope':'Matches realized shared source props; does not realize different per-unit proposed book-count seeds'},indent=2)+'\n');print('DETAIL_LAYERS_EXPORTED',len(rows))
