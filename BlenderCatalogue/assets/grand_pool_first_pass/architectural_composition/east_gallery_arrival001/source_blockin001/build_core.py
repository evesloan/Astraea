"""Two-thread editable core-source build only. Never export, render, or write Game/Catalogue.
Adapted from the audited material/contact/metric-UV construction in
pool-architectural-composition/build_blockin003.py. Existing files are never overwritten.
"""
import bpy,bmesh,json,hashlib,sys,math
from pathlib import Path
from mathutils import Vector
S=Path(__file__).resolve().parent;C=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(v):
    if isinstance(v,(str,int,float,bool))or v is None:return v
    try:return [canonical(x)for x in v]
    except TypeError:return str(v)
def mat_state(mat):
    nodes=[]
    for n in mat.node_tree.nodes:
        row={'name':n.name,'type':n.type,'inputs':{x.name:canonical(x.default_value)for x in n.inputs if hasattr(x,'default_value')}}
        if n.type=='TEX_IMAGE':
            im=n.image;assert im and im.packed_file;row['image']={'packed_sha256':hashlib.sha256(bytes(im.packed_file.data)).hexdigest(),'size':list(im.size),'colorspace':im.colorspace_settings.name,'extension':n.extension,'interpolation':n.interpolation}
        nodes.append(row)
    return {'role':mat.get('astraea_material_role'),'nodes':nodes,'links':sorted([l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name]for l in mat.node_tree.links),'metric_tile_m':canonical(mat.get('meters_per_tile_uv',[1,1])),'backface_culling':mat.use_backface_culling}
def B(p):return Vector((p[0],-p[2],p[1]))
def G(p):return [float(p[0]),float(p[2]),float(-p[1])]
def load_materials(plan):
    need={p['material_role']for p in plan['parts']};materials={};provenance={}
    for path in [C/'assets/grand_pool_orchard_section/source/AST-AQU-016.blend',C/'assets/aquatic_lounge/source/AST-AQU-001.blend']:
        with bpy.data.libraries.load(str(path),link=False)as(src,dst):dst.materials=list(src.materials)
        for mat in dst.materials:
            role=mat.get('astraea_material_role')
            if role in need and role not in materials:
                materials[role]=mat;provenance[role]={'source':str(path),'source_sha256':sha(path),'material_name':mat.name,'material_state':mat_state(mat)}
    if 'lens'in need:
        path=C/'assets/grand_pool_orchard_section/source/AST-AQU-016.blend';exemplar='GP_VaultLamp_-433_-36_Lens'
        with bpy.data.libraries.load(str(path),link=False)as(src,dst):
            assert exemplar in src.objects;dst.objects=[exemplar]
        ob=dst.objects[0];mat=ob.data.materials[0];materials['lens']=mat;provenance['lens']={'source':str(path),'source_sha256':sha(path),'source_exemplar_object':exemplar,'material_name':mat.name,'material_state':mat_state(mat)}
        mesh=ob.data;bpy.data.objects.remove(ob)
        if mesh.users==0:bpy.data.meshes.remove(mesh)
    assert set(materials)==need,('Missing retained role',need-set(materials))
    return materials,provenance

def snapshot(scene,plan):
    expected={p['name']:p for p in plan['parts']};out=[]
    for o in scene.objects:
        if o.type!='MESH' or o.name not in expected:continue
        row=expected[o.name];mesh=o.data;mesh.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(mesh);bm.normal_update()
        assert all(e.is_manifold for e in bm.edges),o.name;volume=bm.calc_volume(signed=True);assert volume>1e-9,(o.name,volume);bm.free()
        verts=[G(o.matrix_world@v.co)for v in mesh.vertices]
        minimum_area=1e99;minimum_uv_area=1e99
        for t in mesh.loop_triangles:
            a,b,c=[mesh.vertices[i].co for i in t.vertices];area=(b-a).cross(c-a).length*.5;assert area>1e-10,(o.name,'collapsed face');minimum_area=min(minimum_area,area)
            uv=[mesh.uv_layers.active.data[i].uv for i in t.loops];ua=abs((uv[1].x-uv[0].x)*(uv[2].y-uv[0].y)-(uv[1].y-uv[0].y)*(uv[2].x-uv[0].x))*.5;assert ua>1e-12,(o.name,'collapsed UV');minimum_uv_area=min(minimum_uv_area,ua)
        out.append(dict(row,vertices_xyz=verts,faces=[list(f.vertices)for f in mesh.polygons],evaluated_triangles=[list(t.vertices)for t in mesh.loop_triangles],signed_volume_m3=volume,minimum_triangle_area_m2=minimum_area,minimum_uv_area=minimum_uv_area,uv_loops=[list(u.uv)for u in mesh.uv_layers.active.data],local_vertices_blender=[list(v.co)for v in mesh.vertices],matrix_world_blender=[list(row)for row in o.matrix_world],material_indices=[int(f.material_index)for f in mesh.polygons],material_states=[mat_state(m)for m in mesh.materials],source_transform={'location':list(o.location),'rotation_euler':list(o.rotation_euler),'scale':list(o.scale)}))
    assert len(out)==len(expected)
    return out

def build_core():
    plan=json.loads((S/'CORE_PLAN.json').read_text());gate=json.loads((S/'CORE_REVIEW.json').read_text());assert gate['status']=='PASS_CORE_PURE_GEOMETRY'and gate['plan_sha256']==sha(S/'CORE_PLAN.json')
    for path,h in plan['input_sha256'].items():assert sha(path)==h,path
    bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;scene.render.threads_mode='FIXED';scene.render.threads=2
    materials,provenance=load_materials(plan);collections={}
    for part in plan['parts']:
        group=part['group']
        if group not in collections:
            collections[group]=bpy.data.collections.new('AST-AQU-016_east_'+group);scene.collection.children.link(collections[group])
        mesh=bpy.data.meshes.new(part['name']+'_editable');mesh.from_pydata([B(v)for v in part['vertices_xyz']],[],part['faces']);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update()
        ob=bpy.data.objects.new(part['name'],mesh);collections[group].objects.link(ob);mat=materials[part['material_role']];mesh.materials.append(mat)
        ob['parent_design_id']='AST-AQU-016';ob['source_group']=group;ob['material_role']=part['material_role'];ob['support_json']=json.dumps(part['support']);ob['collision_contract']=part['collision'];ob['blockin_only']=True;ob['source_plan_sha256']=sha(S/'CORE_PLAN.json');ob['new_floor_owner']=False;ob['semantic_role']=part.get('semantic',part.get('programme_entity',group));ob['coordinate_contract']='Blender Z-up metres; Godot = (x,z,-y)'
        if part.get('programme_entity'):ob['programme_entity']=part['programme_entity']
        if 'cast_shadow'in part:
            ob['cast_shadow']=part['cast_shadow'];ob.visible_shadow=part['cast_shadow']
        uv=mesh.uv_layers.new(name='MetreScaled_SourceRole');scale=mat.get('meters_per_tile_uv',[1,1]);desired=part.get('grain_axis_xyz',[1,0,0])
        for face in mesh.polygons:
            d=desired
            if group=='bench'and part['material_role']=='warm_walnut':
                z=-sum(mesh.vertices[vi].co.y for vi in face.vertices)/len(face.vertices);d=[-.54*(z+449.5)/(1.36**2),0,1]
            axis=B(d);normal=face.normal.normalized();u=axis-normal*axis.dot(normal)
            if u.length<.01:
                alternative=Vector((0,0,1))if abs(normal.z)<.9 else Vector((0,1,0));u=alternative-normal*alternative.dot(normal)
            u.normalize();v=normal.cross(u).normalized()
            for li in face.loop_indices:
                p=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(p.dot(u)/scale[0],p.dot(v)/scale[1])
    # Non-rendering semantic markers document later receiver/selection work.
    markers=bpy.data.collections.new('SOURCE_ONLY_use_and_light_markers');scene.collection.children.link(markers)
    for row in plan['fixture_reservations']:
        ob=bpy.data.objects.new(row['name'],None);markers.objects.link(ob);ob.location=B(row['position_xyz']);ob.empty_display_type='ARROWS';ob.empty_display_size=.15;ob['export_excluded']=True;ob['marker_json']=json.dumps(row);ob['no_native_light_created']=True
    for row in plan['seated_views']:
        ob=bpy.data.objects.new('USE_'+row['name'],None);markers.objects.link(ob);ob.location=B(row['eye_xyz']);ob.empty_display_type='CONE';ob.empty_display_size=.12;ob['export_excluded']=True;ob['use_json']=json.dumps(row)
    scene['status']='Core source block-in only; retained programme integration and visual review pending';scene['parent_design_id']='AST-AQU-016';scene['source_plan_sha256']=sha(S/'CORE_PLAN.json');scene['budget_json']=json.dumps(plan['budget']);scene['no_export_runtime_or_first_pass_acceptance']=True
    bpy.context.view_layer.update()
    return plan,provenance

def main():
    out=S/'build001';assert not out.exists(),'Preserve prior source build. Author a new revision instead.'
    plan,provenance=build_core();actual=snapshot(bpy.context.scene,plan);out.mkdir();(out/'source').mkdir();(out/'qa').mkdir();path=out/'source/AST-AQU-016_east_gallery_core.blend';bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
    actual_plan=dict(plan,parts=actual,status='BUILD_EVALUATED_CORE_PENDING_INDEPENDENT_REOPEN');(out/'qa/BUILD_EVALUATED_PLAN.json').write_text(json.dumps(actual_plan,indent=2)+'\n')
    receipt=dict(status='CORE_SOURCE_SAVED_PENDING_INDEPENDENT_REOPEN',source=str(path),source_sha256=sha(path),plan_sha256=sha(S/'CORE_PLAN.json'),review_sha256=sha(S/'CORE_REVIEW.json'),build_script_sha256=sha(__file__),roundtrip_helper_sha256=sha(S/'source_roundtrip_checks.py'),material_provenance=provenance,mesh_objects=len(actual),triangles=sum(len(p['evaluated_triangles'])for p in actual),source_only_markers=5,evaluated_plan_sha256=sha(out/'qa/BUILD_EVALUATED_PLAN.json'),input_sha256=plan['input_sha256'],exports=[],renders=[],game_writes=[],catalogue_writes=[],pending=plan['pending'])
    for p,h in plan['input_sha256'].items():assert sha(p)==h,p
    (out/'qa/BUILD_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print('CORE_SOURCE_SAVED',path,len(actual),'closed editable objects; no export/render/runtime write',flush=True)
if __name__=='__main__':main()
