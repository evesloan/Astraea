"""New New triage privacy controls and hinge fittings; immutable retained sources untouched."""
from pathlib import Path
import bpy,bmesh,json,math,hashlib,sys
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];C=R/'BlenderCatalogue'
AID='AST-G8-MED-001';FAMILY='group8_medical_privacy_20261012';ROOM='D05_directory_01';F=21.0
assert all(a['catalogue_id']!=AID or a['family']==FAMILY for a in json.load(open(C/'catalogue_manifest.json'))['assets'])
native=W/'MedicalPrivacyControls_r002.blend';out=W/'G8_MEDICAL_PRIVACY_r002_unbatched.glb'
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
    name='G8M_'+UNIT+'_'+name;me=bpy.data.meshes.new(name);me.from_pydata([(x,-z,y)for x,y,z in verts],[],faces);me.update()
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
plan=json.load(open(W/'PLAN.json'));control_rows=[];hinge_rows=[];base_mesh=mesh
pose=Matrix.Identity(4)
def local_box(name,center,size,role,category='fitting',permitted=None):
    cx,cy,cz=center;sx,sy,sz=size;corners=[pose@Vector((cx+a,cy+c,cz+b))for c in[-sy/2,sy/2]for a,b in[(-sx/2,-sz/2),(sx/2,-sz/2),(sx/2,sz/2),(-sx/2,sz/2)]]
    return base_mesh(name,[tuple(p)for p in corners],FACES,role,category,permitted)
for door in plan['doors']:
    UNIT='Pod%02d'%door['source_pod_number'];instances.append({'name':UNIT,'type':'source_bound_privacy_interface','programme_child':door['programme_child']})
    at=door['at'];yaw=door['yaw'];c=math.cos(yaw);s=math.sin(yaw);pose=Matrix(((c,0,s,at[0]),(0,1,0,at[1]),(-s,0,c,at[2]),(0,0,0,1)))
    tag='TRIAGE_%02d'%door['source_pod_number']
    # Public control under the original room placard; private control on the existing sidewall,
    # reachable from outside the whole door swing without increasing the2.5m focus range.
    for side,location,dimensions,normal,support in [('Public',(-2.18,1.20,.035),(.32,.32,.08),(0,0,1),tag+'_front_service_pier'),('Private',(2.265,1.20,-2.45),(.08,.32,.32),(-1,0,0),tag+'_right_wall')]:
        local_box(side+'Backplate',location,dimensions,'champagne_metal','support',[support]);p=Vector(location);n=Vector(normal)
        # Layered physical button face, not an invented diagnostic or pressure screen.
        face=p+n*.047;size=(.235,.235,.025)if side=='Public'else(.025,.235,.235)
        local_box(side+'ButtonCase',tuple(face),size,'staff_bluegrey_paint')
        lens=face+n*.017;ls=(.135,.14,.014)if side=='Public'else(.014,.14,.135)
        local_box(side+'PhysicalButtonFace',tuple(lens),ls,'light_lens','fitting')
        marker='G8M_'+UNIT+'_'+side+'Control';ob=bpy.data.objects.new(marker,None);bpy.context.collection.objects.link(ob);world=pose@(lens+n*.010);ob.location=(world.x,-world.z,world.y)
        control_rows.append({'door_name':door['name'],'side':side,'marker':marker,'at':list(world),'normal_world':list(pose.to_3x3()@n),'size_world_local':list(ls),'source_wall':support})
        mount=pose@(p-n*.037);contacts.append({'unit':UNIT,'kind':'new_control_to_exact_existing_wall','at':list(mount),'direction':list(pose.to_3x3()@(-n)),'expected_prefix':support})
    for hand,x,support in [('Left',-1.87,tag+'_portal_left_receiver'),('Right',1.87,tag+'_portal_right_receiver')]:
        for h in [.40,2.25]:
            loc=pose@Vector((x,h,-.261));name=hand+'HingeBearing'+str(h)
            # Actual small profiled mechanical bearing attached to retained receiver.
            a=pose@Vector((x,h-.10,-.261));b=pose@Vector((x,h+.10,-.261))
            pipe(name,tuple(a),tuple(b),.046,'champagne_metal',16);records[-1]['permitted_retained_context']=[support,tag+'_privacy_leaf_'+hand.lower()]
            hinge_rows.append({'door_name':door['name'],'hand':hand,'at':list(loc),'radius':.046,'height':.20,'source_receiver':support})
            contacts.append({'unit':UNIT,'kind':'new_hinge_to_exact_existing_receiver','at':list(loc),'direction':list(pose.to_3x3()@Vector((0,0,1))),'expected_prefix':support})
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native));bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
plan.update({'catalogue_id_candidate':AID,'family':FAMILY,'native':native.name,'native_sha256':sha(native),'model_file':out.name,'model_sha256':sha(out),'meshes':records,'instances':instances,'control_targets':control_rows,'hinge_bearings':hinge_rows,'retained_contacts':contacts,'lights':[],'supports':[],'source_copies':[],'programme_keys':[ROOM],'new_controllers':0,'collision_policy':{r['name']:{'collide':r['collide'],'category':r['category'],'role':r['role']}for r in records}})
(W/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print('MEDICAL PRIVACY SOURCE',len(records),'meshes',len(control_rows),'physical controls',len(hinge_rows),'hinge fittings')
