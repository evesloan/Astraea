"""Original source-only D05 waiting/support architecture with retained editable components.
No Game or Catalogue writes. Source frame X right, Y depth, Z up, metres.
World mapping: (sx,sy,sz) -> (sx-28,sz+21,-sy-446).
"""
from pathlib import Path
import bpy, bmesh, math, json, hashlib, sys
from mathutils import Vector, Matrix

ROOT=Path(__file__).resolve().parents[1]
CAT=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
PIN=json.loads((ROOT/'qa/INPUT_PINS.json').read_text())
RUN=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else '001'
SOURCE=ROOT/'source'/f'D05_forward_welcome_{RUN}.blend'
EXPORT=ROOT/'exports'/f'D05_forward_welcome_architecture_{RUN}.glb'
assert not SOURCE.exists() and not EXPORT.exists(),'Preserve earlier source revisions'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for p,h in PIN['inputs'].items(): assert sha(p)==h,('input changed',p)
bpy.ops.wm.read_factory_settings(use_empty=True)
SCENE=bpy.context.scene;SCENE.unit_settings.system='METRIC';SCENE.unit_settings.scale_length=1
MATS={};PARTS=[];RETAINED=[];FIXTURES=[];RECEIVERS=[]

def material(name,texture=None,color=(.5,.5,.5,1),metal=0,rough=.8):
    m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value=color;b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal
    if texture:
        t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(texture),check_existing=True);t.image.pack();t.interpolation='Closest';m.node_tree.links.new(t.outputs['Color'],b.inputs['Base Color'])
    m['material_role']=name;m['metres_per_tile']=1 if name=='sage_acoustic' else 2;MATS[name]=m
    return m

for n in ['quiet_ivory','sage_acoustic','warm_sand']:material(n,ROOT/'textures'/f'{n}.png')
for n in ['warm_walnut','champagne_metal','dark_rubber','ivory_enamel','warm_stone']:material(n,CAT/'materials'/f'{n}.png',metal=.25 if n=='champagne_metal' else 0)
material('clinical_ink',color=(.045,.085,.08,1))
material('opal_lens',color=(.92,.87,.7,1));bs=MATS['opal_lens'].node_tree.nodes.get('Principled BSDF');bs.inputs['Emission Color'].default_value=(1,.86,.65,1);bs.inputs['Emission Strength'].default_value=.7

def world(p):return [p[0]-28,p[2]+21,-p[1]-446]

def mesh(name,verts,faces,role,bevel=0):
    if name.startswith('WAIT_'):
        verts=[(max(0,min(14,v[0])),max(-4,min(4,v[1])),v[2]) for v in verts]
    me=bpy.data.meshes.new(name+'_editable');me.from_pydata(verts,[],faces);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);SCENE.collection.objects.link(ob);me.materials.append(MATS[role]);ob['source_package']='D05_forward_welcome_candidate';ob['material_role']=role
    uv=me.uv_layers.new(name='MetreScaled');scale=MATS[role]['metres_per_tile']
    for f in me.polygons:
        a=max(range(3),key=lambda i:abs(f.normal[i]));axes=[i for i in range(3) if i!=a]
        for li in f.loop_indices:
            p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]]/scale,p[axes[1]]/scale)
    if bevel:
        m=ob.modifiers.new('Editable eased use edges','BEVEL');m.width=bevel;m.segments=2;m.limit_method='ANGLE'
        m=ob.modifiers.new('Editable weighted normals','WEIGHTED_NORMAL');m.keep_sharp=True
    PARTS.append(ob);return ob

def box(name,x0,x1,y0,y1,z0,z1,role='quiet_ivory',bevel=.015):
    return mesh(name,[(x,y,z) for z in [z0,z1] for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role,bevel)

def prism(name,poly,z0,z1,role='quiet_ivory',bevel=.012):
    n=len(poly);return mesh(name,[(x,y,z) for z in [z0,z1] for x,y in poly],[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],role,bevel)

def strip(name,points,width,z0,z1,role='quiet_ivory',bevel=.01):
    left=[];right=[]
    for i,p in enumerate(points):
        va=Vector(points[i]-Vector(points[i-1])) if i else Vector(points[1])-Vector(p)
        vb=Vector(points[i+1])-Vector(p) if i<len(points)-1 else va
        va.normalize();vb.normalize();na=Vector((-va.y,va.x));nb=Vector((-vb.y,vb.x));normal=na+nb;normal.normalize();den=max(.3,normal.dot(na));off=normal*(width*.5/den)
        left.append(tuple(Vector(p)+off));right.append(tuple(Vector(p)-off))
    return prism(name,left+list(reversed(right)),z0,z1,role,bevel)

def path(name,points,width,z0,z1,role='quiet_ivory',bevel=.01):
    return strip(name,[Vector(p) for p in points],width,z0,z1,role,bevel)

def arc(cx,cy,r,a,b,n=8):return [(cx+r*math.cos(math.radians(a+(b-a)*i/n)),cy+r*math.sin(math.radians(a+(b-a)*i/n))) for i in range(n+1)]

def marker(name,p,kind,normal=(0,0,1),owner=None):
    ob=bpy.data.objects.new('DATUM_'+name,None);SCENE.collection.objects.link(ob);ob.location=p;ob.empty_display_size=.08;ob['kind']=kind;ob['source_package']='D05_forward_welcome_candidate'
    RECEIVERS.append({'name':name,'kind':kind,'source_xyz':list(p),'world_xyz':world(p),'normal_source':list(normal),'receiver_part':owner})
    return ob

def text(name,label,at,size=.22,rotation=(math.pi/2,0,0),role='clinical_ink'):
    curve=bpy.data.curves.new(name,'FONT');curve.body=label;curve.size=size;curve.align_x='CENTER';curve.align_y='CENTER';curve.extrude=.0012;curve.resolution_u=2
    ob=bpy.data.objects.new(name,curve);SCENE.collection.objects.link(ob);ob.location=at;ob.rotation_euler=rotation;curve.materials.append(MATS[role]);ob['source_package']='D05_forward_welcome_candidate';PARTS.append(ob);return ob

def retain(id_,tag,at,yaw=0):
    row=PIN['retained_assets'][id_];src=CAT/row['source'];pre=set(bpy.data.objects)
    with bpy.data.libraries.load(str(src),link=False) as (a,b):b.objects=list(a.objects)
    objects=[o for o in b.objects if o]
    root=bpy.data.objects.new('INSTANCE_'+tag,None);SCENE.collection.objects.link(root);root.location=at;root.rotation_euler.z=yaw;root['retained_catalogue_id']=id_
    for o in objects:
        if not o.users_collection:SCENE.collection.objects.link(o)
        if o.parent is None:o.parent=root
        o.name=tag+'__'+o.name;o['retained_catalogue_id']=id_
    RETAINED.append({'id':id_,'instance':tag,'source':str(src),'source_sha256':sha(src),'translation_source_xyz':list(at),'yaw_source_z_radians':yaw,'translation_world_xyz':world(at),'scale':[1,1,1],'objects':len(objects)})
    return root

# The clinical rooms retain their exact gross subdivisions. Walls fit inside their outer envelope.
north=[(0,2.55),(1.25,2.95),(2.65,3.65),(4.0,3.88),(11.88,3.88)]+arc(11.88,1.88,2,90,0)[1:]
south=[(0,-2.10),(1.0,-2.35),(2.5,-3.20),(3.6,-3.88),(5.5,-3.88),(6.55,-3.20),(7.0,-2.96),(7.45,-3.20),(8.8,-3.88),(10.5,-3.88),(11.8,-3.20),(12.85,-2.20),(13.88,-1.88)]
for side,pts in [('north',north),('south',south)]:
    path('WAIT_'+side+'_sculpted_enclosure',pts,.24,0,4.2)
    path('WAIT_'+side+'_warm_dado',pts,.255,.10,.82,'warm_walnut',.008)
    path('WAIT_'+side+'_upper_acoustic_reveal',pts,.26,3.34,3.95,'sage_acoustic',.008)
    path('WAIT_'+side+'_ceiling_bearing',pts,.42,4.2,4.4,'warm_walnut')
    for x in [4.5,8.8]:
        y=3.72 if side=='north' else -3.72
        box(f'WAIT_{side}_pier_{x}',x-.13,x+.13,y-.13,y+.13,0,4.2,'quiet_ivory',.025)
        marker(f'waiting_{side}_{x}_floor',(x,y,0),'physical_floor_bearing',owner=f'WAIT_{side}_pier_{x}')

# Shared partition: screened opening stays centred between the two existing children.
for nm,y0,y1 in [('north',1.92,4),('south',-4,-1.92)]:
    box('SHARED_'+nm+'_privacy_partition',-.12,.12,y0,y1,0,4.2)
    box('SHARED_'+nm+'_deep_jamb',-.4,.4,y0,min(y1,y0+.2),0,3.2,'sage_acoustic')
box('SHARED_screened_portal_head',-.40,.40,-1.92,1.92,3.2,4.2,'sage_acoustic')
marker('screened_support_entry',(0,0,0),'unbuilt_clear_threshold_centre')

# Diagnostic support is a quieter, contained technical bay with usable wall-depth storage.
box('SUPPORT_north_wall',-14,0,3.76,4,0,4.2)
box('SUPPORT_south_wall',-14,0,-4,-3.76,0,4.2)
for nm,y0,y1 in [('north',1.8,4),('south',-4,-1.8)]:box('SUPPORT_rear_'+nm,-14,-13.76,y0,y1,0,4.2)
box('SUPPORT_rear_receiver_head',-14,-13.72,-1.8,1.8,2.4,4.2,'sage_acoustic')
box('SUPPORT_temporary_closed_service_receiver',-13.82,-13.76,-1.8,1.8,0,2.4,'sage_acoustic',.004)
marker('clean_staff_service_receiver',(-14,0,0),'closed_uninstalled_service_interface',(-1,0,0),'SUPPORT_temporary_closed_service_receiver')
for x in [-12.7,-8.9,-5.1,-1.3]:
    box('SUPPORT_rear_bearing_'+str(x),x-.13,x+.13,3.48,3.76,0,4.2,'warm_walnut')
    marker('support_floor_'+str(x),(x,3.62,0),'physical_floor_bearing',owner='SUPPORT_rear_bearing_'+str(x))

# Readable supply wall: genuine shelf depths, recessed fronts and terminating service panels.
for i,x in enumerate([-10.9,-9.1,-7.3,-5.5]):
    box(f'STOCK_{i}_left_cheek',x-.76,x-.64,2.7,3.72,0,2.38,'quiet_ivory')
    box(f'STOCK_{i}_right_cheek',x+.64,x+.76,2.7,3.72,0,2.38,'quiet_ivory')
    box(f'STOCK_{i}_back',x-.64,x+.64,3.60,3.72,.12,2.30,'sage_acoustic')
    for j,z in enumerate([.12,.75,1.38,2.20]):box(f'STOCK_{i}_shelf_{j}',x-.64,x+.64,2.73,3.60,z,z+.08,'warm_walnut',.01)
    for j in [0,1,2]:
        z=.20+j*.63
        for k in [-1,1]:
            xx=x+k*.30
            box(f'STOCK_{i}_closed_case_{j}_{k}',xx-.25,xx+.25,2.94,3.48,z,z+.38,'warm_sand',.04)
            box(f'STOCK_{i}_case_pull_{j}_{k}',xx-.11,xx+.11,2.89,2.94,z+.14,z+.22,'champagne_metal',.009)
    box(f'STOCK_{i}_canopy',x-.77,x+.77,2.62,3.75,2.38,2.55,'sage_acoustic')
text('SUPPORT_stock_legend','LOCAL SUPPORT',(-8.2,2.615,2.47),.17)

# Reuse the actual component source meshes and hierarchy; no replacement basin, screen, bed or trolley.
retain('AST-MED-001','PrivacyReturn',(-1.9,1.35,0),math.pi/2)
retain('AST-MED-002','WashSupply',(-3.0,3.28,0),0)
retain('AST-MED-003','SupportPlatform',(-8.5,-1.45,0),math.pi/2)
retain('AST-MED-004','SupplyTrolley',(-11.6,-2.1,0),0)
box('WASH_real_service_receiver',-3.9,-2.1,3.66,3.76,.08,1.50,'sage_acoustic')
for z,name in [(.60,'lower'),(1.25,'upper')]:
    box('WASH_receiver_crossbar_'+name,-3.82,-2.18,3.62,3.66,z,z+.08,'champagne_metal',.005)
marker('wash_back_receiver',(-3,3.66,.80),'proposed_host_service_receiver',(0,-1,0),'WASH_real_service_receiver')

# The welcome desk is part of the inhabited enclosure, with a lower side writing perch.
desk=[(4.35,2.95),(8.8,2.95),(8.8,1.95),(8.4,1.53),(7.5,1.25),(5.8,1.25),(4.85,1.50),(4.35,1.92)]
prism('WELCOME_crescent_supported_counter',desk,.90,.99,'warm_walnut',.035)
path('WELCOME_curved_load_fascia',[(4.53,2.75),(4.53,2.03),(4.98,1.65),(5.84,1.45),(7.4,1.45),(8.21,1.69),(8.60,2.03),(8.60,2.75)],.16,.10,.90,'sage_acoustic',.025)
for x in [4.7,8.45]:box('WELCOME_floor_shoe_'+str(x),x-.22,x+.22,2.4,2.8,0,.13,'dark_rubber')
prism('WELCOME_lower_side_perch',[(8.8,2.8),(10.1,2.8),(10.1,2.1),(9.85,1.9),(8.8,1.9)],.72,.80,'warm_walnut',.025)
box('WELCOME_perch_supported_return',9.75,10.0,2.15,2.7,0,.72,'sage_acoustic',.03)
box('WELCOME_direction_field',5.48,7.82,3.69,3.75,1.65,2.65,'warm_sand',.025)
text('WELCOME_primary_title','CARE & COMPANY',(6.65,3.675,2.28),.28)
text('WELCOME_quiet_secondary','WAITING  /  ASSISTANCE',(6.65,3.67,1.94),.13)
for x in [5.38,7.92]:box('WELCOME_sign_bearing_'+str(x),x-.05,x+.05,3.65,3.80,1.55,2.73,'champagne_metal',.008)

# Six existing waiting units in two conversation-size groups plus two facing returns.
for i,(x,y,yaw) in enumerate([(2.8,-2.0,math.pi),(4.5,-2.76,math.pi),(8.0,-2.25,math.pi),(9.7,-2.70,math.pi),(10.8,2.65,-math.pi/2),(10.35,-2.60,-math.pi/2)]):
    retain('AST-LND-002','WaitingSeat_%02d'%i,(x,y,0),yaw)
    marker('waiting_seat_%02d_floor'%i,(x,y,0),'retained_instance_floor_origin')
for i,x in enumerate([6.1]):
    poly=[(x-.44,-2.85),(x+.44,-2.85),(x+.52,-2.25),(x+.3,-2.03),(x-.3,-2.03),(x-.52,-2.25)]
    prism('WAIT_companion_table_'+str(i),poly,.48,.55,'warm_walnut',.04)
    box('WAIT_table_foot_'+str(i),x-.13,x+.13,-2.65,-2.23,0,.48,'sage_acoustic',.04)

# Long admission connection preserves a 3.6m swept-clear planning spine at x15.2..18.8.
box('ADMISSION_inner_protected_partition',14,14.24,-17,-1.88,0,4.2)
for nm,y0,y1 in [('fore',-17,-15.8),('aft',-12.2,4)]:box('ADMISSION_outer_'+nm,19.76,20,y0,y1,0,4.2)
box('ADMISSION_core_interface_head',19.76,20,-15.8,-12.2,2.4,4.2,'sage_acoustic')
box('ADMISSION_south_end',14,20,-17,-16.76,0,4.2)
box('ADMISSION_north_end',14,20,3.76,4,0,4.2)
for i,y in enumerate([-15.5,-10,-4.5,2.8]):
    for x in [14.38,19.62]:
        box(f'ADMISSION_{i}_{x}_pier',x-.14,x+.14,y-.18,y+.18,0,4.2,'quiet_ivory',.025)
        marker(f'admission_{i}_{x}_floor',(x,y,0),'physical_floor_bearing',owner=f'ADMISSION_{i}_{x}_pier')
    box(f'ADMISSION_{i}_ceiling_tie',14.24,19.76,y-.22,y+.22,4.2,4.40,'warm_walnut')
# Offset curved field screens the approach without entering the 3.6m corridor reservation.
path('ADMISSION_curved_privacy_return',[(14.37,-15.55),(14.55,-14.8),(14.68,-13.65),(14.54,-12.55),(14.36,-12.15)],.22,.0,2.8,'sage_acoustic',.025)
box('ADMISSION_arrival_relief_backing',14.245,14.35,-15.0,-13.0,1.3,2.45,'warm_walnut')
text('ADMISSION_original_arrival_relief','CARE',(14.36,-14.0,1.98),.26,(math.pi/2,0,-math.pi/2))
marker('core_aperture_centre',(20,-14,0),'proposed_uninstalled_core_threshold',(1,0,0))
marker('waiting_admission_centre',(14,0,0),'proposed_internal_threshold',(1,0,0))

# Ceiling surfaces express a shallow faceted vault, not a flat rectangular lid.
for room,x0,x1 in [('WAIT',0,13.85),('SUPPORT',-13.76,-.12)]:
    ys=[-3.75,-2.5,-1.25,-.30,.30,1.25,2.5,3.75]
    def rise(y):return 4.2+.46*(1-abs(y)/3.75)
    for i,(ya,yb) in enumerate(zip(ys,ys[1:])):
        if ya==-.30 and yb==.30:continue
        za,zb=rise(ya),rise(yb)
        verts=[(x,y,z) for zadd in [0,.14] for x,y,z in [(x0,ya,za+zadd),(x1,ya,za+zadd),(x1,yb,zb+zadd),(x0,yb,zb+zadd)]]
        mesh(f'{room}_vault_facet_{i}',verts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'quiet_ivory')
    for x in ([.4,4.5,8.8,13.4] if room=='WAIT' else [-13.5,-8.9,-5.1,-.5]):
        for i,(ya,yb) in enumerate(zip(ys,ys[1:])):
            if ya==-.30 and yb==.30:continue
            za,zb=rise(ya),rise(yb)
            mesh(f'{room}_vault_rib_{x}_{i}',[(xx,y,z) for add in [0,.12] for xx,y,z in [(x-.06,ya,za+add),(x+.06,ya,za+add),(x+.06,yb,zb+add),(x-.06,yb,zb+add)]],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'warm_walnut')
    # The actual central aperture receives the light housing, without a duplicate solid ceiling behind its lens.
    box(room+'_light_slot_backing',x0,x1,-.30,.30,4.64,4.74,'warm_walnut')
    for y in [-.27,.27]:box(room+'_slot_rail_'+str(y),x0,x1,y-.03,y+.03,4.50,4.64,'champagne_metal',.007)
    for i,x in enumerate([x0+(x1-x0)*f for f in [.18,.5,.82]]):
        box(f'{room}_opal_light_{i}',x-1.0,x+1.0,-.24,.24,4.52,4.55,'opal_lens',.01)
        FIXTURES.append({'name':f'{room}_opal_light_{i}','source_exit':(x,0,4.50),'aim':(x,0,0),'energy':420,'size':2.0})
for i,(y0,y1) in enumerate([(-16.76,-11.2),(-11.2,-5.4),(-5.4,3.76)]):
    box('ADMISSION_ceiling_panel_'+str(i),14.24,19.76,y0,y1,4.2,4.36,'quiet_ivory')
    y=(y0+y1)/2
    box('ADMISSION_recess_housing_'+str(i),16.0,18.0,y-.32,y+.32,4.2,4.36,'warm_walnut')
    box('ADMISSION_lens_'+str(i),16.12,17.88,y-.20,y+.20,4.185,4.2,'opal_lens',.009)
    FIXTURES.append({'name':'ADMISSION_lens_'+str(i),'source_exit':(17,y,4.17),'aim':(17,y,0),'energy':350,'size':1.6})

# Replace the waiting roof facets with one ceiling fitted to its actual scalloped enclosure.
for o in list(PARTS):
    if o.name.startswith('WAIT_vault_'):
        PARTS.remove(o);bpy.data.objects.remove(o,do_unlink=True)
for side,outer,inner_y in [('north',north,.30),('south',south,-.30)]:
    for i,(a,b) in enumerate(zip(outer,outer[1:])):
        x0,y0=a;x1,y1=b
        if x1-x0<.001:continue
        low=[(x0,y0,4.2),(x1,y1,4.2),(x1,inner_y,4.66),(x0,inner_y,4.66)]
        verts=low+[(x,y,z+.14) for x,y,z in low]
        mesh(f'WAIT_fitted_vault_{side}_{i}',verts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'quiet_ivory')
        if i%2==0:
            xx=(x0+x1)/2;yy=(y0+y1)/2
            mesh(f'WAIT_fitted_rib_{side}_{i}',[(x,y,z) for add in [0,.11] for x,y,z in [(xx-.05,yy,4.2+add),(xx+.05,yy,4.2+add),(xx+.05,inner_y,4.66+add),(xx-.05,inner_y,4.66+add)]],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'warm_walnut')

# A true shaped portal rhythm compresses and releases the admission route, keeping x15.2..18.8 clear.
arch=[(14.25,4.20),(19.75,4.20),(19.75,0),(18.95,0),(18.95,3.10),(18.65,3.40),(17.80,3.68),(17,3.75),(16.20,3.68),(15.35,3.40),(15.05,3.10),(15.05,0),(14.25,0)]
for i,y in enumerate([-11.25,-5.5,.85]):
    n=len(arch);verts=[(x,yy,z) for yy in [y-.20,y+.20] for x,z in arch]
    mesh(f'ADMISSION_faceted_portal_{i}',verts,[tuple(reversed(range(n))),tuple(n+j for j in range(n))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)],'sage_acoustic',.035)
    for x in [14.65,19.35]:
        box(f'ADMISSION_portal_{i}_{x}_shoe',x-.39,x+.39,y-.23,y+.23,0,.12,'warm_walnut',.015)
    marker(f'admission_portal_{i}_opening',(17,y,0),'clear_route_centre')
box('ADMISSION_wayfinding_backplate',19.56,19.76,-8.95,-5.95,1.1,2.75,'warm_walnut')
text('ADMISSION_waiting_direction','WAITING',(19.545,-7.45,2.2),.28,(math.pi/2,0,-math.pi/2))
text('ADMISSION_support_direction','CARE  /  SUPPORT',(19.54,-7.45,1.77),.16,(math.pi/2,0,-math.pi/2))

# A fitted service work edge makes the diagnostic support's blank side useful without inventing treatment equipment.
workpoly=[(-6.5,-3.72),(-1.5,-3.72),(-1.5,-2.95),(-2.0,-2.70),(-6.1,-2.70),(-6.5,-2.95)]
prism('SUPPORT_sorting_worktop',workpoly,.90,.99,'warm_walnut',.025)
for x in [-6.15,-2.0]:
    box('SUPPORT_worktop_pier_'+str(x),x-.15,x+.15,-3.6,-2.9,0,.9,'sage_acoustic',.03)
box('SUPPORT_work_backpanel',-6.5,-1.5,-3.76,-3.64,1.15,2.75,'sage_acoustic')
for x in [-5.65,-4.0,-2.35]:
    box('SUPPORT_work_divider_'+str(x),x-.045,x+.045,-3.64,-3.1,1.18,2.3,'quiet_ivory')
box('SUPPORT_work_upper_shelf',-6.5,-1.5,-3.64,-3.1,2.3,2.38,'warm_walnut')

# Integrate the welcome ledge with a real wall return and shaped ceiling canopy.
# Its staff assistance stance is at the open west end, not a claimed usable slot behind a desk.
for o in PARTS:
    if any(o.name.startswith(prefix) for prefix in ['WELCOME_crescent','WELCOME_curved_load','WELCOME_floor_shoe','WELCOME_lower_side','WELCOME_perch_supported']):
        o.location.y+=.75
box('WELCOME_wall_bearing_return',4.35,8.8,3.70,3.76,.10,.99,'sage_acoustic',.01)
profile=[(2.68,0),(3.76,0),(3.76,4.2),(3.20,4.2),(3.02,3.75),(2.80,3.1),(2.68,2.6)]
n=len(profile);mesh('WELCOME_swept_side_receiver',[(x,y,z) for x in [4.15,4.4] for y,z in profile],[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],'sage_acoustic',.025)
canopy=[(4.15,3.76),(10.2,3.76),(10.2,2.75),(9.8,2.48),(8.4,2.22),(7.5,2.0),(5.8,2.0),(4.85,2.25),(4.15,2.7)]
prism('WELCOME_fitted_canopy',canopy,4.2,4.39,'warm_walnut',.03)
marker('welcome_staff_assistance_stance',(3.6,2.5,0),'proposed_standing_stance_not_species_fit')

# Existing wall sconces meet actual wall receiver planes at y3.76; warm source light stays local.
for i,x in enumerate([4.0,10.4]):
    retain('AST-GST-002','WaitingSconce_'+str(i),(x,3.76,2.30),0)
    marker('sconce_'+str(i)+'_wall',(x,3.76,2.30),'physical_wall_receiver',(0,-1,0),'WAIT_north_sculpted_enclosure')
    FIXTURES.append({'name':'WaitingSconce_'+str(i),'source_exit':(x,3.52,2.35),'aim':(x,1.8,.8),'energy':65,'size':.25})

# Room identities and exact parent-controlled interfaces are machine-readable, not new destinations.
SCENE['scope']='Source-only uninstalled candidate; no floor slabs, operating clinic, runtime access, population or capacity acceptance.'
SCENE['world_origin_xyz']=(-28,21,-446)
SCENE['preserved_children']='D05_directory_01_local_waiting_and_escort_01;D05_directory_01_local_diagnostic_support_01'
SCENE['catalogue_id']='Unreserved scratch assembly; parent must assign/register before catalogue adoption'
SCENE['fixture_clearance_note']='Vault clear >=4.2m; admission lens underside 4.185m, aperture clear 2.4m.'
bpy.context.view_layer.update()
part_records=[]
for o in PARTS:
    if o.type=='MESH':
        verts=[o.matrix_world@v.co for v in o.data.vertices]
        part_records.append({'name':o.name,'material_role':o.get('material_role'),'bounds_source_xyz':[list(map(min,zip(*verts))),list(map(max,zip(*verts)))],'vertices':len(verts)})
REPORT={'scope':SCENE['scope'],'run':RUN,'source_frame':'Blender metres X/Y/Z-up','world_mapping':'world=(sx-28,sz+21,-sy-446)','children':['D05_directory_01_local_waiting_and_escort_01','D05_directory_01_local_diagnostic_support_01'],'new_editable_parts':len(PARTS),'retained_component_instances':RETAINED,'new_part_records':part_records,'receiver_markers':RECEIVERS,'fixture_sources':FIXTURES,'floor_ownership':'No production floor in source/export; parent compiler union required. Preview floor is QA-only.','core_aperture_proposal':{'world_clear_bounds_x_y_z':[[-7.88,-7.635],[21,23.4],[-433.8,-430.2]],'affected_existing_nodes':['CORE_OuterWall_04_-1','CORE_WallDado_04_-1'],'supporting_floor_connector_xz':[-8,-7.8,-433.8,-430.2],'floor_y':21,'core_identity':'forward_public_core_001','status':'parent review only; core untouched'},'clinical_targets_preserved':[20,4,12,8,6,2],'service_decision':'Retain approved exterior controlled crossing and unresolved internal handoff; no new corridor network in this package.'}

# Save editable assembly before QA floor, cameras or light objects are introduced.
bpy.context.preferences.filepaths.save_version=0
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
bpy.ops.object.select_all(action='DESELECT')
for o in PARTS:o.select_set(True)
for o in bpy.data.objects:
    if o.name.startswith('DATUM_') and o.get('source_package')=='D05_forward_welcome_candidate':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(EXPORT),export_format='GLB',export_yup=True,use_selection=True,export_extras=True,export_apply=True,export_cameras=False,export_lights=False)
REPORT.update(source=str(SOURCE),source_sha256=sha(SOURCE),architecture_export=str(EXPORT),export_sha256=sha(EXPORT),generator_sha256=sha(__file__))
for p,h in PIN['inputs'].items():assert sha(p)==h,('input changed during build',p)
(ROOT/'qa'/f'SOURCE_MANIFEST_{RUN}.json').write_text(json.dumps(REPORT,indent=2)+'\n')
print('SOURCE_READY',SOURCE,EXPORT,len(PARTS),flush=True)
