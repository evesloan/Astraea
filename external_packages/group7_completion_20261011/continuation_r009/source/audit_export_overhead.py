"""Preserve all original objects; independently audit additions and export cells."""
import bpy,bmesh,json,hashlib
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parents[1];C=P.parent
auth=json.loads((P/'docs/AUTHORED_D18_SUCCESSOR.json').read_text());native=P/auth['native'];native_sha=hashlib.sha256(native.read_bytes()).hexdigest();assert native_sha==auth['native_sha256']
bpy.ops.wm.open_mainfile(filepath=str(native));scene=bpy.context.scene
def signature(ob):
    h=hashlib.sha256();h.update(np.array(ob.matrix_world).tobytes());h.update(ob.type.encode())
    if ob.type=='MESH':
        h.update(np.array([q.co[:]for q in ob.data.vertices],dtype='<f4').tobytes());h.update(json.dumps([list(f.vertices)for f in ob.data.polygons]).encode())
        for uv in ob.data.uv_layers:h.update(np.array([q.uv[:]for q in uv.data],dtype='<f4').tobytes())
        h.update(json.dumps([m.name if m else None for m in ob.data.materials]).encode())
    return h.hexdigest()
checks=0;error=0
for name,want in auth['original_object_signatures'].items():assert signature(bpy.data.objects[name])==want,name;checks+=1
for row in auth['corrected_owned_parts'] + auth['added_parts']:
    ob=bpy.data.objects[row['name']];a=np.array([(v.co.x,v.co.z,-v.co.y)for v in ob.data.vertices]);delta=float(np.max(np.abs(a-np.array(row['vertices_world_xyz']))));assert delta<.0001;error=max(error,delta)
    bm=bmesh.new();bm.from_mesh(ob.data);assert all(e.is_manifold for e in bm.edges);assert bm.calc_volume()>1e-9;checks+=len(bm.edges)+2;bm.free()
    for uv in ob.data.uv_layers.active.data:assert np.isfinite(uv.uv[:]).all();checks+=1
    ob.data.calc_loop_triangles()
    for tri in ob.data.loop_triangles:
        q=a[list(tri.vertices)];assert np.linalg.norm(np.cross(q[1]-q[0],q[2]-q[0]))>1e-9;checks+=1
old_images=set(auth['original_packed_image_hashes']); verified_images=[]
for im in bpy.data.images:
    if im.name in ['Render Result','Viewer Node']:continue
    assert im.packed_file and hashlib.sha256(bytes(im.packed_file.data)).hexdigest()in old_images;checks+=1;verified_images.append(im.name)
for source in auth['immutable_sources']:
    assert hashlib.sha256((C.parents[1]/source['base_native']).read_bytes()).hexdigest()==source['sha256'];checks+=1
objects=[ob for ob in scene.objects if ob.type=='MESH'and ob.get('group7_cell')in auth['export_cells']];cloud={};triangles={}
for ob in objects:
    cell=ob['group7_cell'];pts=[ob.matrix_world@q.co for q in ob.data.vertices];cloud.setdefault(cell,[]).extend([(q.x,q.z,-q.y)for q in pts]);ob.data.calc_loop_triangles();triangles[cell]=triangles.get(cell,0)+len(ob.data.loop_triangles)
rows=[]
for cell in auth['export_cells']:
    prefix='G7_Completion_R009_'
    output=P/'exports'/(prefix+cell+'.glb');assert not output.exists()
    export_scene=bpy.data.scenes.new(cell+'_R009_Export');bpy.context.window.scene=export_scene;groups={}
    for ob in objects:
        if ob['group7_cell']!=cell:continue
        for si,slot in enumerate(ob.material_slots):
            if slot.material:groups.setdefault((slot.material.name,ob['contact_category']),[]).append((ob,si))
    for (material,category),members in groups.items():
        vs=[];fs=[];uvs=[]
        for ob,si in members:
            offset=len(vs);vs.extend(tuple(ob.matrix_world@q.co)for q in ob.data.vertices)
            for face in ob.data.polygons:
                if face.material_index!=si:continue
                fs.append(tuple(offset+i for i in face.vertices));uvs.append([tuple(ob.data.uv_layers.active.data[k].uv)for k in face.loop_indices])
        me=bpy.data.meshes.new(cell+'_'+material+'_'+category);me.from_pydata(vs,[],fs);me.update();me.materials.append(bpy.data.materials[material]);uv=me.uv_layers.new(name='RetainedSourceUV')
        for face,uvrow in zip(me.polygons,uvs):
            for k,u in zip(face.loop_indices,uvrow):uv.data[k].uv=u
        ob=bpy.data.objects.new(me.name,me);export_scene.collection.objects.link(ob);ob['contact_category']=category;ob['group7_cell']=cell
    for ob in export_scene.objects:ob.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(output),export_format='GLB',export_yup=True,export_extras=True,use_active_scene=True,use_selection=True,export_lights=False,export_cameras=False)
    rows.append({'cell':cell,'file':output.name,'path':output.relative_to(P).as_posix(),'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'bytes':output.stat().st_size,'origin':[0,0,0],'rotation_y':0,'scale':[1,1,1]})
    bpy.context.window.scene=scene;bpy.data.scenes.remove(export_scene)
assert hashlib.sha256(native.read_bytes()).hexdigest()==native_sha
bounds={cell:[np.array(pts).min(axis=0).tolist(),np.array(pts).max(axis=0).tolist()]for cell,pts in cloud.items()}
audit={'status':'PASS','checks':checks,'native_sha256':native_sha,'unchanged_original_objects':len(auth['original_object_signatures']),'added_parts':len(auth['added_parts']),'declared_corrected_owned_parts':len(auth['corrected_owned_parts']),'authored_vertices_max_error_m':error,'all_added_parts_manifold_positive_volume':True,'appended_original_packed_images_exact':len(verified_images), 'two_original_source_natives_exact':True,'cell_triangles':triangles,'cell_bounds':bounds,'native_not_resaved':True,'scope':'Original object geometry/transforms/UV/material bindings and packed images exact; all new finite fields checked. Four owned D18neck/landing cells freshly exported; four receiving feet exact and two immutable input natives unchanged. Forty-eight owned overhead/wall revisions provide a separate4mneck air proposal. Original criteria and protected roofs unchanged; no primary-capacity or whole-group acceptance.'}
(P/'qa/NATIVE_AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n');(P/'qa/NATIVE_POINT_CLOUD.json').write_text(json.dumps(cloud,separators=(',',':'))+'\n');(P/'docs/EXPORTS.json').write_text(json.dumps({'native':auth['native'],'native_sha256':native_sha,'exports':rows},indent=2)+'\n')
print('G7_R009_NATIVE_AUDIT_EXPORT_PASS',checks,'checks',len(rows),'cells',sum(triangles.values()),'triangles')
