"""Portable WP02 source candidate. Blender 4.3.2; no live Game/Catalogue writes.
blender --background --factory-startup --threads 2 --python source/build_section.py
"""
from pathlib import Path
import bpy, bmesh, math, json, hashlib, sys
from mathutils import Vector, Matrix

ROOT=Path(__file__).resolve().parents[1]
for p in ('source','exports','qa','renders','docs'): (ROOT/p).mkdir(exist_ok=True)
ROW=json.loads((ROOT/'docs/current_allocation.json').read_text(encoding='utf-8-sig'))
assert ROW['portal']==[8,35.5,460] and ROW['key']=='D07_directory_10'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
for a in ROW['asset_sources']:
    assert sha(ROOT/'dependencies/assets'/f"{a['id']}.blend")==a['source_sha256_current'],a['id']
bpy.ops.wm.read_factory_settings(use_empty=True)
SC=bpy.context.scene;SC.unit_settings.system='METRIC';SC.unit_settings.scale_length=1
COLL=bpy.data.collections.new('WP02_ARCHITECTURE');SC.collection.children.link(COLL)
PRE=bpy.data.collections.new('SOURCE_PREVIEW_ONLY');SC.collection.children.link(PRE)
MAT={};PARTS=[];COLLISIONS=[];INSTANCES=[];LIGHTS=[]
manifest=json.loads((ROOT/'dependencies/materials/material_manifest.json').read_text())['materials']
for role in ['ivory_enamel','warm_walnut','warm_stone','champagne_metal','teal_weave','clay_weave','oatmeal_weave']:
    spec=manifest[role];m=bpy.data.materials.new('WP02_'+role);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=spec['roughness'];bs.inputs['Metallic'].default_value=spec['metallic']
    tx=m.node_tree.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(ROOT/'dependencies/materials'/spec['base_color_file']));tx.interpolation='Closest'
    m.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color']);m['meters_per_tile_uv']=spec['meters_per_tile_uv'];MAT[role]=m
for role,col,emit in [('opal',(1,.79,.48,1),2.5),('dark',(.045,.072,.074,1),0),('cool_opal',(.7,.9,1,1),2)]:
    m=bpy.data.materials.new('WP02_'+role);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=col;bs.inputs['Roughness'].default_value=.7
    bs.inputs['Emission Color'].default_value=col;bs.inputs['Emission Strength'].default_value=emit;MAT[role]=m

def p(x,z,h=0): return Vector((x-8,460-z,h))
def uv(o):
    me=o.data;lay=me.uv_layers.new(name='UV_Metric')
    scale=me.materials[0].get('meters_per_tile_uv',[1,1])
    for f in me.polygons:
        ax=max(range(3),key=lambda k:abs(f.normal[k]));axes=[k for k in range(3) if k!=ax]
        for li in f.loop_indices:
            q=me.vertices[me.loops[li].vertex_index].co;lay.data[li].uv=(q[axes[0]]/scale[0],q[axes[1]]/scale[1])
def mesh(name,vs,fs,role,preview=False):
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
    o=bpy.data.objects.new(name,me);(PRE if preview else COLL).objects.link(o);me.materials.append(MAT[role]);uv(o);o['material_role']=role;o['package']='WP02';o['export_enabled']=not preview;PARTS.append(o);return o
def poly(name,xz,lo,hi,role,preview=False):
    n=len(xz);vs=[tuple(p(x,z,h)) for h in (lo,hi) for x,z in xz]
    fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(name,vs,fs,role,preview)
def box(name,x0,x1,z0,z1,h0,h1,role='ivory_enamel',collision=False,preview=False,bevel=0):
    o=poly(name,[(x0,z0),(x1,z0),(x1,z1),(x0,z1)],h0,h1,role,preview)
    if bevel:
        mod=o.modifiers.new('Readable edge easing','BEVEL');mod.width=bevel;mod.segments=2
    if collision:COLLISIONS.append({'name':name,'type':'box','local_glb_min':[x0-8,h0,z0-460],'local_glb_max':[x1-8,h1,z1-460]})
    return o
def beam(name,a,b,width,depth,role='champagne_metal'):
    a,b=Vector(a),Vector(b);d=b-a;mid=(a+b)/2
    bpy.ops.mesh.primitive_cube_add(size=1,location=mid);o=bpy.context.object;o.name=name;o.dimensions=(width,depth,d.length);o.rotation_euler=d.to_track_quat('Z','Y').to_euler()
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(o.users_collection):c.objects.unlink(o)
    COLL.objects.link(o);o.data.materials.append(MAT[role]);uv(o);PARTS.append(o);o['export_enabled']=True;return o
def text(name,body,x,z,h,size=.35,face='south',role='dark'):
    cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.align_x='CENTER';cu.size=size;cu.extrude=.004;cu.resolution_u=2
    o=bpy.data.objects.new(name,cu);COLL.objects.link(o);o.location=p(x,z,h)
    o.rotation_euler=(math.pi/2,0,0 if face=='south' else math.pi if face=='north' else math.pi/2)
    cu.materials.append(MAT[role]);o['export_enabled']=True;o['original_text']=body;PARTS.append(o);return o
def sign(name,body,x,z,h=2.6,width=3.5,face='south'):
    box(name+'_plaque',x-width/2,x+width/2,z-.045,z+.045,h-.1,h+.62,'warm_walnut',bevel=.035)
    text(name,body,x,z+(.05 if face=='south' else -.05),h,.28,face=face,role='oatmeal_weave')
def asset(aid,name,x,z,h=0,yaw=0):
    with bpy.data.libraries.load(str(ROOT/'dependencies/assets'/f'{aid}.blend'),link=False) as (src,dst):dst.objects=list(src.objects)
    obs=[o for o in dst.objects if o and o.type in {'MESH','EMPTY','CURVE','LIGHT'}]
    root=bpy.data.objects.new(name+'_placement',None);COLL.objects.link(root);root.location=p(x,z,h);root.rotation_euler.z=math.radians(yaw);root['source_catalogue_id']=aid
    for o in obs:
        COLL.objects.link(o);o.name=name+'__'+o.name;o['export_enabled']=True;o['source_catalogue_id']=aid
        if not o.parent:o.parent=root
        for m in getattr(o.data,'materials',[]) if o.type in {'MESH','CURVE'} else []:
            if m and m.use_nodes:
                for nd in m.node_tree.nodes:
                    if nd.type=='TEX_IMAGE' and nd.image and not nd.image.packed_file:
                        found=list((ROOT/'dependencies/materials').rglob(Path(nd.image.filepath).name))
                        if found:nd.image.filepath=str(found[0]);nd.image.reload()
    INSTANCES.append({'name':name,'catalogue_id':aid,'world_xzy':[x,z,35.5+h],'yaw_blender_deg':yaw,'native_source_unscaled':True})
    return root
def lamp(name,x,z,ceiling=5.45,cool=False,power=190):
    # Ceiling housing, rod, yoke and diffuser are all physically contiguous.
    box(name+'_mount',x-.24,x+.24,z-.24,z+.24,ceiling-.1,ceiling+.08,'champagne_metal')
    beam(name+'_stem',p(x,z,ceiling-.08),p(x,z,ceiling-.55),.055,.055)
    box(name+'_housing',x-.42,x+.42,z-.42,z+.42,ceiling-.72,ceiling-.52,'champagne_metal',bevel=.08)
    box(name+'_diffuser',x-.34,x+.34,z-.34,z+.34,ceiling-.75,ceiling-.70,'cool_opal' if cool else 'opal',bevel=.04)
    d=bpy.data.lights.new(name+'_effective_light','POINT');d.energy=power;d.color=(.68,.83,1) if cool else (1,.78,.52);d.shadow_soft_size=.34
    o=bpy.data.objects.new(name+'_effective_light',d);COLL.objects.link(o);o.location=p(x,z,ceiling-.84);o['export_enabled']=True
    LIGHTS.append({'name':name,'local_blender':list(o.location),'power_W':power,'mount':'ceiling bearing/rod/housing/diffuser; light just below diffuser','kind':'point'})
def bench(name,x0,x1,z,front=1):
    box(name+'_base',x0+.12,x1-.12,z-.65,z+.65,0,.38,'ivory_enamel',True,bevel=.09)
    box(name+'_seat',x0,x1,z-.68,z+.68,.38,.57,'teal_weave',bevel=.12)
    zb=z-.50*front;box(name+'_back',x0,x1,zb-.12,zb+.12,.53,1.18,'warm_walnut',True,bevel=.08)
    for x in (x0+.12,x1-.12):box(name+'_arm',x-.10,x+.10,z-.54,z+.54,.55,.79,'champagne_metal',bevel=.04)
def locker(name,x,z,face='west'):
    # Full furniture construction, recessed door, frame, handle, vent and number.
    box(name+'_carcass',x,x+1.0,z,z+1.3,.08,2.3,'warm_walnut',True,bevel=.04)
    xf=x-.035 if face=='west' else x+1.035
    box(name+'_door',xf-.035,xf+.035,z+.07,z+1.23,.15,2.23,'ivory_enamel',bevel=.025)
    box(name+'_handle',xf-.07,xf+.07,z+.90,z+.94,.95,1.25,'champagne_metal',bevel=.018)
    for k in range(3):box(name+'_vent'+str(k),xf-.045,xf+.045,z+.23,z+1.03,1.8+.07*k,1.82+.07*k,'dark')
    direction=1 if face=='east' else -1
    label=text(name+'_number',name.rsplit('_',1)[-1].zfill(2),xf+direction*.078,z+.65,1.50,.16,role='dark')
    label.rotation_euler.z=direction*math.pi/2
def screen(name,x,z0,z1,height=3.2):
    box(name,x,x+.28,z0,z1,0,height,'ivory_enamel',True,bevel=.035)
    box(name+'_cap',x-.035,x+.315,z0,z1,height,height+.12,'warm_walnut')

# Sole current public boundary opening at X8,Z460. Entire candidate remains within allocation.
box('SOURCE_PREVIEW_ONLY_floor',8,54,398,466,-.18,0,'warm_stone',preview=True)
box('SOURCE_PREVIEW_ONLY_dry_walk',18.9,29.1,400,452,.001,.002,'oatmeal_weave',preview=True)
box('SOURCE_PREVIEW_ONLY_wet_zone',29,49.7,398.4,425,.001,.002,'ivory_enamel',preview=True)
box('WestWall_fore',8,8.38,398,458,0,7.8,collision=True)
box('WestWall_aft',8,8.38,462,466,0,7.8,collision=True)
box('WestPortalLintel',8,8.65,458,462,3.4,7.8,collision=True)
box('EastWall',53.62,54,398,466,0,7.8,collision=True)
box('ForeWall',8.38,53.62,398,398.38,0,7.8,collision=True)
box('AftWall',8.38,53.62,465.62,466,0,7.8,collision=True)
box('OpaqueDeckBoundaryEnclosure',8,54,398,466,7.62,7.8,'ivory_enamel',True)
for z0,z1 in [(457.45,458),(462,462.55)]:
    box('DeepPortalJamb',8.38,11.2,z0,z1,0,3.65,'warm_walnut',True)
box('DeepPortalCeiling',8.38,12,457.45,462.55,3.4,3.7,'warm_walnut',True)
sign('Welcome','SPORTS  /  CARE & CHANGING',19,465.25,2.65,8)

# Public reception: faceted fitted desk, warm waiting edges, clear 4m arrival lane.
poly('ReceptionDesk',[(26,455),(30,455),(31.2,456.2),(31.2,459),(30,460.2),(26,460.2)],0,1.03,'warm_walnut')
poly('ReceptionCounter',[(25.8,454.8),(30.1,454.8),(31.4,456.1),(31.4,459.1),(30.1,460.4),(25.8,460.4)],1.03,1.15,'warm_stone')
box('LowerAccessibleCounter',23.8,26,455,457,.68,.80,'warm_stone',True,bevel=.06)
box('CounterPedestal',24,25.8,455.3,456.8,0,.68,'ivory_enamel',True)
bench('ArrivalRestA',11,17,464.1);bench('ArrivalRestB',33,40,464.1)
bench('WaitingFacing',33,39,453.5,-1)
for x in (13,36):
    box('FittedSideTable',x-.55,x+.55,462.15,463.15,0,.6,'warm_walnut',True,bevel=.10)
    asset('AST-LGT-001','TableLantern'+str(x),x,462.6,.6)
asset('AST-AQU-007','ReceptionCleanTextiles',22,464.8,0,180)
sign('WingWayfinding','CHANGING     /     LOCKERS     /     RINSE',24,451.1,3.25,10)

# Main promenade: alternating weighted piers with curved, bearing-supported canopy.
# Profile rises from 4.4m at edges to 5.9m at centre, with real 0.30m shell and fascia.
for z in range(404,452,6):
    for x in (19.15,29.0):
        box('SpinePier',x-.3,x+.3,z-.35,z+.35,0,4.35,'ivory_enamel',True,bevel=.08)
        box('PierFoot',x-.44,x+.44,z-.49,z+.49,0,.3,'warm_stone',True,bevel=.07)
        box('PierCapital',x-.46,x+.46,z-.50,z+.50,4.2,4.55,'champagne_metal',bevel=.05)
    pts=[p(19.15+9.85*i/10,z,4.45+1.35*math.sin(math.pi*i/10)) for i in range(11)]
    for i in range(10):beam('VaultBearingRib',pts[i],pts[i+1],.34,.42,'warm_walnut')
for z in range(404,446,6):
    for i in range(10):
        xa=19.15+9.85*i/10;xb=19.15+9.85*(i+1)/10
        ha=4.45+1.35*math.sin(math.pi*i/10);hb=4.45+1.35*math.sin(math.pi*(i+1)/10)
        vs=[tuple(p(x,zz,h)) for zz in (z+.18,z+5.82) for x,h in [(xa,ha),(xb,hb),(xb,hb+.22),(xa,ha+.22)]]
        mesh('VaultBackedPanel',vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(3,7,6,2),(0,4,7,3),(1,2,6,5)],'ivory_enamel')
for x in (19.15,29):box('CanopyTerminationRail',x-.22,x+.22,403.5,446.5,4.37,4.66,'champagne_metal')

# Complete fitted private changing rooms along a quiet wing; 6 units are a design choice.
for i,z in enumerate(range(404,440,6)):
    pref=f'Changing_{i+1:02d}'
    box(pref+'_rear',8.4,16.9,z,z+.25,0,3.4,collision=True)
    box(pref+'_front',8.4,16.9,z+5.65,z+5.9,0,3.4,collision=True)
    # Doorless two-turn privacy entry, 2m clear turning bay outside each compartment.
    screen(pref+'_inner_return',15.9,z+.25,z+3.35)
    screen(pref+'_outer_screen',18.0,z+1.35,z+5.65)
    box(pref+'_ceiling',8.4,18.3,z,z+5.9,3.4,3.64,'ivory_enamel')
    bench(pref+'_bench',10.0,13.8,z+4.6)
    locker(pref+'_lockerA',9.0,z+.7,'east');locker(pref+'_lockerB',9.0,z+2.1,'east')
    for xx in (11.4,12.2,13.0):box(pref+'_hook_mount',xx-.10,xx+.10,z+.27,z+.33,1.55,1.72,'champagne_metal')
    sign(pref+'_identity',f'PRIVATE CHANGING  {i+1:02d}',12.3,z+5.5,2.5,5.8)
    lamp(pref+'_lamp',12.5,z+2.8,3.4,power=95)

# Locker gallery: two sculpted islands leave 4m access lanes and seated changing edges.
for bank,x in enumerate((33.1,44.5)):
    # Both working faces open into the seated changing court. Back panels lie on
    # the opposite/outboard side, never over a door or handle.
    face='east' if bank==0 else 'west'
    for i,z in enumerate([427+1.55*k for k in range(13)]):locker(f'GalleryLocker_{bank}_{i+1:02d}',x,z,face)
    back=(x-.20,x-.04) if face=='east' else (x+1.04,x+1.20)
    box('LockerSpineBack_'+str(bank),*back,426.8,447.4,0,2.42,'warm_walnut',True)
for z in (431,441):bench('LockerGalleryBench',36.4,41.8,z)
sign('Lockers','DAY LOCKERS',39,449.1,2.7,7)
for x in (32,39,47):
    box('LockerCeilingBearer',x-.18,x+.18,425.2,450,4.10,4.48,'warm_walnut')
    for z in (425.2,450):box('LockerBearerPier',x-.22,x+.22,z-.25,z+.25,0,4.10,'ivory_enamel',True)
box('LockerCanopy',29.5,49.7,425.2,450,4.48,4.7,'ivory_enamel')

# Wet support: four rinse cells and two WC compartments behind staggered screens.
box('WetPrivacyWall',29.4,29.7,398.4,419.5,0,3.6,'ivory_enamel',True)
screen('WetThresholdScreen',31.3,420.2,424.3,3.6)
box('WetRoof',29.4,49.7,398.4,425,3.6,3.88,'ivory_enamel')
sign('Rinse','RINSE   /   WASH',37,424.8,2.8,6)
for i,z in enumerate((400.0,406.0,412.0,418.0)):
    box('RinseRear'+str(i),43,49.65,z,z+.24,0,3.6,'ivory_enamel',True)
    box('RinseFront'+str(i),43,49.65,z+5.1,z+5.35,0,3.6,'ivory_enamel',True)
    screen('RinsePrivacy'+str(i),42.3,z+.6,z+3.7,3.6)
    asset('AST-SAN-003','RinseFixture'+str(i),47.6,z+1.2,0,0)
    # Source shower riser back faces +Z after placement; host panel gives an actual mount.
    box('RinseMountWall'+str(i),46.5,48.7,z+1.86,z+2.08,0,2.6,'ivory_enamel',True)
    bench('RinseDrySeat'+str(i),44.5,46.0,z+4.25)
    asset('AST-AQU-008','RinseUsedReturn'+str(i),48.3,z+4.1)
    lamp('RinseLamp'+str(i),45.8,z+2.6,3.6,cool=True,power=90)
for i,z in enumerate((401.5,409.5,417.5)):
    asset('AST-SAN-001','SupportedWashVanity'+str(i),29.75,z,0)
    box('VanityMountBacking'+str(i),29.66,29.78,z-.6,z+.6,.25,2.25,'warm_walnut')
    beam('VanitySupply'+str(i),p(29.82,z,.35),p(29.82,z,0.1),.08,.08)
for i,z in enumerate((400,408)):
    box('WCCellRear'+str(i),34,40,z,z+.25,0,3.6,'ivory_enamel',True)
    box('WCCellFront'+str(i),34,40,z+6,z+6.25,0,3.6,'ivory_enamel',True)
    screen('WCPrivacy'+str(i),39.5,z+1.2,z+5.8,3.6)
    asset('AST-SAN-002','WCFixture'+str(i),36.4,z+2.2,0)
    box('WCTankHost'+str(i),35.6,37.2,z+2.80,z+3.02,0,1.1,'ivory_enamel',True)
sign('DryThreshold','DRY ROUTE  /  TEXTILE RETURN',24,400,2.6,8)
asset('AST-AQU-007','DryTransitionCleanTextiles',30.6,424.2,0,180)
asset('AST-AQU-008','DryTransitionUsedReturn',48.5,424)

# Back-of-house enclosed local spine; no external staff doorway cut.
for a,b in [(398.4,423),(425.5,450),(453,465.6)]:screen('ServiceScreen',49.7,a,b,4.5)
box('ServiceCeiling',49.7,53.62,398.4,465.6,4.5,4.74,'ivory_enamel')
box('ServiceSupplyEnclosure',42,49.7,451,451.3,0,4.5,'ivory_enamel',True)
box('ServiceSupplyCanopy',42,49.7,451,465.6,4.5,4.75,'ivory_enamel')
asset('AST-STF-007','CleaningCupboard',46.1,464.5,0,180)
# Original cabinet manifest fixes its physical work-surface top at0.94m.
# Local clean cloth and bottle details sit on that exact surface, not in mid-air.
for k in range(3):
    box('CleanFoldedCloth_'+str(k),45.55,45.94,464.26,464.57,.94+k*.036,.976+k*.036,'oatmeal_weave',bevel=.018)
    box('ClothWovenHem_'+str(k),45.56,45.93,464.25,464.27,.951+k*.036,.960+k*.036,'teal_weave')
for i,x in enumerate((46.28,46.60)):
    ring=[(x+.085*math.cos(j*math.tau/8),464.43+.085*math.sin(j*math.tau/8)) for j in range(8)]
    poly('CareSupplyBottle_'+str(i),ring,.94,1.23,'ivory_enamel')
    box('BottleShoulder_'+str(i),x-.065,x+.065,464.365,464.495,1.23,1.27,'ivory_enamel',bevel=.02)
    box('BottleClosure_'+str(i),x-.035,x+.035,464.395,464.465,1.27,1.32,'champagne_metal',bevel=.015)
    box('BottleLabel_'+str(i),x-.061,x+.061,464.342,464.351,1.015,1.135,'teal_weave' if i==0 else 'clay_weave')
sign('CareStockLabel','CLEAN CLOTHS  /  CARE STOCK',46.1,465.58,1.65,4.4,face='north')
asset('AST-AQU-007','CleanReserve',43.0,464.6,0,180)
asset('AST-AQU-008','UsedTextileHoldA',48.2,454.7)
asset('AST-AQU-008','UsedTextileHoldB',48.2,456.3)
asset('AST-STF-008','InternalStaffThreshold',49.84,451.7,0,90)
sign('ServiceDesignation','STAFF  /  CARE STOCK',46,451.35,2.6,6)
box('SealedFutureServicePanel',23.5,26.5,465.30,465.60,0,3.2,'warm_walnut',True)
sign('SealedStaffNote','SERVICE RESERVATION',25,465.2,2.6,4)

# Reception canopy is suspended visibly from the opaque overhead shell.
for x in (12,22,32,41):
    box('ReceptionCeilingRib',x-.18,x+.18,450.2,465.5,4.45,4.85,'warm_walnut')
    for z in (451.0,464.9):beam('VisibleCanopyHanger',p(x,z,4.85),p(x,z,7.62),.10,.10)
box('ReceptionBackedSoffit',8.7,42,450.2,465.5,4.85,5.02,'ivory_enamel')
for x in (8.75,42):box('ReceptionSoffitEndCap',x-.08,x+.08,450.2,465.5,4.42,5.02,'champagne_metal')
for z in (404,410,416,422,428,434,440,446):lamp('PromenadePendant'+str(z),24,z,5.85,power=230)
for x in (13,23,35):
    for z in (454,462):lamp('ArrivalPendant'+str((x,z)),x,z,4.85,power=240)
for x in (31.4,39,47.5):
    for z in (429,437,445):lamp('LockerPendant'+str((x,z)),x,z,4.48,power=160)
for z in (405,416,427,439,458):lamp('ServiceLamp'+str(z),51.8,z,4.5,cool=True,power=115)
lamp('CareStockRoomLight',45.8,460.8,4.5,cool=True,power=300)
# Dedicated cabinet task light, attached to the aft wall with visible plates and
# cantilever brackets. Light is just below its opal diffuser, clear of housing.
for x in (44.85,47.35):
    box('CareTaskBackingPlate',x-.12,x+.12,465.38,465.62,2.34,2.90,'champagne_metal')
    beam('CareTaskWallBracket',p(x,465.40,2.66),p(x,464.08,2.66),.09,.11)
box('CareTaskHousing',44.65,47.55,463.94,464.24,2.54,2.74,'champagne_metal',bevel=.04)
box('CareTaskDiffuser',44.75,47.45,463.97,464.21,2.505,2.545,'cool_opal',bevel=.025)
task_data=bpy.data.lights.new('CareTask_effective_light','POINT');task_data.energy=180;task_data.color=(.78,.88,1);task_data.shadow_soft_size=.25
task_light=bpy.data.objects.new('CareTask_effective_light',task_data);COLL.objects.link(task_light);task_light.location=p(46.1,464.07,2.43);task_light['export_enabled']=True
LIGHTS.append({'name':'CareTask','local_blender':list(task_light.location),'power_W':180,'mount':'aft wall plates and continuous cantilever brackets to housing/diffuser','kind':'point'})
for x,z in ((33,404),(33,413),(36,420)):lamp('WashLight'+str((x,z)),x,z,3.6,cool=True,power=90)

# Explicit source review cameras at eye height, no cutaway used as normal-view proof.
CAMERAS={
 '01_arrival':((10,460,1.65),(27,458,1.65)),
 '02_reception_reverse':((38,459,1.65),(11,460,1.65)),
 '03_changing_spine':((24,447,1.65),(24,416,2.0)),
 '04_private_changing':((15.2,432.3,1.65),(10.5,432,1.1)),
 '05_locker_gallery':((39,448,1.65),(39,430,1.9)),
 '06_wash_threshold':((35,422,1.65),(34,411,1.5)),
 '07_service_stock':((45,455,1.65),(46,464,1.5)),
 '08_ceiling_mounts':((24,436,1.65),(24,426,5.3)),
 '09_service_returns':((45.3,459,1.65),(48.1,455.1,1.2)),
 '10_locker_working_face':((38,436,1.65),(34.0,436,1.4))}
for name,(eye,target) in CAMERAS.items():
    d=bpy.data.cameras.new(name);d.lens=23;d.clip_end=180;o=bpy.data.objects.new('REVIEW_'+name,d);PRE.objects.link(o);o.location=p(*eye);o.rotation_euler=(p(*target)-o.location).to_track_quat('-Z','Y').to_euler()
SC.camera=bpy.data.objects['REVIEW_01_arrival']
SC.render.engine='CYCLES';SC.cycles.samples=32;SC.cycles.use_denoising=True;SC.render.resolution_x=1280;SC.render.resolution_y=720;SC.render.resolution_percentage=100
SC.world=bpy.data.worlds.new('WP02 restrained ambient');SC.world.use_nodes=True;SC.world.node_tree.nodes['Background'].inputs[0].default_value=(.1,.12,.14,1);SC.world.node_tree.nodes['Background'].inputs[1].default_value=.08
SC.view_settings.view_transform='AgX'
bpy.context.view_layer.update()
missing=[]
for im in bpy.data.images:
    if im.source=='FILE' and not im.packed_file:
        if not Path(bpy.path.abspath(im.filepath)).exists():missing.append(im.filepath)
assert not missing,missing
bpy.ops.file.pack_all()
source=ROOT/'source/WP02_sports_care.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source))
# Selection-based export definitively omits source-only floor/cameras; static light objects exported.
# Preserve editable native FONT objects above, then turn lettering into real export meshes.
# A receiving check requires every authored native sign name to survive in the GLB.
bpy.ops.object.select_all(action='DESELECT')
for o in list(COLL.objects):
    if o.type=='FONT':
        o.select_set(True);bpy.context.view_layer.objects.active=o
        bpy.ops.object.convert(target='MESH');o.select_set(False)
bpy.ops.object.select_all(action='DESELECT')
for o in COLL.objects:
    if o.type in {'MESH','CURVE','EMPTY','LIGHT'}:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'exports/WP02_sports_care.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_lights=True,export_cameras=False)
def dump(path,obj): (ROOT/path).write_text(json.dumps(obj,indent=2)+'\n')
dump('docs/floor_contact_proposal.json',{'scope':'not installed','frame':'ship Godot metres','floor_y':35.5,'polygon_xz':[[8,398],[54,398],[54,466],[8,466]],'receiver_portal':[8,35.5,460],'external_link_x':[4,8],'external_link_owner':'Higgins held unbuilt','asset_floor_exported':False,'parent_to_choose_single_floor_owner':True,'no_cross_datum_cuts':True})
dump('docs/collision_proposal.json',{'scope':'source primitive proposals only; live physical testing absent','frame':'package-local GLB Y-up origin world[8,35.5,460]','primitives':COLLISIONS,'asset_collisions':'derive from actual imported semantic/source contact profiles; do not substitute blanket convex hulls','runtime_accepted':False})
dump('docs/instances.json',INSTANCES);dump('docs/lights.json',LIGHTS)
dump('qa/build_receipt.json',{'blender_version':bpy.app.version_string,'source_sha256':sha(source),'glb_sha256':sha(ROOT/'exports/WP02_sports_care.glb'),'geometry_authored':True,'reference_plan':'docs/BRIEF.md','export_floor_excluded':True,'mesh_objects':len([o for o in COLL.objects if o.type=='MESH']),'light_count':len(LIGHTS),'source_images_missing':missing,'live_integration':False,'normal_eye_visual_review':'pending','native_reopen':'pending','source_bounds_check':'pending independent reopen','claim':'complete fitted source candidate; not integrated ship section'})
print('WP02_SOURCE_BUILD_COMPLETE',str(source),flush=True)
