"""Original aquatic towel-use components, Blender 4.3.2.

Source-only: this file + unchanged standards material loaders and their complete
texture inputs. No QA file, earlier asset or pre-existing new output is read.
Run blender -b -t 2 --python assets/aquatic_towel_use/source/build_towel_use.py
"""
from pathlib import Path
import bpy, bmesh, json, math, hashlib, sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE=Path(__file__).resolve();ROOT=HERE.parents[1];CAT=ROOT.parents[1]
sys.path.insert(0,str(CAT/'standards'))
from materials import materials
from aquatic_materials import materials as aquatic_materials
for p in ('source','exports','qa'):(ROOT/p).mkdir(exist_ok=True,parents=True)
PARTS=[];MARKERS=[];COL=[];M={};ROOTOB=None;BIN=None

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(path,obj):path.write_text(json.dumps(obj,indent=2)+'\n')
def reset(asset):
    global PARTS,MARKERS,COL,M,ROOTOB,BIN
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
    PARTS=[];MARKERS=[];COL=[];M=materials();M.update(aquatic_materials());BIN=None
    ROOTOB=bpy.data.objects.new(asset+'_floor_origin',None);bpy.context.collection.objects.link(ROOTOB)
    ROOTOB['catalogue_id']=asset;ROOTOB['coordinate_contract']='metres; source X width / Y depth / Z up / front -Y; native GLB (X,Z,-Y)'
    ROOTOB['provenance']='Original script-assisted component design; source parts are editable'

def uv(ob):
    me=ob.data
    for layer in list(me.uv_layers):me.uv_layers.remove(layer)
    lay=me.uv_layers.new(name='UV_Metric_Metres');lay.active_render=True
    scale=me.materials[0].get('meters_per_tile_uv',[1,1])
    for f in me.polygons:
        ax=max(range(3),key=lambda k:abs(f.normal[k]));axes=[k for k in range(3) if k!=ax]
        for li in f.loop_indices:
            v=me.vertices[me.loops[li].vertex_index].co
            lay.data[li].uv=(v[axes[0]]/scale[0],v[axes[1]]/scale[1])

def mesh(name,vs,fs,role,bevel=0,moving=False):
    me=bpy.data.meshes.new(name+'_editable_mesh');me.from_pydata(vs,[],fs);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(M[role]);uv(ob)
    ob['semantic_role']=role;ob['motion_group']='container' if moving else 'fixed';ob.parent=BIN if moving else ROOTOB
    if bevel:
        mod=ob.modifiers.new('Editable edge easing','BEVEL');mod.width=bevel;mod.segments=2
    PARTS.append(ob);return ob

def extrude(name,p,lo,hi,role,axis='x',bevel=.002,moving=False):
    vs=[(v,a,b) if axis=='x' else (a,v,b) if axis=='y' else (a,b,v) for v in (lo,hi) for a,b in p]
    n=len(p);fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(name,vs,fs,role,bevel,moving)

def box(name,lo,hi,role,bevel=.002,moving=False):
    ob=extrude(name,[(lo[0],lo[1]),(hi[0],lo[1]),(hi[0],hi[1]),(lo[0],hi[1])],lo[2],hi[2],role,'z',bevel,moving)
    return ob

def roundrect(w,d,r,n=5):
    p=[]
    for cx,cy,a in [(w/2-r,d/2-r,0),(-w/2+r,d/2-r,90),(-w/2+r,-d/2+r,180),(w/2-r,-d/2+r,270)]:
        for j in range(n):
            t=math.radians(a+90*j/(n-1));p.append((cx+r*math.cos(t),cy+r*math.sin(t)))
    return p

def slab(name,w,d,z0,z1,role,xy=(0,0),r=.025,bevel=.002,moving=False):
    return extrude(name,[(x+xy[0],y+xy[1]) for x,y in roundrect(w,d,r)],z0,z1,role,'z',bevel,moving)

def wheel(name,x,y,moving=True):
    # Real axle supported on a bracket; wheel bottom is exactly Z0.
    p=[(y+.050*math.cos(math.tau*i/16+math.pi/16),.050*math.cos(math.pi/16)+.050*math.sin(math.tau*i/16+math.pi/16)) for i in range(16)]
    ob=extrude(name+'_tread',p,x-.026,x+.026,'aquatic_dark_grip',bevel=.001,moving=moving)
    box(name+'_axle_bracket',(x-.018,y-.038,.044),(x+.018,y+.038,.128),'aquatic_satin_alloy',.002,moving)
    return ob

def text(name,body,x,y,z,size,role,back=False,moving=False):
    cu=bpy.data.curves.new(name+'_editable_letters','FONT');cu.body=body;cu.align_x='CENTER';cu.size=size;cu.extrude=.0015;cu.resolution_u=3
    ob=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(ob);ob.location=(x,y,z);ob.rotation_euler=(math.pi/2,0,math.pi if back else 0)
    cu.materials.append(M[role]);ob['semantic_role']=role;ob['motion_group']='container' if moving else 'fixed';ob.parent=BIN if moving else ROOTOB
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH')
    ob=bpy.context.object;bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.0000001);bmesh.ops.dissolve_degenerate(bm,edges=bm.edges,dist=.0000001);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(ob.data);bm.free();uv(ob)
    ob['original_lettering']=body;ob['lettering_source']='Editable glyph mesh; generator preserves text, size and placement; numerical duplicates merged at0.1 micrometre';PARTS.append(ob)
    return ob

def marker(name,point,normal,part,kind='physical_surface',moving=False):
    ob=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(ob);ob.location=point;ob.parent=BIN if moving else ROOTOB
    ob.empty_display_type='ARROWS';ob.empty_display_size=.06
    ob['kind']=kind;ob['source_part']=part;ob['position_blender_source_m']=list(point);ob['normal_blender_source']=list(normal)
    ob['position_gltf_yup_m']=[point[0],point[2],-point[1]];ob['normal_gltf_yup']=[normal[0],normal[2],-normal[1]]
    ob['normal_status']='Physical outward surface normal, not approach direction' if kind=='physical_surface' else 'Nonphysical mouth orientation proposal; this direction is not asserted as a surface normal'
    MARKERS.append(ob);return ob

def cbox(name,lo,hi,moving=False):COL.append({'name':name,'type':'aabb','min_m':list(lo),'max_m':list(hi),'motion_group':'container' if moving else 'fixed'})
def cprofile(name,p,lo,hi,axis='x',moving=False):COL.append({'name':name,'type':'extruded_polygon','axis':axis,'profile_2d_m':p,'interval_m':[lo,hi],'motion_group':'container' if moving else 'fixed'})

def towel(name,x,y,z,role='oatmeal_weave'):
    # A shallow crowned fold, open-looking horizontal front hem, supported on
    # the previous folded layer. These are integrated stock, not inventory.
    p=[(-.205,z),(.205,z),(.213,z+.017),(.195,z+.046),(.12,z+.057),(-.12,z+.057),(-.195,z+.046),(-.213,z+.017)]
    ob=extrude(name,[(a+x,b) for a,b in p],y-.15,y+.15,role,'y',.004)
    box(name+'_folded_front_hem',(x-.188,y-.153,z+.010),(x+.188,y-.147,z+.018),'teal_weave',.001)
    return ob

def dry():
    asset='AST-AQU-007';reset(asset)
    # The thick U-section is an authored profile, not a bevel-only box.
    outer=[(-.67,.08),(-.67,1.52),(-.66,1.61),(-.62,1.71),(-.55,1.78),(-.45,1.82),(.45,1.82),(.55,1.78),(.62,1.71),(.66,1.61),(.67,1.52),(.67,.08)]
    inner=[(.563,.08),(.563,1.49),(.55,1.56),(.51,1.61),(.44,1.645),(-.44,1.645),(-.51,1.61),(-.55,1.56),(-.563,1.49),(-.563,.08)]
    arch=extrude('dry_continuous_sculpted_hood',outer+inner,-.31,.31,'ivory_enamel','y',.005)
    cprofile('hood_U_section',outer+inner,-.31,.31,'y')
    slab('dry_bearing_plinth',1.30,.59,.022,.145,'ivory_enamel',r=.10,bevel=.004)
    for x in (-.49,.49):
        for y in (-.18,.18):slab('dry_floor_shoe_'+str((x,y)),.20,.14,0,.035,'aquatic_dark_grip',(x,y),.025,.002)
    cbox('low_plinth',(-.65,-.295,0),(.65,.295,.145))
    box('dry_opaque_restock_back',(-.583,.248,.13),(.583,.292,1.66),'aquatic_clay_sling',.004)
    cbox('opaque_back',(-.583,.248,.13),(.583,.292,1.66))
    box('dry_lower_stock_guard',(-.58,-.205,.13),(.58,.252,.615),'aquatic_clay_sling',.008)
    cbox('lower_solid_guard',(-.58,-.205,.13),(.58,.252,.615))
    shelves=[]
    for i,z in enumerate((.615,1.075),1):
        shelves.append(slab('dry_retrieval_shelf_'+str(i),1.17,.49,z,z+.035,'ivory_enamel',(0,.020),.04,.003))
        cbox('shelf_'+str(i),(-.585,-.225,z),(.585,.265,z+.035))
        # Separate short front lip stops stock while leaving a genuinely useful
        # 1.10m wide mouth; there is no full transparent collision hull.
        box('dry_shelf_front_stop_'+str(i),(-.555,-.229,z+.02),(.555,-.214,z+.060),'aquatic_satin_alloy',.002)
        for x in (-.27,.27):
            for j in range(3 if i==1 else 2):towel('dry_folded_stock_'+str((i,x,j)),x,.040,z+.033+j*.052)
    # Header hangs from the continuous arch with a deliberate clay recess and
    # ivory letters. Its back is buried 9mm into the back panel at top corners.
    box('dry_inviting_sign_lintel',(-.565,-.270,1.485),(.565,.265,1.665),'aquatic_clay_sling',.007)
    cbox('header',(-.565,-.270,1.485),(.565,.265,1.665))
    text('dry_wordmark','DRY',.11,-.272,1.526,.115,'ivory_enamel')
    for j,w in enumerate((.18,.155,.13)):
        box('dry_original_fold_symbol_'+str(j),(-.37,-.275,1.527+j*.033),(-.37+w,-.270,1.550+j*.033),'ivory_enamel',.001)
    # Opaque service panel is an intentionally bounded face, not a claimed
    # passage to the historical aft staff room. Front loading needs no motion.
    box('dry_rear_service_panel',(-.40,.289,.28),(.40,.303,.54),'aquatic_satin_alloy',.003)
    text('dry_restock_face_text','FRONT LOAD',0,.305,.375,.062,'aquatic_dark_grip',True)
    for x in (-.36,.36):
        box('dry_service_key_'+str(x),(x-.012,.300,.385),(x+.012,.309,.43),'aquatic_dark_grip',.002)
    marker('dry_lower_shelf_contact',(0,-.19,.650),(0,0,1),'dry_retrieval_shelf_1')
    marker('dry_upper_shelf_contact',(0,-.19,1.110),(0,0,1),'dry_retrieval_shelf_2')
    marker('dry_restock_service_face',(0,.303,.33),(0,1,0),'dry_rear_service_panel')
    marker('dry_floor_contact',(-.49,-.18,0),(0,0,-1),'dry_floor_shoe_'+str((-.49,-.18)))
    return {'catalogue_id':asset,'name':'Protected dry towel and supply niche','design_count':1,'restock':'Front loading through the two open retrieval shelves. The opaque rear panel is an inspection/service face, not a loading door or room aperture. No removable rear state claimed.',
      'use_roles':['dry guest retrieval','front restocking','opaque rear service face'],
      'clear_volumes':[{'name':'lower_front_retrieval_mouth','min_m':[-.52,-.48,.82],'max_m':[.52,-.155,1.04]},{'name':'upper_front_retrieval_mouth','min_m':[-.52,-.48,1.24],'max_m':[.52,-.155,1.47]},{'name':'front_restock_approach','min_m':[-.7,-1.0,.10],'max_m':[.7,-.34,1.75]}],
      'integrated_stock':'Ten original folded textile forms with supported hems. Not additional designs, implemented inventory or safe capacity.',
      'collision_notes':'U-profile hood plus actual shelves, back, solid lower guard and header. Towels and small hems remain visual stock; no whole-niche hull fills the shelf mouths.'}

def returned():
    global BIN
    asset='AST-AQU-008';reset(asset)
    BIN=bpy.data.objects.new('return_container_translation',None);bpy.context.collection.objects.link(BIN);BIN.parent=ROOTOB
    BIN['motion_type']='proposed_translation';BIN['translation_blender_source_m']=[0,.92,0];BIN['translation_gltf_yup_m']=[0,0,-.92];BIN['continuous_stroke_m']=.92
    BIN['support']='Four 100mm diameter floor-contact wheels. Visual states and geometric travel only; rolling, bearings, forces and game operation unimplemented.'
    side=[(-.375,.025),(.335,.025),(.335,1.14),(.30,1.195),(.15,1.22),(-.18,1.22),(-.31,1.18),(-.375,1.08)]
    for label,x0,x1 in [('L',-.50,-.402),('R',.402,.50)]:
        extrude('return_'+label+'_formed_load_cheek',side,x0,x1,'ivory_enamel',bevel=.004)
        cprofile('housing_'+label,side,x0,x1)
        slab('return_'+label+'_floor_shoe',.102,.57,0,.039,'aquatic_dark_grip',((x0+x1)/2,-.005),.028,.002)
    # Front skirt masks the lowered container front; the rear is intentionally
    # open for an independently rolling container.
    box('return_front_low_guard',(-.418,-.365,.035),(.418,-.321,.820),'aquatic_clay_sling',.007)
    cbox('front_guard',(-.418,-.365,.035),(.418,-.321,.820))
    top=[(-.36,1.070),(-.32,1.165),(-.20,1.215),(.18,1.215),(.33,1.155),(.33,1.088),(.17,1.125),(-.18,1.125),(-.265,1.087)]
    extrude('return_curved_guard_hood',top,-.420,.420,'ivory_enamel',bevel=.004)
    cprofile('curved_guard_hood',top,-.420,.420)
    # Narrow fixed down-turn chute: side walls + sloping bottom + opaque back.
    # Bottom .495m clears the moving bin front rim (.465m) by 30mm. Its sides
    # remain within +/- .322, outside bin sidewalls starting at +/- .346.
    chute_side=[(-.345,.820),(-.345,1.080),(-.25,1.120),(.20,.760),(.20,.495),(.14,.495),(-.03,.690)]
    for s in (-1,1):
        x0,x1=(.302,.322) if s==1 else (-.322,-.302)
        extrude('return_chute_side_'+str(s),chute_side,x0,x1,'aquatic_satin_alloy',bevel=.002)
        cprofile('chute_side_'+str(s),chute_side,x0,x1)
    chute_bottom=[(-.346,.820),(-.336,.846),(-.032,.716),(.143,.513),(.126,.495),(-.048,.690)]
    extrude('return_downturn_receiving_floor',chute_bottom,-.310,.310,'aquatic_satin_alloy',bevel=.001)
    cprofile('receiving_floor',chute_bottom,-.310,.310)
    baffle=[(-.252,1.100),(-.237,1.119),(.218,.764),(.218,.495),(.192,.495),(.192,.752)]
    extrude('return_opaque_dogleg_baffle',baffle,-.311,.311,'aquatic_clay_sling',bevel=.002)
    cprofile('opaque_baffle',baffle,-.311,.311)
    # Broad back curtain above bin height ensures ordinary approach rays do not
    # read through beside the narrow chute into the service zone.
    box('return_upper_back_curtain',(-.414,.269,.750),(.414,.304,1.144),'aquatic_clay_sling',.003)
    cbox('upper_back_curtain',(-.414,.269,.750),(.414,.304,1.144))
    # Side-mouth seals remain above high sidewall rims (max .710m).
    for s in (-1,1):
        x0,x1=(.31,.414) if s==1 else (-.414,-.31)
        box('return_mouth_side_guard_'+str(s),(x0,-.336,.804),(x1,.285,1.105),'aquatic_clay_sling',.003)
        cbox('mouth_side_guard_'+str(s),(x0,-.336,.804),(x1,.285,1.105))
    # This is a removable open-top rigid receiver, not a visual closed box.
    slab('bin_real_bottom',.728,.552,.113,.142,'aquatic_satin_alloy',r=.032,bevel=.003,moving=True)
    cbox('bin_bottom',(-.364,-.276,.113),(.364,.276,.142),True)
    bin_side=[(-.276,.131),(.276,.131),(.276,.710),(-.14,.710),(-.276,.465)]
    for s in (-1,1):
        x0,x1=(.345,.367) if s==1 else (-.367,-.345)
        extrude('bin_rising_side_'+str(s),bin_side,x0,x1,'aquatic_teal_sling',bevel=.003,moving=True)
        cprofile('bin_side_'+str(s),bin_side,x0,x1,moving=True)
    box('bin_low_front_wall',(-.360,-.278,.129),(.360,-.252,.465),'aquatic_teal_sling',.003,True)
    cbox('bin_low_front_wall',(-.360,-.278,.129),(.360,-.252,.465),True)
    box('bin_rear_service_wall',(-.360,.251,.129),(.360,.280,.710),'aquatic_teal_sling',.003,True)
    cbox('bin_rear_service_wall',(-.360,.251,.129),(.360,.280,.710),True)
    # Handle has a genuine 37mm finger gap to the rear wall and no invisible
    # full-width collision slab across its hand cavity.
    for x in (-.14,.14):box('bin_pull_handle_standoff_'+str(x),(x-.016,.275,.550),(x+.016,.353,.578),'aquatic_satin_alloy',.004,True)
    box('bin_pull_handle_grip',(-.156,.327,.547),(.156,.371,.581),'aquatic_satin_alloy',.008,True)
    cbox('handle_left',(-.156,.275,.547),(-.124,.371,.581),True);cbox('handle_right',(.124,.275,.547),(.156,.371,.581),True);cbox('handle_bar',(-.124,.327,.547),(.124,.371,.581),True)
    for x in (-.274,.274):
        for y in (-.195,.195):
            wheel('bin_wheel_'+str((x,y)),x,y)
            COL.append({'name':'wheel_'+str((x,y)),'type':'cylinder','axis':'x','center_m':[x,y,.05*math.cos(math.pi/16)],'radius_m':.05,'depth_m':.052,'motion_group':'container','approximation':'Circular proposal overreaches the flat polygon floor contact by0.961mm; exact tread is a16-sided polygon with a flat bottom face atZ0'})
    text('bin_service_word','PULL',0,.282,.375,.065,'ivory_enamel',True,True)
    # Original simple textile-return symbol plus RETURN, physically impressed
    # on the fixed front shield with tiny buried backs, not coplanar decals.
    text('return_wordmark','RETURN',.045,-.367,.602,.088,'ivory_enamel')
    box('return_symbol_stem',(-.056,-.369,.437),(-.020,-.362,.533),'ivory_enamel',.002)
    extrude('return_symbol_arrow',[(-.095,.455),(.019,.455),(-.038,.403)],-.369,-.362,'ivory_enamel','y',.001)
    for j,w in enumerate((.20,.17)):
        box('return_symbol_fold_'+str(j),(-w/2-.038,-.369,.352+j*.035),(w/2-.038,-.362,.374+j*.035),'ivory_enamel',.003)
    marker('return_receiving_lip',(0,-.346,.832),(.394,-.919,0),'return_downturn_receiving_floor',kind='mouth_position_proposal')
    marker('return_container_grip',(0,.371,.565),(0,1,0),'bin_pull_handle_grip',moving=True)
    marker('return_container_floor',(-.274,-.195,0),(0,0,-1),'bin_wheel_'+str((-.274,-.195))+'_tread',moving=True)
    marker('return_fixed_floor',(-.451,-.005,0),(0,0,-1),'return_L_floor_shoe')
    marker('return_bin_bottom_contact',(0,0,.142),(0,0,1),'bin_real_bottom',moving=True)
    return {'catalogue_id':asset,'name':'Guarded used-towel return with rolling receiver','design_count':1,'use_roles':['guarded guest return','rear container extraction'],
      'motion':{'group':'return_container_translation','direction_blender_source':[0,1,0],'direction_gltf_yup':[0,0,-1],'travel_m':.92,'states':{'closed_m':0,'withdrawn_m':.92},'support':'Four real wheel treads reach floor Z0 in both states and during a horizontal translation. Bearings, traction, loads and game motion are unimplemented.','swept_reserve_min_m':[-.385,-.29,0],'swept_reserve_max_m':[.385,1.305,.73],'service_staging_min_m':[-.62,.39,0],'service_staging_max_m':[.62,1.82,1.0]},
      'clear_volumes':[{'name':'guest_mouth_aperture','min_m':[-.28,-.48,.878],'max_m':[.28,-.339,1.045]},{'name':'bin_internal_collection','min_m':[-.32,-.23,.15],'max_m':[.32,.23,.44]},{'name':'rear_handle_finger_gap','min_m':[-.12,.287,.550],'max_m':[.12,.322,.578]}],
      'collision_notes':'Fixed profile-following cheeks/chute/hood/baffle and explicit thin container floor/walls/handle/wheels preserve the mouth, receiving cavity and rear travel. Small labels omitted. Source open/closed exports count once.',
      'sightline_scope':'Fixed dogleg chute and opaque upper rear curtain. Ordinary guest-eye finite rays require fresh measured evidence in both states. No privacy certification or whole-room implication.',
      'limitations_extra':['Lower container front rim passes below fixed chute. Receiver is not a sealed laundry or fluid vessel','No laundry, saturation, disposal, collection automation, hygienic material or mechanical validation']}

def evaluated(ob,dg):
    eo=ob.evaluated_get(dg);me=eo.to_mesh();me.calc_loop_triangles()
    vs=[tuple(ob.matrix_world@v.co) for v in me.vertices];fs=[tuple(t.vertices) for t in me.loop_triangles]
    tree=BVHTree.FromPolygons(vs,fs,all_triangles=True)
    row={'name':ob.name,'role':ob['semantic_role'],'motion_group':ob['motion_group'],'triangles':len(fs),'bounds_min_m':[min(v[k] for v in vs) for k in range(3)],'bounds_max_m':[max(v[k] for v in vs) for k in range(3)],'editable_type':ob.type,'editable_modifiers':[m.name for m in ob.modifiers]}
    eo.to_mesh_clear();return row,tree,vs,fs

def finish(info):
    asset=info['catalogue_id'];bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
    rec={};trees={};allvs=[];geom={}
    for ob in PARTS:
        row,tree,vs,fs=evaluated(ob,dg);rec[ob.name]=row;trees[ob.name]=tree;geom[ob.name]=(vs,fs);allvs+=vs
    lo=[min(v[k] for v in allvs) for k in range(3)];hi=[max(v[k] for v in allvs) for k in range(3)]
    contacts=[]
    for markerob in MARKERS:
        row={k:markerob[k] for k in markerob.keys()};row['name']=markerob.name
        row={k:list(v) if hasattr(v,'to_list') or type(v).__name__=='IDPropertyArray' else v for k,v in row.items()}
        loc,nor,index,d=trees[row['source_part']].find_nearest(markerob.matrix_world.translation)
        row['actual_source_surface_m']=list(loc);row['actual_source_surface_normal']=list(nor);row['distance_to_source_surface_m']=d
        if row['kind']=='physical_surface':
            assert d<.0005,(markerob.name,d)
            assert Vector(row['normal_blender_source']).dot(nor)>.96,(markerob.name,list(nor))
        contacts.append(row)
    # Full semantic-part support graph from actual evaluated triangles, with
    # nearest vertex tests admitting exact coplanar supported faces <=0.6mm.
    edges=[];names=list(rec)
    for i,a in enumerate(names):
        for b in names[i+1:]:
            ra,rb=rec[a],rec[b]
            if ra['motion_group']!=rb['motion_group']:continue
            if any(min(ra['bounds_max_m'][k],rb['bounds_max_m'][k]) < max(ra['bounds_min_m'][k],rb['bounds_min_m'][k])-.0006 for k in range(3)):continue
            pairs=len(trees[a].overlap(trees[b]));dist=None
            if not pairs:
                dist=min([trees[b].find_nearest(Vector(p))[3] for p in geom[a][0]]+[trees[a].find_nearest(Vector(p))[3] for p in geom[b][0]])
            if pairs or dist<.0006:edges.append({'a':a,'b':b,'surface_intersection_pairs':pairs,'nearest_vertex_distance_m':dist})
    anchors=[n for n,r in rec.items() if abs(r['bounds_min_m'][2])<1e-5]
    reached=set(anchors)
    while True:
        old=len(reached)
        for e in edges:
            if e['a'] in reached or e['b'] in reached:reached.update((e['a'],e['b']))
        if len(reached)==old:break
    support={'method':'Evaluated triangle BVH overlap; exact contact fallback <=0.6mm vertex-to-surface; isolated moving group separately grounded on its wheels','floor_anchors':anchors,'edges':edges,'supported_parts':len(reached),'total_parts':len(names),'unsupported_parts':sorted(set(names)-reached),'passed':len(reached)==len(names)}
    info.update({'units':'metres','coordinate_frame':'Blender source X width, Y depth, Z up, front -Y; native GLB (X,Z,-Y)','pivot_m':[0,0,0],'datum':'Floor Z0','blender_version':bpy.app.version_string,'dimensions_m':[hi[k]-lo[k] for k in range(3)],'bounds_min_m':lo,'bounds_max_m':hi,'triangles':sum(r['triangles'] for r in rec.values()),'editable_semantic_parts':len(PARTS),'parts':list(rec.values()),'material_roles':sorted({o['semantic_role'] for o in PARTS}),'contacts':contacts,'source':f'source/{asset}.blend','export':f'exports/{asset}.glb','generator':'source/build_towel_use.py','reference_manifest':'../../batches/batch14/reference_manifest.json','programme_handoff':'../../references/aquatic_program/D08_programme_handoff.json','provenance':'Original script-assisted geometry and glyph forms; waterpark and public blueprint pixels inspected for resort material/use guidance only; no sampled pixels, reused clinical forms or external meshes','limitations':['Component proposals; no original engine adoption, species/actor fit, real hygiene, plumbing, mechanical certification or target-PC performance','D08_bath6 dry changing and aft D08_service9 towels/care are distinct historical allocations, not adjoining rooms']+info.get('limitations_extra',[]),'export_settings':{'static_meshes':'one per material role','moving_meshes':'one per material role under the one actual bin translation node','uv':'evaluated copies reprojected per face in metric material units; original semantic source retained','lights':False,'textures':'shared unchanged images packed in source and embedded in GLB'}})
    bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/info['source']))
    exports=[]
    for group in ('fixed','container'):
        for role in info['material_roles']:
            sources=[ob for ob in PARTS if ob['semantic_role']==role and ob['motion_group']==group]
            if not sources:continue
            bpy.ops.object.select_all(action='DESELECT');copies=[]
            for source in sources:
                me=bpy.data.meshes.new_from_object(source.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg)
                ob=bpy.data.objects.new('EXPORT_'+source.name,me);bpy.context.collection.objects.link(ob);ob.matrix_world=source.matrix_world.copy();uv(ob)
                ob.select_set(True);copies.append(ob)
            bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();out=bpy.context.object;out.name=asset+'__'+group+'__'+role
            bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);out.parent=BIN if group=='container' else ROOTOB
            out['material_role']=role;out['motion_group']=group;exports.append(out);out.select_set(False)
    bpy.ops.object.select_all(action='DESELECT')
    for ob in exports+MARKERS+[ROOTOB]+([BIN] if BIN else []):ob.select_set(True)
    def export(suffix):
        bpy.ops.export_scene.gltf(filepath=str(ROOT/'exports'/f'{asset}{suffix}.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_materials='EXPORT',export_extras=True,export_animations=False)
    export('')
    if BIN:
        BIN.location.y=.92;bpy.context.view_layer.update();export('_withdrawn');BIN.location.y=0
        info['state_exports']=[f'exports/{asset}.glb',f'exports/{asset}_withdrawn.glb']
    info['source_sha256']=sha(ROOT/info['source']);info['glb_sha256']=sha(ROOT/info['export']);info['generator_sha256']=sha(HERE)
    if BIN:info['withdrawn_glb_sha256']=sha(ROOT/'exports'/f'{asset}_withdrawn.glb')
    dump(ROOT/f'{asset}.manifest.json',info)
    dump(ROOT/f'{asset}.collision_proposal.json',{'catalogue_id':asset,'coordinate_frame':'Blender source metres; shape and movement coordinates require native C mapping','status':'Component geometric proposals only, no engine physics validation','shapes':COL,'clear_volumes':info['clear_volumes'],'motion':info.get('motion'),'limitations':info['collision_notes']})
    dump(ROOT/'qa'/f'{asset}_source_support.json',support)
    dump(ROOT/'qa'/f'{asset}_source_contacts.json',{'contacts':contacts})
    print('BUILT',asset,info['dimensions_m'],info['triangles'],'support',support['passed'],support['unsupported_parts'])
    return info

def dependencies():
    paths=[HERE,CAT/'standards/materials.py',CAT/'standards/aquatic_materials.py',CAT/'materials/material_manifest.json',CAT/'materials/aquatic/manifest.json']
    spec=json.loads((CAT/'materials/material_manifest.json').read_text())
    paths += [CAT/'materials'/r['base_color_file'] for r in spec['materials'].values()]
    spec=json.loads((CAT/'materials/aquatic/manifest.json').read_text())
    paths += [CAT/'materials/aquatic'/r['file'] for r in spec['materials'].values()]
    dump(ROOT/'dependency_manifest.json',{'scope':'Every file the generator opens as input, including material roles loaded but unused. Source-only rebuild starts with these and no QA or pre-existing new outputs.','inputs':[{'path_from_catalogue_root':str(p.relative_to(CAT)),'sha256':sha(p)} for p in paths],'generated_outputs_are_not_dependencies':True})

if __name__=='__main__':
    rows=[finish(dry()),finish(returned())];dependencies()
    dump(ROOT/'manifest.json',{'family':'Aquatic towel-use components','batch':'14','unique_design_count':2,'state_derivatives_count_as_designs':False,'assets':[{k:v for k,v in r.items() if k!='parts'} for r in rows]})
