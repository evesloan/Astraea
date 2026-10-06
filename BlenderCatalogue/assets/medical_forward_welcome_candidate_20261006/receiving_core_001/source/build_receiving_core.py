"""Bounded D05 port receiving derivative. Existing source and Game remain untouched."""
from pathlib import Path
import bpy,bmesh,json,hashlib,math
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
CAT=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
SPEC=json.loads((ROOT/'qa/APPROVED_RECEIVING_SCOPE.json').read_text())
SOURCE=Path(SPEC['existing_editable_source'])
SOURCE_OUT=ROOT/'source'/SPEC['new_source_basename'];EXPORT_OUT=ROOT/'exports'/SPEC['new_export_basename']
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not SOURCE_OUT.exists() and not EXPORT_OUT.exists(),'Never overwrite a surviving derivative'
assert sha(SOURCE)==SPEC['existing_source_sha256']
assert sha(SPEC['existing_runtime_export'])==SPEC['existing_export_sha256']
registry=json.loads((CAT/'catalogue_manifest.json').read_text());rows=[x for x in registry['assets'] if x['catalogue_id']=='AST-CIR-005']
assert len(rows)==1 and rows[0]['family']=='primary_atrium_core'
registry_hash=sha(CAT/'catalogue_manifest.json')
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))

def normal(value):
    if hasattr(value,'to_list'):return value.to_list()
    if isinstance(value,(list,tuple)):return [normal(v) for v in value]
    if isinstance(value,(str,int,float,bool)) or value is None:return value
    try:return list(value)
    except TypeError:return str(value)

def object_record(o):
    row={'type':o.type,'matrix_world':[list(v) for v in o.matrix_world],'parent':o.parent.name if o.parent else None,'extras':{k:normal(o[k]) for k in o.keys()},'modifiers':[(m.name,m.type) for m in o.modifiers]}
    if o.type=='MESH':
        me=o.data;row.update(vertices=[list(v.co) for v in me.vertices],polygons=[list(p.vertices) for p in me.polygons],uv={u.name:[list(x.uv) for x in u.data] for u in me.uv_layers},materials=[m.name if m else None for m in me.materials],material_indices=[p.material_index for p in me.polygons])
    return hashlib.sha256(json.dumps(row,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def material_record():
    out={}
    for m in bpy.data.materials:
        nodes=[]
        if m.use_nodes:
            for n in m.node_tree.nodes:
                d={'name':n.name,'type':n.type,'inputs':[(s.name,normal(s.default_value)) for s in n.inputs if hasattr(s,'default_value')]}
                if n.type=='TEX_IMAGE' and n.image:
                    im=n.image;d['image']={'name':im.name,'size':list(im.size),'packed':hashlib.sha256(bytes(im.packed_file.data)).hexdigest() if im.packed_file else None}
                nodes.append(d)
            links=[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links]
        else:links=[]
        out[m.name]={'nodes':nodes,'links':links}
    return out

before={o.name:object_record(o) for o in bpy.context.scene.objects};materials_before=material_record()
changed=SPEC['changed_existing_nodes'];assert all(n in bpy.data.objects for n in changed)
mats={'ivory_enamel':bpy.data.objects[changed[0]].data.materials[0],'warm_walnut':bpy.data.objects[changed[1]].data.materials[0]}
for name,expected in [(changed[0],[-7.88,-7.72,21,26.76,-445,-412]),(changed[1],[-7.685,-7.635,21.12,21.78,-445,-412])]:
    ob=bpy.data.objects[name];points=[ob.matrix_world@v.co for v in ob.data.vertices]
    actual=[min(p.x for p in points),max(p.x for p in points),min(p.z for p in points),max(p.z for p in points),-max(p.y for p in points)-432,-min(p.y for p in points)-432]
    assert all(abs(a-b)<3e-5 for a,b in zip(actual,expected)),(name,actual)
for name in changed:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)

for part in SPEC['new_parts']:
    name=part['name'];assert name not in bpy.data.objects
    b=part['world_bounds_xyz'];x0,x1=b['x'];y0,y1=b['y'];z0,z1=b['z']
    points=[(x,-(z+432),y) for y in [y0,y1] for x,z in [(x0,z0),(x1,z0),(x1,z1),(x0,z1)]]
    faces=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    me=bpy.data.meshes.new(name);me.from_pydata(points,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(mats[part['retained_material_role']]);o['parent_design_id']='AST-CIR-005';o['derivative_scope']='bounded D05 medical receiving aperture';o['source_role']=part['source_role']
    uv=me.uv_layers.new(name='MetreScaled')
    for face in me.polygons:
        n=face.normal.normalized();u=(Vector((1,0,0))-n*n.x).normalized() if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u)
        for k in face.loop_indices:
            p=me.vertices[me.loops[k].vertex_index].co;uv.data[k].uv=(p.dot(u),p.dot(v))

bpy.context.view_layer.update()
after={o.name:object_record(o) for o in bpy.context.scene.objects}
preserved=set(before)-set(changed);assert all(after[n]==before[n] for n in preserved)
assert set(before)-set(after)==set(changed)
assert set(after)-set(before)=={p['name'] for p in SPEC['new_parts']}
assert material_record()==materials_before
bpy.context.preferences.filepaths.save_version=0;bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE_OUT))
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(EXPORT_OUT),export_format='GLB',export_yup=True,export_extras=True,use_selection=True,export_cameras=False,export_lights=False)
assert sha(SOURCE)==SPEC['existing_source_sha256'] and sha(SPEC['existing_runtime_export'])==SPEC['existing_export_sha256']
assert sha(CAT/'catalogue_manifest.json')==registry_hash
report={'scope':'Source/export candidate only; not installed, no floor or clinical/repair mechanics.','catalogue_id':'AST-CIR-005','new_unique_design_count':0,'source':str(SOURCE_OUT),'source_sha256':sha(SOURCE_OUT),'export':str(EXPORT_OUT),'export_sha256':sha(EXPORT_OUT),'generator_sha256':sha(__file__),'source_preimage':str(SOURCE),'source_preimage_sha256':SPEC['existing_source_sha256'],'runtime_preimage_sha256':SPEC['existing_export_sha256'],'removed':changed,'added':[p['name'] for p in SPEC['new_parts']],'preserved_object_count':len(preserved),'unchanged_object_sha256':{n:before[n] for n in sorted(preserved)},'material_graphs_and_packed_images_unchanged':True,'material_graphs_and_packed_images_sha256':hashlib.sha256(json.dumps(materials_before,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'receiving_spec':SPEC}
(ROOT/'qa/SOURCE_PRESERVATION.json').write_text(json.dumps(report,indent=2)+'\n')
print('MEDICAL_RECEIVING_SOURCE_READY',len(preserved),len(SPEC['new_parts']),sha(EXPORT_OUT),flush=True)
