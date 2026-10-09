#!/usr/bin/env python3
"""Original single rest fixture. Execute: blender -b --python this_file.py -- [--no-render].
No dependencies, network, linked assets, catalogue registration or Game writes.
Design coordinates are glTF/Godot metres (X right, Y up, front -Z);
convert to native Blender with (x, -z, y). Exact native meshes remain editable.
"""
import bpy, math, json, sys
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
ASSET_ID='AST-RST-QC-001'
CAT=OUT.parents[1]/'catalogue_manifest.json'
assert CAT.exists(), str(CAT)
manifest=json.loads(CAT.read_text())
for a in manifest['assets']:
    if a.get('catalogue_id',a.get('id')) == ASSET_ID:
        assert a.get('family') == 'quiet_cocoon_support_20261009', 'Catalogue ID belongs to another family'
assert OUT.name == 'quiet_cocoon_support_20261009'
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for block in list(bpy.data.materials): bpy.data.materials.remove(block)
scene=bpy.context.scene
scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=1.0
bpy.context.preferences.filepaths.save_version=0
collection=bpy.data.collections.new('AST-RST-QC-001 | editable fixture')
scene.collection.children.link(collection)
root=bpy.data.objects.new(ASSET_ID,None); collection.objects.link(root)
root['asset_id']=ASSET_ID; root['functional_family']='quiet_cocoon_support'; root['species_assignment']='unassigned'
root['biological_fit_status']='NOT_VERIFIED'; root['front_gltf']='negative Z'; root['floor_datum_m']=0.0
parts=[]
def B(v): return (v[0],-v[2],v[1])
def G(v): return (v[0],v[2],-v[1])
def mat(name, color, rough=.6,metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    b=m.node_tree.nodes.get('Principled BSDF'); b.inputs['Base Color'].default_value=(*color,1); b.inputs['Roughness'].default_value=rough; b.inputs['Metallic'].default_value=metal
    return m
wood=mat('01 | warm honey ash frame',(0.38,0.19,0.075),.57)
woodlight=mat('02 | soft amber end grain',(0.62,0.36,0.15),.64)
teal=mat('03 | lagoon teal outer acoustic petals',(0.025,0.25,0.235),.76)
teal2=mat('04 | muted seafoam petal alternation',(0.065,0.34,0.305),.77)
ivory=mat('05 | warm ivory woven liner',(0.78,0.72,0.58),.93)
ivory2=mat('06 | pale flax membrane panels',(0.68,0.65,0.52),.92)
dark=mat('07 | soft charcoal seam and feet',(0.035,0.075,0.077),.86)
brass=mat('08 | satin bronze fasteners',(0.52,0.31,0.11),.42,.48)
coral=mat('09 | service tab terracotta',(0.49,0.16,0.10),.75)
def mesh(name,verts,faces,material,role):
    me=bpy.data.meshes.new(name+' geometry'); me.from_pydata([B(v) for v in verts],[],faces); me.materials.append(material); me.update()
    ob=bpy.data.objects.new(name,me); collection.objects.link(ob); ob.parent=root
    ob['component_role']=role; ob['asset_id']=ASSET_ID
    parts.append(ob); return ob
def tube(name,points,radius,material,role,sides=8,closed=False):
    pts=[Vector(v) for v in points]; verts=[]; faces=[]
    for i,p in enumerate(pts):
        if closed: t=(pts[(i+1)%len(pts)]-pts[(i-1)%len(pts)]).normalized()
        else: t=(pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)]).normalized()
        guide=Vector((0,1,0));
        if abs(t.dot(guide))>.94: guide=Vector((0,0,1))
        u=t.cross(guide).normalized(); v=t.cross(u).normalized()
        for j in range(sides):
            a=j*2*math.pi/sides; verts.append(tuple(p+radius*(math.cos(a)*u+math.sin(a)*v)))
    count=len(pts) if closed else len(pts)-1
    for i in range(count):
        nxt=(i+1)%len(pts)
        for j in range(sides): faces.append((i*sides+j,i*sides+(j+1)%sides,nxt*sides+(j+1)%sides,nxt*sides+j))
    if not closed: faces.extend([tuple(reversed(range(sides))),tuple((len(pts)-1)*sides+j for j in range(sides))])
    return mesh(name,verts,faces,material,role)
def box(name,center,size,material,role):
    x,y,z=center; a,b,c=[v/2 for v in size]
    verts=[(x+sx*a,y+sy*b,z+sz*c) for sx,sy,sz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    return mesh(name,verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],material,role)
def marker(name,p,kind):
    o=bpy.data.objects.new(name,None);collection.objects.link(o);o.parent=root;o.location=B(p);o.empty_display_type='PLAIN_AXES';o.empty_display_size=.10;o['datum_kind']=kind; return o
# Raised side-only rocking skids and visibly triangulated suspension supports.
for sign,tag in [(-1,'L'),(1,'R')]:
    tube(f'{tag} curved continuous ground skid',[(sign*.90,.11,-1.43),(sign*.96,.075,-1.14),(sign*1.00,.075,-.55),(sign*1.00,.075,.65),(sign*.94,.11,1.37)],.065,wood,'grounded frame')
    for z in [-1.09,1.08]:
        box(f'{tag} replaceable foot {z:+.2f}',(sign*.957,.026,z),(.19,.052,.28),dark,'floor contact')
        tube(f'{tag} splayed suspension fork {z:+.2f}',[(sign*.96,.13,z),(sign*.89,.46,z-.03),(sign*.92,.78,z)],.056,wood,'support frame')
        tube(f'{tag} diagonal cradle receiver {z:+.2f}',[(sign*.98,.13,z-.24),(sign*.87,.47,z),(sign*.92,.78,z+.10)],.038,woodlight,'support frame')
# Cradle surface shaped mathematically; no rectangular mattress or ordinary bed stack.
def width(z):
    t=(z+1.24)/2.48
    return .72+.155*math.sin(math.pi*t)-.105*(t**3)
def height(xnorm,z):
    t=(z+1.24)/2.48
    return .600+.170*xnorm*xnorm+.035*(1-t)**4+.120*t**4
for sign,tag in [(-1,'L'),(1,'R')]:
    for z in [-1.09,1.08]:
        tube(f'{tag} fork to membrane bearing {z:+.2f}',[(sign*.92,.78,z),(sign*(width(z)+.038),height(1,z)+.01,z)],.052,woodlight,'actual fork to rail bearing')
zs=[-1.24+i*2.48/18 for i in range(19)]
vs=[-1+i*2/16 for i in range(17)]
verts=[]
for off in [0,-.038]:
    for z in zs:
        for v in vs: verts.append((v*width(z),height(v,z)+off,z))
N=len(zs)*len(vs); faces=[]
for j in range(len(zs)-1):
    for i in range(len(vs)-1):
        a=j*len(vs)+i; b=a+1;c=b+len(vs);d=a+len(vs)
        faces.append((a,d,c,b));faces.append((N+a,N+b,N+c,N+d))
# complete shell thickness on boundary
for j in [0,len(zs)-1]:
    for i in range(len(vs)-1):
        a=j*len(vs)+i;b=a+1;faces.append((a,b,N+b,N+a) if j==0 else (b,a,N+a,N+b))
for i in [0,len(vs)-1]:
    for j in range(len(zs)-1):
        a=j*len(vs)+i;b=a+len(vs);faces.append((b,a,N+a,N+b) if i==0 else (a,b,N+b,N+a))
mem=mesh('Concave stretched rest membrane',verts,faces,ivory,'actual rest support surface')
mem['support_height_center_m']=height(0,0);mem['not_a_biological_fit_claim']=True
mem.data.materials.append(ivory2)
for p in mem.data.polygons:
    if p.index<2*18*16 and (p.index//2//16)%6==2: p.material_index=1
# Roll-free transfer lip and side tension beads; all remain rounded mesh geometry.
for sign,tag in [(-1,'L'),(1,'R')]:
    path=[(sign*(width(z)+.038),height(sign,z)+.010,z) for z in zs]
    tube(f'{tag} curved ash membrane rail',path,.061,wood,'rest surface edge receiver')
    tube(f'{tag} ivory captive membrane welt',[(sign*width(z),height(sign,z)+.030,z) for z in zs],.014,ivory2,'readable removable liner seam',sides=6)
    for n,z in enumerate([-.98,-.53,-.06,.46,.94]):
        x=sign*width(z)
        tube(f'{tag} tension tie {n+1:02}',[(x-.018*sign,height(1,z)+.01,z),(x+.078*sign,height(1,z)+.035,z),(x+.11*sign,height(1,z)-.045,z)],.014,dark,'membrane suspension seam',sides=6)
        box(f'{tag} bronze retaining tab {n+1:02}',(x+.070*sign,height(1,z)+.04,z),(.067,.025,.085),brass,'removable membrane fastening')
for z,tag in [(-1.24,'Low unobstructed entry'),(1.24,'Raised rear cradle')]:
    tube(f'{tag} membrane piping',[(v*width(z),height(v,z)+.012,z) for v in vs],.018,ivory2,'cradle end seam',sides=6)
for n,z in enumerate([-.72,.0,.72]):
    tube(f'Continuous liner join {n+1:02}',[(v*width(z),height(v,z)+.006,z) for v in vs],.0058,ivory2,'readable support liner join',sides=4)
# Acoustic hood consists of separate thick petal panels with open seams.
# Each transverse ellipse starts at 0.43m, wraps overhead, and ends at 0.43m.
# The front-most hood starts at Z=-0.60, leaving the transfer lip open to the room.
sections=[(-.60,1.10,1.16,1.00),(-.05,1.12,1.18,1.10),(.60,1.10,1.18,1.08),(1.16,.91,1.15,.88),(1.47,.48,1.13,.54)]
def shell(z_idx,angle,offset=0):
    z,rx,cy,ry=sections[z_idx];a=math.radians(angle)
    return ((rx+offset)*math.cos(a),cy+(ry+offset)*math.sin(a),z)
angles=[-35,0,35,70,110,145,180,215]
for longitudinal in range(len(sections)-1):
    for arc in range(len(angles)-1):
        lo,hi=angles[arc]+.75,angles[arc+1]-.75
        # one thick editable mesh per petal, both surfaces visible, low-poly facets.
        av=[lo+(hi-lo)*j/3 for j in range(4)];v=[]
        for off in [.012,-.041]:
            for zi in [longitudinal,longitudinal+1]:
                for a in av: v.append(shell(zi,a,off))
        f=[]
        for j in range(3): f.extend([(j,j+1,5+j,4+j),(8+j,12+j,13+j,9+j)])
        f.extend([(0,4,12,8),(3,11,15,7),(0,8,9,1),(1,9,10,2),(2,10,11,3),(4,5,13,12),(5,6,14,13),(6,7,15,14)])
        ob=mesh(f'Hood petal {longitudinal+1:02}-{arc+1:02}',v,f,teal if (arc+longitudinal)%3 else teal2,'partial acoustic shell')
        ob.data.materials.append(ivory)
        for j,p in enumerate(ob.data.polygons):
            if j<6 and j%2==1:p.material_index=1
for zi in range(len(sections)):
    tube(f'Exposed ash hood rib {zi+1:02}',[shell(zi,-35+250*j/25,.035) for j in range(26)],.041,wood if zi!=0 else woodlight,'acoustic shell frame',sides=8)
for n,a in enumerate([-35,35,70,110,145,215]):
    tube(f'Longitudinal hood seam rail {n+1:02}',[shell(zi,a,.018) for zi in range(len(sections))],.021,wood,'readable shell seam',sides=6)
# Rear inner diffuser closes the back at the perimeter but keeps both open side/roof reveals.
rear=[]
for j in range(13):
    a=math.radians(j*180/12); rear.append((.47*math.cos(a),1.12+.51*math.sin(a),1.47))
rear.append((-.47,.79,1.47));rear.append((.47,.79,1.47))
# solid 35mm baffle
rv=rear+[(x,y,z+.035) for x,y,z in rear];nn=len(rear)
rf=[tuple(reversed(range(nn))),tuple(nn+i for i in range(nn))]
rf += [(i,(i+1)%nn,(i+1)%nn+nn,i+nn) for i in range(nn)]
mesh('Rear ivory acoustic diffuser',rv,rf,ivory,'rear acoustic baffle')
# Shell reactions grounded into rear/central skids, rather than unsupported floating shell.
for sign,tag in [(-1,'L'),(1,'R')]:
    for n,(z,x,y) in enumerate([(-.60,.944,.606),(.60,.928,.561),(1.16,.766,.644)]):
        tube(f'{tag} hood reaction strut {n+1:02}',[(sign*.98,.14,z),(sign*x,y,z)],.034,wood,'hood to ground frame')
    box(f'{tag} liner release pull',(sign*.81,.81,-1.04),(.075,.085,.15),coral,'nonfunctional service pull tab')
# Explicit datums, not visible furniture or inferred berth ownership.
marker('RestContact_Center',(0,height(0,0),0),'surface contact')
marker('RestContact_Front',(0,height(0,-1.04),-1.04),'surface contact')
marker('RestContact_Rear',(0,height(0,1.00),1.00),'surface contact')
marker('Transfer_Lip',(0,height(0,-1.24),-1.24),'surface contact')
marker('Approach_Center',(0,0,-1.94),'floor approach design datum')
marker('Floor_Origin',(0,0,0),'floor origin')
# Record native geometry and exact proposed clearance volume for independent testing.
bpy.context.view_layer.update()
allverts=[Vector(G(ob.matrix_world@v.co)) for ob in parts for v in ob.data.vertices]
lo=[min(v[i] for v in allverts) for i in range(3)];hi=[max(v[i] for v in allverts) for i in range(3)]
tri_count=sum(len(p.vertices)-2 for ob in parts for p in ob.data.polygons)
metadata={
 'schema':'astraea.single_component.v1','asset_id':ASSET_ID,'name':'Open Quiet Cocoon Rest Support','family':'quiet_cocoon_support_20261009',
 'scope':'One original rest-support fixture. No room, adoption, occupancy, biological fit or acoustic certification.',
 'coordinates':{'units':'metres','metadata_frame':'Godot/glTF Y-up','front':[0,0,-1],'blender_front':[0,1,0],'source_to_export':'(x,y,z) -> (x,z,-y)','datum':'floor origin'},
 'bounds_gltf':{'min':lo,'max':hi,'size':[hi[i]-lo[i] for i in range(3)]},
 'target_max_dimensions_xyz_m':[2.4,2.4,3.2],
 'support':{'object':'Concave stretched rest membrane','type':'concave stretched membrane with edge tension rails','x_extent_m':[-max(width(z) for z in zs),max(width(z) for z in zs)],'z_extent_m':[-1.24,1.24],'central_height_m':height(0,0),'front_center_height_m':height(0,-1.24),'rear_center_height_m':height(0,1.24),'top_function':'height(v,z)=0.600+0.170*v^2+0.035*(1-t)^4+0.120*t^4; t=(z+1.24)/2.48; x=v*(0.72+0.155*sin(pi*t)-0.105*t^3); -1<=v<=1','sample_contacts':[{'name':o.name,'position':G(o.location)} for o in collection.objects if o.type=='EMPTY' and o.get('datum_kind')=='surface contact']},
 'approach':{'direction':[0,0,1],'external_floor_rectangle_xz_m':[[-.70,-2.54],[.70,-1.50]],'internal_front_clear_prism':{'min':[-.67,.045,-1.50],'max':[.67,1.90,-1.27]},'no_front_bar':True,'transfer_opening_width_m':1.34,'contact_lip_height_m':height(0,-1.24),'note':'Open front approach and low transfer edge only; not a walk-through enclosure or certified wheelchair/species access.'},
 'proposed_room_reservation_gltf':{'min':[-1.20,0,-2.54],'max':[1.20,2.40,1.60]},
 'geometry':{'native_mesh_objects':len(parts),'triangles':tri_count,'materials':len(bpy.data.materials),'external_textures':0,'native_mesh_vertices':sum(len(ob.data.vertices) for ob in parts)},
 'species_assignment':None,'support_pose_status':'Requires actual actor/body and animation fit review','acoustics_status':'Visual absorption/diffusion intent; no simulation or measurable attenuation claimed',
 'source_read':['Game/docs/master_source/MASTER_CURRENT_APPLICATION.json','Game/docs/master_source/MASTER_FULL_CONTENT_INDEX.json chapters 6 and 8','BlenderCatalogue/standards/COORDINATE_CONTRACT.md'],
 'reference_inspected':'BlenderCatalogue/references/intimate/image(20261002-000722).png; warm ivory/wood/teal material and resort scale cues only; new fixture silhouette',
 'validation_limits':['No full Game import or tests','No in-engine collision, actor, animation, acoustic, hardware or final art acceptance','No structural engineering or load rating','No species mapping or berth capacity changes','Component preview lighting only; no lamp nodes exported'],
 'authoring':'Original deterministic Python mesh recipe; native separate meshes/materials; no downloaded assets, paid services or generated textures'
}
assert all(metadata['bounds_gltf']['size'][i] <= metadata['target_max_dimensions_xyz_m'][i]+1e-6 for i in range(3)), metadata['bounds_gltf']
assert lo[1] >= -1e-6
(OUT/'component_metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
# Export only fixture meshes, root and explicit datums, excluding preview setup.
bpy.ops.object.select_all(action='DESELECT')
for o in collection.objects:o.select_set(True)
bpy.context.view_layer.objects.active=root
bpy.ops.export_scene.gltf(filepath=str(OUT/'AST-RST-QC-001.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False,export_animations=False,export_materials='EXPORT')
# Blender-native studio collection stays separate and hidden in viewport by default.
studio=bpy.data.collections.new('Preview only | excluded from GLB');scene.collection.children.link(studio)
def move_studio(o):
    for c in list(o.users_collection):c.objects.unlink(o)
    studio.objects.link(o)
def point_at(o,p):o.rotation_euler=(Vector(B(p))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=B((4.6,3.1,-5.7)));camera=bpy.context.object;move_studio(camera);camera.name='Preview_Camera';camera.data.type='ORTHO';camera.data.ortho_scale=4.95;point_at(camera,(0,1.05,-.05));scene.camera=camera
for name,p,power,size in [('Key',(-3,5,-4),680,4),('Fill',(4,2.8,-1),330,3),('Rim',(1,4,4),600,3)]:
    bpy.ops.object.light_add(type='AREA',location=B(p));o=bpy.context.object;move_studio(o);o.name='Preview_'+name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;point_at(o,(0,1,0))
scene.world.color=(.15,.15,.15)
scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=False
scene.render.resolution_x=900;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'
# Neutral ground preview mesh is not part of the asset or exporter.
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.005));floor=bpy.context.object;move_studio(floor);floor.name='Preview_Ground';floor.data.materials.append(mat('Preview sand studio',(0.34,.31,.265),.92))
bpy.ops.object.select_all(action='DESELECT');mem.select_set(True);bpy.context.view_layer.objects.active=mem
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'AST-RST-QC-001.blend'),compress=True)
if '--no-render' not in sys.argv:
    scene.render.filepath=str(OUT/'preview_front_threequarter.png');bpy.ops.render.render(write_still=True)
print('COMPONENT_SUMMARY '+json.dumps(metadata['bounds_gltf'])+' triangles='+str(tri_count))
