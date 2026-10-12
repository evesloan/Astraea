"""Exact evaluated-triangle batching; original r001 native/unbatched export retained."""
from pathlib import Path
from collections import defaultdict
import bpy,json,math,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2]
out=Path('/tmp/G8_ORCHARD_SERVICE_fresh004.glb');assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(W/'OrchardService_r003.blend'))
p=json.load(open(W/'PLAN.json'));records={d['name']:d for d in p['meshes']}
groups=defaultdict(list);dg=bpy.context.evaluated_depsgraph_get()
for ob in list(bpy.context.scene.objects):
    if ob.type!='MESH':continue
    row=records[ob.name];ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles()
    a=row['world_aabb'];cell=(math.floor((a[0]+a[1])/4),math.floor((a[4]+a[5])/4))
    for tri in me.loop_triangles:
        mat=me.materials[tri.material_index];key=(row['programme_key'],mat.name,row['collide'],row['category']=='light_source',*cell)
        vs=[ev.matrix_world @ me.vertices[i].co for i in tri.vertices]
        uv=[tuple(me.uv_layers.active.data[i].uv) for i in tri.loops] if me.uv_layers.active else [(0,0)]*3
        normal_matrix=ev.matrix_world.to_3x3().inverted().transposed()
        ns=[normal_matrix @ me.corner_normals[i].vector for i in tri.loops]
        groups[key].append((vs,uv,ns,mat,ob.name))
    ev.to_mesh_clear()
    print('READ',ob.name,flush=True)
bpy.ops.object.select_all(action='DESELECT')
for ob in bpy.context.scene.objects:
    if ob.type=='EMPTY':ob.select_set(True)
policy={};batches=[]
for n,(key,items) in enumerate(sorted(groups.items())):
    programme,matname,collide,source,x,z=key;name='G8O_BATCH_%04d_%s'%(n,programme)
    vs=[];faces=[];uvs=[];normals=[]
    for v,uv,ns,mat,src in items:
        faces.append(tuple(range(len(vs),len(vs)+3)));vs.extend(v);uvs.extend(uv);normals.extend(ns)
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],faces);me.update();me.materials.append(items[0][3])
    layer=me.uv_layers.new(name='OriginalSourceUV')
    for i,uv in enumerate(uvs):layer.data[i].uv=uv
    for face in me.polygons:face.use_smooth=True
    me.normals_split_custom_set(normals)
    ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.select_set(True)
    role='task_glass' if source else 'source_fittings'
    policy[name]={'collide':collide,'category':'light_source' if source else 'fitting','role':role}
    wv=[(v.x,v.z,-v.y) for v in vs]
    batches.append({'name':name,'programme_key':programme,'world_aabb':[min(v[0] for v in wv),max(v[0] for v in wv),min(v[1] for v in wv),max(v[1] for v in wv),min(v[2] for v in wv),max(v[2] for v in wv)],'triangles':len(items),'source_members':sorted(set(i[4] for i in items)),'material':matname,'collide':collide})
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False,use_selection=True)

expected=json.load(open(W/'PLAN.json'))['model_sha256'];actual=hashlib.sha256(out.read_bytes()).hexdigest();assert actual==expected,(actual,expected)
(W/'FRESH_NATIVE_REPEAT004.json').write_text(json.dumps({'status':'PASS','native':'OrchardService_r003.blend','runtime':'G8_ORCHARD_SERVICE_r004.glb','repeat_sha256':actual,'repeat_identical':True},indent=2)+'\n');print('FRESH ORCHARD EXPORT IDENTICAL',actual)
