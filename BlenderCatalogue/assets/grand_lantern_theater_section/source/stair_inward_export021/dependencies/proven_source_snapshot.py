"""Read-only evaluated source capture, run by Blender after the parent job gate clears.

blender -b -t 2 --python snapshot_source.py -- --kind envelope|wayfinding \
  --source checked.blend --output new_snapshot.json
No export, source save, render or runtime mutation. Output must not exist.
"""
import argparse, hashlib, json, sys
from pathlib import Path
import bpy
import numpy as np

C = np.array([[1.,0.,0.,0.],[0.,0.,1.,0.],[0.,-1.,0.,0.],[0.,0.,0.,1.]])
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def serial(value):
    if isinstance(value, (str, bool, int, float)) or value is None: return value
    if hasattr(value, 'to_dict'): return {k:serial(v) for k,v in value.to_dict().items()}
    try: return [serial(v) for v in value]
    except TypeError: return str(value)
def props(ob): return {k:serial(ob[k]) for k in ob.keys() if k != '_RNA_UI'}
def material(mat):
    assert mat.use_nodes and mat.node_tree, 'Non-node material: '+mat.name
    nodes=[]
    for n in mat.node_tree.nodes:
        r={'name':n.name,'type':n.type,'active_output':bool(getattr(n,'is_active_output',False)),
           'inputs':{s.name:serial(s.default_value) for s in n.inputs if hasattr(s,'default_value')}}
        if n.type == 'TEX_IMAGE':
            im=n.image; assert im is not None
            packed=im.packed_file or (im.packed_files[0].packed_file if im.packed_files else None)
            assert packed is not None, 'Image not packed: '+im.name
            raw=bytes(packed.data)
            r['image']={'name':im.name,'size':list(im.size),'channels':im.channels,
                'colorspace':im.colorspace_settings.name,'packed_sha256':hashlib.sha256(raw).hexdigest(),
                'packed_bytes':len(raw),'interpolation':n.interpolation,'extension':n.extension,
                'projection':n.projection}
        nodes.append(r)
    return {'name':mat.name,'extras':props(mat),'double_sided':not mat.use_backface_culling,
            'surface_render_method':getattr(mat,'surface_render_method',None),
            'nodes':nodes,'links':[[l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name] for l in mat.node_tree.links]}

def main():
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=['envelope','wayfinding','media','architecture'],required=True)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);assert not a.output.exists()
    before=sha(a.source);bpy.ops.wm.open_mainfile(filepath=str(a.source),load_ui=False)
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
    scene=bpy.context.scene;objects=[];materials={};excluded=[]
    for ob in sorted(scene.objects,key=lambda ob:ob.name):
        selected=(a.kind in ['envelope','media','architecture'] or ob.name=='AST_RES_001_PoolWayfinding' or bool(ob.get('wayfinding_export')))
        if not selected:
            excluded.append({'name':ob.name,'type':ob.type,'extras':props(ob)});continue
        assert ob.type in ['MESH','EMPTY'] and not ob.get('export_excluded'),ob.name
        eo=ob.evaluated_get(dg);mw=np.asarray(eo.matrix_world,dtype=np.float64)
        r={'name':ob.name,'type':ob.type,'parent':ob.parent.name if ob.parent else None,
           'extras':props(ob),'world_matrix_godot':(C@mw@C.T).tolist(),
           'world_origin_godot':(C@mw)[:3,3].tolist()}
        if ob.type=='MESH':
            me=eo.to_mesh(preserve_all_data_layers=True,depsgraph=dg);me.calc_loop_triangles()
            assert me.uv_layers and me.uv_layers.active, 'Missing corner UV: '+ob.name
            assert len(me.materials)==1 and me.materials[0] is not None
            mat=me.materials[0];materials[mat.name]=material(mat);r['material']=mat.name
            r['uv_layer']=me.uv_layers.active.name
            local=np.array([list(v.co) for v in me.vertices],dtype=np.float64)
            world=(C[:3,:3]@((mw[:3,:3]@local.T).T+mw[:3,3]).T).T
            nm=C[:3,:3]@np.linalg.inv(mw[:3,:3]).T
            normals=np.array([list(n.vector) for n in me.corner_normals],dtype=np.float64)
            normals=(nm@normals.T).T;normals/=np.linalg.norm(normals,axis=1)[:,None]
            uv=np.array([list(v.uv) for v in me.uv_layers.active.data],dtype=np.float64);uv[:,1]=1.0-uv[:,1]
            r['positions']=[];r['local_positions']=[];r['normals']=[];r['uvs']=[]
            for t in me.loop_triangles:
                assert t.material_index==0
                r['positions'].append(world[list(t.vertices)].tolist())
                r['local_positions'].append((C[:3,:3]@local[list(t.vertices)].T).T.tolist())
                r['normals'].append(normals[list(t.loops)].tolist())
                r['uvs'].append(uv[list(t.loops)].tolist())
            r['triangles']=len(me.loop_triangles);r['evaluated_vertices']=len(me.vertices)
            eo.to_mesh_clear()
        objects.append(r)
    assert sha(a.source)==before,'Source bytes changed during read-only snapshot'
    meshes=[o for o in objects if o['type']=='MESH'];triangles=sum(o['triangles'] for o in meshes)
    expected={'envelope':(125,2208),'wayfinding':(111,20796)}.get(a.kind)
    if a.kind=='architecture':expected={'AST-AQU-016_pool_loggia.blend':(273,5436),'AST-AQU-016_pool_focal_end.blend':(78,1140),'AST-AQU-016_pool_roof_composition.blend':(100,1200)}[a.source.name]
    if expected: assert (len(meshes),triangles)==expected, (len(meshes),triangles,expected)
    else: assert len(meshes)==99 and sum(o['type']=='EMPTY' for o in objects)==4
    if a.kind=='envelope': assert sum(o['type']=='EMPTY' for o in objects)==14
    else: assert all(o['extras'].get('export_excluded') for o in excluded)
    data={'schema':1,'kind':a.kind,'source':str(a.source.resolve()),'source_sha256':before,
        'source_bytes_unchanged':True,'blender':bpy.app.version_string,'coordinate_frame':'Godot/glTF XYZ, source Blender (x,-z,y)',
        'numeric_method':'Python float64 multiplication of evaluated saved float32 matrices and mesh coordinates; no new float32 world bake',
        'uv_method':'all evaluated triangle corners, active UV, glTF V = 1 - Blender V',
        'mesh_count':len(meshes),'triangle_count':triangles,'objects':objects,
        'materials':materials,'excluded_objects':excluded}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('x') as f:json.dump(data,f,separators=(',',':'));f.write('\n')
    print(json.dumps({'snapshot':str(a.output),'sha256':sha(a.output),'source_sha256':before,'meshes':len(meshes),'triangles':triangles,'materials':len(materials)}))
if __name__=='__main__':main()
