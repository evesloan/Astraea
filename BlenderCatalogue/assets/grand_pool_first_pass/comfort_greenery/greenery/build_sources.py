"""Blender source-only authoring. Parent coordinates exactly one two-thread slot.

blender -b -t 2 --python-exit-code 1 --python build_sources.py -- --output candidate_v001
Writes only fresh candidate descendants of its own installed package. Existing
catalogue inputs and Game files stay unchanged; no render, export or recoloring.
"""
import bpy, json, hashlib, argparse, sys, math
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def resolve_pin(p):
    p=Path(p);return p if p.is_absolute() else (HERE/p).resolve()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--only');args=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    output=(HERE/args.output).resolve();assert output.is_relative_to(HERE) and output!=HERE,'Candidate must be a new descendant of its own installed package'
    pins=json.loads((HERE/'INPUT_PINS.json').read_text());contract=HERE/'greenery_contract.json';assert sha(contract)==pins['contract_sha256'];check=json.loads((HERE/'CONTRACT_CHECK_REPORT.json').read_text());assert check['status']=='PASS' and check['contract_sha256']==sha(contract)
    for path,h in pins['immutable_inputs'].items():assert sha(resolve_pin(path))==h,'Changed input '+path
    plan=json.loads(contract.read_text());assets=[a for a in plan['assets'] if args.only is None or a['name']==args.only];assert assets
    for a in assets:assert not (output/a['source']).exists(),'Refusing to overwrite surviving source: '+a['name']
    (output/'source').mkdir(parents=True,exist_ok=True);(output/'qa').mkdir(exist_ok=True);receipt=[]
    for a in assets:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;sc['derivative_name']=a['name'];sc['parent_design_id']=a['parent_design_id'];sc['unique_catalogue_design']=False;sc['contract_sha256']=sha(contract);sc['authorship']='Transparent deterministic source-derived editable meshes. No reference pixels, unchanged-asset scatter, global squash or material recolor.';sc['runtime_acceptance']='PENDING independent source QA, retention, export, matched engine pixels and circulation'
        roles=sorted(set(p['material_role'] for p in a['parts']));library=Path(pins['source_libraries'][a['parent_design_id']]);assert Path(bpy.data.filepath).resolve()!=library.resolve(),'Never load a blend into itself'
        wanted=['ASTRAEA_'+r for r in roles]
        with bpy.data.libraries.load(str(library),link=False) as (src,dst):
            assert set(wanted)<=set(src.materials),'Source material roles missing';dst.materials=wanted
        mats={m.get('astraea_material_role'):m for m in dst.materials};assert set(mats)==set(roles)
        for mat in mats.values():
            for node in mat.node_tree.nodes:
                if node.type=='TEX_IMAGE' and node.image:
                    assert node.image.packed_file,'Pinned source botanical image must already be packed'
        root=bpy.data.objects.new(a['name'],None);sc.collection.objects.link(root);root['parent_design_id']=a['parent_design_id'];root['placement_name']=a['name'];root['placement_world_xyz']=a['position_xyz'];root['support']=a['support'];root['instance_count']=1;root['internal_soil_crown_count']=len(a['root_parts']);root['source_to_gltf']='(x,y,z)->(x,z,-y)';root['collision']='none'
        for p in a['parts']:
            me=bpy.data.meshes.new(p['name']+'_editable');me.from_pydata(p['vertices'],[],p['faces']);me.update();me.materials.append(mats[p['material_role']]);uv=me.uv_layers.new(name='botanical_shape_uv');uv.active_render=True
            assert len(uv.data)==len(p['loop_uvs'])
            for loop,value in zip(uv.data,p['loop_uvs']):loop.uv=value
            for poly in me.polygons:poly.use_smooth=False
            ob=bpy.data.objects.new(p['name'],me);sc.collection.objects.link(ob);ob.parent=root;ob['parent_design_id']=a['parent_design_id'];ob['material_role']=p['material_role'];ob['surface_kind']=p['surface_kind'];ob['shape_controls']=json.dumps(p['shape_controls']);ob['collision']='decorative_noncolliding';ob['provenance']='Recomposed original botanical source topology/formula; exact source material datablock and packed texture retained'
        for m in a['markers']:
            ob=bpy.data.objects.new(m['name'],None);sc.collection.objects.link(ob);ob.parent=root;ob.location=m['point_local'];ob.empty_display_size=.025;ob['physical_part']=m['physical_part'];ob['marker_kind']=m['kind'];ob['expected_local_position']=m['point_local']
        # Objects are linked and the graph updated before any evaluated transform.
        bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();mesh_count=0;triangles=0
        for ob in sc.objects:
            if ob.type!='MESH':continue
            mesh_count+=1;ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();triangles+=len(me.loop_triangles);ev.to_mesh_clear()
        assert mesh_count==a['part_count'] and triangles==a['planned_triangle_count']
        path=output/a['source'];bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True,check_existing=True)
        receipt.append(dict(name=a['name'],source=str(path),source_sha256=sha(path),parts=mesh_count,triangles=triangles,parent_design_id=a['parent_design_id'],source_library=str(library),source_library_sha256=sha(library)))
        print('SOURCE_ONLY_SAVED',a['name'],mesh_count,triangles,flush=True)
    for path,h in pins['immutable_inputs'].items():assert sha(resolve_pin(path))==h,'Input mutated '+path
    report=dict(status='SOURCE_AUTHORED_NOT_YET_QA',contract_sha256=sha(contract),blender_version=bpy.app.version_string,outputs=receipt,no_export=True,no_render=True,write_scope='New candidate descendants of this installed package only; existing source/export and Game inputs unchanged',installed_package=str(HERE),candidate_directory=str(output),game_writes=False)
    target=output/'qa'/('build_receipt_'+(args.only or 'all')+'.json');assert not target.exists();target.write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
