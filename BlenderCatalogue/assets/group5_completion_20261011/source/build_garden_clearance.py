"""Derived care-niche layouts from hash-pinned retained exports; originals untouched.

Original Blender5.1 files need their proper reader. These new Blender4.3 natives
retain the exported geometry/materials and rotate eleven existing care parts to
the inner side-wall face. No shell, stock shelf, item count or programme changes.
"""
from pathlib import Path
import bpy, json, hashlib, math
import numpy as np
from mathutils import Matrix,Vector

P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
definition=json.loads((ROOT/'Game/data/architecture/SHOPPING_PROMENADE.json').read_text())
geometry_path=ROOT/'BlenderCatalogue/assets/shopping_promenade_20261009/qa/source_geometry.json'
geometry=json.loads(geometry_path.read_text())
source=P/'source/fitout_clearance';source.mkdir(exist_ok=True)
exports=P/'exports/fitout_clearance';exports.mkdir(exist_ok=True)
runtime=ROOT/'Game/assets/models/group5/fitout_clearance';runtime.mkdir(exist_ok=True)
scenes=ROOT/'Game/scenes/group5';scenes.mkdir(exist_ok=True)
B=Matrix(((1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)))
rows=[]
for row in definition['chunks']:
    if row.get('family_index')!=2:continue
    bpy.ops.wm.read_factory_settings(use_empty=True)
    original=ROOT/'Game'/row['layers']['fitout']['path'][6:]
    original_hash=hashlib.sha256(original.read_bytes()).hexdigest()
    assert original_hash==row['layers']['fitout']['sha256']
    bpy.ops.import_scene.gltf(filepath=str(original))
    s=row['front_sign_x']
    G=Matrix(((0,0,-s,-4.7*s),(0,1,0,0),(s,0,0,-3.56),(0,0,0,1)))
    T=B@G@B.inverted()
    moved=[p for p in geometry[row['chunk_id']+'__fitout'] if '__garden_care_niche_' in p['part'] or '__care_trays_' in p['part']]
    assert len(moved)==11
    key=lambda xyz:tuple(round(float(x),5) for x in xyz)
    expected_keys={}
    for part in moved:
        expected_keys.setdefault(part['material'],set()).update(key(v) for v in part['vertices_xyz'])
    found_keys={role:set() for role in expected_keys}
    before={};changed_indices={};topology={}
    for ob in bpy.context.scene.objects:
        if ob.type!='MESH':continue
        before[ob.name]=np.array([tuple(ob.matrix_world@v.co) for v in ob.data.vertices])
        role=ob.name.rsplit('__',1)[-1]
        selected=set()
        for v in ob.data.vertices:
            godot=B.inverted()@(ob.matrix_world@v.co)
            k=key(godot)
            if k in expected_keys.get(role,set()):selected.add(v.index);found_keys[role].add(k)
        changed_indices[ob.name]=selected
        topology[ob.name]=hashlib.sha256(repr(([tuple(p.vertices) for p in ob.data.polygons],[[tuple(v.uv) for v in layer.data] for layer in ob.data.uv_layers])).encode()).hexdigest()
        if not selected:continue
        for face in ob.data.polygons:
            flags=[i in selected for i in face.vertices]
            assert all(flags) or not any(flags),(ob.name,face.index,'mixed original component membership')
        # Runtime exports are bounded material batches. Literal retained source
        # vertex keys identify the complete eleven components within those batches.
        local=ob.matrix_world.inverted()@T@ob.matrix_world
        normal_matrix=local.to_3x3().inverted().transposed()
        normals=[tuple((normal_matrix@ob.data.corner_normals[i].vector).normalized()) if loop.vertex_index in selected else tuple(ob.data.corner_normals[i].vector) for i,loop in enumerate(ob.data.loops)]
        for index in selected:ob.data.vertices[index].co=local@ob.data.vertices[index].co
        ob.data.update();ob.data.normals_split_custom_set(normals)
        for part in moved:
            if part['material']!=role:continue
            keys={key(v) for v in part['vertices_xyz']}
            indices=[i for i in selected if key(B.inverted()@Vector(before[ob.name][i])) in keys]
            if indices:
                group=ob.vertex_groups.new(name=part['part']);group.add(indices,1.0,'REPLACE')
    assert found_keys==expected_keys,(row['chunk_id'],'missing literal source vertex keys')
    bpy.context.view_layer.update()
    errors=[];maximum=0.0
    for ob in bpy.context.scene.objects:
        if ob.type!='MESH':continue
        actual=np.array([tuple(ob.matrix_world@v.co) for v in ob.data.vertices])
        expected=before[ob.name]
        expected=expected.copy()
        indices=sorted(changed_indices[ob.name])
        if indices:expected[indices]=(np.array(T)@np.column_stack((expected[indices],np.ones(len(indices)))).T).T[:,:3]
        delta=float(np.max(np.abs(actual-expected)))
        maximum=max(maximum,delta)
        if delta>1e-5:errors.append(ob.name)
        unchanged_topology=hashlib.sha256(repr(([tuple(p.vertices) for p in ob.data.polygons],[[tuple(v.uv) for v in layer.data] for layer in ob.data.uv_layers])).encode()).hexdigest()==topology[ob.name]
        assert unchanged_topology,ob.name
    assert not errors,errors
    for image in bpy.data.images:
        if image.source=='FILE' and image.has_data and not image.packed_file:image.pack()
    name=row['chunk_id']+'__care_clearance_r002'
    native=source/(name+'.blend');out=exports/(name+'.glb')
    bpy.ops.wm.save_as_mainfile(filepath=str(native))
    bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_texcoords=True,export_materials='EXPORT')
    from shutil import copy2
    copy2(out,runtime/out.name)
    scene=scenes/(row['chunk_id']+'__care_clearance_r002.tscn')
    model='res://assets/models/group5/fitout_clearance/'+out.name
    scene.write_text('[gd_scene load_steps=3 format=3]\n\n'
       +'[ext_resource type="PackedScene" path="'+row['layers']['shell']['path']+'" id="1"]\n'
       +'[ext_resource type="PackedScene" path="'+model+'" id="2"]\n\n'
       +'[node name="AuthoredShoppingChunk" type="Node3D"]\n\n'
       +'[node name="Shell" parent="." instance=ExtResource("1")]\n\n'
       +'[node name="Fitout" parent="." instance=ExtResource("2")]\n')
    rows.append({'chunk_id':row['chunk_id'],'family_index':2,'original_model':row['layers']['fitout']['path'],'original_sha256':original_hash,'source_geometry_sha256':hashlib.sha256(geometry_path.read_bytes()).hexdigest(),'original_scene':row['visual_scene'],'scene_path':'res://scenes/group5/'+scene.name,'scene_sha256':hashlib.sha256(scene.read_bytes()).hexdigest(),'model_path':model,'model_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'native':str(native.relative_to(P)),'export':str(out.relative_to(P)),'moved_parts':[p['part'] for p in moved],'mesh_count':len(before),'geometry_error_m':maximum,'transformed_export_vertices':sum(len(v) for v in changed_indices.values()),'topology_and_UV_unchanged':True,'godot_matrix_rows':[list(r) for r in G],'UV_contract':'v_new=u_old+4.7;u_new=-v_old-3.56;y_new=y_old;back contacts existing u=-5.56 inner wall;v extent-0.1..2.3','scope':'Eleven existing garden-care parts rotate onto the original inner side-wall;all other exported vertices,topology and UV unchanged;new native vertex groups preserve the exact literal part membership;no source originals resaved,programme or item count changed'})
assert len(rows)==10
(P/'docs/FITOUT_CLEARANCE.json').write_text(json.dumps({'schema':'astraea.group5.fitout_clearance.v1','rows':rows,'source_provenance':'hash-pinned retained GLBs;new explicitly derived native layouts;original native5.1 and exports immutable','whole_group_accepted':False},indent=2)+'\n')
print('GROUP5_GARDEN_CLEARANCE',len(rows),'parts',sum(len(r['moved_parts']) for r in rows),'geometry error',max(r['geometry_error_m'] for r in rows))
