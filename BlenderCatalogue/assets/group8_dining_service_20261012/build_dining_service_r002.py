"""Three retained dining service belts: local gateway,hygiene and source fixtures; immutable retained sources untouched."""
from pathlib import Path
import bpy,bmesh,json,math,hashlib,sys
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];C=R/'BlenderCatalogue'
AID='AST-G8-DIN-002';FAMILY='group8_dining_service_20261012';ROOM='';F=61.0
assert all(a['catalogue_id']!=AID or a['family']==FAMILY for a in json.load(open(C/'catalogue_manifest.json'))['assets'])
native=W/'DiningServiceInterfaces_r002.blend';out=W/'G8_DINING_SERVICE_r002_unbatched.glb'
assert not native.exists()and not out.exists(),'Immutable revision already exists'
bpy.ops.wm.read_factory_settings(use_empty=True);sys.path.insert(0,str(C/'standards'))
import staff_materials,materials
mats=staff_materials.materials();mats.update(materials.materials())
for m in mats.values():
    for node in m.node_tree.nodes:
        if node.type=='TEX_IMAGE':node.interpolation='Closest'
mat=bpy.data.materials.new('G8_MED_IndicatorLens');mat.use_nodes=True;mat.diffuse_color=(.75,.9,.9,1)
bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=mat.diffuse_color;bs.inputs['Emission Color'].default_value=mat.diffuse_color;bs.inputs['Emission Strength'].default_value=.35;bs.inputs['Roughness'].default_value=.65
mat['meters_per_tile_uv']=[1,1];mats['light_lens']=mat
records=[];instances=[];lights=[];supports=[];contacts=[];source_copies=[];UNIT=''
FACES=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def mesh(name,verts,faces,role='staff_white_paint',category='fitting',permitted_context=None):
    name='G8D_'+UNIT+'_'+name;me=bpy.data.meshes.new(name);me.from_pydata([(x,-z,y)for x,y,z in verts],[],faces);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(mats[role]);uv=me.uv_layers.new(name='MetreScaled');scale=mats[role].get('meters_per_tile_uv',[1,1])
    for face in me.polygons:
        n=face.normal.normalized();u=Vector((1,0,0))-n*n.x if abs(n.z)>.7 else Vector((-n.y,n.x,0));u.normalize();v=n.cross(u)
        for li in face.loop_indices:
            q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.dot(u)/scale[0],q.dot(v)/scale[1])
    ob['programme_key']=ROOM;ob['unit']=UNIT;ob['category']=category
    records.append({'name':ob.name,'programme_key':ROOM,'unit':UNIT,'role':role,'category':category,'collide':category!='light_source','permitted_retained_context':permitted_context or [],'world_aabb':[min(v[0]for v in verts),max(v[0]for v in verts),min(v[1]for v in verts),max(v[1]for v in verts),min(v[2]for v in verts),max(v[2]for v in verts)]});return ob
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
    assert top>lo,'Footer top must be an absolute elevation above the retained floor'
    box(name,x,(lo+top)/2,z,w,top-lo,d,'dark_rubber');supports.append({'unit':UNIT,'kind':'floor','at':[x,lo,z],'expected_retained':'RemainingBatchStructuralFloors'})
def begin(name,kind,at):
    global UNIT;UNIT=name;instances.append({'name':name,'type':kind,'at':at})
rec=json.load(open(W/'EXACT_RETAINED_DINING_RECOVERY.json'));programmes=[];doors=[];old_contracts={};door_native=R/'BlenderCatalogue/assets/staff_threshold/source/AST-STF-008.blend';door_glb=R/'Game/assets/models/AST-STF-008.glb';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for row in rec['families']:
 ROOM=row['programme_key'];number=int(ROOM.rsplit('_',1)[1]);side=1 if number==2 else-1;z0=-250 if number==3 else-466;UNIT='D10_%02d'%number
 gate_u=43.8 if number==3 else44.4
 docs=Path(row['retained_documents']);old_contracts[ROOM]={'runtime_file':'SOL_'+ROOM+'_remaining_batch.glb','runtime_sha256':row['runtime_sha256'],'native_sha256':row['native_sha256'],'old_counts':json.load(open(docs/'COUNTS.json')),'source_routes':json.load(open(docs.parent/'qa/PLAN.json')),'source_cart_envelope':json.load(open(docs.parent/'qa/validation.json'))['pinned_cart_envelope'],'external_join_owner':'Group1/shared integration; remains held','new_capacity':0}
 def P(u,h,v):return(side*(8+u),F+h,z0+v)
 def B(name,u,h,v,du,dh,dv,role='staff_white_paint',category='fitting',permitted=None):return box(name,*P(u,h,v),du,dh,dv,role,category,permitted)
 def A(name,a,b,r=.025,role='staff_zinc'):return pipe(name,P(*a),P(*b),r,role)
 def tag(name,text,at,normal):
  o=bpy.data.objects.new('G8D_'+UNIT+'_'+name,None);bpy.context.collection.objects.link(o);q=P(*at);o.location=(q[0],-q[2],q[1]);o['programme_key']=ROOM;return o
 instances.append({'name':UNIT+'_ServiceGateway','programme_key':ROOM,'kind':'default_open_local_utility_gateway','source_existing_route':[gate_u,32.25]})
 # The protected clean-rear route remains at u44.4. The actual new scaled frame
 # occupies2.208m across u,inside a2.25m opening. Existing source routes are not rerouted.
 for lo,hi,name in[(41.5,gate_u-1.125,'InnerScreen'),(gate_u+1.125,45.605,'OuterTiePier')]:
  B(name,(lo+hi)/2,1.7,32.25,hi-lo,3.4,.30,'staff_white_paint','support',['C_service_boundary_1']if name=='OuterTiePier'else[])
  B(name+'Dado',(lo+hi)/2,.45,32.055,hi-lo,.84,.06,'staff_bluegrey_paint',permitted=['C_service_boundary_1']if name=='OuterTiePier'else[])
  B(name+'Coping',(lo+hi)/2,3.38,32.25,hi-lo,.08,.34,'champagne_metal',permitted=['C_service_boundary_1']if name=='OuterTiePier'else[])
  for u in [lo+.025,hi-.025]:supports.append({'programme_key':ROOM,'unit':UNIT,'kind':'floor','at':list(P(u,0,32.25)),'expected_retained':'RemainingBatchStructuralFloors'})
 B('GatewayHeader',gate_u,3.12,32.25,2.25,.56,.30,'staff_white_paint','support') # underside2.84,above unchanged2.82m source frame
 B('GatewayHeaderEdge',gate_u,2.87,32.07,2.25,.06,.06,'champagne_metal')
 B('InnerTieFrame',gate_u-1.133,1.7,32.25,.08,3.4,.34,'champagne_metal');B('OuterTieFrame',gate_u+1.133,1.7,32.25,.08,3.4,.34,'champagne_metal',permitted=['C_service_boundary_1'])
 at=P(gate_u,0,32.25);marker=tag('UtilityDoorDatum','', (gate_u,0,32.25),(0,0,1))
 doors.append({'programme_key':ROOM,'name':'Group8DiningUtility_%02d'%number,'persistent_id':ROOM+'_g8_local_utility_001','at':list(at),'yaw':0,'scale':[.8,1,1],'default_open':True,'exact_existing_shared_controller':'res://scripts/service_door.gd','source_frame_aperture_m':[2.4,2.54],'scaled_source_open_handle_clear_m':2.168*.8,'scaled_source_frame_outer_m':[2.76*.8,.36,2.82],'new_opening_m':[2.25,2.84],'marker':marker.name,'clinical_pressure_permission_acceptance':False})
 contacts.append({'programme_key':ROOM,'kind':'new_screen_to_exact_outer_service_boundary','at':list(P(45.599,1.7,32.25)),'direction':[side,0,0],'expected_prefix':'C_service_boundary_1'})
 # Compact real basin/cabinet,paper/soap and drain within the existing outer wall edge.
 # Minimum u45.30 preserves the exact retained0.82m cart envelope centred at44.4.
 instances.append({'name':UNIT+'_HygieneStation','programme_key':ROOM,'kind':'passive_wall_supported_handwash_construction','at':list(P(45.45,.95,27.2))})
 B('WashBackReceiver',45.59,1.08,27.2,.03,1.18,1.02,'staff_zinc','support',['C_service_boundary_1'])
 B('WashCabinetBody',45.46,.48,27.2,.28,.78,.94,'staff_white_paint');B('WashToe',45.465,.11,27.2,.27,.10,.88,'staff_bluegrey_paint')
 B('WashLeftDoor',45.31,.47,26.967,.018,.62,.445,'staff_white_paint');B('WashRightDoor',45.31,.47,27.433,.018,.62,.445,'staff_white_paint')
 for v in [26.967,27.433]:A('WashDoorPull'+str(v),(45.296,.56,v-.085),(45.296,.56,v+.085),.009,'champagne_metal')
 # Layered closed basin with an actual recessed inside and rim; no solid cap over its bowl.
 u0,u1=45.30,45.595;v0,v1=26.70,27.70;inneru0,inneru1=45.34,45.555;innerv0,innerv1=26.75,27.65
 rings=[[(u0,.91,v0),(u1,.91,v0),(u1,.91,v1),(u0,.91,v1)],[(u0,1.0,v0),(u1,1.0,v0),(u1,1.0,v1),(u0,1.0,v1)],[(inneru0,1.0,innerv0),(inneru1,1.0,innerv0),(inneru1,1.0,innerv1),(inneru0,1.0,innerv1)],[(inneru0,.925,innerv0),(inneru1,.925,innerv0),(inneru1,.925,innerv1),(inneru0,.925,innerv1)]]
 vs=[P(*v)for ring in rings for v in ring];faces=[(3,2,1,0),(12,13,14,15)]
 for r in range(3):
  for i in range(4):faces.append((r*4+i,r*4+(i+1)%4,(r+1)*4+(i+1)%4,(r+1)*4+i))
 mesh('RecessedWashBasin',vs,faces,'ivory_enamel')
 A('WashDrainVisible',(45.47,.917,27.2),(45.47,.895,27.2),.022,'staff_zinc');A('WashDrainTrap',(45.46,.89,27.2),(45.46,.77,27.2),.018,'staff_zinc');A('WashWasteToWall',(45.46,.77,27.2),(45.605,.77,27.2),.018,'staff_zinc');records[-1]['permitted_retained_context']=['C_service_boundary_1']
 A('WashTapRiser',(45.565,1.0,27.2),(45.565,1.23,27.2),.012);A('WashTapSpout',(45.565,1.23,27.2),(45.43,1.23,27.2),.012);A('WashTapOutlet',(45.43,1.23,27.2),(45.43,1.195,27.2),.012)
 B('SoapCase',45.53,1.42,26.9,.12,.23,.22,'staff_white_paint');B('SoapNozzle',45.445,1.32,26.9,.035,.045,.065,'staff_zinc')
 B('PaperCase',45.51,1.45,27.52,.16,.32,.30,'staff_bluegrey_paint');B('PaperSlot',45.424,1.35,27.52,.01,.025,.24,'dark_rubber')
 for h,v in[(.75,26.86),(.75,27.54),(1.45,26.9),(1.45,27.52)]:contacts.append({'programme_key':ROOM,'kind':'wall_supported_hygiene_mount','at':list(P(45.60,h,v)),'direction':[side,0,0],'expected_prefix':'C_service_boundary_1'})
 # Housed task sources point from a real receiver at the original wall to the basin/return.
 for label,v,h,aimuvh in[('WashTask',27.2,2.65,(45.445,1.0,27.2)),('UsedReturnTask',46.2,2.82,(42.8,.98,48.0))]:
  B(label+'BackReceiver',45.59,h+.06,v,.03,.22,.22,'staff_zinc','support',['C_service_boundary_1']);exit=Vector(P(45.275,h,v));aim=Vector(P(*aimuvh));direction=(aim-exit).normalized();back=exit-direction*.065
  pipe(label+'Bracket',P(45.595,h+.06,v),tuple(back),.02,'staff_zinc');pipe(label+'HousedShade',tuple(exit-direction*.06),tuple(exit-direction*.015),.105,'staff_bluegrey_paint',16);pipe(label+'PhysicalLens',tuple(exit-direction*.014),tuple(exit-direction*.009),.086,'light_lens',16);records[-1]['category']='light_source';records[-1]['collide']=False
  marker=bpy.data.objects.new('G8D_'+UNIT+'_'+label+'Exit',None);bpy.context.collection.objects.link(marker);marker.location=(exit.x,-exit.z,exit.y);marker['programme_key']=ROOM
  lights.append({'programme_key':ROOM,'name':marker.name,'at':list(exit),'aim':list(aim),'colour':[.88,.94,1],'energy':1.3,'range':5.0,'spot_angle':70,'physical_exit':'modeled shaded lens','operational_acceptance':False})
  contacts.append({'programme_key':ROOM,'kind':'task_fixture_mount','at':list(P(45.60,h+.06,v)),'direction':[side,0,0],'expected_prefix':'C_service_boundary_1'})
 programmes.append(ROOM)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native));bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
plan={'schema':1,'root_name':'Group8LocalDiningService_WIP','family':FAMILY,'native':native.name,'native_sha256':sha(native),'model_file':out.name,'model_sha256':sha(out),'programme_keys':programmes,'retained_contracts':old_contracts,'meshes':records,'instances':instances,'supports':supports,'retained_contacts':contacts,'lights':lights,'doors':doors,'collision_policy':{r['name']:{'collide':r['collide'],'category':r['category'],'role':r['role']}for r in records},'retained_standard_door_source':{'native':str(door_native.relative_to(R)),'native_sha256':sha(door_native),'runtime':'AST-STF-008.glb','runtime_sha256':sha(door_glb)},'new_capacity':0,'new_floor_owners':0,'new_shared_backends':0,'new_standard_controller_instances':3,'external_kitchen_clean_used_catchment_adoption':False,'source_routes_changed':False,'clinical_pressure_food_safety_species_cart_operation_engineering_final_art_acceptance':False}
(W/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print('DINING SOURCE CONSTRUCTION',len(records),'meshes',len(doors),'scaled local utility door instances',len(lights),'housed task sources')
