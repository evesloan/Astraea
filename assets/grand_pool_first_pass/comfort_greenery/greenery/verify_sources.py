"""Independent evaluated Blender source QA; no import of authoring functions.

Reopens saved candidates, inspects evaluated vertices/UVs/triangles, actual
material image bytes, physical joins and octagonal soil contacts, then tests
every new triangle against the 120 approved eye/image probes. Never exports.
"""
import bpy,json,hashlib,math,argparse,sys,collections,importlib.util
sys.dont_write_bytecode=True
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
import numpy as np
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def resolve_pin(p):
    p=Path(p);return p if p.is_absolute() else (HERE/p).resolve()
def inside_polygon(p,poly):
    s=[(b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0]) for a,b in zip(poly,poly[1:]+poly[:1])];return min(s)>=-2e-6 or max(s)<=2e-6
def in_box(p,b):return all(b[0][i]-2e-6<=p[i]<=b[1][i]+2e-6 for i in range(3))
def evaluated(ob):
    ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles();v=[ev.matrix_world@q.co for q in me.vertices];tri=[list(t.vertices) for t in me.loop_triangles];polys=[list(f.vertices) for f in me.polygons];uv=[list(x.uv) for x in me.uv_layers.active.data] if me.uv_layers.active else [];ev.to_mesh_clear();return v,tri,polys,uv
def contains(tree,point):
    """Point on surface or inside an actual closed mesh; not a radius claim."""
    p=Vector(point);hit=tree.find_nearest(p)
    if hit[0] is not None and hit[3]<2e-6:return True
    direction=Vector((.731,.419,.538)).normalized();origin=p.copy();count=0
    for _ in range(256):
        loc,normal,idx,distance=tree.ray_cast(origin,direction,100)
        if loc is None:break
        count+=1;origin=loc+direction*.000002
    else:raise AssertionError('Closed solid parity probe did not terminate')
    return count%2==1
def intersects_segment(triangles,a,b):
    o=np.array(a);d=np.array(b)-o;t=np.array(triangles);e1=t[:,1]-t[:,0];e2=t[:,2]-t[:,0];h=np.cross(np.broadcast_to(d,e2.shape),e2);det=np.sum(e1*h,axis=1);good=np.abs(det)>1e-10;inv=np.divide(1.,det,out=np.zeros_like(det),where=good);s=o-t[:,0];u=inv*np.sum(s*h,axis=1);q=np.cross(s,e1);v=inv*np.sum(d*q,axis=1);depth=inv*np.sum(e2*q,axis=1);return bool(np.any(good&(u>=-1e-7)&(v>=-1e-7)&(u+v<=1+1e-7)&(depth>1e-6)&(depth<1-1e-6)))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--candidate',required=True);ap.add_argument('--only');args=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--'in sys.argv else [])
    out=(HERE/args.candidate).resolve();assert out.is_relative_to(HERE);pins=json.loads((HERE/'INPUT_PINS.json').read_text());contract=HERE/'greenery_contract.json';assert sha(contract)==pins['contract_sha256'];plan=json.loads(contract.read_text());assets=[a for a in plan['assets'] if args.only is None or a['name']==args.only];assert assets
    for p,h in pins['immutable_inputs'].items():assert sha(resolve_pin(p))==h,'Changed original input '+p
    geompath=next(resolve_pin(p) for p in pins['immutable_inputs'] if p.endswith('/stock/geometry.py'));geom_spec=importlib.util.spec_from_file_location('retained_glb_reader',geompath);geom_reader=importlib.util.module_from_spec(geom_spec);geom_spec.loader.exec_module(geom_reader)
    archpath=Path(pins['source_libraries']['AST-AQU-016']).parents[1]/'exports/AST-AQU-016.glb';arch=geom_reader.read_glb(archpath);soil_triangles=[t for m in arch['meshes'] if 'botanical_soil' in m['name'] for t in m['triangles']];assert soil_triangles,'Actual exported soil material triangles missing'
    potpath=Path(pins['source_libraries']['AST-BOT-012']).parents[1]/'exports/AST-BOT-012.glb';pot=geom_reader.read_glb(potpath);pot_top=max(q[1] for q in pot['vertices'])
    records=[];all_triangles=[]
    for a in assets:
        path=out/a['source'];assert path.is_file(),'Missing candidate '+str(path);before=sha(path)
        if bpy.data.filepath and Path(bpy.data.filepath).resolve()==path.resolve():bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update();sc=bpy.context.scene;assert sc['contract_sha256']==sha(contract);assert not any(o.type in {'CAMERA','LIGHT'} for o in sc.objects),'No authored renderer or light substitution'
        actual={o.name:o for o in sc.objects if o.type=='MESH'};expected={p['name']:p for p in a['parts']};assert actual.keys()==expected.keys(),a['name']+' semantic mesh names';assert len(sc.objects)==len(actual)+len(a['markers'])+1
        root=bpy.data.objects[a['name']];assert root.parent is None;assert root.matrix_world==Matrix.Identity(4);assert root['parent_design_id']==a['parent_design_id'];assert root['instance_count']==1
        geos={};trees={};tri_count=0;roles=set();vertex_deviations={};closed_volumes={}
        for name,ob in actual.items():
            p=expected[name];assert ob.parent==root;assert ob.matrix_world==Matrix.Identity(4)
            assert not ob.modifiers and not ob.constraints and ob.type=='MESH';v,tri,polys,uv=evaluated(ob);assert len(v)==len(p['vertices']);assert polys==p['faces']
            # Preserve expected JSON doubles: mathutils.Vector(expected) would
            # truncate them to float32 and hide real source-storage deviation.
            actual_double=np.asarray([[float(c) for c in q] for q in v],dtype=np.float64);planned_double=np.asarray(p['vertices'],dtype=np.float64);deviation=float(np.max(np.linalg.norm(actual_double-planned_double,axis=1)));vertex_deviations[name]=deviation;assert deviation<2e-6,name+' vertex deviation '+str(deviation)
            assert len(uv)==len(p['loop_uvs']);assert max(abs(c-d) for x,y in zip(uv,p['loop_uvs']) for c,d in zip(x,y))<2e-6;assert np.isfinite(actual_double).all();assert np.isfinite(uv).all();assert all(not f.use_smooth for f in ob.data.polygons)
            assert len(ob.data.materials)==1;mat=ob.data.materials[0];role=p['material_role'];roles.add(role);spec=pins['material_spec']['materials'][role];assert mat['astraea_material_role']==role;assert mat['alpha_contract']=='OPAQUE';assert mat.use_backface_culling== (not spec['double_sided']);bs=[n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'];assert len(bs)==1;bs=bs[0];assert abs(bs.inputs['Alpha'].default_value-1)<1e-7;assert bs.inputs['Metallic'].default_value==0;assert abs(bs.inputs['Roughness'].default_value-spec['roughness'])<1e-6;assert not bs.inputs['Emission Color'].links and not bs.inputs['Emission Strength'].links;assert max(abs(c*bs.inputs['Emission Strength'].default_value) for c in bs.inputs['Emission Color'].default_value[:3])<1e-8;assert len(bs.inputs['Base Color'].links)==1;tex=bs.inputs['Base Color'].links[0].from_node;assert tex.type=='TEX_IMAGE' and tex.image.packed_file;assert hashlib.sha256(bytes(tex.image.packed_file.data)).hexdigest()==spec['sha256'],'Image bytes differ from original '+role
            assert ob['surface_kind']==p['surface_kind'];assert ob['parent_design_id']==a['parent_design_id'];geos[name]=(v,tri);trees[name]=BVHTree.FromPolygons(v,tri,all_triangles=True);tri_count+=len(tri)
            assert all((v[t[1]]-v[t[0]]).cross(v[t[2]]-v[t[0]]).length>1e-10 for t in tri),name+' evaluated degenerate triangle'
            edges_count=collections.Counter(tuple(sorted((f[i],f[(i+1)%len(f)]))) for f in polys for i in range(len(f)));adj=collections.defaultdict(set)
            for e in edges_count:adj[e[0]].add(e[1]);adj[e[1]].add(e[0])
            seen={0};todo=[0]
            while todo:
                for nxt in adj[todo.pop()]-seen:seen.add(nxt);todo.append(nxt)
            assert len(seen)==len(v),name+' disconnected mesh islands'
            if p['surface_kind']=='closed_support':
                assert set(edges_count.values())=={2},name+' open physical support'
                # Translation-stable signed volume from local-anchor float64
                # coordinates, never cancellation-prone world/Vector products.
                local_double=actual_double-np.mean(actual_double,axis=0,dtype=np.float64);tt=np.asarray(tri,dtype=np.int64);volume=float(np.sum(np.einsum('ij,ij->i',local_double[tt[:,0]],np.cross(local_double[tt[:,1]],local_double[tt[:,2]])),dtype=np.float64)/6.0);closed_volumes[name]=volume;assert volume>1e-12,name+' inverted/zero support volume'
            else:
                assert set(edges_count.values())<={1,2};boundary=[e for e,n in edges_count.items() if n==1];bc=collections.Counter(k for e in boundary for k in e);assert boundary and set(bc.values())=={2},name+' invalid intentional leaf boundary'
                centered=np.array(v)-np.mean(v,axis=0);sv=np.linalg.svd(centered,compute_uv=False);assert len(tri)>=24 and sv[2]/sv[0]>.009,name+' leaf became a flat billboard'
            w=[[a['position_xyz'][0]+q.x,a['position_xyz'][1]+q.z,a['position_xyz'][2]-q.y] for q in v];assert all(any(in_box(q,r['bounds']) for r in a['approved_reservations']) for q in w),name+' exceeds reserved space';all_triangles.extend([[w[k] for k in t] for t in tri])
        assert tri_count==a['planned_triangle_count'];edges={j['child']:j['parent'] for j in a['joints']};assert len(edges)==len(a['joints']);roots=set(a['root_parts'])
        for n in actual:
            seen=set();cur=n
            while cur not in roots:
                assert cur in edges and cur not in seen,n+' floating support graph';seen.add(cur);cur=edges[cur]
        for j in a['joints']:
            probe=j['probe_local'];child=trees[j['child']];parent=trees[j['parent']];kind=expected[j['child']]['surface_kind']
            assert contains(parent,probe),a['name']+'/'+j['child']+' probe not physically inside/on parent'
            assert contains(child,probe) if kind=='closed_support' else child.find_nearest(Vector(probe))[3]<2e-6,a['name']+'/'+j['child']+' probe absent from child'
        for marker in a['markers']:
            obj=bpy.data.objects[marker['name']];assert np.linalg.norm(np.asarray(list(obj.matrix_world.translation),dtype=np.float64)-np.asarray(marker['point_local'],dtype=np.float64))<2e-6;assert obj['physical_part']==marker['physical_part']
            if marker['kind']=='soil_contact':
                v,_=geos[marker['physical_part']];feet=[q for q in v if abs(q.z)<2e-6];assert len(feet)>=6;assert all(inside_polygon([a['position_xyz'][0]+q.x,a['position_xyz'][2]-q.y],a['soil_polygon_xz']) for q in feet)
                # The export groups source soil objects by material/spatial cell.
                # Select actual top triangles spatially inside this named source
                # octagon instead of pretending source object names survived.
                poly=a['soil_polygon_xz'];xmin,xmax=min(p[0] for p in poly),max(p[0] for p in poly);zmin,zmax=min(p[1] for p in poly),max(p[1] for p in poly)
                top_triangles=[t for t in soil_triangles if all(abs(r[1]-a['position_xyz'][1])<2e-5 and xmin-2e-5<=r[0]<=xmax+2e-5 and zmin-2e-5<=r[2]<=zmax+2e-5 for r in t)];assert top_triangles,'Root plane differs from actual retained soil top'
                for q in feet:
                    point=[a['position_xyz'][0]+q.x,a['position_xyz'][2]-q.y];assert any(inside_polygon(point,[[r[0],r[2]] for r in t]) for t in top_triangles),'Root-foot vertex unsupported by actual soil triangles'
        wet_contact=None
        if a['kind']=='wet_whorl':
            original=Path(pins['source_libraries']['AST-BOT-003']);assert original.resolve()!=path.resolve()
            with bpy.data.libraries.load(str(original),link=False) as (src,dst):assert 'rosette_basal_crown' in src.objects;dst.objects=['rosette_basal_crown']
            retained=dst.objects[0];sc.collection.objects.link(retained);bpy.context.view_layer.update();v,t,_,_=evaluated(retained);tree=BVHTree.FromPolygons(v,t,all_triangles=True);probe=a['markers'][0]['point_local'];assert contains(tree,probe) and contains(trees['additive_crown_sleeve'],probe),'Wet companion has no actual shared-volume crown contact';overlap_radius=min(tree.find_nearest(Vector(probe))[3],trees['additive_crown_sleeve'].find_nearest(Vector(probe))[3]);assert overlap_radius>.004,'Wet join must include positive overlap volume';bpy.data.objects.remove(retained,do_unlink=True)
            # Read actual retained pot triangles; candidate lies strictly above
            # their maximum, so leaf-to-rim intersection is impossible.
            candidate_min=min(q.z for vs,_ in geos.values() for q in vs);clearance=.2+candidate_min-pot_top;assert clearance>.005,'New wet geometry intersects retained pot top/rim';wet_contact=dict(shared_probe=probe,actual_retained_root_contact=True,shared_interior_ball_radius_m=overlap_radius,minimum_actual_pot_vertical_clearance_m=clearance)
        assert sha(path)==before,'QA mutated its source'
        records.append(dict(name=a['name'],source=str(path),source_sha256=before,evaluated_parts=len(actual),evaluated_triangles=tri_count,true_max_vertex_deviation_m=max(vertex_deviations.values()),vertex_deviations_by_part_m=vertex_deviations,closed_support_signed_volumes_m3=closed_volumes,closed_volume_method='float64 triple products after subtracting per-part local mean anchor',physical_joint_count=len(a['joints']),all_parts_root_connected=True,packed_material_roles=sorted(roles),wet_contact=wet_contact))
        print('SOURCE_QA_PASSED',a['name'],tri_count,flush=True)
    media_path=next(resolve_pin(p) for p in pins['immutable_inputs'] if p.endswith('/MEDIA_FITTING_CANDIDATES.json'));media=json.loads(media_path.read_text());probes=0
    for display in media['candidates']:
        for ray in display['sampled_current_triangle_sightlines']:
            assert not intersects_segment(all_triangles,ray['eye_xyz'],ray['target_xyz']),display['name']+' new foliage obscures seated image';probes+=1
    for p,h in pins['immutable_inputs'].items():assert sha(resolve_pin(p))==h,'Original changed during QA '+p
    report=dict(status='PASS_SOURCE_QA_ONLY',contract_sha256=sha(contract),source_count=len(records),sources=records,new_geometry_screen_probes_clear=probes,all_original_hashes_unchanged=True,pending=['Independent retention by parent','Source-context image review','GLB equivalence and imported material/marker checks','Matched ordinary/effects-off 640x360 engine views and pans','Final route/window/void and actor/maintenance circulation checks'])
    dest=out/'qa'/('SOURCE_QA_'+(args.only or 'all')+'.json');assert not dest.exists(),'Preserve previous QA receipt';dest.write_text(json.dumps(report,indent=2)+'\n');print('SOURCE_QA_COMPLETE',len(records),probes)
if __name__=='__main__':main()
