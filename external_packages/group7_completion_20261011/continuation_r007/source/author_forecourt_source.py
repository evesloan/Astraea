"""Author new native with rigid original plant bindings; never resave originals."""
import bpy, bmesh, json, hashlib, math
from pathlib import Path
from mathutils import Vector
import numpy as np

P = Path(__file__).resolve().parents[1]
C = P.parent
R = C.parents[1]
plan = json.loads((P / 'docs/BOTANICAL_PLAN.json').read_text())
parts = json.loads((P / 'docs/ARCHITECTURE_PARTS.json').read_text())['parts']
for name, want in plan['source_pins'].items():
    assert hashlib.sha256((R / name).read_bytes()).hexdigest() == want, name
native = P / 'source/natives' / plan.get('native_filename','G7_ForeGardenCourts_r007.blend')
assert not native.exists(), 'Never overwrite immutable source revision'
native.parent.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
materials = {}
for role, texture, color in [('stone', 'warm_stone.png', (.56,.53,.44)),
                             ('metal', 'champagne_metal.png', (.54,.49,.36)),
                             ('soil', 'botanical/botanical_soil.png', (.18,.14,.1)),
                             ('wood', 'warm_walnut.png', (.40,.29,.16)),
                             ('roof', 'ivory_enamel.png', (.72,.73,.70)),
                             ('bark', 'botanical/botanical_bark.png', (.32,.24,.16)),
                             ('jade', 'botanical/botanical_leaf_jade.png', (.19,.39,.22)),
                             ('sage', 'botanical/botanical_leaf_sage.png', (.36,.48,.28)),
                             ('olive', 'botanical/botanical_leaf_olive.png', (.28,.39,.17))]:
    mat = bpy.data.materials.new('G7C7_' + role)
    mat.use_nodes = True
    bs = mat.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Roughness'].default_value = .76
    path = R / 'BlenderCatalogue/materials' / texture
    if not path.exists(): path = R / 'BlenderCatalogue/materials/warm_stone.png'
    image = bpy.data.images.load(str(path), check_existing=True)
    node = mat.node_tree.nodes.new('ShaderNodeTexImage'); node.image = image; node.interpolation = 'Closest'
    mat.node_tree.links.new(node.outputs['Color'], bs.inputs['Base Color'])
    if role in ['jade','sage','olive']: mat.use_backface_culling = False
    materials[role] = mat
mat = bpy.data.materials.new('G7C7_opal');mat.use_nodes = True
bs = mat.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value = (1,.94,.82,1)
bs.inputs['Emission Color'].default_value = (1,.88,.64,1);bs.inputs['Emission Strength'].default_value = 1.4
materials['opal'] = mat
for part in parts:
    mesh = bpy.data.meshes.new(part['name'])
    mesh.from_pydata([(x,-z,y) for x,y,z in part['vertices_world_xyz']], [], part['faces']);mesh.update()
    bm = bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    if not part.get("open_foliage", False):
        assert all(e.is_manifold for e in bm.edges), part['name']
        # Evaluate volume in double precision around a local origin. The thin
        # soil/belt faces use world-space float coordinates; their measured
        # quantization allowance is bounded by two 10-micrometre face offsets.
        center = np.mean(np.array([v.co[:] for v in bm.verts], dtype=float), axis=0)
        volume = 0.0
        for face in bm.faces:
            points = np.array([v.co[:] for v in face.verts], dtype=float) - center
            for j in range(1, len(points) - 1):
                volume += float(np.dot(points[0], np.cross(points[j], points[j+1]))) / 6
        assert volume > 1e-8, part['name']
        depth = max(q[1] for q in part['vertices_world_xyz']) - min(q[1] for q in part['vertices_world_xyz'])
        volume_tolerance = max(.00004, 2 * (part['volume_m3'] / depth) * .00001)
        assert abs(volume - part['volume_m3']) < volume_tolerance, (part['name'], volume, part['volume_m3'], volume_tolerance)
    else:
        assert part["category"] == "visual_foliage" and part["role"] in ["jade", "sage", "olive"]
    bm.to_mesh(mesh);bm.free()
    ob = bpy.data.objects.new(part['name'], mesh);bpy.context.collection.objects.link(ob)
    mesh.materials.append(materials[part['role']]);uv = mesh.uv_layers.new(name='MetreScaled')
    for f in mesh.polygons:
        n=f.normal;u=Vector((0,1,0)) if abs(n.x)>.8 else Vector((1,0,0));w=n.cross(u)
        for k in f.loop_indices:
            v=mesh.vertices[mesh.loops[k].vertex_index].co
            uv.data[k].uv=part['uv_per_vertex'][mesh.loops[k].vertex_index] if 'uv_per_vertex' in part else (v.dot(u),v.dot(w))
    ob['group7_cell']=part['cell'];ob['contact_category']=part['category'];ob['new_room_id']=False
    if part.get('new_tree_source'): ob['original_tree_hierarchy_source']=json.dumps({key:part[key]for key in ['parent_path','editable_control_path_local_xyz','control_radii_m']if key in part},separators=(',',':'))

templates={};bindings=[]
hidden=bpy.data.collections.new('IMMUTABLE_ORIGINAL_BINDING_TEMPLATES');bpy.context.scene.collection.children.link(hidden)
hidden.hide_render=True;hidden.hide_viewport=True
def signature(ob):
    h=hashlib.sha256();h.update(np.array([v.co[:] for v in ob.data.vertices],dtype='<f4').tobytes())
    h.update(json.dumps([list(f.vertices) for f in ob.data.polygons]).encode())
    for uv in ob.data.uv_layers:h.update(np.array([q.uv[:] for q in uv.data],dtype='<f4').tobytes())
    return h.hexdigest()
for file in sorted({q['file'] for q in plan['plants']}):
    before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(R/'Game/assets/models'/file))
    added=list(set(bpy.data.objects)-before);mesh_objects=[q for q in added if q.type=='MESH']
    templates[file]=[]
    for ob in mesh_objects:
        world=ob.matrix_world.copy()
        ob.parent=None;ob.matrix_world=world
        for collection in list(ob.users_collection):collection.objects.unlink(ob)
        hidden.objects.link(ob)
        templates[file].append((ob,signature(ob)))
    for ob in added:
        if ob.type!='MESH':bpy.data.objects.remove(ob,do_unlink=True)
for row in plan['plants']:
    cell=row['cell']
    root=bpy.data.objects.new(row['id'],None);bpy.context.collection.objects.link(root)
    at=row['position'];root.location=(at[0],-at[2],at[1]);root.rotation_euler.z=row['yaw']
    names=[]
    for template,want in templates[row['file']]:
        assert signature(template)==want
        ob=template.copy();ob.data=template.data;ob.name=row['id']+'__'+template.name
        bpy.context.collection.objects.link(ob);ob.parent=root
        ob['group7_cell']=cell;ob['retained_original_family']=row['file']
        ob['contact_category']='solid_tree_bark' if 'bark' in template.name and row['layer']=='canopy' else 'visual_foliage'
        ob['rigid_original_mesh_signature']=want;names.append(ob.name)
    bindings.append({**row,'cell':cell,'source_sha256':plan['source_pins']['Game/assets/models/'+row['file']], 'mesh_nodes':names})
bpy.context.view_layer.update()
for row in plan['lights']:
    data=bpy.data.lights.new(row['id'],'SPOT');data.energy=220;data.color=row['color'];data.spot_size=math.radians(row['angle']*2)
    data.use_custom_distance=True;data.cutoff_distance=row['range']
    ob=bpy.data.objects.new(row['id'],data);bpy.context.collection.objects.link(ob);x,y,z=row['position'];ob.location=(x,-z,y);ob['fixture_source']=row['source_hardware']
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
report={'status':'SOURCE_AUTHORED_ORIGINALS_RIGID', 'native':native.relative_to(P).as_posix(),
        'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(), 'architectural_parts':sum(not q.get('new_tree_source',False) for q in parts),'source_mesh_parts':len(parts),'new_original_tree_mesh_parts':sum(q.get('new_tree_source',False)for q in parts),
        'original_family_bindings':bindings,'terrace_cells':[q['id'] for q in plan['terraces']],
        'template_mesh_signatures':{file:{ob.name:want for ob,want in rows}for file,rows in templates.items()},
        'all_source_pins_exact':True,'originals_resaved':False,'whole_group_accepted':False}
(P/'docs/AUTHORED_SOURCE.json').write_text(json.dumps(report,indent=2)+'\n')
print('G7_R007_SOURCE',len(parts),'architecture parts',len(bindings),'rigid bindings',report['native_sha256'])
