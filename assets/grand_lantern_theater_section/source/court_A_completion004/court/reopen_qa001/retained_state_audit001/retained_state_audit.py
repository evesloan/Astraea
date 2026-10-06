"""Disposable-session native state/evaluated-geometry comparison. No source saves.
All retained pairs are checked before a single consolidated failure is raised.
"""
from pathlib import Path
import collections, hashlib, json, math, re, time


def canonical(value):
    return json.loads(json.dumps(value, sort_keys=True, allow_nan=False))


def field_differences(a, b, path='$'):
    if isinstance(a, dict) and isinstance(b, dict):
        out=[]
        for key in sorted(set(a)|set(b)):
            if key not in a or key not in b:
                out.append({'path':path+'.'+key,'actual':a.get(key,'<absent>'),'native':b.get(key,'<absent>')})
            else:out.extend(field_differences(a[key],b[key],path+'.'+key))
        return out
    if isinstance(a,list) and isinstance(b,list):
        out=[]
        if len(a)!=len(b):out.append({'path':path+'.length','actual':len(a),'native':len(b)})
        for i,(x,y)in enumerate(zip(a,b)):out.extend(field_differences(x,y,path+'['+str(i)+']'))
        return out
    return [] if a==b else [{'path':path,'actual':a,'native':b}]


def audit_retained_pairs(bpy, pairs, qa_globals, output_dir):
    q=qa_globals; digest=q['digest']; mesh_record=q['mesh_record']; material_record=q['material_record']
    # Stable semantic ID references prevent Blender append-name suffixes from
    # disguising or manufacturing differences in object/action targets.
    actual_ids=collections.defaultdict(list); native_ids=collections.defaultdict(list)
    for row in pairs:
        key=row['asset']+'/'+row['source_name']
        for ob,ids in [(row['actual'],actual_ids),(row['native'],native_ids)]:
            ids[ob].append(key)
            if ob.data is not None:ids[ob.data].append(key+'/data')
            for label,owner in [('object',ob),('data',ob.data),('shape_keys',getattr(ob.data,'shape_keys',None))]:
                ad=getattr(owner,'animation_data',None)
                if ad and ad.action:ids[ad.action].append(key+'/'+label+'/action')
    for ids in [actual_ids,native_ids]:
        for key in ids:ids[key]=sorted(ids[key])
    skip={'rna_type','id_data','original','users','use_fake_user','is_updated','is_updated_data','is_updated_transform','is_evaluated','is_library_indirect','is_embedded_data','is_missing','is_runtime_data','tag','session_uid','execution_time','persistent_uid','error_location','error_rotation','is_valid','is_active','active','active_index'}
    def record(value,ids,trail=(),depth=0,expand_id=False):
        if value is None or isinstance(value,(str,int,float,bool)):return value
        if depth>28:raise ValueError('Authored RNA recursion exceeds supported depth: '+'.'.join(trail))
        if isinstance(value,(set,tuple,list)):return [record(v,ids,trail,depth+1)for v in (sorted(value)if isinstance(value,set)else value)]
        if isinstance(value,bpy.types.ID)and not expand_id:
            ident={'id_type':value.bl_rna.identifier,'semantic_targets':ids.get(value)}
            if isinstance(value,bpy.types.Material):ident['exact_material_graph']=q['graph_record'](value,material_record)
            elif isinstance(value,bpy.types.Image):ident['exact_image']=q['image_record'](value)
            elif isinstance(value,bpy.types.Action):ident['action']=record(value,ids,trail+('action',),depth+1,True)
            elif isinstance(value,bpy.types.NodeTree):ident['node_tree']=record(value,ids,trail+('node_tree',),depth+1,True)
            elif not ident['semantic_targets']:
                # Unknown external ID cannot be certified by a coincidental name.
                raise ValueError('Unmapped authored ID target '+value.bl_rna.identifier+':'+value.name)
            return ident
        if not hasattr(value,'bl_rna'):
            if hasattr(value,'to_list'):return record(value.to_list(),ids,trail,depth+1)
            try:return [record(v,ids,trail,depth+1)for v in value]
            except TypeError:raise ValueError('Unsupported authored value '+type(value).__name__)
        output={'rna_type':value.bl_rna.identifier}
        for prop in value.bl_rna.properties:
            name=prop.identifier
            if name in skip:continue
            if isinstance(value,bpy.types.ID)and name in {'name','name_full','library','override_library','preview','asset_data','weak_library_reference'}:continue
            # Internal readonly back-pointers do not encode authored behavior.
            if prop.type=='POINTER' and prop.is_readonly and name in {'parent','node','owner','from_node','to_node','from_socket','to_socket'}:
                continue
            val=getattr(value,name)
            if prop.type in {'BOOLEAN','INT','FLOAT','STRING','ENUM'}:
                if isinstance(val,set):output[name]=sorted(val)
                elif isinstance(val,(str,int,float,bool)):output[name]=val
                else:output[name]=list(val)
            elif prop.type=='POINTER':output[name]=record(val,ids,trail+(name,),depth+1)
            elif prop.type=='COLLECTION':output[name]=[record(v,ids,trail+(name,),depth+1)for v in val]
        if hasattr(value,'keys'):
            # Modifier custom ID-properties include Geometry Nodes input values.
            try:output['custom_properties']={k:record(value[k],ids,trail+(str(k),),depth+1)for k in value.keys()if k!='_RNA_UI'}
            except TypeError:pass
        return output
    def state(ob,ids):
        return canonical({'modifiers':[record(m,ids)for m in ob.modifiers],
                          'constraints':[record(c,ids)for c in ob.constraints],
                          'object_animation':record(ob.animation_data,ids),
                          'data_animation':record(getattr(ob.data,'animation_data',None),ids),
                          'shape_key_state':record(getattr(ob.data,'shape_keys',None),ids,expand_id=True) if getattr(ob.data,'shape_keys',None) else None})
    descriptors=[]; failures=[]
    for row in pairs:
        key={'asset':row['asset'],'source_name':row['source_name'],'actual_name':row['actual'].name,'native_name':row['native'].name}
        try:
            a=state(row['actual'],actual_ids);b=state(row['native'],native_ids);diffs=field_differences(a,b)
            descriptors.append({**key,'actual_state':a,'native_state':b,'actual_state_sha256':digest(a),'native_state_sha256':digest(b),'exact_differences':diffs})
            if diffs:failures.append({**key,'kind':'authored_state_mismatch','difference_count':len(diffs)})
        except Exception as e:
            descriptors.append({**key,'error':type(e).__name__+': '+str(e)});failures.append({**key,'kind':'authored_state_not_fully_inspected','error':str(e)})
    frame=bpy.context.scene.frame_current; subframe=bpy.context.scene.frame_subframe
    scenes=[];evaluated=[]
    def evaluated_records(scene,field):
        result={};layer=scene.view_layers[0]
        with bpy.context.temp_override(scene=scene,view_layer=layer):
            scene.frame_set(frame,subframe=subframe);layer.update();depsgraph=bpy.context.evaluated_depsgraph_get()
            for row in pairs:
                ob=row[field];key=(row['asset'],row['source_name'])
                if ob.type not in {'MESH','CURVE','FONT'}:continue
                obj=None;mesh=None
                try:
                    obj=ob.evaluated_get(depsgraph)
                    mesh=obj.to_mesh(preserve_all_data_layers=True,depsgraph=depsgraph)
                    if mesh is None:raise ValueError('Evaluated geometry did not produce a mesh')
                    rec=q['canonical_mesh'](mesh,mesh_record)
                    rec['edges']=[list(e.vertices)for e in mesh.edges]
                    rec['polygon_normals']=[list(p.normal)for p in mesh.polygons]
                    rec['corner_normals']=[list(n.vector)for n in mesh.corner_normals]
                    rec['evaluated_matrix_world']=[list(r)for r in obj.matrix_world]
                    if not all(math.isfinite(float(x))for v in rec['vertices']for x in v):raise ValueError('Nonfinite evaluated vertex')
                    result[key]={'record':canonical(rec),'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'uv_layers':list(rec['uvs'])}
                except Exception as e:result[key]={'error':type(e).__name__+': '+str(e)}
                finally:
                    if obj is not None and mesh is not None:obj.to_mesh_clear()
        return result
    try:
        for side in ['actual','native']:
            scene=bpy.data.scenes.new('QA_DISPOSABLE_'+side+'_RETAINED_EVALUATION');scenes.append(scene)
            for ob in {r[side]for r in pairs}:scene.collection.objects.link(ob)
        aa=evaluated_records(scenes[0],'actual');bb=evaluated_records(scenes[1],'native')
        for key in sorted(set(aa)|set(bb)):
            a=aa.get(key,{'error':'absent'});b=bb.get(key,{'error':'absent'})
            row={'asset':key[0],'source_name':key[1]}
            if 'error'in a or 'error'in b:
                row.update({'actual_error':a.get('error'),'native_error':b.get('error')});failures.append({**row,'kind':'evaluated_geometry_not_fully_inspected'})
            else:
                diffs=field_differences(a['record'],b['record']);row.update({'actual_sha256':digest(a['record']),'native_sha256':digest(b['record']),'actual_vertices':a['vertices'],'native_vertices':b['vertices'],'actual_faces':a['faces'],'native_faces':b['faces'],'uv_layers':a['uv_layers'],'exact_difference_count':len(diffs),'first_100_exact_differences':diffs[:100]})
                if diffs:failures.append({**row,'kind':'evaluated_geometry_uv_mismatch'})
            evaluated.append(row)
    finally:
        # Disposable scenes only; original object data, modifiers and source files
        # are neither removed, applied, edited nor saved.
        for scene in scenes:bpy.data.scenes.remove(scene)
    report={'status':'PASS_RETAINED_AUTHORED_AND_EVALUATED_FIDELITY_ONLY'if not failures else'FAIL_RETAINED_AUTHORED_OR_EVALUATED_FIDELITY',
            'source_resaved':False,'source_modifiers_applied_or_removed':False,'frame':frame,'subframe':subframe,
            'prototype_objects':len(pairs),'authored_state_rows':descriptors,'evaluated_geometry_rows':evaluated,'failures':failures,
            'limits':['Disposable viewport dependency-graph evaluation only, no renderer or game engine','Modifier viewport/render flags are compared exactly; render-context evaluation is not claimed','Current saved frame only; complete animation curve/driver/NLA authored state is compared but no animation sweep is claimed','A source-state mismatch or uninspected referenced ID fails; all new-mesh no-modifier checks remain active']}
    output_dir=Path(output_dir);path=output_dir/('RETAINED_STATE_EVALUATED_AUDIT_'+str(time.time_ns())+'.json')
    with path.open('x')as h:json.dump(report,h,indent=2,allow_nan=False);h.write('\n')
    print(json.dumps({'retained_fidelity_status':report['status'],'objects':len(pairs),'evaluated_objects':len(evaluated),'failure_count':len(failures),'report':str(path)}))
    return {'status':report['status'],'report':str(path),'failures':failures,'objects':len(pairs),'evaluated_objects':len(evaluated)}
