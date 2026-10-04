"""Metadata-only source revision; compare all captured content before and after reload.
Run: blender -b -t 1 --python this_file.py -- /absolute/catalogue/root
"""
import bpy, hashlib, json, runpy, sys
from pathlib import Path
BASE=Path(sys.argv[sys.argv.index('--')+1]).resolve()
QA=BASE/'qa/batch05/cabinet_metadata_revision'
ASSET=BASE/'assets/staff_workbay'
SOURCE=ASSET/'AST-STF-007_supply_work_cabinet.blend'
HINGE='AST-STF-007_door_hinge_pivot'

def simple(value):
    if value is None or isinstance(value,(str,int,float,bool)):return value
    if hasattr(value,'to_dict'):return {k:simple(v) for k,v in value.to_dict().items()}
    if hasattr(value,'to_list'):return [simple(v) for v in value.to_list()]
    if isinstance(value,bpy.types.ID):return {'id_type':value.bl_rna.identifier,'name':value.name_full}
    if isinstance(value,(list,tuple)) or hasattr(value,'__iter__'):
        try:return [simple(v) for v in value]
        except (TypeError,ValueError):pass
    if hasattr(value,'name'):return {'name':value.name,'type':value.bl_rna.identifier}
    if hasattr(value,'bl_rna'):return {'rna_type':value.bl_rna.identifier,'properties':rna(value)}
    return str(value)

def props(value):return {k:simple(v) for k,v in value.items() if not (k=='cycles' and simple(v)=={})}
def rna(value,exclude=()):
    out={}
    for p in value.bl_rna.properties:
        if p.identifier in ('rna_type','id_data','session_uid','cycles') or p.identifier in exclude or p.type=='COLLECTION':continue
        try:out[p.identifier]=simple(getattr(value,p.identifier))
        except (AttributeError,TypeError,ValueError):pass
    return out

def mesh(me):
    me.calc_loop_triangles()
    return {'vertices':[list(v.co) for v in me.vertices],
        'edges':[list(e.vertices) for e in me.edges],
        'loops':[(l.vertex_index,l.edge_index) for l in me.loops],
        'polygons':[(list(p.vertices),p.material_index,p.use_smooth) for p in me.polygons],
        'triangles':[(list(t.vertices),t.polygon_index,list(t.normal)) for t in me.loop_triangles],
        'uv_layers':{u.name:{'active_render':u.active_render,'data':[list(d.uv) for d in u.data]} for u in me.uv_layers},
        'attributes':{a.name:{'domain':a.domain,'data_type':a.data_type,'data':[rna(d) for d in a.data]} for a in me.attributes},
        'materials':[m.name if m else None for m in me.materials],
        'custom_properties':props(me)}

def snapshot():
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
    out={'objects':{},'meshes':{},'evaluated_geometry':{},'materials':{},'images':{},'scenes':{}}
    for ob in sorted(bpy.data.objects,key=lambda x:x.name):
        ip=props(ob)
        if ob.name==HINGE:
            ip.pop('axis',None)
            for k in tuple(ip):
                if k.startswith('hinge_') or k=='coordinate_metadata_revision':ip.pop(k)
        out['objects'][ob.name]={'rna':rna(ob,('bound_box','dimensions','is_updated','is_updated_data','is_updated_transform','is_evaluated','original')),'custom_properties':ip,
            'matrix_world':[list(row) for row in ob.matrix_world],
            'matrix_local':[list(row) for row in ob.matrix_local],
            'matrix_parent_inverse':[list(row) for row in ob.matrix_parent_inverse],
            'modifiers':[rna(m) for m in ob.modifiers],
            'constraints':[rna(c) for c in ob.constraints],
            'vertex_groups':[rna(g) for g in ob.vertex_groups],
            'material_slots':[(s.name,s.link,s.material.name if s.material else None) for s in ob.material_slots]}
        if ob.type=='MESH':
            eo=ob.evaluated_get(dg);me=eo.to_mesh(preserve_all_data_layers=True,depsgraph=dg)
            out['evaluated_geometry'][ob.name]=mesh(me);eo.to_mesh_clear()
    for me in sorted(bpy.data.meshes,key=lambda x:x.name):out['meshes'][me.name]=mesh(me)
    for mat in sorted(bpy.data.materials,key=lambda x:x.name):
        tree=mat.node_tree
        out['materials'][mat.name]={'rna':rna(mat,('is_updated','is_updated_data','is_updated_transform','is_evaluated','original')),'custom_properties':props(mat),
            'nodes':{n.name:{'rna':rna(n),'inputs':{s.identifier:rna(s,('node',)) for s in n.inputs},'outputs':{s.identifier:rna(s,('node',)) for s in n.outputs}} for n in tree.nodes} if tree else None,
            'links':[(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in tree.links] if tree else None}
    for img in sorted(bpy.data.images,key=lambda x:x.name):
        out['images'][img.name]={'filepath':img.filepath,'source':img.source,'colorspace':img.colorspace_settings.name,'size':list(img.size),'packed_sha256':hashlib.sha256(img.packed_file.data).hexdigest() if img.packed_file else None}
    for scene in bpy.data.scenes:out['scenes'][scene.name]={'unit_settings':rna(scene.unit_settings),'objects':sorted(ob.name for ob in scene.objects),'world':scene.world.name if scene.world else None}
    return out

def sha_data(data):return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def sha_file(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    old_sha=sha_file(SOURCE);before=snapshot();old_props=props(bpy.data.objects[HINGE])
    (QA/'source_before_snapshot.json').write_text(json.dumps(before,sort_keys=True,separators=(',',':'))+'\n')
    module=runpy.run_path(str(ASSET/'build_staff_workbay.py'))
    module['set_hinge_metadata'](bpy.data.objects[HINGE])
    bpy.context.preferences.filepaths.save_version=0
    # Explicitly write all datablocks, preserving the five unused packed staff tiles
    # that normal save/reload would purge. No fake-user flags are added.
    all_ids=set()
    for prop in bpy.data.bl_rna.properties:
        if prop.type=='COLLECTION':
            for block in getattr(bpy.data,prop.identifier):
                if isinstance(block,bpy.types.ID) and not isinstance(block,(bpy.types.WindowManager,bpy.types.Screen,bpy.types.WorkSpace)):all_ids.add(block)
    bpy.data.libraries.write(str(SOURCE),all_ids,path_remap='NONE',fake_user=False,compress=False)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    after=snapshot();new_props=props(bpy.data.objects[HINGE])
    rows={k:{'before_sha256':sha_data(before[k]),'after_sha256':sha_data(after[k]),'unchanged':before[k]==after[k],'count':len(after[k])} for k in before}
    report={'revision':'hinge-frame-metadata-02','method':'Open reviewed source; change only hinge custom properties through generator helper; write all existing datablocks at same path without remapping or fake-user changes, retaining unused packed tiles; reopen final source and compare semantic content. Both base and evaluated mesh coordinates/topology/normals/UV/attributes, material graphs, packed images, object hierarchy/transforms/modifiers/constraints and scene units are captured.','source_before_sha256':old_sha,'source_after_sha256':sha_file(SOURCE),'components':rows,'legacy_hinge_custom_properties':old_props,'current_hinge_custom_properties':new_props,'unqualified_axis_absent':'axis' not in new_props,'all_invariants_unchanged':all(row['unchanged'] for row in rows.values())}
    (QA/'source_preservation_report.json').write_text(json.dumps(report,indent=2)+'\n')
    if before!=after:
        (QA/'source_after_snapshot.json').write_text(json.dumps(after,sort_keys=True,separators=(',',':'))+'\n')
        raise AssertionError('Non-metadata source content changed; inspect snapshots')
    assert 'axis' not in new_props
    for k,v in module['HINGE_METADATA'].items():assert new_props[k]==v,(k,new_props[k],v)
    print('PASS source geometry/material/hierarchy/transform invariants unchanged after metadata-only save and reload')
    print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
