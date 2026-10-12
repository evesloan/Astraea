"""Audit immutable selected source and freshly export four spatial cells."""
import bpy,bmesh,json,hashlib
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parents[1];C=P.parent;R=C.parents[1]
plan=json.loads((P/'docs/SEAM_PLAN.json').read_text());native=P/'source/natives'/plan['native_filename'];native_sha=hashlib.sha256(native.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(native));source=bpy.context.scene;parts={q['name']:q for q in plan['parts']};objects=[ob for ob in source.objects if ob.type=='MESH']
assert len(objects)==len(parts)==64;cloud={};triangles={};checks=0;error=0;material_pins={}
for ob in objects:
    row=parts[ob.name];a=np.array([(q.co.x,q.co.z,-q.co.y)for q in ob.data.vertices]);want=np.array(row['vertices_world_xyz']);assert a.shape==want.shape
    delta=float(np.max(np.abs(a-want)));assert delta<.0001;error=max(error,delta);checks+=len(a)
    assert ob['group7_cell']==row['cell'] and ob['contact_category']==row['category'];assert np.isfinite(a).all()
    bm=bmesh.new();bm.from_mesh(ob.data);assert all(e.is_manifold for e in bm.edges);assert bm.calc_volume()>1e-8;checks+=len(bm.edges)+2;bm.free()
    me=ob.data;me.calc_loop_triangles();cell=row['cell'];cloud.setdefault(cell,[]).extend(a.tolist());triangles[cell]=triangles.get(cell,0)+len(me.loop_triangles)
    assert me.uv_layers.active
    for loop in me.uv_layers.active.data:assert np.isfinite(loop.uv[:]).all();checks+=1
    for tri in me.loop_triangles:
        pts=a[list(tri.vertices)];assert np.linalg.norm(np.cross(pts[1]-pts[0],pts[2]-pts[0]))>1e-9;checks+=1
for image in bpy.data.images:
    if image.name in ['Render Result','Viewer Node']:continue
    assert image.packed_file;packed=bytes(image.packed_file.data);name='BlenderCatalogue/materials/'+Path(image.filepath).name
    assert hashlib.sha256(packed).hexdigest()==plan['source_pins'][name];material_pins[name]=hashlib.sha256(packed).hexdigest();checks+=1
bounds={cell:[np.array(a).min(axis=0).tolist(),np.array(a).max(axis=0).tolist()]for cell,a in cloud.items()};exports=[]
for cell in plan['cells']:
    scene=bpy.data.scenes.new(cell+'_Export');bpy.context.window.scene=scene;groups={}
    for ob in objects:
        if ob['group7_cell']!=cell:continue
        groups.setdefault((ob.data.materials[0].name,ob['contact_category']),[]).append(ob)
    for (material,category),members in groups.items():
        vs=[];fs=[];uvs=[]
        for ob in members:
            offset=len(vs);vs.extend(tuple(ob.matrix_world@q.co)for q in ob.data.vertices)
            for f in ob.data.polygons:fs.append(tuple(offset+i for i in f.vertices));uvs.append([tuple(ob.data.uv_layers.active.data[k].uv)for k in f.loop_indices])
        me=bpy.data.meshes.new(cell+'_'+category);me.from_pydata(vs,[],fs);me.update();me.materials.append(bpy.data.materials[material]);uv=me.uv_layers.new(name='RetainedSourceUV')
        for f,uvrow in zip(me.polygons,uvs):
            for k,u in zip(f.loop_indices,uvrow):uv.data[k].uv=u
        ob=bpy.data.objects.new(me.name,me);scene.collection.objects.link(ob);ob['contact_category']=category;ob['group7_cell']=cell
    for ob in scene.objects:ob.select_set(True)
    file=P/'exports'/('G7_Completion_R004_'+cell+'.glb');assert not file.exists()
    bpy.ops.export_scene.gltf(filepath=str(file),export_format='GLB',export_yup=True,export_extras=True,use_active_scene=True,use_selection=True,export_lights=False,export_cameras=False)
    exports.append({'cell':cell,'file':file.name,'path':file.relative_to(P).as_posix(),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'bytes':file.stat().st_size,'placement':[0,0,0],'rotation_y':0,'scale':[1,1,1]})
    bpy.context.window.scene=source;bpy.data.scenes.remove(scene)
assert hashlib.sha256(native.read_bytes()).hexdigest()==native_sha
audit={'status':'PASS','checks':checks,'parts':64,'native':native.relative_to(P).as_posix(),'native_sha256':native_sha,'max_authored_vertex_error_m':error,'manifold_positive_closed_parts':True,'finite_uvs_and_nonzero_triangles':True,'cell_triangles':triangles,'cell_bounds':bounds,'packed_original_texture_pins':material_pins,'native_resaved_during_audit_or_export':False,'engineering_or_whole_group_accepted':False}
(P/'qa/NATIVE_AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n');(P/'qa/NATIVE_POINT_CLOUD.json').write_text(json.dumps(cloud,separators=(',',':'))+'\n');(P/'docs/EXPORTS.json').write_text(json.dumps({'native':audit['native'],'native_sha256':native_sha,'exports':exports},indent=2)+'\n')
print('G7_R004_NATIVE_AUDIT_EXPORT_PASS',checks,'checks',sum(triangles.values()),'triangles',len(exports),'exports',native_sha)
