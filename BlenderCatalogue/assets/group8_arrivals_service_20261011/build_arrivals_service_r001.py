"""New Orchard work-bay and receiving fittings; immutable retained sources untouched."""
from pathlib import Path
import bpy,bmesh,json,math,hashlib,sys
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];C=R/'BlenderCatalogue'
AID='AST-G8-ARR-001';FAMILY='group8_arrivals_service_20261011';ROOM='D01_directory_01';F=0.0
assert all(a['catalogue_id']!=AID or a['family']==FAMILY for a in json.load(open(C/'catalogue_manifest.json'))['assets'])
native=W/'ArrivalsService_r001.blend';out=W/'G8_ARRIVALS_SERVICE_r001_unbatched.glb'
assert not native.exists()and not out.exists(),'Immutable revision already exists'
bpy.ops.wm.read_factory_settings(use_empty=True);sys.path.insert(0,str(C/'standards'))
import staff_materials,materials
mats=staff_materials.materials();mats.update(materials.materials())
for m in mats.values():
    for node in m.node_tree.nodes:
        if node.type=='TEX_IMAGE':node.interpolation='Closest'
mat=bpy.data.materials.new('G8_ARR_OpalLens');mat.use_nodes=True;mat.diffuse_color=(.98,.92,.79,1)
bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=mat.diffuse_color;bs.inputs['Emission Color'].default_value=mat.diffuse_color;bs.inputs['Emission Strength'].default_value=.35;bs.inputs['Roughness'].default_value=.65
mat['meters_per_tile_uv']=[1,1];mats['light_lens']=mat
records=[];instances=[];lights=[];supports=[];contacts=[];source_copies=[];UNIT=''
FACES=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def mesh(name,verts,faces,role='staff_white_paint',category='fitting',permitted_context=None):
    name='G8A_'+UNIT+'_'+name;me=bpy.data.meshes.new(name);me.from_pydata([(x,-z,y)for x,y,z in verts],[],faces);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(mats[role]);uv=me.uv_layers.new(name='MetreScaled');scale=mats[role].get('meters_per_tile_uv',[1,1])
    for face in me.polygons:
        n=face.normal.normalized();u=Vector((1,0,0))-n*n.x if abs(n.z)>.7 else Vector((-n.y,n.x,0));u.normalize();v=n.cross(u)
        for li in face.loop_indices:
            q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.dot(u)/scale[0],q.dot(v)/scale[1])
    ob['programme_key']=ROOM;ob['unit']=UNIT;ob['category']=category
    records.append({'name':name,'programme_key':ROOM,'unit':UNIT,'role':role,'category':category,'collide':category!='light_source','permitted_retained_context':permitted_context or [],'world_aabb':[min(v[0]for v in verts),max(v[0]for v in verts),min(v[1]for v in verts),max(v[1]for v in verts),min(v[2]for v in verts),max(v[2]for v in verts)]});return ob
def box(name,x,y,z,sx,sy,sz,role='staff_white_paint',category='fitting',permitted=None):
    return mesh(name,[(x+a,y+c,z+b)for c in [-sy/2,sy/2]for a,b in [(-sx/2,-sz/2),(sx/2,-sz/2),(sx/2,sz/2),(-sx/2,sz/2)]],FACES,role,category,permitted)
def round_slab(name,x,y,z,w,d,h,r,role='staff_zinc'):
    pts=[]
    for cx,cz,angle in [(x+w/2-r,z+d/2-r,0),(x-w/2+r,z+d/2-r,90),(x-w/2+r,z-d/2+r,180),(x+w/2-r,z-d/2+r,270)]:
        for j in range(4):
            a=math.radians(angle+j*30);pts.append((cx+r*math.cos(a),cz+r*math.sin(a)))
    n=len(pts);vs=[(px,y+dy,pz)for dy in [-h/2,h/2]for px,pz in pts]
    return mesh(name,vs,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)],role)
def pipe(name,a,b,r=.025,role='staff_zinc',sides=10):
    a=Vector(a);b=Vector(b);axis=(b-a).normalized();u=axis.cross(Vector((0,1,0))if abs(axis.y)<.9 else Vector((1,0,0))).normalized();v=axis.cross(u)
    vs=[tuple(p+r*(math.cos(math.tau*i/sides)*u+math.sin(math.tau*i/sides)*v))for p in [a,b]for i in range(sides)]
    return mesh(name,vs,[tuple(reversed(range(sides))),tuple(range(sides,2*sides))]+[(i,(i+1)%sides,(i+1)%sides+sides,i+sides)for i in range(sides)],role)
def foot(name,x,z,top=F+.15,w=.10,d=.10,lo=F):
    box(name,x,(lo+top)/2,z,w,top-lo,d,'dark_rubber');supports.append({'unit':UNIT,'kind':'floor','at':[x,lo,z],'expected_retained':'ORCH_StaffFloorFinish_'if lo>F else'CompiledStructuralFloors_NotFinishedRooms'})
def wall(name,a,b,lo,hi,width,role='ivory_enamel'):
    ax,az=a;bx,bz=b;dx=bx-ax;dz=bz-az;length=math.hypot(dx,dz);nx=-dz/length*width/2;nz=dx/length*width/2
    return mesh(name,[(x+s*nx,y,z+s*nz)for s in [-1,1]for x,y,z in [(ax,lo,az),(bx,lo,bz),(bx,hi,bz),(ax,hi,az)]],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role,'architecture')
def extrude(name,outline,lo,hi,role='ivory_enamel',allowed=None):
    n=len(outline);return mesh(name,[(x,y,z)for y in [lo,hi]for x,z in outline],[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)],role,'architecture',allowed)
def ceiling_fixture(name,x,z,at_y=3.88,warm=False):
    global UNIT;UNIT=name;instances.append({'name':name,'type':'visible_ceiling_task_fixture','at':[x,at_y,z]})
    box('CanopyStem',x,(at_y+.12+4.30)/2,z,.055,4.30-at_y-.12,.055,'staff_zinc')
    box('Case',x,at_y+.07,z,.64,.14,.40,'champagne_metal'if warm else'staff_white_paint')
    box('Lens',x,at_y-.01,z,.54,.018,.30,'light_lens','light_source')
    marker='G8A_LIGHT_'+name;ob=bpy.data.objects.new(marker,None);bpy.context.collection.objects.link(ob);ob.location=(x,-z,at_y-.027)
    lights.append({'name':marker,'programme_key':ROOM,'at':[x,at_y-.027,z],'range':6.5,'energy':.95,'colour':[1,.94,.85]if warm else[.82,.93,1]})
def baggage_case(name,x,y,z,w=.58,d=.55,h=.48):
    # Original inactive case silhouettes, no owner/inventory or mobile cart.
    round_slab(name+'_Shell',x,y+h/2,z,w,d,h,.085,'staff_bluegrey_paint')
    box(name+'_Spine',x+w/2-.017,y+h/2,z,.035,h*.80,d*.70,'dark_rubber')
    for dz in [-d*.36,d*.36]:box(name+'_Band'+str(dz),x,y+h/2,z+dz,w+.022,h+.01,.027,'champagne_metal')
    for dx in [-.13,.13]:pipe(name+'_GripEnd'+str(dx),(x+dx,y+h,z),(x+dx,y+h+.075,z),.018)
    pipe(name+'_Grip',(x-.13,y+h+.075,z),(x+.13,y+h+.075,z),.018)
def rack(name,z):
    global UNIT;UNIT=name;instances.append({'name':name,'type':'inactive_baggage_rack','at':[-52.65,0,z]})
    for dx in [-.60,.60]:
        for dz in [-1.40,1.40]:
            foot('Foot'+str((dx,dz)),-52.65+dx,z+dz,.17,.16,.16)
            box('Upright'+str((dx,dz)),-52.65+dx,1.48,z+dz,.085,2.80,.085,'staff_zinc')
    for y in [.21,1.06,1.91,2.78]:
        box('Shelf'+str(y),-52.65,y,z,1.30,.07,2.90,'staff_zinc')
        box('ShelfStop'+str(y),-53.20,y+.10,z,.065,.15,2.9,'staff_bluegrey_paint')
    for row,y in enumerate([.245,1.095,1.945]):
        for col in [-1,0,1]:baggage_case('Case_%s_%s'%(row,col),-52.55,y,z+col*.89)
def packing_table(name,x,z,w=4.6):
    global UNIT;UNIT=name;instances.append({'name':name,'type':'inspection_and_repacking_surface','at':[x,0,z]})
    for dx in [-w/2+.22,w/2-.22]:
        for dz in [-.40,.40]:
            foot('Foot'+str((dx,dz)),x+dx,z+dz,.17,.16,.14)
            box('Leg'+str((dx,dz)),x+dx,.50,z+dz,.12,.70,.12,'staff_zinc')
    box('LowerShelf',x,.25,z,w-.32,.065,.80,'staff_bluegrey_paint')
    round_slab('Worktop',x,.94,z,w,1.13,.12,.10,'staff_zinc')
    for dx in [-1.3,0,1.3]:
        round_slab('SoftWorkPad'+str(dx),x+dx,1.015,z,1.00,.85,.03,.06,'teal_weave')
    for dx in [-w/2+.18,w/2-.18]:pipe('BackShelfSupport'+str(dx),(x+dx,.95,z+.44),(x+dx,1.85,z+.44),.028)
    box('LabelSupplyShelf',x,1.80,z+.39,w-.10,.065,.26,'staff_white_paint')
    for dx in [-1.5,-.75,0,.75,1.5]:round_slab('SupplyCassette'+str(dx),x+dx,1.94,z+.39,.52,.20,.23,.035,'staff_bluegrey_paint')
def desk(name,x,z):
    global UNIT;UNIT=name;instances.append({'name':name,'type':'passive_baggage_records_desk','at':[x,0,z]})
    for dx in [-1.18,1.18]:
        foot('Foot'+str(dx),x+dx,z,.15,.36,.64)
        box('Pedestal'+str(dx),x+dx,.51,z,.35,.72,.62,'staff_bluegrey_paint')
    round_slab('Top',x,.94,z,3.1,1.08,.12,.08,'staff_zinc')
    for dx in [-.85,.85]:
        box('TerminalFoot'+str(dx),x+dx,1.02,z-.17,.34,.035,.25,'dark_rubber')
        box('TerminalStand'+str(dx),x+dx,1.18,z-.17,.045,.29,.045,'staff_zinc')
        box('TerminalBack'+str(dx),x+dx,1.42,z-.17,.68,.42,.08,'staff_bluegrey_paint')
        box('InactiveReadout'+str(dx),x+dx,1.42,z-.119,.59,.33,.018,'dark_rubber')
        for j in range(5):box('ReadoutTick'+str((dx,j)),x+dx-.22+j*.11,1.42,z-.104,.026,.10+j%2*.06,.012,'staff_opal')
def hatch_counter():
    global UNIT;UNIT='PublicBaggageHandoff';instances.append({'name':UNIT,'type':'profiled_split_height_handoff','at':[-40,0,-458]})
    for z in [-459.55,-456.45]:
        foot('OuterFoot'+str(z),-39.60,z,.16,.40,.32)
        box('OuterPedestal'+str(z),-39.60,.41,z,.32,.70,.40,'warm_walnut')
    round_slab('PublicStoneLip',-39.86,.75,-458,1.68,3.78,.10,.13,'warm_stone')
    box('OuterValance',-39.07,.57,-458,.09,.35,3.50,'warm_walnut')
    round_slab('InnerStaffLip',-40.70,.94,-458,1.09,3.90,.12,.12,'staff_zinc')
    for z in [-459.55,-456.45]:
        foot('InsideFoot'+str(z),-40.80,z,.16,.36,.34)
        box('InsideLeg'+str(z),-40.8,.50,z,.12,.72,.12,'staff_zinc')
    for z in [-459.85,-456.15]:
        box('HatchCheek'+str(z),-40,1.48,z,.38,1.06,.16,'warm_walnut')
    box('HatchTopReveal',-40,2.01,-458,.42,.16,3.90,'ivory_enamel')
    box('DocumentInset',-39.57,.815,-457.2,.54,.025,.60,'dark_rubber')
    box('ReceiptReaderCase',-40.61,1.105,-457.15,.46,.27,.35,'staff_bluegrey_paint')
    # Cold staff side and low public handoff remain a construction proposal, not species fit.
UNIT='BaggageEnclosure';instances.append({'name':UNIT,'type':'screened_holding_enclosure','reuses_existing_walls':['ARR_WestLowerOpaque','ARR_OuterEnd_-465.85']})
outline=[[-53.85,-465.85],[-40,-465.85],[-40,-450],[-42,-448],[-53.85,-448]]
# New interior south/front boundaries reuse the original north/west shell.
wall('SouthWall',(-53.70,-448),(-42,-448),0,4.40,.20,'staff_white_paint')
wall('SouthChamfer',(-42,-448),(-40,-450),0,4.40,.20,'ivory_enamel')
for lo,hi in [(-465.75,-459.85),(-456.15,-453.375),(-450.625,-450)]:wall('FrontSolid_'+str(lo),(-40,lo),(-40,hi),0,4.40,.20,'ivory_enamel')
wall('DoorHeader',(-40,-453.375),(-40,-450.625),2.815,4.40,.20,'ivory_enamel')
wall('HatchPlinth',(-40,-459.85),(-40,-456.15),0,.69,.20,'warm_walnut')
wall('HatchHeader',(-40,-459.85),(-40,-456.15),2.03,4.40,.20,'ivory_enamel')
# A shaped low roof creates a purpose-specific staff volume off the tall ceremonial court.
extrude('Roof',outline,4.25,4.40,'staff_white_paint',['ARR_WestLowerOpaque','ARR_OuterEnd_'])
for z in [-464.8,-460.8,-454.3]:
    box('FrontFloorBearingPier'+str(z),-40.14,2.15,z,.26,4.30,.28,'warm_stone')
    supports.append({'unit':UNIT,'kind':'floor','at':[-40.14,0,z],'expected_retained':'CompiledStructuralFloors_NotFinishedRooms'})
for x in [-51,-46,-41.5]:
    for z in [-462.8,-455.7]:
        box('UpperSlabTie_'+str((x,z)),x,(4.38+5.765)/2,z,.075,5.765-4.38,.075,'staff_zinc','support')
        contacts.append({'unit':UNIT,'at':[x,5.758,z],'expected_prefix':'CompiledStructuralFloors_NotFinishedRooms','kind':'tie_to_original_D02_underside','floor_y':6,'thickness':.24})
# Source-owned low threshold/cornice returns give the hatch depth and an identifiable arrival.
for z in [-459.95,-456.05]:box('HatchPortalPier'+str(z),-39.94,1.35,z,.38,2.7,.22,'warm_stone')
box('HatchPortalCrown',-39.94,2.60,-458,.46,.22,4.12,'warm_walnut')
for z in [-453.49,-450.51]:box('DoorReveal'+str(z),-39.97,1.43,z,.34,2.86,.18,'warm_walnut')
box('DoorCrown',-39.97,2.94,-452,.36,.20,3.18,'warm_stone')
for z in [-463.2,-459.7,-456.2,-451.8]:rack('HoldingRack_'+str(z),z)
packing_table('PackingInspection',-48.4,-449.25);desk('RecordsDispatch',-44.4,-463.2);hatch_counter()
for name,x,z,warm in [('Handoff',-40.10,-458,True),('Entry',-41.45,-452,True),('HoldingNorth',-49.6,-463.2,False),('HoldingMiddle',-49.6,-457.9,False),('HoldingSouth',-49.6,-451.8,False),('Packing',-48.4,-449.50,False),('Records',-44.4,-463.2,False)]:ceiling_fixture(name,x,z,3.88,warm)
# Exact original chairs, no new passenger places or species-ready claim.
source_path=C/'assets/furniture/AST-FUR-002_day_reading_chair.blend'
with bpy.data.libraries.load(str(source_path),link=False)as(src,dst):dst.objects=src.objects
for ob in dst.objects:
    if ob:bpy.context.collection.objects.link(ob)
bpy.context.view_layer.update();sources=[o for o in dst.objects if o and o.type=='MESH'];poses={o.name:o.matrix_world.copy()for o in sources}
for index,x in enumerate([-45.25,-43.55]):
    UNIT='RecordsOperator'+str(index);placement=Matrix.Translation((x,461.0,0))@Matrix.Rotation(math.pi,4,'Z')
    instances.append({'name':UNIT,'type':'original_staff_operator_chair_copy','at':[x,0,-461.0],'yaw':math.pi})
    for original in sources:
        ob=original.copy();ob.data=original.data.copy();bpy.context.collection.objects.link(ob);ob.parent=None;ob.name='G8A_'+UNIT+'_'+original.name;ob.matrix_world=placement@poses[original.name]
        corners=[ob.matrix_world@Vector(c)for c in ob.bound_box];v=[(q.x,q.z,-q.y)for q in corners]
        records.append({'name':ob.name,'programme_key':ROOM,'unit':UNIT,'role':'original_staff_chair','category':'furniture','collide':True,'permitted_retained_context':[],'world_aabb':[min(q[0]for q in v),max(q[0]for q in v),min(q[1]for q in v),max(q[1]for q in v),min(q[2]for q in v),max(q[2]for q in v)]})
        source_copies.append({'name':ob.name,'source_name':original.name,'source_native':str(source_path.relative_to(R)),'placement_blender':[[float(q)for q in row]for row in placement]})
for ob in dst.objects:
    if ob:bpy.data.objects.remove(ob,do_unlink=True)
marker='G8A_DOOR_BaggageEntry';ob=bpy.data.objects.new(marker,None);bpy.context.collection.objects.link(ob);ob.location=(-40,452,0)
door={'name':'BaggageServiceDoor','persistent_id':'D01_arrivals_g8_baggage_service_001','identity_provenance':'new authored local door;not recovered historical room/save identity','marker':marker,'at':[-40,0,-452],'yaw':math.pi/2,'catalogue_file':'AST-STF-008.glb','original_controller':'res://scripts/service_door.gd','aperture_half_width':1.375,'aperture_height':2.815,'initial_open_fraction':0,'initial_desired_open':False}
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native));bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan={'schema':1,'baseline_commit':'affc5c807087ff87da29f3642c2d6e418241b896','latest_main_inspected':'bc731d6d6d54bb2595331ee2f4368558d4d24fda','catalogue_id_candidate':AID,'family':FAMILY,'active':False,'root_name':'Group8ArrivalsService_WIP','programme_keys':[ROOM],'native':native.name,'native_sha256':sha(native),'model_file':out.name,'model_sha256':sha(out),'new_floor_owners':0,'new_programmes':0,'new_capacity':0,'new_doors':1,'new_controllers':0,'door':door,'meshes':records,'instances':instances,'lights':lights,'supports':supports,'retained_contacts':contacts,'source_copies':source_copies,'enclosure_boundary':outline,'physical_baggage_case_silhouettes':36,'floor_y':0,'protected_opaque_D03_underside_y':11.76,'collision_policy':{q['name']:{'collide':q['collide'],'category':q['category'],'role':q['role']}for q in records},'operational_acceptance':False,'species_or_occupied_work_acceptance':False,'structural_capacity_acceptance':False,'final_art_acceptance':False,'limits':['Local handoff/holding/repacking/records architecture;no guest luggage ownership,stock,save/check-in or embarkation simulation','Original crescent reception,waiting groups,stair/lift,sealed machinery/screens and D03 cap unchanged','No exterior staff aperture or upper maintenance route modification;Group3 external service interface remains open','One new authored local standard service door;no historical room identity or permission migration','No cart-turn/biological/species/pressure/primary engineering/final art acceptance']}
(W/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print('ARRIVALS SOURCE BUILD',len(records),'meshes',len(instances),'assemblies',len(lights),'fixtures',len(source_copies),'exact original chair meshes')
