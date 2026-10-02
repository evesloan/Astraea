"""Original aquatic lounge furniture. Blender 4.3.2 script-assisted authoring.

Run blender -b -t 2 --python source/build_aquatic_lounge.py
The script saves editable sources, then evaluates and consolidates export copies.
No reference pixels, game files, external meshes or paid tools are used.
"""
from pathlib import Path
import sys, math, json, hashlib
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1]
CAT=ROOT.parents[1]
sys.path.insert(0,str(CAT/'standards'))
from materials import materials
from aquatic_materials import materials as aquatic_materials
M={};PARTS=[];JOINS=[];COLLISIONS=[]

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system='METRIC'
    bpy.context.scene.unit_settings.scale_length=1
    global M,PARTS,JOINS,COLLISIONS
    M=materials();M.update(aquatic_materials());PARTS=[];JOINS=[];COLLISIONS=[]

def metric_uv(ob):
    me=ob.data;uv=me.uv_layers.active or me.uv_layers.new(name='UV_Metric_Metres')
    uv.name='UV_Metric_Metres'
    scale=ob.data.materials[0].get('meters_per_tile_uv',[1,1])
    for face in me.polygons:
        ax=max(range(3),key=lambda i:abs(face.normal[i]));axes=[k for k in range(3) if k!=ax]
        for li in face.loop_indices:
            v=me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv=(v[axes[0]]/scale[0],v[axes[1]]/scale[1])

def mesh(name,vs,fs,role,bevel=0,segments=2):
    me=bpy.data.meshes.new(name+'_editable_mesh');me.from_pydata(vs,[],fs);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob)
    me.materials.append(M[role]);ob['semantic_role']=role;metric_uv(ob)
    if bevel:
        m=ob.modifiers.new('Editable contact edge easing','BEVEL');m.width=bevel;m.segments=segments
        m=ob.modifiers.new('Weighted broad surface normals','WEIGHTED_NORMAL');m.keep_sharp=True
    PARTS.append(ob);return ob

def extrude(name,profile,lo,hi,role,axis='x',bevel=0):
    vs=[(x,a,b) if axis=='x' else (a,b,x) for x in (lo,hi) for a,b in profile]
    n=len(profile);fs=[tuple(reversed(range(n))),tuple(range(n,n*2))]
    fs +=[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(name,vs,fs,role,bevel)

def rounded(w,d,r,n=4):
    p=[]
    for cx,cy,deg in [(w/2-r,d/2-r,0),(-w/2+r,d/2-r,90),(-w/2+r,-d/2+r,180),(w/2-r,-d/2+r,270)]:
        for j in range(n):
            a=math.radians(deg+90*j/(n-1));p.append((cx+r*math.cos(a),cy+r*math.sin(a)))
    return p

def slab(name,w,d,z0,z1,role,center=(0,0),r=.03,bevel=.003):
    return extrude(name,[(x+center[0],y+center[1]) for x,y in rounded(w,d,r)],z0,z1,role,'z',bevel)

def beam(name,a,b,width,depth,role,bevel=.003):
    a,b=Vector(a),Vector(b);mid=(a+b)*.5;delta=b-a
    vs=[(sx*width/2,sy*depth/2,sz*delta.length/2) for sz in (-1,1) for sy in (-1,1) for sx in (-1,1)]
    fs=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
    ob=mesh(name,vs,fs,role,bevel);ob.location=mid;ob.rotation_euler=delta.to_track_quat('Z','Y').to_euler()
    return ob

def catmull(points,steps=4):
    out=[]
    for i in range(len(points)-1):
        p0=Vector(points[max(0,i-1)]);p1=Vector(points[i]);p2=Vector(points[i+1]);p3=Vector(points[min(len(points)-1,i+2)])
        for j in range(steps):
            t=j/steps
            out.append(tuple(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t)))
    out.append(points[-1]);return out

KNOTS=[(-1.04,.335),(-.90,.355),(-.68,.399),(-.43,.452),(-.22,.441),(-.02,.445),(.15,.503),(.37,.658),(.60,.833),(.80,.953),(.94,.986)]
PATH=catmull(KNOTS,4)
def height(y):
    for (a,za),(b,zb) in zip(PATH,PATH[1:]):
        if a<=y<=b:return za+(zb-za)*(y-a)/(b-a)
    return PATH[0][1] if y<PATH[0][0] else PATH[-1][1]
def halfwidth(y):return .334-.025*(abs(y)/1.04)**2

def curved_band(name,path,xc,w,t,role,bevel=.004):
    p=[(y,z+t/2) for y,z in path]+[(y,z-t/2) for y,z in reversed(path)]
    return extrude(name,p,xc-w/2,xc+w/2,role,bevel=bevel)

def sling_strip(name,strip,role):
    # Six contiguous load surfaces with open 8 mm drains, transverse soft crown,
    # and 22 mm closed thickness. The longitudinal profile creates the silhouette.
    vs=[];n=len(PATH)
    for lower in (True,False):
        for y,z in PATH:
            span=2*halfwidth(y);pitch=span/6;x0=-span/2+strip*pitch+.004;x1=-span/2+(strip+1)*pitch-.004
            for f in (0,.5,1):
                x=x0+(x1-x0)*f;rise=.007*(x/halfwidth(y))**2+(.003 if f==.5 else 0)
                vs.append((x,y,z+rise-(.022 if lower else 0)))
    fs=[]
    for layer in range(2):
        o=layer*n*3
        for j in range(n-1):
            for k in range(2):fs.append((o+j*3+k,o+j*3+k+1,o+(j+1)*3+k+1,o+(j+1)*3+k))
    for j in range(n-1):
        for k in (0,2):fs.append((j*3+k,(j+1)*3+k,n*3+(j+1)*3+k,n*3+j*3+k))
    for j in (0,n-1):
        for k in range(2):fs.append((j*3+k,j*3+k+1,n*3+j*3+k+1,n*3+j*3+k))
    ob=mesh(name,vs,fs,role,.0015,1)
    ob['design']='Water-shedding polymer-coated tension panel proposal; no absorbent domestic cushion, no tested drainage coefficient'
    return ob

def join(a,b,intent):JOINS.append({'members':[a.name,b.name],'intent':intent})
def box_collision(name,center,size,quat=None):
    row={'name':name,'type':'oriented_box_proposal','center_m':list(center),'size_m':list(size),'rotation_quaternion_wxyz':list(quat or (1,0,0,0))}
    COLLISIONS.append(row)
def beam_collision(name,a,b,width,depth):
    a,b=Vector(a),Vector(b);d=b-a;box_collision(name,(a+b)/2,(width,depth,d.length),d.to_track_quat('Z','Y'))

def reclining_crossbeam(name,y,role):
    # Match the local reclining tangent, so an underside support cannot cut
    # through the upper shoulder/foot contact surface on a slope.
    slope=(height(y+.008)-height(y-.008))/.016
    theta=math.atan(slope);c=math.cos(theta);s=math.sin(theta);z=height(y)-.039
    vs=[(x,y+t*c-n*s,z+t*s+n*c) for x in (-.36,.36) for n in (-.026,.026) for t in (-.028,.028)]
    fs=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
    ob=mesh(name,vs,fs,role,.004)
    ob['support_slope_degrees']=math.degrees(theta)
    box_collision(name,(0,y,z),(.72,.056,.052),(math.cos(theta/2),math.sin(theta/2),0,0))
    return ob

def lounger():
    rails={};legs={};runners={}
    for sign,label in [(-1,'L'),(1,'R')]:
        xc=sign*.357
        # True drawn ribbon, shaped through shin, thigh, pelvic dip and back.
        rail=curved_band(label+'_continuous_sculpted_side_rail',[(y,z-.039) for y,z in PATH],xc,.068,.066,'ivory_enamel',.006)
        rails[label]=rail
        runner=slab(label+'_swept_runner',.105,1.61,.020,.068,'ivory_enamel',(xc,-.035),.045,.006);runners[label]=runner
        for y,tag in [(-.74,'front'),(.67,'rear')]:
            shoe=slab(label+'_'+tag+'_floor_grip',.113,.185,0,.026,'aquatic_dark_grip',(xc,y),.045,.003);join(shoe,runner,'Shoe upper 6 mm is housed in bottom runner')
            box_collision(shoe.name,(xc,y,.013),(.113,.185,.026))
        front=[(-.783,.056),(-.686,.056),(-.505,.368),(-.507,.418),(-.594,.417),(-.641,.323)]
        rear=[(.622,.056),(.745,.056),(.568,.436),(.422,.674),(.331,.648),(.423,.441)]
        for tag,prof in [('front',front),('rear',rear)]:
            leg=extrude(label+'_'+tag+'_curved_load_leg',prof,xc-.036,xc+.036,'ivory_enamel',bevel=.006);legs[label,tag]=leg
            join(leg,runner,'Formed leg lower tongue overlaps runner');join(leg,rail,'Load leg top fitted into sculpted side rail')
        # Two real pin heads express the join without decorative outlines.
        for yy,zz,tag in [(-.555,.402,'front'),(.389,.639,'rear')]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.012,depth=.005,location=(xc+sign*.038,yy,zz),rotation=(0,math.pi/2,0))
            ob=bpy.context.object;ob.name=label+'_'+tag+'_recessed_join_cap';ob.data.materials.append(M['aquatic_satin_alloy']);ob['semantic_role']='aquatic_satin_alloy';metric_uv(ob);PARTS.append(ob)
        box_collision(runner.name,(xc,-.035,.044),(.105,1.61,.048))
        beam_collision(label+'_front_leg', (xc,-.736,.056),(xc,-.551,.407),.084,.085)
        beam_collision(label+'_rear_leg',(xc,.682,.056),(xc,.391,.650),.088,.092)
        for n,((ya,za),(yb,zb)) in enumerate(zip(KNOTS,KNOTS[1:])):
            beam_collision(label+'_curved_rail_segment_'+str(n),(xc,ya,za-.039),(xc,yb,zb-.039),.070,.068)
    strips=[sling_strip('drained_contact_panel_'+str(i+1),i,'aquatic_clay_sling') for i in range(6)]
    for yy,tag in [(-.90,'foot'),(-.54,'knee'),(-.13,'hip'),(.25,'lumbar'),(.58,'shoulder'),(.85,'head')]:
        bar=reclining_crossbeam(tag+'_fitted_cross_support',yy,'aquatic_satin_alloy')
        join(bar,rails['L'],'Cross support end intersects side rail');join(bar,rails['R'],'Cross support end intersects side rail')
        for panel in strips:join(bar,panel,'Slope-aligned cross support overlaps panel underside while remaining below top contact face')
    # Back/foot/contact collision follows profile, keeps under-seat and side approach open.
    for n,((ya,za),(yb,zb)) in enumerate(zip(KNOTS,KNOTS[1:])):
        beam_collision('contact_surface_segment_'+str(n),(0,ya,za-.011),(0,yb,zb-.011),.665,.028)
    return {'catalogue_id':'AST-AQU-001','name':'Sculpted drained wet-area lounger','unique_design':True,
      'dimensions_design_m':[.827,1.98,1.0],
      'contact_proposals':{'pelvic_contact_m':[.055,-.12,height(-.12)+.003],'thigh_contact_m':[.055,-.40,height(-.40)+.003],'shoulder_contact_m':[.055,.61,height(.61)+.003],'foot_contact_m':[.055,-.91,height(-.91)+.003],'maximum_contact_width_m':.66,'back_slope_degrees_from_horizontal':math.degrees(math.atan2(.953-.503,.80-.15)),'interpretation':'Human-scale reclining zones only. No universal-species, comfort, load, accessibility or safety certification.'},
      'drainage_design':{'open_longitudinal_slots_count':5,'nominal_slot_width_m':.008,'foot_and_head_edges':'Open discharge. No fabric pocket or closed basin','limitation':'Geometry proposal only; permeability and wet grip untested'},
      'approach_proposal':{'left_clear_rectangle_m':[[-1.15,-.55,0],[-.43,.25,0]],'right_clear_rectangle_m':[[.43,-.55,0],[1.15,.25,0]],'foot_clear_rectangle_m':[[-.44,-1.7,0],[.44,-1.10,0]],'status':'Placement proposal pending original engine and actor rigs'},
      'support_design':'Paired sled runners, four floor grips, four shaped load legs, six cross supports and two continuous rails. Open underside retained.'}

def elliptical_strip(name,x0,x1,rx,ry,z0,z1,role,steps=8):
    # The ends follow the tabletop ellipse; panels are separate closed solids.
    xs=[x0+(x1-x0)*i/steps for i in range(steps+1)]
    p=[(x,ry*math.sqrt(max(0,1-(x/rx)**2))) for x in xs]
    p +=[(x,-ry*math.sqrt(max(0,1-(x/rx)**2))) for x in reversed(xs)]
    return extrude(name,p,z0,z1,role,'z',.002)

def ellipse_arc(name,a0,a1,rx,ry,width,z0,z1,role,n=16):
    angles=[a0+(a1-a0)*i/n for i in range(n+1)]
    p=[(rx*math.cos(a),ry*math.sin(a)) for a in angles]
    p +=[((rx-width)*math.cos(a),(ry-width)*math.sin(a)) for a in reversed(angles)]
    return extrude(name,p,z0,z1,role,'z',.003)

def table():
    supports={};cross=[]
    for xc,label in [(-.204,'L'),(.204,'R')]:
        # Bowed trestle flares into four floor contacts and upper tray bearings.
        profile=[(-.210,.022),(-.141,.022),(-.099,.113),(-.081,.204),(-.104,.305),(-.174,.394),(-.187,.407),
                 (.187,.407),(.174,.394),(.104,.305),(.081,.204),(.099,.113),(.141,.022),(.210,.022),(.171,.147),(.154,.215),(.175,.292),(.231,.382),(.231,.423),(-.231,.423),(-.231,.382),(-.175,.292),(-.154,.215),(-.171,.147)]
        # Each open trestle is a U-shaped cross-section with slender bowed legs.
        trestle=extrude(label+'_bowed_open_trestle',profile,xc-.032,xc+.032,'ivory_enamel',bevel=.006);supports[label]=trestle
        # Blender's concave bevel shoulder creates duplicate vertices ~30 nm
        # apart. Retain the bevel and merge only this numerical residue locally.
        weld=trestle.modifiers.new('Merge submicron bevel duplicates','WELD');weld.merge_threshold=.000001
        trestle['numerical_correction']='Scoped 1 micrometre post-bevel weld; original rejected check retained in qa/initial_rejected'
        for yy,tag in [(-.178,'front'),(.178,'rear')]:
            shoe=slab(label+'_'+tag+'_floor_grip',.087,.099,0,.028,'aquatic_dark_grip',(xc,yy),.022,.003);join(shoe,trestle,'6 mm shoe/trestle bottom overlap')
            box_collision(shoe.name,(xc,yy,.014),(.087,.099,.028))
            beam_collision(label+'_'+tag+'_lower_leg',(xc,yy,.027),(xc,math.copysign(.12,yy),.216),.072,.065)
            beam_collision(label+'_'+tag+'_upper_leg',(xc,math.copysign(.12,yy),.216),(xc,math.copysign(.205,yy),.408),.072,.065)
        box_collision(label+'_top_bearing',(xc,0,.407),(.070,.466,.034))
    for y in (-.155,.155):
        ob=beam('tray_bearing_cross_rail_'+str(y),(-.246,y,.402),(.246,y,.402),.044,.048,'aquatic_satin_alloy',.004);cross.append(ob)
        for s in supports.values():join(ob,s,'Cross rail inset into formed trestle top')
        beam_collision(ob.name,(-.246,y,.402),(.246,y,.402),.044,.048)
    # Two-piece rim is deliberately interrupted for drain discharge at front/rear.
    rims=[]
    for sign in (-1,1):
        a0=-math.pi/2+.035 if sign==1 else math.pi/2+.035;a1=math.pi/2-.035 if sign==1 else 3*math.pi/2-.035
        rims.append(ellipse_arc(('R' if sign==1 else 'L')+'_raised_draining_tray_rim',a0,a1,.333,.283,.023,.414,.453,'ivory_enamel'))
    # Four stone contact panels, distinct central narrow teal strip and true slots.
    panels=[]
    for i,(a,b) in enumerate([(-.305,-.162),(-.154,-.043),(.043,.154),(.162,.305)]):
        panels.append(elliptical_strip('stone_use_surface_'+str(i+1),a,b,.311,.26,.416,.438,'warm_stone'))
    panels.append(elliptical_strip('teal_center_wet_channel',-.035,.035,.311,.26,.414,.431,'aquatic_teal_sling'))
    for p in panels:
        for c in cross:join(p,c,'Surface slab underside bears on two cross rails')
    for rim in rims:
        join(rim,supports[rim.name[0]],'Outer tray rim bears on same-side formed trestle top')
    # Rim and top collisions are separate slabs; under-table access stays open.
    box_collision('usable_top_contact_slab',(0,0,.427),(.613,.510,.026))
    for i in range(16):
        a=i*math.pi/8;b=(i+1)*math.pi/8
        beam_collision('tray_rim_segment_'+str(i),(.322*math.cos(a),.272*math.sin(a),.435),(.322*math.cos(b),.272*math.sin(b),.435),.026,.039)
    return {'catalogue_id':'AST-AQU-002','name':'Companion drained tray table','unique_design':True,
      'contact_proposals':{'stone_surface_height_m':.438,'center_channel_height_m':.431,'rim_height_m':.453,'usable_ellipse_axes_m':[.622,.520],'placement':'Side reach companion surface, not a seated knee-overhang dining table','interpretation':'Human-scale dimensional proposal. Stability, tip loads, wet friction and all-species use untested.'},
      'drainage_design':{'open_parallel_slot_width_m':.008,'stone_to_teal_channel_height_drop_m':.007,'rim_discharge_apertures':'Two 19 mm nominal end gaps at front/rear ellipse tips','limitation':'Geometric drain intent, no flow simulation'},
      'support_design':'Two open bowed trestles, four separate floor grips and two cross rails under the segmented tray',
      'approach_proposal':{'preferred_placement_to_lounger':'Either side of hip zone with a clear transfer route retained on the other side','status':'Proposal only; no species, interaction or real room validation'}}

def evaluated(ob,dg):
    eo=ob.evaluated_get(dg);me=eo.to_mesh();me.calc_loop_triangles()
    vs=[tuple(ob.matrix_world@v.co) for v in me.vertices];fs=[tuple(t.vertices) for t in me.loop_triangles]
    row={'name':ob.name,'role':ob['semantic_role'],'triangles':len(fs),'bounds_min_m':[min(v[k] for v in vs) for k in range(3)],'bounds_max_m':[max(v[k] for v in vs) for k in range(3)],'editable_modifiers':[m.name for m in ob.modifiers]}
    tree=BVHTree.FromPolygons(vs,fs,all_triangles=True)
    eo.to_mesh_clear();return row,tree,vs

def finish(info):
    asset=info['catalogue_id'];bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
    records={};trees={};allvs=[]
    for ob in PARTS:
        ob['catalogue_id']=asset;ob['provenance']='New independent original script-assisted design, 2026-10-02'
        row,tree,vs=evaluated(ob,dg);records[ob.name]=row;trees[ob.name]=tree;allvs+=vs
    if asset=='AST-AQU-001':
        samples={}
        for label,y in [('pelvic',-.12),('thigh',-.4),('shoulder',.61),('foot',-.91)]:
            hits=[]
            for name,tree in trees.items():
                if not name.startswith('drained_contact_panel_'):continue
                loc,normal,idx,distance=tree.ray_cast(Vector((.055,y,2)),Vector((0,0,-1)),3)
                if loc is not None:hits.append((loc.z,name,list(loc),list(normal)))
            z,name,loc,normal=max(hits)
            samples[label]={'position_m':loc,'surface_normal':normal,'source_part':name,'method':'Vertical BVH ray to evaluated coated contact panel at X0.055; avoids central drain slot'}
            info['contact_proposals'][label+'_contact_m']=loc
        info['measured_contact_samples']=samples
    lo=[min(v[k] for v in allvs) for k in range(3)];hi=[max(v[k] for v in allvs) for k in range(3)]
    checks=[]
    for row in JOINS:
        a,b=row['members'];ra,rb=records[a],records[b]
        overlap=[min(ra['bounds_max_m'][k],rb['bounds_max_m'][k])-max(ra['bounds_min_m'][k],rb['bounds_min_m'][k]) for k in range(3)]
        hits=len(trees[a].overlap(trees[b]));checks.append(dict(row,aabb_overlap_xyz_m=overlap,evaluated_surface_intersection_pairs=hits,status='PASS' if hits else 'REVIEW'))
    info.update({'blender_version':bpy.app.version_string,'units':'metres','pivot_m':[0,0,0],'datum':'Floor at Z0; width X, head +Y, front/feet -Y, up +Z. GLB standard Y-up conversion.','dimensions_m':[hi[k]-lo[k] for k in range(3)],'bounds_min_m':lo,'bounds_max_m':hi,'triangles':sum(r['triangles'] for r in records.values()),'editable_semantic_parts':len(PARTS),'parts':list(records.values()),'material_roles':sorted({o['semantic_role'] for o in PARTS}),'floor_contact_checks':{'minimum_z_m':lo[2],'floor_z_zero_pass':abs(lo[2])<1e-6,'grips':[r for r in records.values() if 'floor_grip' in r['name']]},'join_checks':checks,'source':f'source/{asset}.blend','export':f'exports/{asset}.glb','generator':'source/build_aquatic_lounge.py','reference_manifest':'../../batches/batch05/reference_manifest.json','provenance':'New original catalogue asset. Aquatic reference used as warm sculpted form/use guidance; no sampled pixels, recovered game content or literal recreation.','limitations':['Component QA only; no original game adoption','No wet material, physical load, flow, human ergonomics, species rig or safety certification','Collision/contact/approach data are untested numerical proposals'],'export_settings':{'format':'GLB','Y_up':True,'evaluated_modifiers':True,'materials':'One static mesh per semantic role','textures':'Packed in source and embedded in GLB','active_uv_normalization':'UV_Metric_Metres before joining evaluated copies','lights':False}})
    root=bpy.data.objects.new(asset+'_floor_origin',None);bpy.context.collection.objects.link(root)
    root['catalogue_id']=asset;root['pivot']='Floor origin Z0'
    for ob in PARTS:ob.parent=root
    bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source'/f'{asset}.blend'))
    bpy.ops.object.select_all(action='DESELECT');exports=[]
    for role in info['material_roles']:
        copies=[]
        for source in [o for o in PARTS if o['semantic_role']==role]:
            me=bpy.data.meshes.new_from_object(source.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg)
            if not me.uv_layers.active:raise ValueError('Missing UV '+source.name)
            active=me.uv_layers.active
            for layer in list(me.uv_layers):
                if layer!=active:me.uv_layers.remove(layer)
            active.name='UV_Metric_Metres';active.active_render=True
            ob=bpy.data.objects.new('EXPORT_'+source.name,me);bpy.context.collection.objects.link(ob);ob.matrix_world=source.matrix_world.copy()
            if 'bowed_open_trestle' in source.name:
                # Reproject the newly welded corner faces in metric units; the
                # nondirectional ivory finish keeps its role and true scale.
                metric_uv(ob)
            ob.select_set(True);copies.append(ob)
        bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();out=bpy.context.object;out.name=asset+'__'+role
        bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);out['material_role']=role;exports.append(out)
        out.select_set(False)
    for ob in exports:ob.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(ROOT/'exports'/f'{asset}.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_materials='EXPORT',export_extras=True)
    for key,path in [('source_sha256',ROOT/info['source']),('glb_sha256',ROOT/info['export']),('generator_sha256',Path(__file__))]:info[key]=hashlib.sha256(path.read_bytes()).hexdigest()
    info['collision_proposal_file']=f'{asset}.collision_proposal.json'
    (ROOT/f'{asset}.collision_proposal.json').write_text(json.dumps({'catalogue_id':asset,'coordinates':'Blender metres Z-up; quaternions WXYZ','status':'Geometric proposals only. Not imported, simulated or validated in engine. Segmental contact collision bridges drain slots; open underside and side approach remain.','shapes':COLLISIONS,'approach':info['approach_proposal']},indent=2)+'\n')
    (ROOT/f'{asset}.manifest.json').write_text(json.dumps(info,indent=2)+'\n')
    return info

if __name__=='__main__':
    rows=[]
    for builder in [lounger,table]:
        reset();rows.append(finish(builder()))
    (ROOT/'manifest.json').write_text(json.dumps({'family':'Aquatic lounge furniture','assets':[{k:v for k,v in r.items() if k not in ['parts','join_checks']} for r in rows],'scope':'Independent original catalogue; two unique artistic assets; original game remains untouched'},indent=2)+'\n')
    (ROOT/'qa'/'join_checks.json').write_text(json.dumps({r['catalogue_id']:r['join_checks'] for r in rows},indent=2)+'\n')
    print('LOUNGE_COMPLETE',[(r['catalogue_id'],r['dimensions_m'],r['triangles'],sum(j['status']!='PASS' for j in r['join_checks'])) for r in rows])
