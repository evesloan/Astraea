"""Astraea view reveal kit 01. Original, script-assisted editable asset design.
Run: blender -b --python source/build_reveal.py
Metres, Z up, front -Y. No room, glass, game or controller is authored.
"""
import bpy, bmesh, math, json, hashlib, sys, importlib.util
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
CAT=ROOT.parents[1]
for d in ('source','exports','qa'): (ROOT/d).mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('astraea_materials',CAT/'standards/materials.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
MATS=module.materials()
ALL_META=[]
R=.3
DEPTH=(-.25,.18)

def clear():
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    for c in list(bpy.data.collections):
        if c.name!='Collection': bpy.data.collections.remove(c)

def enamel(w):
    return [(w,.18),(w,-.02),(w-.015,-.095),(w-.055,-.17),(w-.105,-.23),(.115,-.25),(.093,-.22),(.09,-.175),(.083,-.17),(.083,.15),(.02,.15),(.02,.18)]

def walnut(w):
    return [(0,.145),(0,-.155),(.008,-.181),(.025,-.202),(.069,-.20),(.08,-.181),(.08,.145)]

def make_sweep(name,path,profile,role,terminal=False):
    verts=[];uvs=[];s=0.0;prev=None
    for k,(x,z,nx,nz,w) in enumerate(path):
        if prev:s+=math.hypot(x-prev[0],z-prev[1])
        prev=(x,z);section=profile(w);q=0
        # Terminal shrinks the matching cross section into a genuinely closed, eased end.
        t=(x-.001)/.239 if terminal else 0
        shrink=1-.22*(t*t*(3-2*t)) if terminal else 1
        push=.065*(t*t*(3-2*t)) if terminal else 0
        for j,(r,y) in enumerate(section):
            if j:q+=math.hypot(r-section[j-1][0],y-section[j-1][1])
            rr=.175+(r-.175)*shrink if terminal else r
            yy=y+push if terminal else y
            verts.append((x+nx*rr,yy,z+nz*rr))
            uv_scale=(.65,1.3) if role=='warm_walnut' else (1,1)
            uvs.append((q/uv_scale[0],s/uv_scale[1]))
    m=len(profile(path[0][-1]));faces=[]
    for k in range(len(path)-1):
        for j in range(m):faces.append((k*m+j,k*m+(j+1)%m,(k+1)*m+(j+1)%m,(k+1)*m+j))
    faces.append(tuple(range(m-1,-1,-1)))
    faces.append(tuple((len(path)-1)*m+j for j in range(m)))
    mesh=bpy.data.meshes.new(name+'_editable_mesh');mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
    mesh.materials.append(MATS[role]);obj['material_role']=role;obj['units']='metres';obj['grain_axis']='pathwise V, metric UV' if role=='warm_walnut' else 'metric unwrap'
    uv=mesh.uv_layers.new(name='metric_material_uv')
    for p in mesh.polygons:
        p.use_smooth=p.index<len(faces)-2
        for li in p.loop_indices:
            vi=mesh.loops[li].vertex_index
            if p.index>=len(faces)-2:
                # The cross section cap is a real surface, not a collapsed pathwise UV row.
                k=0 if p.index==len(faces)-2 else len(path)-1
                x,z,nx,nz,w=path[k];v=mesh.vertices[vi].co
                radial=(v.x-x)*nx+(v.z-z)*nz
                uv_scale=(.65,1.3) if role=='warm_walnut' else (1,1)
                uv.data[li].uv=(v.y/uv_scale[0],radial/uv_scale[1])
            else:uv.data[li].uv=uvs[vi]
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
    bevel=obj.modifiers.new('Editable subtle edge easing 1.2 mm','BEVEL');bevel.width=.0012;bevel.segments=2;bevel.limit_method='ANGLE';bevel.angle_limit=math.radians(38)
    bevel.affect='EDGES';bevel.use_clamp_overlap=True
    normal=obj.modifiers.new('Weighted surface normals','WEIGHTED_NORMAL');normal.keep_sharp=True;normal.weight=40
    return obj

def jamb_path():
    p=[]
    # Top half of the right hand jamb. Elliptical outer shoulder fits exact envelope.
    for i in range(13):
        a=math.pi/2*(1-i/12);nx,nz=math.cos(a),math.sin(a)
        w=1/math.sqrt(nx*nx/.575**2+nz*nz/.65**2)-.3
        x=.3*nx;z=-.3+.3*nz
        if i==0:x=.001
        p.append((x,z,nx,nz,w))
    p.extend([(.3,-.8,1,0,.275),(.3,-1.3,1,0,.275),(.3,-1.9,1,0,.275)])
    for i in range(1,13):
        a=-math.pi/2*i/12;nx,nz=math.cos(a),math.sin(a)
        w=1/math.sqrt(nx*nx/.575**2+nz*nz/1.0**2)-.3
        x=.3*nx;z=-1.9+.3*nz
        if i==12:x=.001
        p.append((x,z,nx,nz,w))
    return p

def paths(kind):
    if kind=='header':return[(.001,0,0,1,.35),(2.199,0,0,1,.35)]
    if kind=='sill':return[(.001,0,0,-1,.70),(2.199,0,0,-1,.70)]
    if kind=='jamb':return jamb_path()
    if kind=='terminal':return[(x,0,0,1,.35) for x in (.001,.045,.095,.15,.195,.225,.24)]

def create(kind,prefix=''):
    p=paths(kind)
    objs=[make_sweep(prefix+kind+'_sculpted_ivory',p,enamel,'ivory_enamel',kind=='terminal'),make_sweep(prefix+kind+'_deep_timber_return',p,walnut,'warm_walnut',kind=='terminal')]
    for o in objs:o['catalogue_family']='AST-VR-01';o['module']=kind;o['source_method']='Original script-assisted intentionally shaped cross-section sweep';o['editable_profile']='source/build_reveal.py';o['seam_clearance_m']=.002
    return objs

def bounds(objects,evaluated=True):
    pts=[];dg=bpy.context.evaluated_depsgraph_get()
    for o in objects:
        ob=o.evaluated_get(dg) if evaluated else o
        pts.extend(ob.matrix_world@Vector(v) for v in ob.bound_box)
    mi=[min(v[i] for v in pts) for i in range(3)];ma=[max(v[i] for v in pts) for i in range(3)]
    return {'min_m':mi,'max_m':ma,'dimensions_m':[ma[i]-mi[i] for i in range(3)]}

def triangles(objects):
    d=bpy.context.evaluated_depsgraph_get();n=0
    for o in objects:
        me=o.evaluated_get(d).to_mesh();me.calc_loop_triangles();n+=len(me.loop_triangles);o.evaluated_get(d).to_mesh_clear()
    return n

def export(objects,path):
    bpy.ops.object.select_all(action='DESELECT')
    # Consolidate evaluated runtime parts by role; the saved source stays semantic/editable.
    dg=bpy.context.evaluated_depsgraph_get();groups={};temporary=[]
    for original in objects:
        me=bpy.data.meshes.new_from_object(original.evaluated_get(dg))
        # Bevel interpolation may collapse a few microscopic corner UV triangles.
        # Give only those evaluated runtime polygons a metric dominant-plane map.
        me.calc_loop_triangles();uv=me.uv_layers.active.data;repair=set()
        for tr in me.loop_triangles:
            a,b,c=[uv[i].uv.copy() for i in tr.loops]
            if abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))<2e-12:repair.add(tr.polygon_index)
        uv_scale=(.65,1.3) if original['material_role']=='warm_walnut' else (1,1)
        for pi in repair:
            face=me.polygons[pi];axis=max(range(3),key=lambda i:abs(face.normal[i]));a,b=[i for i in range(3) if i!=axis]
            for li in face.loop_indices:
                v=me.vertices[me.loops[li].vertex_index].co;uv[li].uv=(v[a]/uv_scale[0],v[b]/uv_scale[1])
        o=bpy.data.objects.new('runtime_'+original.name,me);bpy.context.collection.objects.link(o);o.matrix_world=original.matrix_world.copy()
        role=original['material_role'];groups.setdefault(role,[]).append(o);temporary.append(o)
    runtime=[]
    for role,parts in groups.items():
        bpy.ops.object.select_all(action='DESELECT')
        for p in parts:p.select_set(True)
        bpy.context.view_layer.objects.active=parts[0]
        bpy.ops.object.join();joined=parts[0];joined.name='ASTRAEA_runtime_'+role;joined['material_role']=role;joined['source_semantic_parts']=json.dumps([o.name for o in objects if o['material_role']==role]);runtime.append(joined)
    bpy.ops.object.select_all(action='DESELECT')
    for o in runtime:o.select_set(True)
    bpy.context.view_layer.objects.active=runtime[0]
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_materials='EXPORT',export_texcoords=True,export_normals=True,export_cameras=False,export_lights=False)
    for o in runtime:bpy.data.objects.remove(o,do_unlink=True)

def settings():
    sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
    sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=128
    sc.render.image_settings.file_format='PNG';sc.render.resolution_percentage=100
    sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.22,.25,.29,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.45
    sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.render.film_transparent=False

def camera(name,loc,target,lens=42,ortho=None):
    d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens
    if ortho:d.type='ORTHO';d.ortho_scale=ortho
    bpy.context.scene.camera=o;return o

def stage():
    mat=bpy.data.materials.new('QA neutral backdrop');mat.diffuse_color=(.19,.22,.235,1);mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.19,.22,.235,1);mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.8
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.007));floor=bpy.context.object;floor.name='QA_ONLY_neutral_floor';floor.data.materials.append(mat)
    for name,loc,power,size in [('key',(-3.5,-4,6),900,5),('fill',(4,-1,3),700,4),('rim',(0,3,5),1000,3)]:
        d=bpy.data.lights.new('QA_ONLY_'+name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(d.name,d);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,1.6))-o.location).to_track_quat('-Z','Y').to_euler()

def render(file,loc,target,res=(640,360),lens=40,ortho=None):
    if '--no-render' in sys.argv:return
    c=camera('QA_ONLY_'+file,loc,target,lens,ortho);sc=bpy.context.scene;sc.render.resolution_x,sc.render.resolution_y=res;sc.render.filepath=str(ROOT/'qa'/file);bpy.ops.render.render(write_still=True);bpy.data.objects.remove(c,do_unlink=True)

def all_sources():
    catalogue={'header':'AST-VR-01-H','sill':'AST-VR-01-S','jamb':'AST-VR-01-J','terminal':'AST-VR-01-T'}
    joins={
      'header':[{'datum':[0,0,0],'normal':[-1,0,0],'profile':'crown_350'},{'datum':[2.2,0,0],'normal':[1,0,0],'profile':'crown_350'}],
      'sill':[{'datum':[0,0,0],'normal':[-1,0,0],'profile':'sill_700'},{'datum':[2.2,0,0],'normal':[1,0,0],'profile':'sill_700'}],
      'jamb':[{'datum':[0,0,0],'normal':[-1,0,0],'profile':'crown_350'},{'datum':[0,0,-2.2],'normal':[-1,0,0],'profile':'sill_700'}],
      'terminal':[{'datum':[0,0,0],'normal':[-1,0,0],'profile':'crown_350'}]}
    for kind,cid in catalogue.items():
        clear();settings();objs=create(kind);bpy.context.view_layer.update()
        source=ROOT/'source'/(cid+'.blend');out=ROOT/'exports'/(cid+'.glb')
        bpy.context.scene['asset_qa_only']=True;bpy.context.scene['catalogue_id']=cid
        for o in objs:o['catalogue_id']=cid;o['pivot_description']='Nominal left seam at origin; jamb pivot is nominal top seam';o['seams_json']=json.dumps(joins[kind])
        bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True);export(objs,out)
        meta={'catalogue_id':cid,'kind':kind,'source_blend':str(source.relative_to(ROOT)),'runtime_glb':str(out.relative_to(ROOT)),'bounds':bounds(objs),'triangles_evaluated':triangles(objs),'editable_objects':[o.name for o in objs],'modifiers_retained':['Bevel 1.2 mm / 2 segments','Weighted normals'],'material_roles':['ivory_enamel','warm_walnut'],'pivot_local_m':[0,0,0],'seams':joins[kind],'seam_air_gap_m':.002,'intended_use':{'header':'Straight repeatable crown above an aperture; X length can be authored parametrically, continuous profiles at both ends.','sill':'Straight deep sill and floor-reaching plinth; X length can be authored parametrically.','jamb':'Right-hand full height jamb with upper and lower rounded corner/shoulder; left side is mirrored and applied at export.','terminal':'Closed header-to-wall crown termination; one matching crown seam, eased and fully capped outside end. Crown profile only.'}[kind], 'provenance':'New original script-assisted design referencing supplied images for shape/material guidance; no recovered game content','export':{'Blender':'4.3.2','format':'glTF 2.0 GLB','apply_modifiers':True,'Y_up':True,'selection_only':True,'unit_scale':1.0,'embedded_material_textures':True},'contact_annotations':'Architectural surface only; no actor or physics acceptance. Sill foot at assembly Z0. Optional pane interface lies at Y+0.145; no pane provided.'}
        ALL_META.append(meta)

def assembly(exploded=False):
    objs=[]
    for kind,pos,mirror in [('header',(-1.1,0,2.9),False),('sill',(-1.1,0,.7),False),('jamb',(1.1,0,2.9),False),('jamb',(-1.1,0,2.9),True)]:
        parts=create(kind,('left_' if mirror else 'right_' if kind=='jamb' else ''))
        for o in parts:
            if mirror:
                for v in o.data.vertices:v.co.x=-v.co.x
                bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
                o['handedness']='Left derived from same J source; mirror baked in mesh, positive object scale'
            o.location=pos
            if exploded:
                if kind=='header':o.location.z+=.38
                if kind=='sill':o.location.z=.7
                if kind=='jamb':o.location.x+=-.35 if mirror else .35
        objs.extend(parts)
    bpy.context.view_layer.update();return objs

def collision_proposals():
    p={'status':'PROPOSAL ONLY; no engine, actor, approach, motion or contact acceptance','units':'metres in Blender source local coordinates','pieces':{}}
    for kind in ('header','sill','jamb','terminal'):
        rings=paths(kind);hulls=[]
        for a,b in zip(rings,rings[1:]):
            points=[]
            for x,z,nx,nz,w in (a,b):
                for r,y in [(0,-.16),(w,-.02),(w,.18),(0,.18)]:points.append([x+nx*r,y,z+nz*r])
                if kind=='terminal':
                    points.append([x,.245,z+w]);points.append([x,.245,z])
            hulls.append({'type':'convex_hull_points','points':points})
        p['pieces'][kind]={'method':'Separate longitudinal convex segments; never whole opening convex hull','volumes':hulls,'caveat':'Conservative simplified proposals follow the perimeter; corner chord error remains to be tuned against original engine/rig.'}
    (ROOT/'collision_proposals.json').write_text(json.dumps(p,indent=2))

def main():
    all_sources();collision_proposals();clear();settings();objs=assembly();stage()
    bpy.context.scene['asset_qa_only']=True;bpy.context.scene['scope']='Separate uninstalled reveal component assembly; no glass, room hull, controller, view or game'
    export(objs,ROOT/'exports/AST-VR-01-ASSEMBLY.glb')
    meta={'family':'AST-VR-01','unique_assets':4,'assembly':{'bounds':bounds(objs),'triangles_evaluated':triangles(objs),'clear_aperture_bounds_m':{'min':[-1.4,.145,.7],'max':[1.4,.145,2.9]},'clear_aperture_width_height_m':[2.8,2.2],'inner_corner_radius_m':.3,'outer_width_height_depth_m':[3.35,3.25,.43],'floor_contact_min_z_m':bounds(objs)['min_m'][2],'instances':[{'id':'AST-VR-01-H','translation':[-1.1,0,2.9]},{'id':'AST-VR-01-S','translation':[-1.1,0,.7]},{'id':'AST-VR-01-J','translation':[1.1,0,2.9]},{'id':'AST-VR-01-J','translation':[-1.1,0,2.9],'handedness':'mirrored mesh with recalculated outward normals'}]},'assets':ALL_META,'QA_status':'Blender component inspection only. No original room fit, scene view, game/performance, actor contact or physics acceptance.','design':'Substantial radial ivory envelope with depth-shaped shoulder and exposed 0.347 m timber throat; ellipse-derived outer corners keep exact exterior envelope. Header/sill modular seams have designed 2 mm gap. Terminal is separately demonstrated and is not needed on the closed loop.','join_support':{'H_to_J':'crown_350 exact cross-section at nominal X seam; surfaces set back 1 mm on each side','S_to_J':'sill_700 exact cross-section at nominal X seam; surfaces set back 1 mm on each side','H_to_T':'crown_350 exact cross-section; T is fully capped at distal end','J_left':'Mirror geometry across local X, recalculate normals, retain scale(+1,+1,+1)','unsupported':'No wall/hull boolean, pane, door, generic arbitrary-angle transition, or terminal-to-sill claim'},'references':[str(p.relative_to(CAT)) for p in sorted((CAT/'references').rglob('*.png'))]}
    render('neutral_640.png',(4.3,-6.8,3.35),(0,0,1.65),ortho=6.8)
    render('standing_640.png',(0,-5.25,1.65),(0,0,1.65),lens=30)
    render('seated_640.png',(.45,-5.25,1.15),(.1,0,1.45),lens=30)
    render('detail_1280.png',(3.6,-4.1,3.6),(.75,-.03,2.25),res=(1280,960),ortho=2.05)
    c=camera('QA_ONLY_saved_camera',(4.3,-6.8,3.35),(0,0,1.65),ortho=6.8)
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source/AST-VR-01-ASSEMBLY.blend'),compress=True)
    clear();settings();objs=assembly(True);stage()
    render('join_exploded_1280.png',(4.7,-7,3.6),(0,0,1.7),res=(1280,960),ortho=5.7)
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'qa/joins_editable.blend'),compress=True)
    clear();settings();h=create('header');t=create('terminal')
    for o in h:o.location=(-1.1,0,1.15)
    for o in t:o.location=(1.1,0,1.15)
    stage();render('terminal_closed_1280.png',(3.3,-3.8,2.6),(.85,0,1.33),res=(1280,960),ortho=1.35)
    render('terminal_rear_1280.png',(3.3,3.4,2.5),(1.11,0,1.34),res=(1280,960),ortho=.9)
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'qa/terminal_editable.blend'),compress=True)
    (ROOT/'manifest.json').write_text(json.dumps(meta,indent=2))
    print('REVEAL_KIT_COMPLETE',ROOT)

if __name__=='__main__':main()
