"""DEFERRED source-only adapter of retained comfort greenery build_sources.py.
Parent must coordinate this job. Nothing in this package launches Blender.
Example: blender -b -t 2 --python-exit-code 1 --python build_sources.py -- --output candidate_v001
No render, export, Game/Catalogue writes or material mutation. Never overwrite.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import bpy,json,argparse
from source_common import HERE,CONTRACT,sha,guard_inputs,candidate_path,append_materials,material_signature,material_specs,check_material_spec

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True)
    args=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    pins,plan=guard_inputs();assert len(plan['assets'])==6
    out=candidate_path(args.output);assert not out.exists(),'Preserve surviving candidate: '+str(out)
    out.mkdir();(out/'source').mkdir();(out/'qa').mkdir();records=[];specs=material_specs()
    for a in plan['assets']:
        bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene
        sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
        sc.render.threads_mode='FIXED';sc.render.threads=2
        sc['contract_sha256']=sha(CONTRACT);sc['derivative_name']=a['name'];sc['parent_design_id']='AST-BOT-002'
        sc['unique_catalogue_design']=False;sc['source_formula_lineage']=json.dumps(a['source_formula_lineage'])
        sc['authorship']='Deterministic original source-derived broad-leaf meshes; fitted authored reach, no asset scale/clipping/material recolor'
        sc['runtime_acceptance']='PENDING independent reopen, retention, composed pixels, export and native QA'
        mats,provenance,availability=append_materials(bpy,plan)
        for role,mat in mats.items():check_material_spec(mat,role,specs[role])
        sc['material_provenance_json']=json.dumps(provenance,sort_keys=True)
        root=bpy.data.objects.new(a['name'],None);sc.collection.objects.link(root)
        root['parent_design_id']='AST-BOT-002';root['placement_name']=a['replaces_instance']
        root['placement_world_xyz']=a['position_xyz'];root['placement_yaw_radians']=a['yaw_radians']
        root['support']=a['support'];root['instance_count']=1;root['collision']='none'
        root['source_to_gltf']='(x,y,z)->(x,z,-y), then unchanged runtime Y yaw'
        for p in a['parts']:
            me=bpy.data.meshes.new(p['name']+'_editable');me.from_pydata(p['vertices'],[],p['faces']);me.update()
            me.materials.append(mats[p['material_role']]);uv=me.uv_layers.new(name='botanical_shape_uv');uv.active_render=True
            assert len(uv.data)==len(p['loop_uvs'])
            for loop,value in zip(uv.data,p['loop_uvs']):loop.uv=value
            for poly in me.polygons:poly.use_smooth=False
            ob=bpy.data.objects.new(p['name'],me);sc.collection.objects.link(ob);ob.parent=root
            ob['parent_design_id']='AST-BOT-002';ob['material_role']=p['material_role'];ob['surface_kind']=p['surface_kind']
            ob['shape_controls']=json.dumps(p['shape_controls']);ob['collision']='decorative_noncolliding'
            ob['source_material_library']=provenance[p['material_role']]['library']
        for marker in a['markers']:
            ob=bpy.data.objects.new(marker['name'],None);sc.collection.objects.link(ob);ob.parent=root;ob.location=marker['point_local']
            ob.empty_display_size=.025;ob['physical_part']=marker['physical_part'];ob['marker_kind']=marker['kind']
        bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();count=triangles=0
        for ob in sc.objects:
            if ob.type!='MESH':continue
            count+=1;ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();triangles+=len(me.loop_triangles);ev.to_mesh_clear()
        assert count==a['part_count'] and triangles==a['planned_triangle_count']
        for role,mat in mats.items():assert material_signature(mat)==provenance[role]['material_signature'],'Material changed during source build'
        path=out/a['source'];assert not path.exists()
        bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True,check_existing=True)
        records.append(dict(name=a['name'],source=str(path),source_sha256=sha(path),parts=count,triangles=triangles,material_provenance=provenance,material_library_availability=availability))
        print('SOURCE_AUTHORED_NOT_QA',a['name'],flush=True)
    guard_inputs()
    report=dict(status='SOURCE_AUTHORED_NOT_YET_REOPENED',contract_sha256=sha(CONTRACT),outputs=records,blender_version=bpy.app.version_string,write_scope=str(out),no_export=True,no_render=True,no_game_or_catalogue_write=True)
    (out/'qa/BUILD_RECEIPT.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
