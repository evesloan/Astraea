from pathlib import Path
import bpy,json,hashlib,struct
root=Path(__file__).resolve().parents[4]
definition=json.loads((root/'Game/data/architecture/group5/LARGE_VENUE_LIGHTING.json').read_text())
rows=[]
for venue in definition['venues']:
    native=root/venue['native'];before=hashlib.sha256(native.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(native))
    model=root/'Game'/venue['model_path'][6:];data=model.read_bytes();n=struct.unpack_from('<I',data,12)[0];gltf=json.loads(data[20:20+n])
    materials=[]
    for original in gltf['materials']:
        name=original['name'];m=bpy.data.materials.get(name)
        if m is None:m=bpy.data.materials.get(name.rsplit('.',1)[0])
        if m is None or not m.use_nodes:
            materials.append({'name':name,'status':'HOLD_NATIVE_GRAPH_MISSING'});continue
        node=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
        if node is None:
            materials.append({'name':name,'status':'HOLD_NATIVE_PRINCIPLED_MISSING'});continue
        base=node.inputs['Base Color'];links=list(base.links)
        row={'name':name,'native_material':m.name,'original_export_pbr':original.get('pbrMetallicRoughness',{}),'native_base_color_default':list(base.default_value),'native_base_color_link_nodes':[l.from_node.type for l in links]}
        if len(links)==1 and links[0].from_node.type=='MIX_RGB':
            mix=links[0].from_node
            row.update(blend_type=mix.blend_type,factor=float(mix.inputs[0].default_value),factor_linked=mix.inputs[0].is_linked,color1_link_nodes=[l.from_node.type for l in mix.inputs[1].links],color2=list(mix.inputs[2].default_value),color2_linked=mix.inputs[2].is_linked,use_clamp=mix.use_clamp)
            if mix.blend_type=='MULTIPLY' and not mix.inputs[0].is_linked and not mix.inputs[2].is_linked and len(mix.inputs[1].links)==1 and mix.inputs[1].links[0].from_node.type=='TEX_IMAGE':
                f=float(mix.inputs[0].default_value)
                row['source_texture_multiplier_linear_rgba']=[(1-f)+f*float(c) for c in mix.inputs[2].default_value[:3]]+[1]
                row['status']='EXACT_IMAGE_MULTIPLIER_SUPPORTED'
            else:row['status']='HOLD_COMPLEX_MIX_GRAPH'
        else:row['status']='NO_SELECTED_MULTIPLY_GRAPH'
        materials.append(row)
    assert hashlib.sha256(native.read_bytes()).hexdigest()==before
    rows.append({'programme_key':venue['programme_key'],'native':venue['native'],'native_sha256':before,'original_native_unchanged':True,'model_path':venue['model_path'],'model_sha256':venue['model_sha256'],'materials':materials})
out={'scope':'Read-only original material graph audit;no runtime or source changes;exact supported multipliers only;not complete shader fidelity or visual acceptance','rows':rows}
(Path(__file__).resolve().parents[1]/'qa/LARGE_VENUE_NATIVE_MATERIAL_GRAPHS.json').write_text(json.dumps(out,indent=2)+'\n')
print('GROUP5_NATIVE_MATERIAL_GRAPH_READ_ONLY',[(r['programme_key'],sum(m['status']=='EXACT_IMAGE_MULTIPLIER_SUPPORTED' for m in r['materials'])) for r in rows])
