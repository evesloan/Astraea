"""AST-RES-001 fitted pool signs. Default: editable .blend ONLY, no export/render.

Run only after the parent clears the engine-job gate:
  blender -b -t 2 --python build_pool_wayfinding.py -- --output-dir NEW_DIRECTORY

Export is a separate invocation requiring a reviewed source and explicit receipt:
  blender -b -t 2 --python build_pool_wayfinding.py -- --export-blend SOURCE.blend \
    --export-approval APPROVAL.json --output-dir NEW_EXPORT_DIRECTORY

Never opens an original source for writing, modifies runtime, registers an ID,
launches a render, or overwrites existing outputs. Standard-library preflight can
be run separately without importing Blender: python check_wayfinding.py.
"""
import argparse, json, math, sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from wayfinding_geometry import *
from check_wayfinding import screen

FACES=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]

def arguments():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--contract',type=Path,default=HERE/'wayfinding_contract.json')
    p.add_argument('--catalogue',type=Path);p.add_argument('--game',type=Path)
    p.add_argument('--output-dir',type=Path,default=HERE/'build')
    p.add_argument('--export-blend',type=Path)
    p.add_argument('--export-approval',type=Path)
    return p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])

def run(args):
    # No bpy import and no scene edits until immutable-input/source-fit preflight passes.
    report=screen(args.contract,args.catalogue,args.game)
    if not report['pass']:raise RuntimeError('Source preflight failed closed: '+json.dumps(report['issues']))
    d=json.loads(args.contract.read_text());cat=Path(args.catalogue or d['source_defaults']['catalogue'])
    out=args.output_dir.resolve()
    protected=[cat.resolve(),Path(args.game or d['source_defaults']['game']).resolve()]
    approved_new=(cat/'assets/grand_pool_first_pass/finish_envelope/wayfinding').resolve()
    if any(out==p or p in out.parents for p in protected) and out!=approved_new:
        raise RuntimeError('Only the explicitly approved new finish_envelope/wayfinding subfolder may receive catalogue output; originals/runtime remain read-only')
    import bpy, bmesh
    from mathutils import Vector
    if args.export_blend:
        export_reviewed(args,d,out,bpy)
        return
    if args.export_approval:raise RuntimeError('Export approval is only valid with --export-blend')
    source=out/'source/grand_pool_wayfinding.blend';qa=out/'qa/wayfinding_source_build.json'
    if source.exists() or qa.exists():raise FileExistsError('Preserve surviving output; choose a new --output-dir')
    source.parent.mkdir(parents=True,exist_ok=True);qa.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
    root=bpy.data.objects.new('AST_RES_001_PoolWayfinding',None);scene.collection.objects.link(root)
    root['catalogue_id']='AST-RES-001';root['source_family']='residential_wayfinding_bay';root['new_design_count']=0
    root['derivative_export']='AST-RES-001_pool_wayfinding.glb';root['contract_sha256']=sha(args.contract)
    root['source_status']='Editable fitted derivative; engine adoption and low-resolution visual acceptance pending'
    mats={}
    for role,row in d['material_roles'].items():
        texture=cat/'materials'/row['base_color_file']
        if sha(texture)!=row['sha256']:raise RuntimeError('Retained texture changed: '+role)
        mat=bpy.data.materials.new(role);mat.use_nodes=True;n=mat.node_tree.nodes.get('Principled BSDF')
        n.inputs['Roughness'].default_value=row['roughness'];n.inputs['Metallic'].default_value=row['metallic']
        mat['meters_per_tile_uv']=row['meters_per_tile_uv'];mat['texture_sha256']=row['sha256'];mat['source_catalogue_material']=role
        tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(texture),check_existing=True);tex.interpolation='Closest'
        mat.node_tree.links.new(tex.outputs['Color'],n.inputs['Base Color']);mats[role]=mat
    parts=[];glyph_reports=[]
    def uv(me,role,origin_world):
        for lay in list(me.uv_layers):me.uv_layers.remove(lay)
        layer=me.uv_layers.new(name='MetreScaled');tile=d['material_roles'][role]['meters_per_tile_uv']
        origin=Vector((origin_world[0],-origin_world[2],origin_world[1]))
        for poly in me.polygons:
            n=poly.normal.normalized()
            u=(Vector((1,0,0))-n*n.x).normalized() if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized()
            v=n.cross(u).normalized()
            for li in poly.loop_indices:
                q=me.vertices[me.loops[li].vertex_index].co-origin
                layer.data[li].uv=(q.dot(u)/tile[0],q.dot(v)/tile[1])
    def mesh(name,vs,fs,role,parent,sign_id,collision=True,origin=(0,0,0)):
        # Keep small lettering in local coordinates. Baking it hundreds of metres
        # from the origin rounds curve vertices together at float32 precision.
        # This changes authorship coordinates, never the fitted world placement.
        origin_b=(origin[0],-origin[2],origin[1])
        local_vs=[(v[0]-origin[0],-v[2]+origin[2],v[1]-origin[1]) for v in vs]
        me=bpy.data.meshes.new(name+'_EditableMesh');me.from_pydata(local_vs,[],fs);me.update()
        bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
        bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-9);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
        me.update();me.materials.append(mats[role]);uv(me,role,(0,0,0))
        o=bpy.data.objects.new(name,me);scene.collection.objects.link(o);o.parent=parent;o.location=origin_b
        o['catalogue_id']='AST-RES-001';o['source_family']='residential_wayfinding_bay';o['source_sign_id']=sign_id
        o['semantic_role']=role;o['collision_contract']='concave_static_surface' if collision else 'visual_only_glyph_or_fastener'
        o['wayfinding_export']=True;o['metric_uv']=True;parts.append(o);return o
    def box_geometry(b):
        a,z=b
        vs=[[a[0],a[1],a[2]],[a[0],a[1],z[2]],[a[0],z[1],a[2]],[a[0],z[1],z[2]],
            [z[0],a[1],a[2]],[z[0],a[1],z[2]],[z[0],z[1],a[2]],[z[0],z[1],z[2]]]
        return vs,FACES
    def prism_shape(s,outline,d0,d1):
        vs=[local_point(s,[x,y,z]) for z in [d0,d1] for x,y in outline];n=len(outline)
        fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
        return vs,fs
    def raw_font(body,name):
        font=bpy.data.curves.new(name+'_FontRecipe','FONT');font.body=body;font.size=1;font.align_x='LEFT';font.extrude=.002;font.resolution_u=6
        ob=bpy.data.objects.new(name,font);scene.collection.objects.link(ob)
        bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH')
        ob=bpy.context.object;vs=[list(v.co) for v in ob.data.vertices];fs=[tuple(p.vertices) for p in ob.data.polygons]
        bpy.data.objects.remove(ob,do_unlink=True)
        return vs,fs
    hv,_=raw_font('H','Measurement_H');hb=bounds(hv);unit_cap=hb[1][1]-hb[0][1]
    for s in d['signs']:
        parent=bpy.data.objects.new('SIGN_'+s['id'],None);scene.collection.objects.link(parent);parent.parent=root
        parent['wayfinding_export']=True;parent['source_sign_id']=s['id'];parent['text_lines']=json.dumps(s['text_lines']);parent['source_mounts']=json.dumps(s['contact_patches'])
        parent['outward_normal_xyz']=s['normal_xyz'];parent['right_xyz']=s['right_xyz'];parent['dimensions_m']=[s['width_m'],s['height_m']]
        for c in s['components']:
            if c.get('shape')=='octagonal_fastener':
                lo,hi=c['local_bounds_uvd'];cx=(lo[0]+hi[0])/2;cy=(lo[1]+hi[1])/2;r=(hi[0]-lo[0])/2
                outline=[(cx+r*math.cos(math.tau*i/8),cy+r*math.sin(math.tau*i/8)) for i in range(8)]
                vs,fs=prism_shape(s,outline,lo[2],hi[2])
            else:vs,fs=box_geometry(c['world_bounds_xyz'])
            o=mesh('PWF_'+s['id']+'_'+c['name'],vs,fs,c['role'],parent,s['id'],c['collision'],s['origin_xyz'])
            o['source_reference']='RES_MapFrame' if c['name']=='MapFrame' else 'RES_MapBacking' if c['name']=='MapBacking' else 'Fitted physical mount derived from named retained receiver'
        lo,hi=s['glyph_envelope_local_uvd'];left,right=lo[0],hi[0]
        if 'arrow' in s:right-=.28
        line_count=len(s['text_lines']);line_centres=[0] if line_count==1 else [.105,-.105]
        for index,(line,centre_v) in enumerate(zip(s['text_lines'],line_centres)):
            vs,fs=raw_font(line,'PWF_Font_'+s['id']+'_'+str(index));b=bounds(vs)
            factor=min(s['glyph_cap_height_m']/unit_cap,(right-left)/(b[1][0]-b[0][0]))
            half_available=(hi[1]-lo[1])/2 if line_count==1 else .087
            factor=min(factor,2*half_available/(b[1][1]-b[0][1]))
            actual_cap=unit_cap*factor
            if actual_cap<s['minimum_glyph_cap_height_m']-1e-6:raise RuntimeError('Letter size fails closed: '+s['id']+' '+line+' '+str(actual_cap))
            cx=(b[0][0]+b[1][0])/2;cy=(b[0][1]+b[1][1])/2;mid=(left+right)/2;zd=b[1][2]-b[0][2]
            xyz=[local_point(s,[(v[0]-cx)*factor+mid,(v[1]-cy)*factor+centre_v,.123+(v[2]-b[0][2])/zd*.006]) for v in vs]
            ob=mesh('PWF_'+s['id']+'_Glyphs_'+str(index),xyz,fs,'warm_walnut',parent,s['id'],False,s['origin_xyz'])
            ob['original_lettering']=line;ob['font_recipe']='Blender built-in font, size 1, cap-H normalized, uniform fit only';ob['actual_cap_height_m']=actual_cap
            actual=bounds(xyz);reserved=s['glyph_envelope_world_xyz']
            if any(actual[0][i]<reserved[0][i]-1e-5 or actual[1][i]>reserved[1][i]+1e-5 for i in range(3)):raise RuntimeError('Glyph escapes envelope: '+s['id'])
            glyph_reports.append({'sign':s['id'],'line':line,'cap_height_m':actual_cap,'bounds_xyz':actual})
        if 'arrow' in s:
            # Derive orientation from stored actual route projection, never a hard-coded cardinal guess.
            direction=s['arrow']['unit_arrow_uv'];cx=hi[0]-.12;cy=0
            base=[(-.105,-.025),(.025,-.025),(.025,-.073),(.115,0),(.025,.073),(.025,.025),(-.105,.025)]
            outline=[(cx+x*direction[0]-y*direction[1],cy+x*direction[1]+y*direction[0]) for x,y in base]
            vs,fs=prism_shape(s,outline,.123,.129);arrow=mesh('PWF_'+s['id']+'_RouteArrow',vs,fs,'warm_walnut',parent,s['id'],False,s['origin_xyz'])
            arrow['route_projection']=json.dumps(s['arrow'])
        for i,patch in enumerate(s['contact_patches']):
            ob=bpy.data.objects.new('DATUM_PWF_'+s['id']+'_mount_'+str(i),None);scene.collection.objects.link(ob);ob.parent=parent
            q=mul(add(*patch['bounds_xyz']),.5);ob.location=(q[0],-q[2],q[1]);ob['source_receiver']=patch['support'];ob['wayfinding_export']=True
    # Saved source includes actual receiver geometry as hidden, editable context only.
    context=bpy.data.collections.new('Verified_Mount_Receivers_REFERENCE_ONLY');scene.collection.children.link(context)
    for key,rec in d['supports'].items():
        if rec['kind'] in ['evaluated_source_triangles','source_named_export_triangles']:vs,fs=rec['world_vertices'],rec['triangles']
        else:vs,fs=box_geometry(rec['bounds_xyz'])
        me=bpy.data.meshes.new('Reference_'+rec['object']);me.from_pydata([(v[0],-v[2],v[1]) for v in vs],[],fs);me.update()
        ob=bpy.data.objects.new('REFERENCE_'+key.replace('/','_'),me);context.objects.link(ob);ob.hide_render=True;ob.hide_set(True);ob.display_type='WIRE';ob['export_excluded']=True;ob['source_receiver_record']=rec['record'];ob['retained_source_part']=rec['object']
    bpy.context.view_layer.update()
    geometry=[]
    for ob in parts:
        me=ob.data;me.calc_loop_triangles()
        if not len(me.loop_triangles):raise RuntimeError('No physical triangles: '+ob.name)
        areas=[]
        for tri in me.loop_triangles:
            a,b,c=[me.vertices[i].co for i in tri.vertices];areas.append((b-a).cross(c-a).length/2)
        if min(areas)<1e-12:raise RuntimeError('Degenerate geometry: '+ob.name)
        if not me.uv_layers or any(not math.isfinite(v) for datum in me.uv_layers.active.data for v in datum.uv):raise RuntimeError('Invalid metric UV: '+ob.name)
        geometry.append({'name':ob.name,'triangles':len(me.loop_triangles),'minimum_triangle_area_m2':min(areas),'collision_contract':ob['collision_contract']})
    bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(source))
    build_report={'status':'source_built_export_not_run','contract_sha256':sha(args.contract),'source_file':str(source),'source_sha256':sha(source),'source_screen':report,'glyphs':glyph_reports,'geometry':geometry,'material_texture_sha256':{k:v['sha256'] for k,v in d['material_roles'].items()},'required_next_gates':d['required_gates'][1:],'blender_version':bpy.app.version_string}
    dump(qa,build_report)
    print('EDITABLE_SOURCE_SAVED',source,'NO_EXPORT_RENDER_OR_RUNTIME_CHANGE')

def export_reviewed(args,d,out,bpy):
    if not args.export_approval:raise RuntimeError('Export requires an explicit parent source-review receipt')
    receipt=json.loads(args.export_approval.read_text());source=args.export_blend.resolve()
    expected={'kind':'pool_wayfinding_export_approval','catalogue_id':'AST-RES-001','derivative_export':'AST-RES-001_pool_wayfinding.glb','contract_sha256':sha(args.contract),'source_sha256':sha(source),'source_review_passed':True,'no_unresolved_mounting_compromises':True,'parent_export_approved':True}
    if any(receipt.get(k)!=v for k,v in expected.items()):raise RuntimeError('Export receipt does not approve this exact source/contract')
    if source.name!='grand_pool_wayfinding.blend':raise RuntimeError('Unexpected source identity')
    dest=out/'exports'/d['derivative_export'];record=out/'qa/wayfinding_export.json'
    if dest.exists() or record.exists():raise FileExistsError('Never overwrite a surviving source/export')
    dest.parent.mkdir(parents=True,exist_ok=True);record.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(source));root=bpy.data.objects.get('AST_RES_001_PoolWayfinding')
    if not root or root.get('contract_sha256')!=sha(args.contract):raise RuntimeError('Source ownership/contract does not match')
    bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
    selected=[]
    for ob in bpy.context.scene.objects:
        if ob.get('wayfinding_export'):
            if ob.get('export_excluded'):raise RuntimeError('Reference receiver cannot enter export')
            ob.hide_set(False);ob.select_set(True);selected.append(ob)
    if len([o for o in selected if o.type=='EMPTY' and o.name.startswith('SIGN_')])!=11:raise RuntimeError('Source does not contain exactly 11 signs')
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.gltf(filepath=str(dest),export_format='GLB',export_yup=True,export_extras=True,use_selection=True,export_cameras=False,export_lights=False)
    dump(record,{'status':'export_created_not_adopted','source_sha256':sha(source),'contract_sha256':sha(args.contract),'export_sha256':sha(dest),'export_file':str(dest),'parent_receipt_sha256':sha(args.export_approval),'source_export_equivalence':'Independent GLB/evaluated-source comparison still required','remaining_gates':d['required_gates'][2:]})
    print('DERIVATIVE_EXPORTED_NO_REGISTRATION_OR_RUNTIME_CHANGE',dest)

if __name__=='__main__':run(arguments())
