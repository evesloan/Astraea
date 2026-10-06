"""DEFERRED Blender job. Independently snapshot selected saved evaluated source.
Read-only source, all actual corner attributes and parent/local/world frames.
No save/export/render/native invocation. New scratch snapshots only.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(HERE/'vendor')]
import argparse, json
import bpy
import numpy as np
from gate import gate, read, sha, require, write_new, run_path, INPUTS
from snapshot_source import C, props, material
from source_common import material_signature

def selected_snapshot(g,a):
    bpy.ops.wm.open_mainfile(filepath=g['source'], load_ui=False)
    require(bpy.app.version_string==g['blender_version'], 'Unreviewed Blender version')
    bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get(); scene=bpy.context.scene
    inv=sorted([o.name,o.type,o.parent.name if o.parent else None] for o in scene.objects)
    require(inv==read(g['source_inventory'])['object_inventory'], 'Saved source inventory changed')
    objects=[]; mats={}; graphs={}; names=tuple(a['mesh_parts']+a['empty_objects'])
    for name in sorted(names):
        ob=scene.objects[name]; eo=ob.evaluated_get(dg)
        require(not ob.modifiers and not ob.constraints and not ob.animation_data, 'Unexpected dynamic state: '+name)
        mw=np.asarray(eo.matrix_world,dtype=float)
        require(np.linalg.det(mw[:3,:3])>0,'Mirrored/degenerate source frame')
        row=dict(name=name,type=ob.type,parent=ob.parent.name if ob.parent else None,extras=props(ob),
            matrix_basis_blender=np.asarray(ob.matrix_basis,dtype=float).tolist(),
            matrix_parent_inverse_blender=np.asarray(ob.matrix_parent_inverse,dtype=float).tolist(),
            local_matrix_godot=(C@np.asarray(ob.matrix_local,dtype=float)@C.T).tolist(),
            world_matrix_godot=(C@mw@C.T).tolist(), world_origin_godot=(C@mw)[:3,3].tolist())
        if ob.type=='MESH':
            require(row['extras'].get('parent_design_id')==a['parent_design_id'], 'Source family mismatch: '+name)
            me=eo.to_mesh(preserve_all_data_layers=True,depsgraph=dg)
            try:
                me.calc_loop_triangles()
                require(len(me.uv_layers)==1 and me.uv_layers.active is not None, 'Expected one active actual UV layer')
                require(len(me.materials)==1 and me.materials[0] is not None, 'Expected one actual material')
                mat=me.materials[0];require(not mat.animation_data and not mat.node_tree.animation_data,'Animated source material')
                mats[mat.name]=material(mat);graphs[mat.name]=material_signature(mat)
                xyz=np.asarray([tuple(v.co) for v in me.vertices],dtype=float)
                local=(C[:3,:3]@xyz.T).T;world=(C[:3,:3]@((mw[:3,:3]@xyz.T).T+mw[:3,3]).T).T
                normal=np.asarray([tuple(n.vector) for n in me.corner_normals],dtype=float)
                local_normal=(C[:3,:3]@normal.T).T;local_normal/=np.linalg.norm(local_normal,axis=1)[:,None]
                world_normal=(C[:3,:3]@np.linalg.inv(mw[:3,:3]).T@normal.T).T;world_normal/=np.linalg.norm(world_normal,axis=1)[:,None]
                uv=np.asarray([tuple(v.uv) for v in me.uv_layers.active.data],dtype=float);uv[:,1]=1.-uv[:,1]
                row.update(material=mat.name,uv_layer=me.uv_layers.active.name,triangles=len(me.loop_triangles),evaluated_vertices=len(me.vertices),positions=[],local_positions=[],normals=[],local_normals=[],uvs=[],triangle_provenance=[])
                for ti,t in enumerate(me.loop_triangles):
                    require(t.material_index==0, 'Nonzero material slot')
                    vi=list(t.vertices);li=list(t.loops)
                    for key,data,ix in [('positions',world,vi),('local_positions',local,vi),('normals',world_normal,li),('local_normals',local_normal,li),('uvs',uv,li)]:row[key].append(data[ix].tolist())
                    row['triangle_provenance'].append(dict(source_triangle=ti,polygon=t.polygon_index,vertices=vi,loops=li))
                require(row['triangles']==a['expected_mesh_triangles'][name], 'Saved triangulation differs: '+name)
            finally: eo.to_mesh_clear()
        objects.append(row)
    require(sum(x.get('triangles',0) for x in objects)==a['triangles'],'Wrong source triangles')
    require(sha(g['source'])==g['source_sha256'],'Source bytes changed')
    return dict(schema=1,kind='east_gallery_selected',asset=a['name'],source=g['source'],source_sha256=g['source_sha256'],source_bytes_unchanged=True,blender=bpy.app.version_string,
        inputs_sha256=sha(INPUTS),scene_extras=props(scene),scene_inventory=inv,objects=objects,materials=mats,full_material_graphs=graphs,
        parent_design_id=a['parent_design_id'],selection=names,coordinate_frame='glTF/Godot XYZ: Blender (x,y,z) -> (x,z,-y)',
        numeric_method='float64 transformation of actual saved evaluated float32 local coordinates and matrices; no world baking',
        uv_method='Actual evaluated active triangle corner UVs; glTF V = 1 - Blender V',
        light_proposal_path=g['light_proposal'],light_proposal_sha256=sha(g['light_proposal']),
        light_note='Actual source marker positions and unmodified placeholder metadata only; measured proposal is separate and native aim/range/power remain unaccepted.',native_acceptance='NOT_RUN')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',required=True);args=ap.parse_args(sys.argv[sys.argv.index('--')+1:])
    g=gate();out=run_path(args.run);require(not out.exists(),'Preserve surviving runs');out.parent.mkdir(exist_ok=True);out.mkdir();(out/'snapshots').mkdir()
    rows=[]
    for a in g['assets']:
        p=out/'snapshots'/(a['name']+'.json');write_new(p,selected_snapshot(g,a));rows.append(dict(asset=a['name'],snapshot=str(p),snapshot_sha256=sha(p),source_sha256=g['source_sha256']))
        print('READ_ONLY_SELECTED_SOURCE_SNAPSHOT',a['name'],flush=True)
    gate();write_new(out/'SNAPSHOT_RECEIPT.json',dict(status='PASS_FOUR_READ_ONLY_SOURCE_SNAPSHOTS',inputs_sha256=sha(INPUTS),assets=rows,exports_created=False,source_saved=False))
if __name__=='__main__':main()
