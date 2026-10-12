"""Reopen original and candidate native files; compare actual chair data and rigid poses."""
from pathlib import Path
from collections import defaultdict
import bpy,json,hashlib,math
from mathutils import Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];p=json.load(open(W/'PLAN.json'))
def snapshot(ob):
    me=ob.data
    geometry={'vertices':[list(v.co)for v in me.vertices],'polygons':[list(f.vertices)for f in me.polygons],
              'uv':[[list(v.uv)for v in layer.data]for layer in me.uv_layers],
              'modifiers':[{'type':m.type,'width':getattr(m,'width',None),'segments':getattr(m,'segments',None),'levels':getattr(m,'levels',None),'show_viewport':m.show_viewport,'show_render':m.show_render}for m in ob.modifiers]}
    material=[]
    for m in me.materials:
        tex=[]
        for n in m.node_tree.nodes:
            if n.type=='TEX_IMAGE':tex.append(hashlib.sha256(n.image.packed_file.data).hexdigest())
        bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        material.append({'texture_sha256':tex,'roughness':float(bs.inputs['Roughness'].default_value),'metallic':float(bs.inputs['Metallic'].default_value)})
    return geometry,material
bpy.ops.wm.open_mainfile(filepath=str(R/p['source_chair']['path']))
bpy.context.view_layer.update();original=defaultdict(list)
for ob in bpy.context.scene.objects:
    if ob.type!='MESH':continue
    geom,mat=snapshot(ob);key=hashlib.sha256(json.dumps(geom,sort_keys=True).encode()).hexdigest()
    original[key].append({'name':ob.name,'matrix':ob.matrix_world.copy(),'materials':mat})
bpy.ops.wm.open_mainfile(filepath=str(W/p['native']));bpy.context.view_layer.update()
count=0;maximum=0.0
for instance in p['instances']:
    if instance['type']!='original_reading_chair_rigid_copy':continue
    prefix='G8_'+instance['programme_key']+'_'+instance['name']+'_'
    objs=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith(prefix)]
    assert len(objs)==sum(len(v)for v in original.values()),(prefix,len(objs))
    x,y,z=instance['at'];yaw=instance['yaw'];pose=Matrix.Translation((x,-z,y)) @ Matrix.Rotation(-yaw,4,'Z')
    for ob in objs:
        geom,mat=snapshot(ob);key=hashlib.sha256(json.dumps(geom,sort_keys=True).encode()).hexdigest()
        assert key in original,(ob.name,'mesh/faces/UV/modifier mutation')
        candidates=original[key];errors=[]
        for src in candidates:
            expected=pose@src['matrix'];error=max(abs(ob.matrix_world[r][c]-expected[r][c])for r in range(4)for c in range(4))
            if mat==src['materials']:errors.append(error)
        assert errors and min(errors)<.0001,(ob.name,'non-rigid pose or material mutation',errors)
        maximum=max(maximum,min(errors));count+=1
report={'status':'PASS','actual_source_meshes_per_chair':sum(len(v)for v in original.values()),'rigid_chair_copies':sum(i['type']=='original_reading_chair_rigid_copy'for i in p['instances']),'native_chair_meshes_verified':count,'maximum_matrix_error':maximum,'vertices_faces_uv_modifiers_materials_and_packed_texture_bytes_preserved':True,'original_source_sha256':p['source_chair']['sha256'],'candidate_native_sha256':p['native_sha256']}
(W/'EXACT_NATIVE_CHAIR_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
