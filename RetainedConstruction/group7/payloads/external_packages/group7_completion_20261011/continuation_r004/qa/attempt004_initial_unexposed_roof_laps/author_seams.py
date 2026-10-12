"""Editable additive seam source, retaining all previous native revisions."""
import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];C=P.parent;R=C.parents[1]
plan=json.loads((P/'docs/SEAM_PLAN.json').read_text());native=P/'source/natives/G7_FiniteSeams_r004.blend'
assert not native.exists(),'Never overwrite an immutable seam native'
for name,want in plan['source_pins'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==want
assert not plan['conservative_original_architecture_hits']
bpy.ops.wm.read_factory_settings(use_empty=True);materials={}
for role,texture,color in [('metal','champagne_metal.png',(.54,.49,.36)),('shell','ivory_enamel.png',(.72,.73,.70))]:
    m=bpy.data.materials.new('G7C4_'+role);m.use_nodes=True;m.diffuse_color=(*color,1);node=m.node_tree.nodes.get('Principled BSDF');node.inputs['Roughness'].default_value=.76
    im=bpy.data.images.load(str(R/'BlenderCatalogue/materials'/texture),check_existing=True);t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=im;m.node_tree.links.new(t.outputs['Color'],node.inputs['Base Color']);materials[role]=m
for row in plan['parts']:
    name=row['name'];me=bpy.data.meshes.new(name);me.from_pydata([(x,-z,y)for x,y,z in row['vertices_world_xyz']],[],row['faces']);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),name;assert bm.calc_volume()>1e-8,name;bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(materials[row['role']]);uv=me.uv_layers.new(name='MetreScaled')
    for f in me.polygons:
        n=f.normal;u=Vector((0,1,0))if abs(n.x)>.8 else Vector((1,0,0));w=n.cross(u)
        for k in f.loop_indices:q=me.vertices[me.loops[k].vertex_index].co;uv.data[k].uv=(q.dot(u),q.dot(w))
    ob['group7_cell']=row['cell'];ob['contact_category']=row['category'];ob['interface_function']=row['function'];ob['engineering_capacity_accepted']=False
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
print('G7_R004_NATIVE_AUTHORED',len(plan['parts']),hashlib.sha256(native.read_bytes()).hexdigest())
