"""Append retained programme to build_core()'s unsaved Blender scene.
Callable only: never open/save a scene, export, render, or launch any process.
"""
import sys,json,hashlib,importlib.util
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from programme_common import S,CORE,FULL,MEDIA,SIGNS,sha,read,verify_inputs,source_inventory,display_frames,sign_frames,arrow_spec,B,G

def load_named_objects(bpy, path, select):
    """Keep immutable requested names: Blender replaces its transfer list in place."""
    with bpy.data.libraries.load(str(path),link=False)as(src,dst):
        requested=tuple(select(tuple(src.objects)))
        assert requested and len(set(requested))==len(requested)
        assert all(isinstance(n,str)for n in requested)and set(requested)<=set(src.objects)
        dst.objects=list(requested)  # Never hand Blender our identity tuple.
    loaded=tuple(dst.objects)
    assert len(loaded)==len(requested)and all(loaded),'Incomplete source-object append'
    return dict(zip(requested,loaded))

def append_retained_programme(core_plan_path=CORE):
    import bpy,bmesh
    from mathutils import Matrix,Vector
    plan=verify_inputs(core_plan_path);gate=read(S/'PROGRAMME_REVIEW.json')
    assert gate['status']=='PASS_PURE_RETAINED_PROGRAMME'and gate['core_plan_sha256']==sha(core_plan_path),'Pure programme gate must pass this exact plan'
    assert gate['inputs_sha256']==sha(S/'INPUT_PINS.json')
    scene=bpy.context.scene
    assert scene.get('source_plan_sha256')==sha(core_plan_path),'Call build_core.build_core() first'
    expected={p['name']for p in plan['parts']};assert expected<={o.name for o in scene.objects}
    assert 'SOURCE_ONLY_RetainedProgramme'not in bpy.data.collections,'Do not append twice to an existing scene'
    spec=importlib.util.spec_from_file_location('retained_material_fingerprint',FULL/'source_common.py');common=importlib.util.module_from_spec(spec);spec.loader.exec_module(common)
    plain=common.plain
    def properties(ob):return {str(k):plain(ob[k])for k in ob.keys()if k!='_RNA_UI'}
    def encoded(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    def mesh_state(ob):
        if ob.type!='MESH':return None
        me=ob.data
        return encoded({'vertices':[list(v.co)for v in me.vertices],'faces':[list(p.vertices)for p in me.polygons],'edges':[list(e.vertices)for e in me.edges],'uvs':{uv.name:[list(d.uv)for d in uv.data]for uv in me.uv_layers},'material_slots':[common.material_signature(m)['sha256']if m else None for m in me.materials],'smooth':[p.use_smooth for p in me.polygons],'modifiers':[(m.name,m.type)for m in ob.modifiers]})
    def frame_matrix(f):
        cols=[B(f[k])for k in ['right_xyz','up_xyz','normal_xyz']];t=B(f['origin_xyz'])
        result=Matrix(tuple(tuple(cols[j][i]for j in range(3))+(t[i],)for i in range(3))+((0,0,0,1),));assert abs(result.to_3x3().determinant()-1)<1e-6;return result
    parent_collection=bpy.data.collections.new('SOURCE_ONLY_RetainedProgramme');scene.collection.children.link(parent_collection);parent_collection['export_excluded']=True
    receipts=[];retained=[];baselines={};source_names={};expected_world={};root_names=[]
    def group(name):
        col=bpy.data.collections.new(name);parent_collection.children.link(col);col['export_excluded']=True;return col
    def append_objects(path,names,col):
        objects=load_named_objects(bpy,path,names)
        for original,ob in objects.items():
            assert ob.type in {'EMPTY','MESH'},('Unexpected source type',original,ob.type)
            col.objects.link(ob);source_names[ob]=original;baselines[ob]=mesh_state(ob);ob['retained_original_properties_json']=json.dumps(properties(ob),sort_keys=True);retained.append(ob)
        bpy.context.view_layer.update();return objects
    def provenance(ob,path,family,source_family,instance,support):
        ob['retained_source_file']=str(path);ob['retained_source_sha256']=sha(path);ob['retained_source_object']=source_names[ob];ob['parent_design_id']=family;ob['source_family']=source_family;ob['programme_instance']=instance;ob['support']=support;ob['support_json']=json.dumps([support]);ob['export_excluded']=True;ob['architecture_export_excluded']=True;ob['source_reference_only']=True;ob['new_catalogue_design_id']=False;ob['source_plan_sha256']=sha(core_plan_path)
    for a in source_inventory(plan):
        path=Path(a['source']);r=a['reservation'];col=group('REFERENCE_'+a['instance_name']);objects=append_objects(path,lambda available:available,col)
        root=objects[a['source_root']];assert root.type=='EMPTY'and root.parent is None
        assert all(ob is root or ob.parent==root for ob in objects.values()),'Unexpected retained botanical hierarchy'
        original_world={ob.name:[list(row)for row in ob.matrix_world]for ob in objects.values()};source_inverse=root.matrix_world.inverted();target=Matrix.Translation(Vector(B(r['position_xyz'])))@Matrix.Rotation(r['yaw_radians'],4,'Z')
        expected_world.update({ob:target@source_inverse@ob.matrix_world for ob in objects.values()});expected_world[root]=target
        root.name=a['instance_name'];root.matrix_world=target;root_names.append(root.name)
        for original,ob in objects.items():
            if ob!=root:ob.name=a['instance_name']+'__'+original
            provenance(ob,path,a['parent_design_id'],a['family'],a['instance_name'],r['soil_object'])
            ob['placement_name']=a['instance_name'];ob['placement_world_xyz']=r['position_xyz'];ob['placement_yaw_radians']=r['yaw_radians'];ob['placement_scale_xyz']=[1,1,1];ob['physical_interface_owner']='AST-AQU-016';ob['new_soil_receiver']=r['soil_object']
            if 'physical_part'in ob:ob['physical_part']=a['instance_name']+'__'+ob['physical_part']
        root['original_placement_provenance_json']=json.dumps({'source_asset':a['source_root'],'position_xyz':a['asset']['position_xyz'],'yaw_radians':a['asset'].get('yaw_radians',0),'support':a['asset']['support'],'original_world_matrices':original_world})
        root['collision']='none';receipts.append({'instance':a['instance_name'],'kind':a['kind'],'source':str(path),'source_sha256':sha(path),'meshes':sum(o.type=='MESH'for o in objects.values()),'soil':r['soil_object']})
    # Only the named display collection. Local geometry really is UVN, so replace
    # its UVN root frame directly. Never reinterpret it as ordinary Blender XYZ.
    display_source=MEDIA/'source/AST-LIB-010_pool_leisure_displays.blend';colname='POOL_DISPLAY_market_rest_0_screen'
    with bpy.data.libraries.load(str(display_source),link=False)as(src,dst):
        assert colname in src.collections;dst.collections=[colname]
    col=dst.collections[0];assert col;parent_collection.children.link(col);col.name='REFERENCE_EAST_HousedDisplay';col['export_excluded']=True
    bpy.context.view_layer.update();loaded=list(col.all_objects);assert len(loaded)==27
    roots=[o for o in loaded if o.type=='EMPTY'and o.get('candidate_name')=='market_rest_0_screen'and o.get('parent_design_id')=='AST-LIB-010'];assert len(roots)==1
    root=roots[0];objects={'AST-LIB-010_POOL_market_rest_0_screen':root}
    candidate=next(c for c in read(MEDIA/'source_contract.json')['candidates']if c['name']=='market_rest_0_screen')
    expected_parts={p['name']for p in candidate['parts']}
    for ob in loaded:
        if ob is root:continue
        part=ob.get('part_spec_name');assert ob.type=='MESH'and ob.parent==root and part in expected_parts
        original='M0__'+part;assert original not in objects;objects[original]=ob
    assert len(objects)==27 and {o.get('part_spec_name')for o in loaded if o.type=='MESH'}==expected_parts
    for original,ob in objects.items():
        assert ob is root or(original.startswith('M0__')and ob.parent==root and ob.type=='MESH')
        source_names[ob]=original;baselines[ob]=mesh_state(ob);ob['retained_original_properties_json']=json.dumps(properties(ob),sort_keys=True);retained.append(ob)
    oldf,newf=display_frames(plan);target=frame_matrix(newf);source_inverse=root.matrix_world.inverted();expected_world.update({ob:target@source_inverse@ob.matrix_world for ob in objects.values()});expected_world[root]=target;root.parent=None;root.matrix_world=target;root.name='EAST_HousedDisplay';root_names.append(root.name)
    for original,ob in objects.items():
        if ob!=root:ob.name='EAST_Display__'+original
        provenance(ob,display_source,'AST-LIB-010','library_use','EAST_HousedDisplay','EAST_Display_AngledReceiver')
        ob['placement_frame_json']=json.dumps(newf);ob['original_source_frame_json']=json.dumps(oldf);ob['support_owner']='AST-AQU-016'
        if 'contact_json'in ob:ob['contact_json']=json.dumps({'receiver':'EAST_Display_AngledReceiver','rear_plane_local_n':-.17999389648434772,'new_frame':newf,'original_contact_saved_in':'retained_original_properties_json'})
    receipts.append({'instance':'EAST_HousedDisplay','kind':'single_housed_display','source':str(display_source),'source_sha256':sha(display_source),'meshes':26,'retained_artwork':'SunCorp lagoon, original packed image/material graph','future_derivative':'Extract only this display after separate approval; never duplicate four-display assembly'})
    signs=sign_frames(plan)
    for s in signs:
        path=Path(s['source']);prefix='PWF_'+s['id']+'_';col=group('REFERENCE_'+s['instance_name']);objects=append_objects(path,lambda names:[n for n in names if n==s['source_root']or n.startswith(prefix)or n.startswith('DATUM_PWF_'+s['id']+'_')],col)
        root=objects[s['source_root']];old_world={ob:ob.matrix_world.copy()for ob in objects.values()};old_frame=frame_matrix(s['old_frame']);new_frame=frame_matrix(s['new_frame']);root.parent=None;root.matrix_parent_inverse=Matrix.Identity(4);root.matrix_world=new_frame;root.name=s['instance_name'];root_names.append(root.name);expected_world.update({ob:new_frame@old_frame.inverted()@old_world[ob] for ob in objects.values()});expected_world[root]=new_frame
        for original,ob in objects.items():
            if ob!=root:
                # Historical sign children carry old world placements even though
                # their parent is an identity empty. Convert through old sign frame.
                local=old_frame.inverted()@old_world[ob];ob.parent=root;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_basis=local;ob.name='EAST_'+original
            provenance(ob,path,'AST-RES-001','residential_wayfinding_bay',s['instance_name'],'EAST_Lift_AftMountingField')
            ob['child_source_family_id']='AST-RES-001';ob['source_sign_id']=s['id'];ob['placement_frame_json']=json.dumps(s['new_frame']);ob['original_source_frame_json']=json.dumps(s['old_frame']);ob['outward_normal_xyz']=[0,0,1];ob['right_xyz']=[1,0,0]
            if original.startswith('DATUM_PWF_'):
                local=ob.matrix_basis.copy();local.translation.z=s['physical_rear_local_d'];ob.matrix_basis=local;expected_world[ob]=new_frame@local;ob['source_receiver']='EAST_Lift_AftMountingField';ob['mount_datum_adjustment']='Original source frame retained; contact depth follows unchanged pad back at the new actual field'
        root['source_mounts']=json.dumps({'receiver':'EAST_Lift_AftMountingField','surface_z':s['mount_surface_z'],'rear_local_d':s['physical_rear_local_d'],'physical_contact':'Both original FixedPads meet flat field; retained pad geometry unchanged'})
        if s['id']=='threshold_lift':
            a=arrow_spec(s);outline=a['outline_uv'];n=len(outline);vs=[(x,y,z)for z in a['depth_d']for x,y in outline];fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)]
            me=bpy.data.meshes.new(a['name']+'_editable');me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);assert bm.calc_volume(signed=True)>0;bm.to_mesh(me);bm.free();me.update()
            mat=objects[a['material_from']].data.materials[0];me.materials.append(mat);uv=me.uv_layers.new(name='MetreScaled_RetainedRole');tile=mat.get('meters_per_tile_uv',[1,1])
            for face in me.polygons:
                axis=max(range(3),key=lambda i:abs(face.normal[i]));axes=[i for i in range(3)if i!=axis]
                for li in face.loop_indices:
                    v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/tile[0],v[axes[1]]/tile[1])
            ob=bpy.data.objects.new(a['name'],me);col.objects.link(ob);ob.parent=root;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_basis=Matrix.Identity(4);ob['parent_design_id']='AST-RES-001';ob['child_source_family_id']='AST-RES-001';ob['source_family']='residential_wayfinding_bay';ob['programme_instance']=s['instance_name'];ob['source_sign_id']=s['id'];ob['semantic_role']='closed_directional_arrow';ob['route_projection_json']=json.dumps(a);ob['export_excluded']=True;ob['architecture_export_excluded']=True;ob['support']='EAST_PWF_threshold_lift_MapBacking';ob['collision_contract']='visual_only_glyph_or_fastener'
        receipts.append({'instance':s['instance_name'],'kind':'retained_sign','source':str(path),'source_sha256':sha(path),'text':s['source_spec']['text_lines'],'meshes':sum(o.type=='MESH'for o in objects.values()),'frame':s['new_frame'],'lettering_geometry_changed':False,'lettering_translation_m':[0,0,0]})
    bpy.context.view_layer.update()
    for ob in retained:
        assert mesh_state(ob)==baselines[ob],('Retained mesh/material/UV changed',ob.name)
        assert ob.matrix_world.to_3x3().determinant()>0,('Mirrored source',ob.name)
        assert max(abs(ob.matrix_world[i][j]-expected_world[ob][i][j])for i in range(4)for j in range(4))<=5e-5,('Source frame mismatch',ob.name)
    assert not any(ob.type in {'LIGHT','CAMERA'}for ob in parent_collection.all_objects)
    scene['retained_programme_receipt_json']=json.dumps(receipts);scene['retained_programme_pure_review_sha256']=sha(S/'PROGRAMME_REVIEW.json');scene['retained_programme_inputs_sha256']=sha(S/'INPUT_PINS.json');scene['status']='Combined editable source block-in; independent source reopen and visual review pending'
    verify_inputs(core_plan_path)
    return {'collection':parent_collection.name,'instances':receipts,'retained_object_count':len(retained),'root_names':root_names,'object_names':sorted(o.name for o in parent_collection.all_objects),'retained_source_object_fingerprints':{o.name:baselines[o]for o in retained if o.type=='MESH'},'intended_frame_verified':True,'retained_mesh_material_uv_fingerprints_unchanged':True,'source_reopen_required':True,'saved':False,'exported':False,'rendered':False}

def snapshot_retained_programme():
    """Return full evaluated/world and unchanged raw source evidence, never write.
    The combined builder should persist this beside its own build evidence and
    compare a fresh reopened call exactly before any semantic tolerance checks.
    """
    import bpy
    spec=importlib.util.spec_from_file_location('retained_snapshot_fingerprint',FULL/'source_common.py');common=importlib.util.module_from_spec(spec);spec.loader.exec_module(common)
    collection=bpy.data.collections.get('SOURCE_ONLY_RetainedProgramme');assert collection
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();objects=[];parts=[]
    for ob in sorted(collection.all_objects,key=lambda o:o.name):
        row={'name':ob.name,'type':ob.type,'parent':ob.parent.name if ob.parent else None,'matrix_world':[list(r)for r in ob.matrix_world],'matrix_basis':[list(r)for r in ob.matrix_basis],'matrix_parent_inverse':[list(r)for r in ob.matrix_parent_inverse],'properties':{str(k):common.plain(ob[k])for k in sorted(ob.keys())if k!='_RNA_UI'}}
        if ob.type=='MESH':
            me=ob.data;raw={'vertices':[list(v.co)for v in me.vertices],'faces':[list(p.vertices)for p in me.polygons],'uv_layers':{u.name:[list(d.uv)for d in u.data]for u in me.uv_layers},'material_signatures':[common.material_signature(m)for m in me.materials],'smooth':[p.use_smooth for p in me.polygons]};row['raw_source']=raw
            evaluated=ob.evaluated_get(dg);em=evaluated.to_mesh();em.calc_loop_triangles();vs=[G(evaluated.matrix_world@v.co)for v in em.vertices];tris=[[vs[i]for i in t.vertices]for t in em.loop_triangles]
            source=ob.get('retained_source_object','new closed route arrow');instance=ob['programme_instance'];family=ob['parent_design_id'];group='plants'if family.startswith('AST-BOT-')else'display'if family=='AST-LIB-010'else'signs'
            p={'name':ob.name,'vertices':vs,'triangles':tris,'bounds':[list(map(min,zip(*vs))),list(map(max,zip(*vs)))],'group':group,'instance':instance,'source_part':source,'open_surface':ob.get('surface_kind','').startswith('open')or source=='M0__original_pool_leisure_image','source_sha256':ob.get('retained_source_sha256'),'raw_source_sha256':hashlib.sha256(json.dumps(raw,sort_keys=True,separators=(',',':')).encode()).hexdigest()};parts.append(p);row['evaluated_vertices_world_xyz']=vs;row['evaluated_triangle_indices']=[list(t.vertices)for t in em.loop_triangles];evaluated.to_mesh_clear()
        objects.append(row)
    return {'schema':1,'status':'EVALUATED_SOURCE_SNAPSHOT_NOT_REOPENED','core_plan_sha256':bpy.context.scene['source_plan_sha256'],'programme_review_sha256':bpy.context.scene['retained_programme_pure_review_sha256'],'input_pins_sha256':sha(S/'INPUT_PINS.json'),'objects':objects,'parts':parts,'no_save_export_render':True}
