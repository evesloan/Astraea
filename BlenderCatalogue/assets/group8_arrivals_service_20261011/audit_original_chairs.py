"""Reopen actual originals and compare every copied native mesh and rigid matrix."""
from pathlib import Path
import bpy,json,hashlib
from mathutils import Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];p=json.load(open(W/'PLAN.json'))
def signature(ob):
    me=ob.data;materials=[]
    for m in me.materials:
        bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        materials.append({'roughness':float(bs.inputs['Roughness'].default_value),'metallic':float(bs.inputs['Metallic'].default_value),'packed_images':[hashlib.sha256(n.image.packed_file.data).hexdigest()for n in m.node_tree.nodes if n.type=='TEX_IMAGE']})
    return {'vertices':[list(v.co)for v in me.vertices],'faces':[list(v.vertices)for v in me.polygons],'uv':[[list(v.uv)for v in layer.data]for layer in me.uv_layers],'modifiers':[{'type':m.type,'width':getattr(m,'width',None),'segments':getattr(m,'segments',None),'levels':getattr(m,'levels',None),'show_viewport':m.show_viewport,'show_render':m.show_render}for m in ob.modifiers],'materials':materials}
source=p['source_copies'][0]['source_native'];bpy.ops.wm.open_mainfile(filepath=str(R/source));bpy.context.view_layer.update()
original={o.name:{'signature':signature(o),'matrix':o.matrix_world.copy()}for o in bpy.context.scene.objects if o.type=='MESH'}
bpy.ops.wm.open_mainfile(filepath=str(W/p['native']));bpy.context.view_layer.update();maximum=0
for row in p['source_copies']:
    ob=bpy.data.objects[row['name']];src=original[row['source_name']];assert signature(ob)==src['signature'],row['name']
    expected=Matrix(row['placement_blender'])@src['matrix'];error=max(abs(ob.matrix_world[r][c]-expected[r][c])for r in range(4)for c in range(4));assert error<.0001,(row['name'],error);maximum=max(maximum,error)
report={'status':'PASS','actual_original_meshes':len(original),'rigid_original_staff_operator_chairs':2,'native_meshes_exactly_verified':len(p['source_copies']),'vertices_faces_uv_modifiers_materials_and_packed_bytes_preserved':True,'maximum_rigid_matrix_error':maximum,'source_native_sha256':hashlib.sha256((R/source).read_bytes()).hexdigest(),'candidate_native_sha256':p['native_sha256']}
(W/'EXACT_ORIGINAL_CHAIR_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
