"""Blender read-only source audit and evaluated-geometry cache; never save/render."""
from pathlib import Path
import bpy, hashlib, json, sys
import numpy as np
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'qa/batch06'
FAMILIES=['utility_machines','utility_console','utility_pipework']
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
paths=[Path(x).resolve() for x in args] if args else [p for f in FAMILIES for p in (ROOT/'assets'/f).rglob('*.blend')]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def prop(v):
    if hasattr(v,'to_dict'):return {k:prop(x) for k,x in v.to_dict().items()}
    if hasattr(v,'to_list'):return [prop(x) for x in v.to_list()]
    if isinstance(v,(str,int,float,bool)):return v
    try:return [prop(x) for x in v]
    except TypeError:return str(v)
reports=[]
for path in sorted(paths):
    before=sha(path); bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False)
    deps=bpy.context.evaluated_depsgraph_get();scene=bpy.context.scene
    row={'path':str(path.relative_to(ROOT)),'sha256':before,'blender_version':bpy.app.version_string,
         'units':{'system':scene.unit_settings.system,'scale_length':scene.unit_settings.scale_length},
         'objects':[],'used_materials':[],'used_images':[],'load_success':True}
    materials=set(); triangles=[];labels=[]; all_vertices=[]
    for obj in scene.objects:
        rec={'name':obj.name,'type':obj.type,'parent':obj.parent.name if obj.parent else None,
             'matrix_world':[[float(v) for v in r] for r in obj.matrix_world],
             'properties':{k:prop(v) for k,v in obj.items() if k!='_RNA_UI'},
             'modifiers':[{'name':m.name,'type':m.type,'enabled':m.show_viewport} for m in obj.modifiers]}
        if obj.type in {'MESH','CURVE','FONT'}:
            ev=obj.evaluated_get(deps);mesh=ev.to_mesh();mesh.calc_loop_triangles()
            vs=np.asarray([obj.matrix_world@v.co for v in mesh.vertices]);ts=np.asarray([t.vertices for t in mesh.loop_triangles])
            if len(vs):
                all_vertices.extend(vs);triangles.extend(vs[ts]); labels.extend([obj.name]*len(ts))
                rec.update(evaluated_triangles=len(ts),min_xyz=vs.min(axis=0).tolist(),max_xyz=vs.max(axis=0).tolist())
            rec['source_vertices']=len(obj.data.vertices) if obj.type=='MESH' else None
            rec['uv_layers']=list(mesh.uv_layers.keys());rec['materials']=[m.name for m in mesh.materials if m]
            materials.update(m.name for m in mesh.materials if m);ev.to_mesh_clear()
        row['objects'].append(rec)
    images=set()
    for name in sorted(materials):
        m=bpy.data.materials[name];rec={'name':name,'use_nodes':m.use_nodes,'images':[],'principled':[]}
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
    cache=OUT/('independent_source_geometry_'+path.stem+'.npz')
    np.savez_compressed(cache,triangles=np.asarray(triangles),object_names=np.asarray(labels))
    row['geometry_cache']=str(cache.relative_to(ROOT)); reports.append(row)
    print('INDEPENDENT_SOURCE',path.name,len(row['objects']),len(triangles),'used images',len(images),flush=True)
    (OUT/('independent_source_'+path.stem+'.json')).write_text(json.dumps(row,indent=2)+'\n')
print('Completed',len(reports),'read-only source audits')
