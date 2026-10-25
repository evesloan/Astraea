"""Blender background authoring; saves a new native and spatially batched GLB."""
import bpy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[4]
plan = json.loads((ROOT/'PLAN.json').read_text(encoding='utf-8'))
for name, expected in plan['source_pins'].items():
    if hashlib.sha256((REPO/name).read_bytes()).hexdigest() != expected:
        raise RuntimeError('Receiving source changed: '+name)
native = ROOT/'G7_TerminalRoofLinks_r011.blend'
export = ROOT/'G7_TerminalRoofLinks_r011.glb'
if native.exists() or export.exists():
    raise RuntimeError('Preserving existing output; use a new revision for a rebuild')

bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
scene.unit_settings.system='METRIC'
scene['scope']='Paired neck-to-crown gallery candidate; engineering and runtime acceptance pending'
scene['capacity_delta']=0
scene['source_plan_sha256']=hashlib.sha256((ROOT/'PLAN.json').read_bytes()).hexdigest()
parts=bpy.data.collections.new('Editable_Authored_Parts');scene.collection.children.link(parts)
batches=bpy.data.collections.new('Runtime_Spatial_Batches');scene.collection.children.link(batches)
materials={}
for role, texture in [('enamel','ivory_enamel.png'),('metal','champagne_metal.png')]:
    mat=bpy.data.materials.new('G7R11_'+role);mat.use_nodes=True
    bsdf=mat.node_tree.nodes.get('Principled BSDF')
    image=bpy.data.images.load(str(REPO/'BlenderCatalogue/materials'/texture),check_existing=True)
    image.pack()
    tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image;tex.interpolation='Closest'
    mat.node_tree.links.new(tex.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value=.65
    bsdf.inputs['Metallic'].default_value=.35 if role=='metal' else .05
    materials[role]=mat
for role in ['glass','lens']:
    mat=bpy.data.materials.new('G7R11_'+role);mat.use_nodes=True
    bsdf=mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value=(.22,.42,.43,.18) if role=='glass' else (1,.82,.55,1)
    bsdf.inputs['Roughness'].default_value=.22
    if role=='glass':
        bsdf.inputs['Alpha'].default_value=.18
        mat.surface_render_method='DITHERED'
    else:
        bsdf.inputs['Emission Color'].default_value=(1,.76,.4,1)
        bsdf.inputs['Emission Strength'].default_value=1.3
    materials[role]=mat


def make_mesh(name, vertices, faces, role, collection):
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata([(x,-z,y) for x,y,z in vertices],[],faces)
    mesh.update()
    obj=bpy.data.objects.new(name,mesh);collection.objects.link(obj)
    mesh.materials.append(materials[role])
    uv=mesh.uv_layers.new(name='MetricUV')
    for poly in mesh.polygons:
        normal=poly.normal
        axis=max(range(3),key=lambda i:abs(normal[i]))
        uvaxes=[i for i in range(3) if i!=axis]
        for index in poly.loop_indices:
            v=mesh.vertices[mesh.loops[index].vertex_index].co
            uv.data[index].uv=(v[uvaxes[0]]*.3,v[uvaxes[1]]*.3)
    return obj


groups={}
for part in plan['parts']:
    obj=make_mesh(part['name'],part['vertices'],part['faces'],part['role'],parts)
    obj['stable_part_id']='G7R11_'+part['name'];obj['cell']=part['cell']
    obj['role']=part['role'];obj['primary_capacity_accepted']=False
    key=(part['cell'],part['role'])
    vertices,faces=groups.setdefault(key,([],[]));offset=len(vertices)
    vertices.extend(part['vertices']);faces.extend([[offset+i for i in face] for face in part['faces']])
for (cell,role),(vertices,faces) in groups.items():
    obj=make_mesh('G7R11_'+cell+'_'+role,vertices,faces,role,batches)
    obj['cell']=cell;obj['role']=role
    obj['contact_category']='visual_lens' if role=='lens' else 'solid_'+role

# Correct outward winding for both fore and aft segment orientations.
for obj in list(parts.objects)+list(batches.objects):
    import bmesh
    bm=bmesh.new();bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(obj.data);bm.free()
parts.hide_render=True
parts.hide_viewport=True
bpy.ops.object.select_all(action='DESELECT')
for obj in batches.objects: obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,
                          export_extras=True,export_yup=True,export_materials='EXPORT',
                          export_cameras=False,export_lights=False)
# Default native view shows editable parts, not coincident export batches.
parts.hide_viewport=False;parts.hide_render=False
batches.hide_viewport=True;batches.hide_render=True
bpy.ops.wm.save_as_mainfile(filepath=str(native),relative_remap=True)
receipt=dict(native=native.name,export=export.name,parts=len(plan['parts']),batches=len(groups),
             material_roles=list(materials),source_plan_sha256=scene['source_plan_sha256'],
             native_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),
             export_sha256=hashlib.sha256(export.read_bytes()).hexdigest(),
             acceptance='Native/export generated; reopen, runtime and visual checks pending')
(ROOT/'BUILD_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt))
