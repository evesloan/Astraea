"""One new editable Astraea staff work cabinet; intentional script-assisted sheet-metal authoring.
Run Blender 4.3.2: blender -b -t 4 --python build_staff_workbay.py
All coordinates in metres; Z up; approach/front is negative Y. No game code.
"""
from pathlib import Path
import sys, math, json, hashlib
import bpy, bmesh
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parents[1]
sys.path.insert(0,str(BASE/'standards'))
from staff_materials import materials
ID='AST-STF-007'; SLUG=ID+'_supply_work_cabinet'
PARTS=[]; COLL=[]; M={}; PIVOT=(-.837,-.317,.2)
ROLE_BODY='staff_bluegrey_paint'; ROLE_TOP='staff_zinc'; ROLE_DARK='staff_rubber'; ROLE_LIGHT='staff_white_paint'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def uv_metric(ob):
    me=ob.data;uv=me.uv_layers.active or me.uv_layers.new(name='UV_Metric_Metres');uv.name='UV_Metric_Metres';uv.active_render=True
    for other in list(me.uv_layers):
        if other!=uv:me.uv_layers.remove(other)
    scale=me.materials[0].get('meters_per_tile_uv',[1,1])
    for p in me.polygons:
        axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis]
        for li in p.loop_indices:
            co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]]/scale[0],co[axes[1]]/scale[1])

def mesh(name,vs,fs,role,bevel=.001,assembly='static',collision=True):
    me=bpy.data.meshes.new(name+'_mesh');me.from_pydata(vs,[],fs);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(M[role]);uv_metric(ob)
    ob['catalogue_id']=ID;ob['semantic_role']=role;ob['assembly']=assembly
    if bevel:
        md=ob.modifiers.new('Editable formed edge easing','BEVEL');md.width=bevel;md.segments=2;md.use_clamp_overlap=True
        md=ob.modifiers.new('Weighted panel normals','WEIGHTED_NORMAL');md.keep_sharp=True
    PARTS.append(ob)
    if collision:
        lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)]
        COLL.append({'source_part':name,'assembly':assembly,'shape':'box_proposal','centre_m':[(a+b)/2 for a,b in zip(lo,hi)],'size_m':[b-a for a,b in zip(lo,hi)],'note':'Per-part conservative solid only; verify/adopt in original engine.'})
    return ob

def box(name,lo,hi,role,bevel=.001,assembly='static',collision=True):
    x0,y0,z0=lo;x1,y1,z1=hi
    return mesh(name,[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role,bevel,assembly,collision)

def extrude(name,profile,a,b,axis,role,bevel=.001,assembly='static',collision=False):
    if axis=='x':vs=[(v,p,q) for v in (a,b) for p,q in profile]
    elif axis=='y':vs=[(p,v,q) for v in (a,b) for p,q in profile]
    else:vs=[(p,q,v) for v in (a,b) for p,q in profile]
    n=len(profile);fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(name,vs,fs,role,bevel,assembly,collision)

def cylinder(name,centre,r,depth,role,assembly='static',axis='z',n=12):
    vs=[]
    for v in (-depth/2,depth/2):
        for i in range(n):
            a=2*math.pi*i/n;p=r*math.cos(a);q=r*math.sin(a)
            delta=(p,q,v) if axis=='z' else ((p,v,q) if axis=='y' else (v,p,q))
            vs.append(tuple(centre[k]+delta[k] for k in range(3)))
    return mesh(name,vs,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],role,.0006,assembly)

def collision_box(name,lo,hi,assembly='static',note='Separate formed-sheet region, storage void preserved.'):
    COLL.append({'source_part':name,'assembly':assembly,'shape':'box_proposal','centre_m':[(a+b)/2 for a,b in zip(lo,hi)],'size_m':[b-a for a,b in zip(lo,hi)],'note':note})

def tray(name,x0,x1,y0,y1,z,role,lip=.018):
    # A continuous U-shaped sheet: actual front/rear upturned safety lips, 4 mm steel.
    t=.004;p=[(y0,z+lip),(y0+t,z+lip),(y0+t,z+t),(y1-t,z+t),(y1-t,z+lip),(y1,z+lip),(y1,z),(y0,z)]
    ob=extrude(name,p,x0,x1,'x',role,.0007)
    collision_box(name+'_deck',(x0,y0,z),(x1,y1,z+t))
    collision_box(name+'_front_lip',(x0,y0,z),(x1,y0+t,z+lip))
    collision_box(name+'_rear_lip',(x0,y1-t,z),(x1,y1,z+lip))
    return ob

def perforated_leaf():
    x0,x1=-.815,-.065;z0,z1=.202,.858;y0,y1=-.306,-.300
    slotx=(-.742,-.232);slots=[(.635+i*.027,.646+i*.027) for i in range(6)]
    xs=sorted({x0,x1,*slotx});zs=sorted({z0,z1,*[p for pair in slots for p in pair]})
    filled={}
    for i in range(len(xs)-1):
        for j in range(len(zs)-1):
            xc=(xs[i]+xs[i+1])/2;zc=(zs[j]+zs[j+1])/2
            filled[i,j]=not (slotx[0]<xc<slotx[1] and any(a<zc<b for a,b in slots))
    vs=[];index={};fs=[]
    def vi(x,y,z):
        p=(x,y,z)
        if p not in index:index[p]=len(vs);vs.append(p)
        return index[p]
    for (i,j),yes in filled.items():
        if not yes:continue
        a,b=xs[i:i+2];c,d=zs[j:j+2]
        fs += [(vi(a,y0,c),vi(b,y0,c),vi(b,y0,d),vi(a,y0,d)),(vi(a,y1,c),vi(a,y1,d),vi(b,y1,d),vi(b,y1,c))]
        for dx,dz,ps in [(-1,0,[(a,y0,c),(a,y0,d),(a,y1,d),(a,y1,c)]),(1,0,[(b,y0,c),(b,y1,c),(b,y1,d),(b,y0,d)]),(0,-1,[(a,y0,c),(a,y1,c),(b,y1,c),(b,y0,c)]),(0,1,[(a,y0,d),(b,y0,d),(b,y1,d),(a,y1,d)])]:
            if not filled.get((i+dx,j+dz),False):fs.append(tuple(vi(*p) for p in ps))
        collision_box('door_face_solid_cell_%02d_%02d'%(i,j),(a,y0,c),(b,y1,d),'door_leaf','Actual solid cell; ventilation apertures retained.')
    ob=mesh('DOOR_perforated_folded_leaf',vs,fs,ROLE_BODY,.00065,'door_leaf',False)
    ob['construction']='One connected 6 mm sheet mesh with six real through-slots; welded grid topology; no hidden front faces or alpha cutout.'
    for label,lo,hi in [('left',(-.815,-.300,.202),(-.809,-.285,.858)),('right',(-.071,-.300,.202),(-.065,-.285,.858)),('top',(-.809,-.300,.852),(-.071,-.285,.858)),('bottom',(-.809,-.300,.202),(-.071,-.285,.208))]:
        box('DOOR_'+label+'_fold_return',lo,hi,ROLE_BODY,.0008,'door_leaf')
    # Plain metal label window: no invented inventory story.
    for label,lo,hi in [('upper',(-.606,-.309,.818),(-.374,-.306,.822)),('lower',(-.606,-.309,.791),(-.374,-.306,.795)),('endL',(-.606,-.309,.795),(-.602,-.306,.818)),('endR',(-.378,-.309,.795),(-.374,-.306,.818))]:
        box('DOOR_blank_label_holder_'+label,lo,hi,ROLE_TOP,.0004,'door_leaf')
    box('DOOR_vertical_pull_grip',(-.147,-.355,.432),(-.129,-.337,.592),ROLE_DARK,.004,'door_handle')
    for z,label in [(.432,'bottom'),(.574,'top')]:box('DOOR_pull_'+label+'_stand_off',(-.148,-.345,z),(-.128,-.303,z+.018),ROLE_TOP,.002,'door_handle')
    for z,label in [(.29,'lower'),(.754,'upper')]:
        # Genuine outside-front hinge: static pin, clear axial interval, radial bore in moving barrel.
        box('HINGE_'+label+'_static_mount',(-.87,-.319,z-.041),(-.850,-.255,z+.041),ROLE_TOP,.001,'bearing_static')
        for dz,end in [(-.037,'lower'),(.026,'upper')]:box('HINGE_'+label+'_'+end+'_pin_ear',(-.857,-.328,z+dz),(-.827,-.307,z+dz+.011),ROLE_TOP,.0006,'bearing_static')
        cylinder('HINGE_'+label+'_fixed_pin',(PIVOT[0],PIVOT[1],z),.004,.080,ROLE_TOP,'bearing_static')
        # Annular eight-sided barrel creates a real pivot bore rather than filling it.
        vs=[];n=12
        for zz in (z-.025,z+.025):
            for r in (.0046,.009):
                for i in range(n):
                    a=2*math.pi*i/n;vs.append((PIVOT[0]+r*math.cos(a),PIVOT[1]+r*math.sin(a),zz))
        fs=[]
        for i in range(n):
            k=(i+1)%n
            fs.extend([(i,k,24+k,24+i),(12+i,36+i,36+k,12+k),(i,12+i,12+k,k),(24+i,24+k,36+k,36+i)])
        mesh('DOOR_'+label+'_bored_hinge_knuckle',vs,fs,ROLE_TOP,.00025,'bearing_moving',False)
        box('DOOR_'+label+'_hinge_strap',(-.830,-.320,z-.023),(-.798,-.310,z+.023),ROLE_TOP,.0006,'door_leaf')


def build():
    global M
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
    M=materials()
    # Four grounded supports carry the hemmed base and corner channels.
    for x,side in [(-.812,'L'),(.812,'R')]:
        for y,end in [(-.218,'front'),(.226,'rear')]:
            cylinder('FOOT_'+side+'_'+end+'_rubber_pad',(x,y,.012),.036,.024,ROLE_DARK)
            cylinder('FOOT_'+side+'_'+end+'_level_spindle',(x,y,.049),.010,.058,ROLE_TOP)
            box('LEG_'+side+'_'+end+'_square_tube',(x-.023,y-.023,.059),(x+.023,y+.023,.186),ROLE_BODY,.002)
    # Formed C side cheeks; open front and actual rear returns.
    p=[(-.875,-.270),(-.841,-.270),(-.841,-.262),(-.867,-.262),(-.867,.276),(-.841,.276),(-.841,.284),(-.875,.284)]
    for side,pp in [('L',p),('R',[(-x,y) for x,y in reversed(p)])]:
        ob=extrude('BODY_'+side+'_formed_side_channel',pp,.165,.919,'z',ROLE_BODY,.0013)
        ob['construction']='8 mm outer panel with 34 mm folded front/rear end returns; continuous extruded C profile.'
        xx=(-.875,-.867) if side=='L' else (.867,.875)
        collision_box(ob.name+'_skin',(xx[0],-.270,.165),(xx[1],.284,.919))
        xx=(-.875,-.841) if side=='L' else (.841,.875)
        collision_box(ob.name+'_front_fold',(xx[0],-.270,.165),(xx[1],-.262,.919));collision_box(ob.name+'_rear_fold',(xx[0],.276,.165),(xx[1],.284,.919))
    box('BODY_washable_rear_panel',(-.867,.277,.177),(.867,.285,.920),ROLE_LIGHT,.0012)
    box('BODY_central_divider',(-.043,-.257,.183),(-.035,.277,.915),ROLE_BODY,.001)
    box('BODY_centre_front_fold',(-.054,-.270,.182),(-.024,-.256,.916),ROLE_BODY,.001)
    tray('BASE_continuous_folded_catch_deck',-.867,.867,-.265,.278,.166,ROLE_BODY,.026)
    box('BASE_recessed_toe_cross_member',(-.83,-.238,.128),(.83,-.206,.166),ROLE_TOP,.002)
    box('BASE_rear_support_cross_member',(-.83,.218,.128),(.83,.25,.166),ROLE_TOP,.002)
    # Worktop is a folded cross-section, not a solid countertop block.
    p=[(-.31,.940),(.31,.940),(.31,.914),(.304,.914),(.304,.934),(-.304,.934),(-.304,.899),(-.280,.899),(-.280,.893),(-.31,.893)]
    top=extrude('COUNTER_continuous_rolled_nose',p,-.9,.9,'x',ROLE_TOP,.0015)
    top['construction']='6 mm continuous worktop sheet, 47 mm closed front downturn with inward safety hem, 26 mm rear return.'
    collision_box(top.name+'_work_plane',(-.9,-.31,.934),(.9,.31,.940))
    collision_box(top.name+'_front_nose',(-.9,-.31,.893),(.9,-.304,.934));collision_box(top.name+'_front_hem',(-.9,-.304,.893),(.9,-.28,.899));collision_box(top.name+'_rear_return',(-.9,.304,.914),(.9,.31,.934))
    for x,side in [(-.9,'L'),(.894,'R')]:box('COUNTER_'+side+'_end_fold',(x,-.304,.904),(x+.006,.304,.934),ROLE_TOP,.001)
    box('FRAME_front_under_counter_rail',(-.868,-.269,.875),(.868,-.243,.915),ROLE_BODY,.0015)
    box('FRAME_rear_under_counter_rail',(-.868,.244,.875),(.868,.276,.915),ROLE_BODY,.0015)
    # Simple usable splash/backboard, with stiffened cap and visible end returns.
    box('BACKBOARD_washable_splash_sheet',(-.89,.296,.939),(.89,.302,1.146),ROLE_LIGHT,.0008)
    extrude('BACKBOARD_folded_top_safety_cap',[(.282,1.150),(.309,1.150),(.309,1.132),(.303,1.132),(.303,1.144),(.282,1.144)],-.89,.89,'x',ROLE_BODY,.0008)
    collision_box('BACKBOARD_folded_top_safety_cap',(-.89,.282,1.132),(.89,.309,1.150))
    for x,side in [(-.890,'L'),(.884,'R')]:box('BACKBOARD_'+side+'_end_return',(x,.281,.940),(x+.006,.302,1.144),ROLE_BODY,.0008)
    # Real open storage bays with upturned retaining lips and attached support cleats.
    for zone,x0,x1 in [('locker',-.839,-.056),('open',-.020,.839)]:
        tray('SHELF_'+zone+'_folded_mid_deck',x0,x1,-.238,.271,.505,ROLE_LIGHT,.020)
        for x,side in [(x0,'L'),(x1-.014,'R')]:box('SHELF_'+zone+'_'+side+'_support_cleat',(x,-.232,.487),(x+.014,.270,.506),ROLE_TOP,.0006)
    # Exposed feet, formed side cheeks, empty shelves, and metal fasteners remain legible.
    for x,side in [(-.869,'L'),(.869,'R')]:
        for z,level in [(.244,'low'),(.843,'high')]:
            cylinder('JOIN_'+side+'_'+level+'_panel_rivet',(x,0,z),.006,.003,ROLE_TOP,axis='x',n=8)
    perforated_leaf()
    root=bpy.data.objects.new(ID+'_floor_origin',None);bpy.context.collection.objects.link(root);root['catalogue_id']=ID;root['datum']='Floor origin; X width, Z up, front -Y'
    pivot=bpy.data.objects.new(ID+'_door_hinge_pivot',None);bpy.context.collection.objects.link(pivot);pivot.location=PIVOT;pivot.parent=root
    bpy.context.view_layer.update()
    pivot['axis']='Local +Z, negative rotation opens outward';pivot['normal_open_range_degrees']=[0,-105];pivot['runtime_status']='Articulation proposal only; no animation/controller/gameplay implemented'
    for ob in PARTS:
        world=ob.matrix_world.copy();ob.parent=pivot if ob['assembly'] in ['door_leaf','door_handle','bearing_moving'] else root;ob.matrix_world=world
    bpy.context.view_layer.update()
    return root,pivot


def stats(objects):
    dg=bpy.context.evaluated_depsgraph_get();out=[];allvs=[];count=0
    for ob in objects:
        eo=ob.evaluated_get(dg);me=eo.to_mesh();me.calc_loop_triangles();vs=[tuple(ob.matrix_world@v.co) for v in me.vertices];allvs.extend(vs);count+=len(me.loop_triangles)
        out.append({'name':ob.name,'assembly':ob['assembly'],'material_role':ob['semantic_role'],'vertices':len(me.vertices),'triangles':len(me.loop_triangles),'bounds_min_m':[min(v[i] for v in vs) for i in range(3)],'bounds_max_m':[max(v[i] for v in vs) for i in range(3)],'modifiers':[m.name for m in ob.modifiers],'uv_layer':me.uv_layers.active.name})
        eo.to_mesh_clear()
    lo=[min(v[i] for v in allvs) for i in range(3)];hi=[max(v[i] for v in allvs) for i in range(3)]
    return {'bounds_min_m':lo,'bounds_max_m':hi,'dimensions_m':[b-a for a,b in zip(lo,hi)],'triangles_evaluated':count,'parts':out}


def export(root,pivot):
    # Save clean editable source before creating evaluated export copies.
    bpy.ops.file.pack_all();bpy.ops.object.select_all(action='DESELECT');root.select_set(True);bpy.context.view_layer.objects.active=root
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/(SLUG+'.blend')))
    dg=bpy.context.evaluated_depsgraph_get();groups={};created=[]
    for source in PARTS:
        ass=source['assembly'];group='static' if ass in ['static','bearing_static'] else ('door_handle' if ass=='door_handle' else 'door_leaf')
        key=(group,source['semantic_role']);groups.setdefault(key,[])
        me=bpy.data.meshes.new_from_object(source.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg)
        active=me.uv_layers.active
        if not active:raise RuntimeError('Missing UV: '+source.name)
        for layer in list(me.uv_layers):
            if layer!=active:me.uv_layers.remove(layer)
        active.name='UV_Metric_Metres';active.active_render=True
        ob=bpy.data.objects.new('EXPORT_'+source.name,me);bpy.context.collection.objects.link(ob);ob.matrix_world=source.matrix_world.copy();uv_metric(ob);groups[key].append(ob)
    for (ass,role),objects in groups.items():
        bpy.ops.object.select_all(action='DESELECT')
        for ob in objects:ob.select_set(True)
        bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();ob=bpy.context.object
        ob.name=ID+'_'+ass+'_'+role;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
        world=ob.matrix_world.copy();ob.parent=root if ass=='static' else pivot;ob.matrix_world=world
        ob['assembly']=ass;ob['semantic_role']=role;ob['source_semantic_part_count']=len(objects);ob['collision']='None; separate JSON proposals preserve storage voids';created.append(ob)
    bpy.ops.object.select_all(action='DESELECT')
    for ob in created+[root,pivot]:ob.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(ROOT/(SLUG+'.glb')),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_materials='EXPORT',export_extras=True)
    return [{'name':ob.name,'assembly':ob['assembly'],'role':ob['semantic_role']} for ob in created]


def main():
    root,pivot=build();data=stats(PARTS)
    data.update({'catalogue_id':ID,'name':'Astraea Staff Supply / Work Cabinet','unique_design_count':1,'units':'metres','axis':'Blender Z up; front -Y; GLB standard Y-up conversion','pivot_m':[0,0,0],'work_surface_z_m':.940,'body_width_m':1.8,'counter_depth_m':.620,'closed_total_depth_including_handle_m':.665,'backboard_top_z_m':1.15,'door':{'pivot_blender_m':list(PIVOT),'axis_blender':[0,0,1],'closed_degrees':0,'open_degrees':-105,'source_objects_independent':True,'glb_leaf_handle_nodes_independent':True,'sweep_check':'qa/door_sweep_report.json','status':'Geometric source/export proposal only; controller, rig, physical interaction and room fit untested'},'storage_openings':{'left_locker_cavity_envelope_m':{'min':[-.839,-.238,.192],'max':[-.056,.270,.874],'mid_shelf_top_m':.525,'note':'Overall cavity envelope includes the fixed shelf; use the separate clear volumes for access.'},'left_locker_clear_volumes_m':[{'min':[-.839,-.238,.192],'max':[-.056,.270,.487],'compartment':'lower'},{'min':[-.839,-.238,.525],'max':[-.056,.270,.874],'compartment':'upper'}],'right_open_bays_m':[{'min':[-.020,-.238,.192],'max':[.839,.271,.487]},{'min':[-.020,-.238,.525],'max':[.839,.271,.875]}]},'approach_proposal':{'min_m':[-1.08,-1.42,0],'max_m':[.95,-.365,1.9],'purpose':'Front work/storage access and outward door sweep; proposal only, route width and actor contact not accepted'},'target_proposals':{'counter_front_contact_m':[.3,-.28,.94],'door_handle_closed_m':[-.138,-.346,.512],'open_shelf_reach_m':[.42,-.238,.69]},'material_roles':sorted({ob['semantic_role'] for ob in PARTS}),'authoring':'Script-assisted original folded/extruded sheet construction, one connected perforated leaf, separate hardware, editable semantic source and bevel modifiers','source_generator':Path(__file__).name,'source_generator_sha256':sha(__file__),'shared_material_source':'standards/staff_materials.py','shared_material_source_sha256':sha(BASE/'standards/staff_materials.py'),'dependencies':['standards/staff_materials.py','materials/staff/manifest.json'],'source_reference_manifest':'batches/batch03/reference_manifest.json','reference_manifest_sha256':sha(BASE/'batches/batch03/reference_manifest.json'),'reference_pixels_inspected':['corridor01/image(20261001-185254).png','corridor02/image(20261001-185255).png','staff-room/image(20261001-190513).png'],'reference_use':'Plain washable surfaces, exposed useful construction, cooler paint, accessible empty storage. Reference pixels not copied; no narrow corridor dimensions, crew count or room assignments adopted.','provenance':'New independent asset; missing original ship and earlier catalogue families untouched.','qa_scope':'Blender component evidence only. No Godot/game/room/rig/route/save/audio/performance claim.'})
    mm=json.loads((BASE/'materials/staff/manifest.json').read_text())
    data['shared_material_manifest_sha256']=sha(BASE/'materials/staff/manifest.json')
    data['resources']=[{'role':role,'source':'materials/staff/'+mm['materials'][role]['file'],'source_sha256':mm['materials'][role]['sha256'],'metric_uv_metres_per_tile':mm['materials'][role]['meters_per_tile_uv'],'embedded_in_blend_and_glb':True} for role in data['material_roles']]
    data['door'].update({'pivot_gltf_Yup_m':[-.837,.2,.317],'axis_gltf_Yup':[0,1,0],'front_blender':[0,-1,0],'front_gltf_Yup':[0,0,1],'rotation_degrees_about_positive_axis':[0,-105],'pivot_node_name':ID+'_door_hinge_pivot','leaf_node_names':[ID+'_door_leaf_staff_bluegrey_paint',ID+'_door_leaf_staff_zinc'],'handle_node_names':[ID+'_door_handle_staff_rubber',ID+'_door_handle_staff_zinc'],'coordinate_conversion':'Blender (X,Y,Z) -> glTF (X,Z,-Y). Same signed rotation around converted positive axis. Blender imports glTF back to Blender Z-up.','source_origin_and_export_conversion':'Pivot location given in each declared coordinate frame, never apply Blender Z rotation directly in glTF Y-up. Godot adoption pending.'})
    nodes=export(root,pivot)
    data['export']={'format':'GLB','embedded_textures':True,'modifiers_evaluated':True,'UV_active_name':'UV_Metric_Metres','static_consolidation':'by semantic material role','moving_consolidation':'leaf and handle separate per-role nodes parented to genuine hinge pivot','visual_nodes':nodes,'animation_controllers':False}
    for suffix in ['blend','glb']:data[suffix+'_sha256']=sha(ROOT/(SLUG+'.'+suffix));data[suffix+'_bytes']=(ROOT/(SLUG+'.'+suffix)).stat().st_size
    (ROOT/(SLUG+'.manifest.json')).write_text(json.dumps(data,indent=2))
    (ROOT/(SLUG+'.collision_proposal.json')).write_text(json.dumps({'catalogue_id':ID,'status':'Proposals only; no engine physics authored or accepted. No full-cabinet convex proxy; storage apertures and hollow volume remain unfilled.','coordinates':'Blender metres, Z up, front -Y; initial closed state','compound_parts':COLL,'moving_parts_transform':{'hinge_pivot_m':PIVOT,'axis':[0,0,1],'rotation_degrees':[0,-105]},'approach':data['approach_proposal'],'sweep_evidence':'qa/door_sweep_report.json'},indent=2))
    print('COMPLETE',SLUG,data['triangles_evaluated'],data['dimensions_m'])
if __name__=='__main__':main()
