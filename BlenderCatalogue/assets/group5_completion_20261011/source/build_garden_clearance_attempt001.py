"""Derived care-niche layouts from hash-pinned retained exports; originals untouched.

Original Blender5.1 files need their proper reader. These new Blender4.3 natives
retain the exported geometry/materials and rotate nine existing care parts to
the inner side-wall face. No shell, stock shelf, item count or programme changes.
"""
from pathlib import Path
import bpy, json, hashlib, math
import numpy as np
from mathutils import Matrix

P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
definition=json.loads((ROOT/'Game/data/architecture/SHOPPING_PROMENADE.json').read_text())
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
    G=Matrix(((0,0,-s,-5*s),(0,1,0,0),(s,0,0,-3.56),(0,0,0,1)))
    T=B@G@B.inverted()
    moved=[];before={}
    for ob in bpy.context.scene.objects:
        if ob.type!='MESH':continue
        before[ob.name]=np.array([tuple(ob.matrix_world@v.co) for v in ob.data.vertices])
        if '__garden_care_niche_' in ob.name or '__care_trays_' in ob.name:
            ob.matrix_world=T@ob.matrix_world
            moved.append(ob.name)
    assert len(moved)==9,(row['chunk_id'],moved)
    bpy.context.view_layer.update()
    errors=[];maximum=0.0
    for ob in bpy.context.scene.objects:
        if ob.type!='MESH':continue
        actual=np.array([tuple(ob.matrix_world@v.co) for v in ob.data.vertices])
        expected=before[ob.name]
        if ob.name in moved:
            expected=(np.array(T)@np.column_stack((expected,np.ones(len(expected)))).T).T[:,:3]
        delta=float(np.max(np.abs(actual-expected)))
        maximum=max(maximum,delta)
        if delta>1e-5:errors.append(ob.name)
    assert not errors,errors
    for image in bpy.data.images:
        if image.source=='FILE' and image.has_data and not image.packed_file:image.pack()
    name=row['chunk_id']+'__care_clearance_r001'
    native=source/(name+'.blend');out=exports/(name+'.glb')
    bpy.ops.wm.save_as_mainfile(filepath=str(native))
    bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_texcoords=True,export_materials='EXPORT')
    from shutil import copy2
    copy2(out,runtime/out.name)
    scene=scenes/(row['chunk_id']+'__care_clearance_r001.tscn')
    model='res://assets/models/group5/fitout_clearance/'+out.name
    scene.write_text('[gd_scene load_steps=3 format=3]\n\n'
       +'[ext_resource type="PackedScene" path="'+row['layers']['shell']['path']+'" id="1"]\n'
       +'[ext_resource type="PackedScene" path="'+model+'" id="2"]\n\n'
       +'[node name="AuthoredShoppingChunk" type="Node3D"]\n\n'
       +'[node name="Shell" parent="." instance=ExtResource("1")]\n\n'
       +'[node name="Fitout" parent="." instance=ExtResource("2")]\n')
    rows.append({'chunk_id':row['chunk_id'],'family_index':2,'original_model':row['layers']['fitout']['path'],'original_sha256':original_hash,'original_scene':row['visual_scene'],'scene_path':'res://scenes/group5/'+scene.name,'scene_sha256':hashlib.sha256(scene.read_bytes()).hexdigest(),'model_path':model,'model_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'native':str(native.relative_to(P)),'export':str(out.relative_to(P)),'moved_parts':moved,'mesh_count':len(before),'geometry_error_m':maximum,'godot_matrix_rows':[list(r) for r in G],'UV_contract':'v_new=u_old+5;u_new=-v_old-3.56;y_new=y_old;back contacts existing u=-5.56 inner wall;v extent0.2..2.6','scope':'Nine existing garden-care parts rotate onto the original inner side-wall;all other exported meshes unchanged;no source originals resaved,programme or item count changed'})
assert len(rows)==10
(P/'docs/FITOUT_CLEARANCE.json').write_text(json.dumps({'schema':'astraea.group5.fitout_clearance.v1','rows':rows,'source_provenance':'hash-pinned retained GLBs;new explicitly derived native layouts;original native5.1 and exports immutable','whole_group_accepted':False},indent=2)+'\n')
print('GROUP5_GARDEN_CLEARANCE',len(rows),'parts',sum(len(r['moved_parts']) for r in rows),'geometry error',max(r['geometry_error_m'] for r in rows))
