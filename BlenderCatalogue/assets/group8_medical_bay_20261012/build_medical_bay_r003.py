"""Medical Bay: four native-derived clinical privacy pairs and fitted controls; immutable retained sources untouched."""
from pathlib import Path
import bpy,bmesh,json,math,hashlib,sys
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];C=R/'BlenderCatalogue'
AID='AST-G8-MED-002';FAMILY='group8_medical_bay_20261012';ROOM='D05_directory_02';F=21.0
assert all(a['catalogue_id']!=AID or a['family']==FAMILY for a in json.load(open(C/'catalogue_manifest.json'))['assets'])
native=W/'MedicalBayInterfaces_r002.blend';out=W/'G8_MEDICAL_BAY_r002_unbatched.glb'
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
    name='G8B_'+UNIT+'_'+name;me=bpy.data.meshes.new(name);me.from_pydata([(x,-z,y)for x,y,z in verts],[],faces);me.update()
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
recovery=json.load(open(W/'EXACT_RETAINED_MEDICAL_BAY_RECOVERY.json'))
leaf_rec=json.load(open(W.parent/'group8_medical_privacy_20261012/EXACT_RETAINED_SOURCE_RECOVERY.json'))
leaf_native=Path(leaf_rec['native']);sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert sha(leaf_native)==leaf_rec['native_sha256']
doors=[];controls=[];hinges=[]
source_names=['TRIAGE_01_privacy_leaf_'+s for s in ['left','right']]
source_names+=['TRIAGE_01_leaf_'+s+'_'+part for s in ['left','right'] for part in ['upper_field','kick_receiver','bearing_0.42','bearing_1.93']]
source_door_center=Vector((11.5,14,0))
for number,x,z,yaw in [(1,25.5,-418,math.pi/2),(2,30.5,-418,-math.pi/2),(3,25.5,-410,math.pi/2),(4,30.5,-410,-math.pi/2)]:
    UNIT='Surgery%02d'%number;child=ROOM+'_surgical_suite_%02d'%number
    at=Vector((x,F,z));c=math.cos(yaw);s=math.sin(yaw)
    pose=Matrix(((c,0,s,x),(0,1,0,F),(-s,0,c,z),(0,0,0,1)))
    name='Group8MedicalBayPrivacy%02d'%number
    row={'name':name,'persistent_id':'D05_surgical_g8_privacy_%02d'%number,'programme_child':child,'source_pod_number':number,'at':list(at),'yaw':yaw,'members':{'left':[],'right':[]},'default_open':True,'existing_portal_clear_m':[3.6,2.65],'source_hinge_local_xz':[[-1.87,-.261],[1.87,-.261]],'geometry_origin':'New rigid copies of exact retained TRIAGE01 leaf source;original surgical architecture and triage meshes remain unchanged'}
    with bpy.data.libraries.load(str(leaf_native),link=False) as (src,dst):
        assert all(n in src.objects for n in source_names);dst.objects=list(source_names)
    originals=[o for o in dst.objects if o]
    for o in originals:bpy.context.collection.objects.link(o)
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
    for original in originals:
        side='left' if 'left' in original.name else 'right';source_name=original.name
        ev=original.evaluated_get(dg);me=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=dg)
        suffix=source_name.removeprefix('TRIAGE_01_');new_name='G8B_'+UNIT+'_'+suffix
        native_to_godot=Matrix(((1,0,0),(0,0,1),(0,-1,0)))
        normal_matrix=native_to_godot.transposed()@pose.to_3x3()@native_to_godot@ev.matrix_world.to_3x3().inverted().transposed()
        exact_normals=[(normal_matrix@n.vector).normalized()for n in me.corner_normals]
        for v in me.vertices:
            native_world=ev.matrix_world@v.co;local=native_world-source_door_center
            g=pose@Vector((local.x,local.z,-local.y));v.co=(g.x,-g.z,g.y)
        me.update()
        for face in me.polygons:face.use_smooth=True
        me.normals_split_custom_set(exact_normals)
        ob=bpy.data.objects.new(new_name,me);bpy.context.collection.objects.link(ob)
        ob['programme_key']=ROOM;ob['unit']=UNIT;ob['programme_child']=child
        ob['source_copy_native_sha256']=leaf_rec['native_sha256'];ob['source_copy_original_name']=source_name;ob['category']='native_leaf_copy'
        me.calc_loop_triangles();vs=[(v.co.x,v.co.z,-v.co.y) for v in me.vertices]
        a=[min(v[0] for v in vs),max(v[0] for v in vs),min(v[1] for v in vs),max(v[1] for v in vs),min(v[2] for v in vs),max(v[2] for v in vs)]
        records.append({'name':ob.name,'programme_key':ROOM,'unit':UNIT,'role':'exact_retained_clinical_leaf_copy','category':'moving_leaf','collide':True,'permitted_retained_context':[],'world_aabb':a})
        source_copies.append({'new_name':ob.name,'original_name':source_name,'original_native_sha256':leaf_rec['native_sha256'],'rigid_world_transform':sum([list(r) for r in pose],[]),'source_uv_material_geometry_preserved':True,'actual_evaluated_triangles':len(me.loop_triangles)})
        row['members'][side].append(ob.name.replace('.','_'));bpy.data.objects.remove(original,do_unlink=True)
    def LB(label,center,size,role='staff_white_paint',category='fitting',permitted=None):
        cx,cy,cz=center;sx,sy,sz=size
        v=[pose@Vector((cx+a,cy+b,cz+d)) for b in [-sy/2,sy/2] for a,d in [(-sx/2,-sz/2),(sx/2,-sz/2),(sx/2,sz/2),(-sx/2,sz/2)]]
        return mesh(label,[tuple(q) for q in v],FACES,role,category,permitted)
    for side,xx in [('Left',-1.90),('Right',1.90)]:
        source_pier='A_Surgery%d_portal_pier%d'%(number,1 if (side=='Left')==(yaw>0) else 0)
        receiver=LB(side+'Receiver',(xx,1.315,-.2015),(.20,2.63,.207),'champagne_metal','support',[source_pier])
        row.setdefault('receivers',{})[side.lower()]=receiver.name
        for h in [.40,2.25]:
            axis=-1.87 if side=='Left' else 1.87
            a=pose@Vector((axis,h-.10,-.261));b=pose@Vector((axis,h+.10,-.261))
            pipe(side+'HingeBearing'+str(h),tuple(a),tuple(b),.046,'champagne_metal',16)
            hinges.append({'door_name':name,'side':side.lower(),'name':records[-1]['name'],'at':list(pose@Vector((axis,h,-.261))),'radius':.046,'height':.20,'receiver':receiver.name})
        contact=pose@Vector((xx,1.35,-.10))
        contacts.append({'unit':UNIT,'programme_child':child,'kind':'new_receiver_to_existing_surgical_pier','at':list(contact),'direction':list(pose.to_3x3()@Vector((0,0,1))),'expected_prefix':source_pier})
        for dx in [-.055,.055]:supports.append({'unit':UNIT,'programme_child':child,'kind':'floor','at':list(pose@Vector((xx+dx,0,-.25))),'expected_retained':'RemainingBatchStructuralFloors'})
    source_pier='A_Surgery%d_portal_pier%d'%(number,1 if yaw>0 else 0)
    for side,zz,normal in [('Public',.135,Vector((0,0,1))),('Private',-.135,Vector((0,0,-1)))]:
        loc=Vector((-2.18,1.20,zz))
        LB(side+'ControlBack',tuple(loc),(.32,.32,.08),'champagne_metal','support',[source_pier])
        face=loc+normal*.047;LB(side+'ControlCase',tuple(face),(.235,.235,.025),'staff_bluegrey_paint')
        lens=face+normal*.017;LB(side+'ControlLens',tuple(lens),(.135,.14,.014),'light_lens')
        marker=bpy.data.objects.new('G8B_'+UNIT+'_'+side+'Control',None);bpy.context.collection.objects.link(marker)
        v=pose@(lens+normal*.010);marker.location=(v.x,-v.z,v.y);marker['programme_key']=ROOM
        controls.append({'door_name':name,'side':side,'marker':marker.name,'at':list(v),'normal':list(pose.to_3x3()@normal),'size_door_local':[.135,.14,.014],'source_pier':source_pier})
        contact=pose@(loc-normal*.037)
        contacts.append({'unit':UNIT,'kind':'physical_control_to_exact_surgical_pier','at':list(contact),'direction':list(pose.to_3x3()@(-normal)),'expected_prefix':source_pier})
    doors.append(row);instances.append({'name':UNIT,'type':'local_surgical_privacy_fitting','programme_child':child,'source_original_geometry_changes':0})
entry=next(r for r in json.load(open(R/'Game/data/architecture/REMAINING_BATCH_SECTIONS.json'))['sections'] if r['key']==ROOM)
bay_bounds={r['name']:r['world_aabb'] for r in json.load(open(W/'ACTUAL_MEDICAL_BAY_NATIVE_BOUNDS.json'))}
for original in entry['fixture_lights']:
    n=original['name'];a=bay_bounds['A_'+n+'_lens'];at=original['world_xyz']
    assert a[0]-.001<at[0]<a[1]+.001 and a[4]-.001<at[2]<a[5]+.001 and .015<a[2]-at[1]<.03
    lights.append({'name':'G8B_'+n+'_TaskSource','original_generic_name':n+'_PhysicalSource','physical_lens_name':'A_'+n+'_lens','at':at,'aim':[at[0],F+.8,at[2]],'colour':original['color'],'range':6.0,'energy':1.2,'angle':70,'existing_housing_source_exit_offset_m':a[2]-at[1],'fixture_geometry_added':False,'clinical_or_pressure_operation_accepted':False})
assert len(lights)==39 and len(source_copies)==40
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native))
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
contract=json.load(open(Path(recovery['root'])/'contract.json'))
plan={'schema':1,'root_name':'Group8MedicalBayInterfaces_WIP','programme_key':ROOM,'family':FAMILY,'native':native.name,'native_sha256':sha(native),'model_file':out.name,'model_sha256':sha(out),'original_native_sha256':recovery['native_sha256'],'original_runtime_file':'SOL_D05_directory_02_remaining_batch.glb','original_runtime_sha256':recovery['runtime_sha256'],'original_children':contract['children'],'original_routes':contract['routes'],'meshes':records,'instances':instances,'source_copies':source_copies,'doors':doors,'control_targets':controls,'hinge_bearings':hinges,'supports':supports,'retained_contacts':contacts,'lights':lights,'collision_policy':{r['name']:{'collide':r['collide'],'category':r['category'],'role':r['role']} for r in records},'source_leaf_native_sha256':leaf_rec['native_sha256'],'source_leaf_originals_modified':False,'new_door_instances':4,'new_shared_backends':0,'new_floor_owners':0,'new_capacity':0,'retained_general_bed_ids':20,'retained_surgical_suite_ids':4,'new_physical_light_fixtures':0,'directional_adaptations_of_existing_housings':39,'clinical_pressure_species_cart_engineering_final_art_accepted':False}
(W/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
print('MEDICAL BAY SOURCE',len(records),'meshes',len(source_copies),'exact source leaf copies',len(lights),'existing housings')
