"""Blender read-only source audit and evaluated-geometry cache; never save/render."""
from pathlib import Path
import bpy, hashlib, json, sys
import numpy as np
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
FAMILIES=['housekeeping_equipment','housekeeping_handling']
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
prefix='independent_'
if args and args[0]=='--prefix':prefix=args[1];args=args[2:]
paths=[Path(x).resolve() for x in args] if args else [p for f in FAMILIES for p in (ROOT/'assets'/f).glob('source/*.blend')]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def prop(v):
    if hasattr(v,'to_dict'):return {k:prop(x) for k,x in v.to_dict().items()}
    if hasattr(v,'to_list'):return [prop(x) for x in v.to_list()]
    if isinstance(v,(str,int,float,bool)):return v
    try:return [prop(x) for x in v]
    except TypeError:return str(v)
def driver_signature(data):
    ad=getattr(data,'animation_data',None)
    if not ad:return []
    return [{'data_path':f.data_path,'array_index':f.array_index,'expression':f.driver.expression,'type':f.driver.type,'use_self':f.driver.use_self,'variables':[{'name':v.name,'type':v.type,'targets':[{'id':t.id.name if t.id else None,'data_path':t.data_path,'bone_target':t.bone_target,'transform_type':t.transform_type,'transform_space':t.transform_space}for t in v.targets]}for v in f.driver.variables]}for f in ad.drivers]
def rna_settings(item):
    out={}
    for field in item.bl_rna.properties:
        key=field.identifier
        if key in {'rna_type','name','location','width','width_hidden','height','dimensions','select'} or field.type=='COLLECTION':continue
        try:
            val=getattr(item,key)
            out[key]=getattr(val,'name',None) if field.type=='POINTER' else prop(val)
        except Exception:pass
    return out
def graph(tree):
    if not tree:return None
    return {'nodes':[{'name':n.name,'type':n.bl_idname,'settings':rna_settings(n),'inputs':[{'name':s.name,'identifier':s.identifier,'default':prop(s.default_value) if hasattr(s,'default_value') else None}for s in n.inputs],'outputs':[{'name':s.name,'identifier':s.identifier,'default':prop(s.default_value) if hasattr(s,'default_value') else None}for s in n.outputs]}for n in sorted(tree.nodes,key=lambda n:n.name)],'links':sorted([l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier]for l in tree.links)}
reports=[]
for path in sorted(paths):
    before=sha(path); bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False)
    deps=bpy.context.evaluated_depsgraph_get();scene=bpy.context.scene
    row={'path':str(path.relative_to(ROOT)),'sha256':before,'executed_script_sha256':sha(Path(__file__)),'blender_version':bpy.app.version_string,
         'units':{'system':scene.unit_settings.system,'scale_length':scene.unit_settings.scale_length},
         'scene_properties':{k:prop(v)for k,v in scene.items()if k!='_RNA_UI'},'objects':[],'used_materials':[],'used_images':[],'load_success':True}
    materials=set(); triangles=[];labels=[];matlabels=[]; all_vertices=[]
    for obj in scene.objects:
        rec={'name':obj.name,'type':obj.type,'parent':obj.parent.name if obj.parent else None,
             'matrix_world':[[float(v) for v in r] for r in obj.matrix_world],
             'matrix_basis':[[float(v) for v in r] for r in obj.matrix_basis],
             'matrix_parent_inverse':[[float(v) for v in r] for r in obj.matrix_parent_inverse],
             'visibility':{'hide_render':obj.hide_render,'hide_viewport':obj.hide_viewport},
             'constraints':[rna_settings(c)for c in obj.constraints],
             'properties':{k:prop(v) for k,v in obj.items() if k!='_RNA_UI'},'drivers':driver_signature(obj),
             'modifiers':[{'name':m.name,'type':m.type,'enabled':m.show_viewport} for m in obj.modifiers]}
        if obj.type in {'MESH','CURVE','FONT'}:
            ev=obj.evaluated_get(deps);mesh=ev.to_mesh();mesh.calc_loop_triangles()
            vs=np.asarray([obj.matrix_world@v.co for v in mesh.vertices]);ts=np.asarray([t.vertices for t in mesh.loop_triangles])
            if len(vs):
                all_vertices.extend(vs);triangles.extend(vs[ts]); labels.extend([obj.name]*len(ts));matlabels.extend([mesh.materials[t.material_index].name for t in mesh.loop_triangles])
                rec.update(evaluated_triangles=len(ts),min_xyz=vs.min(axis=0).tolist(),max_xyz=vs.max(axis=0).tolist())
            rec['source_vertices']=len(obj.data.vertices) if obj.type=='MESH' else None
            rec['uv_layers']=list(mesh.uv_layers.keys());rec['materials']=[m.name for m in mesh.materials if m]
            materials.update(m.name for m in mesh.materials if m);ev.to_mesh_clear()
        if obj.type=='MESH':
            raw={'vertices':[list(v.co) for v in obj.data.vertices],'edges':[list(e.vertices) for e in obj.data.edges],'polygons':[list(p.vertices) for p in obj.data.polygons],'material_indices':[p.material_index for p in obj.data.polygons],'materials':[m.name if m else None for m in obj.data.materials],'uv_layers':{uv.name:[list(l.uv)for l in uv.data]for uv in obj.data.uv_layers}}
            raw['smooth_faces']=[p.use_smooth for p in obj.data.polygons]
            raw['sharp_edges']=[e.use_edge_sharp for e in obj.data.edges]
            raw['corner_normals']=[list(n.vector)for n in obj.data.corner_normals]
            raw['mesh_properties']={k:prop(v)for k,v in obj.data.items()if k!='_RNA_UI'}
            rec['editable_mesh_sha256']=hashlib.sha256(json.dumps(raw,sort_keys=True).encode()).hexdigest()
            keys=obj.data.shape_keys
            if keys:
                keydata={'use_relative':keys.use_relative,'keys':[{'name':k.name,'value':k.value,'relative_key':k.relative_key.name,'slider_min':k.slider_min,'slider_max':k.slider_max,'mute':k.mute,'interpolation':k.interpolation,'vertex_group':k.vertex_group,'points':[list(v.co)for v in k.data]}for k in keys.key_blocks],'drivers':driver_signature(keys)}
                rec['shape_keys_sha256']=hashlib.sha256(json.dumps(keydata,sort_keys=True).encode()).hexdigest();rec['shape_key_driver_signature']=keydata['drivers'];rec['shape_keys']=[{k:v for k,v in row.items()if k!='points'}for row in keydata['keys']]
        rec['modifier_settings']=[]
        for mod in obj.modifiers:
            settings={}
            for field in mod.bl_rna.properties:
                if field.identifier=='rna_type' or field.type in {'POINTER','COLLECTION'}:continue
                try:settings[field.identifier]=prop(getattr(mod,field.identifier))
                except Exception:pass
            rec['modifier_settings'].append(settings)
        row['objects'].append(rec)
    images=set()
    for name in sorted(materials):
        m=bpy.data.materials[name];rec={'name':name,'use_nodes':m.use_nodes,'images':[],'principled':[], 'properties':{k:prop(v)for k,v in m.items()if k!='_RNA_UI'},'node_graph':graph(m.node_tree)}
        if m.use_nodes:
            for n in m.node_tree.nodes:
                if n.type=='TEX_IMAGE' and n.image:
                    im=n.image;images.add(im.name);rec['images'].append({'name':im.name,'node_name':n.name,
                        'linked_outputs':[{'from':l.from_socket.name,'to_node':l.to_node.type,'to_input':l.to_socket.name} for o in n.outputs for l in o.links]})
                if n.type=='BSDF_PRINCIPLED':rec['principled'].append({key:prop(n.inputs[key].default_value) for key in ['Base Color','Metallic','Roughness','Alpha']})
        row['used_materials'].append(rec)
    for name in sorted(images):
        im=bpy.data.images[name];row['used_images'].append({'name':name,'size':list(im.size),
          'filepath':im.filepath,'packed':bool(im.packed_file),'packed_sha256':hashlib.sha256(bytes(im.packed_file.data)).hexdigest() if im.packed_file else None})
    row['unused_images']=[im.name for im in bpy.data.images if im.name not in images]
    if all_vertices:
        v=np.asarray(all_vertices);row['bounds_min_m']=v.min(axis=0).tolist();row['bounds_max_m']=v.max(axis=0).tolist();row['dimensions_m']=np.ptp(v,axis=0).tolist()
    row['evaluated_triangles']=len(triangles);row['source_unchanged_after_load']=before==sha(path)
    cache=OUT/(prefix+'source_geometry_'+path.stem+'.npz')
    np.savez_compressed(cache,triangles=np.asarray(triangles),object_names=np.asarray(labels),material_names=np.asarray(matlabels))
    row['geometry_cache']=str(cache.relative_to(ROOT)); reports.append(row)
    print('INDEPENDENT_SOURCE',path.name,len(row['objects']),len(triangles),'used images',len(images),flush=True)
    (OUT/(prefix+'source_'+path.stem+'.json')).write_text(json.dumps(row,indent=2)+'\n')
print('Completed',len(reports),'read-only source audits')
