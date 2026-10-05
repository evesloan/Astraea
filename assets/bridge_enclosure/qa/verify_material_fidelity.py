"""Verify the actual used material parameters and packed texture bytes across both revised exports."""
from pathlib import Path
import bpy,json,hashlib
R=Path(__file__).resolve().parents[1];C=R.parents[1]
def signature(material):
    shader=material.node_tree.nodes.get('Principled BSDF')
    signature={}
    for key in ['Base Color','Metallic','Roughness','Alpha']:
        value=shader.inputs[key].default_value
        signature[key]=[round(v,6)for v in value]if hasattr(value,'__len__')else round(value,6)
    # glTF folds sub-unit emission strength into its color; compare the same emitted RGB.
    color=shader.inputs['Emission Color'].default_value
    strength=shader.inputs['Emission Strength'].default_value
    signature['effective_emission_rgb']=[round(v*strength,6)for v in color[:3]]
    signature['textures']=sorted([{'sha256':hashlib.sha256(node.image.packed_file.data).hexdigest(),'size':list(node.image.size),'interpolation':node.interpolation}for node in material.node_tree.nodes if node.type=='TEX_IMAGE'and node.image],key=lambda x:x['sha256'])
    return signature
report={}
for family,asset_id in [('bridge_platform','AST-CMD-003'),('bridge_enclosure','AST-CMD-004')]:
    root=C/'assets'/family;source=root/'source'/(asset_id+'.blend');export=root/'exports'/(asset_id+'.glb')
    bpy.ops.wm.open_mainfile(filepath=str(source))
    before={m.name:signature(m)for o in bpy.context.scene.objects if o.type=='MESH'for m in o.data.materials}
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    for material in list(bpy.data.materials):bpy.data.materials.remove(material,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(export))
    after={m.name:signature(m)for o in bpy.context.scene.objects if o.type=='MESH'for m in o.data.materials}
    assert before==after,(asset_id,before,after)
    report[asset_id]={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'material_count':len(before),'source_export_parameters_and_packed_texture_bytes_equal':True,'materials':before}
(R/'qa/material_fidelity.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({key:{k:v for k,v in value.items()if k!='materials'}for key,value in report.items()}))
