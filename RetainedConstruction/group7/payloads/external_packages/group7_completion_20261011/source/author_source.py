"""Editable Group 7 enclosure and garden courts; immutable retained inputs."""
import bpy,bmesh,json,math,hashlib,random
import numpy as np
from pathlib import Path
import gzip
from mathutils import Vector

P=Path(__file__).resolve().parents[1];R=P.parents[1]
assert not (P/'source/natives/G7_Completion_r001.blend').exists() and not (P/'source/natives/G7_Completion_r001.blend.gz').exists(), 'Never overwrite a retained native revision'
plan=json.load(open(P/'docs/PLAN.json'))
for d in ['source/natives','exports','qa']:(P/d).mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
materials={};parts=[];records=[];omitted=[];families=[];lights=[]
def mat(role,texture,color,alpha=1):
    m=bpy.data.materials.new('G7C3_'+role);m.diffuse_color=(*color,alpha);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,alpha);bs.inputs['Roughness'].default_value=.76
    if texture:
        im=bpy.data.images.load(str(R/'BlenderCatalogue/materials'/texture),check_existing=True)
        t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=im;t.interpolation='Closest';m.node_tree.links.new(t.outputs['Color'],bs.inputs['Base Color'])
    if alpha<1:bs.inputs['Alpha'].default_value=alpha;bs.inputs['Roughness'].default_value=.2;m.surface_render_method='DITHERED'
    materials[role]=m
for role,tex,col in [('shell','ivory_enamel.png',(.72,.73,.70)),('metal','champagne_metal.png',(.54,.49,.36)),('roof','staff/staff_bluegrey_paint.png',(.31,.41,.46)),('stone','warm_stone.png',(.56,.53,.44)),('soil','botanical/botanical_soil.png',(.18,.14,.10)),('bark','botanical/botanical_bark.png',(.32,.24,.16)),('jade','botanical/botanical_leaf_jade.png',(.19,.39,.22)),('sage','botanical/botanical_leaf_sage.png',(.36,.48,.28))]:
    if not (R/'BlenderCatalogue/materials'/tex).exists():tex='warm_stone.png'
    mat(role,tex,col)
mat('glass',None,(.42,.65,.69),.28);mat('opal',None,(1,.91,.69))
materials['opal'].node_tree.nodes.get('Principled BSDF').inputs['Emission Color'].default_value=(1,.86,.6,1)
materials['opal'].node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=1.4
census_file=P/'qa/RETAINED_RUNTIME_CENSUS.json'
census=[q for q in json.loads(census_file.read_bytes() if census_file.exists() else gzip.decompress(census_file.with_suffix('.json.gz').read_bytes()))['meshes'] if 'All18DeckStructuralDatums_NOT_FINISHED_ARCHITECTURE'not in q['path'] and 'CompiledStructuralFloors_NotFinishedRooms'not in q['path']]
retained_min=np.array([row['minimum'] for row in census]);retained_max=np.array([row['maximum'] for row in census])
non_shoulder=np.array(['TheaterWestUpperHull' not in row['path'] for row in census])
screen_cache={}
def occupied(v,ignore_shoulder=False):
    a=np.array(v);mn=a.min(axis=0);mx=a.max(axis=0)
    key=(int(mn[0]//24),int(mn[1]//12),int(mn[2]//24))
    if key not in screen_cache:
        cell_min=np.array(key)*[24,12,24]-12;cell_max=cell_min+[60,48,60]
        screen_cache[key]=np.where(np.all(retained_max>cell_min,axis=1)&np.all(retained_min<cell_max,axis=1)&non_shoulder)[0]
    idx=screen_cache[key];mask=np.all(np.minimum(mx,retained_max[idx])-np.maximum(mn,retained_min[idx])>1e-5,axis=1)
    return [census[int(i)]['path']for i in idx[mask]]
def mesh(name,v,faces,role,category,cell,details=None):
    me=bpy.data.meshes.new(name);me.from_pydata([(x,-z,y)for x,y,z in v],[],faces);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    assert all(e.is_manifold for e in bm.edges),name
    assert abs(bm.calc_volume())>1e-9,name
    bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(materials[role]);uv=me.uv_layers.new(name='MetreScaled')
    for face in me.polygons:
        n=face.normal;u=Vector((0,1,0))if abs(n.x)>.8 else Vector((1,0,0));w=n.cross(u)
        for k in face.loop_indices:q=me.vertices[me.loops[k].vertex_index].co;uv.data[k].uv=(q.dot(u),q.dot(w))
    ob['contact_category']=category;ob['group7_cell']=cell;ob['immutable_originals_preserved']=True
    me.calc_loop_triangles();row={'name':name,'vertices_world_xyz':v,'faces':[list(f)for f in faces],'role':role,'category':category,'cell':cell,'triangles':len(me.loop_triangles)}
    if details:row.update(details)
    records.append(row);parts.append(ob);return ob
def prism(name,poly,y0,y1,role,category,cell):
    n=len(poly);return mesh(name,[(x,y,z)for y in [y0,y1]for x,z in poly],[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)],role,category,cell)
def rect(name,x0,x1,z0,z1,y0,y1,role,category,cell):return prism(name,[(x0,z0),(x1,z0),(x1,z1),(x0,z1)],y0,y1,role,category,cell)
def facet(name,tri,a,b,role,category,cell,screen=True):
    q=[Vector(x)for x in tri];n=(q[1]-q[0]).cross(q[2]-q[0]).normalized();c=sum(q,Vector())/3
    if n.dot(Vector((-c.x,0,-c.z)))<0:n=-n
    h=Vector((n.x,0,n.z));assert h.length_squared>.01
    delta=h/h.length_squared;v=[list(p+delta*d)for d in [a,b]for p in q]
    hits=occupied(v,True)if screen else []
    if hits:omitted.append({'name':name,'candidate_vertices':v,'candidates':hits,'reason':'Conservative retained mesh bounds; source field held, not silently intersected.'});return
    return mesh(name,v,[(2,1,0),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],role,category,cell,{'inward_normal':list(n),'normal_interval_m':[a,b]})
def quad(name,q,a,b,role,category,cell,screen=True):
    facet(name+'_a',[q[0],q[1],q[2]],a,b,role,category,cell,screen);facet(name+'_b',[q[0],q[2],q[3]],a,b,role,category,cell,screen)
def lerp(a,b,t):return list(Vector(a).lerp(Vector(b),t))
def subfield(q,u0,u1,v0,v1):
    def p(u,v):return lerp(lerp(q[0],q[1],u),lerp(q[3],q[2],u),v)
    return [p(u0,v0),p(u1,v0),p(u1,v1),p(u0,v1)]
for panel in plan['panels']:
    q=panel['quad'];name=panel['id'];cell='Body_'+str(panel['side'])+'_'+str(int((panel['z'][0]+510)//120)).zfill(2)
    # Two glass fields with deep continuous mullions, local sills and true-normal frames.
    dy=min(.18/(panel['y'][1]-panel['y'][0]),.15);du=.03
    for suffix,field,role in [('Sill',subfield(q,0,1,0,dy),'shell'),('Pier',subfield(q,0,du,dy,1),'metal'),('Glass',subfield(q,du,1,dy,1),'glass')]:
        quad(name+'_'+suffix,field,0,.18,role,'solid_skin',cell)
    for suffix,field in [('Sill',subfield(q,0,1,0,dy)),('Pier',subfield(q,0,du,dy,1))]:quad(name+'_'+suffix+'_Receiver',field,.18,.4,'metal','solid_frame',cell)
    if panel['y'][1]==106.5:quad(name+'_RoofHead',subfield(q,0,1,1-dy,1),.18,.4,'metal','solid_frame',cell)
# Actual opaque top closure; no slabs in any source-owned roof/crown/route holes.
for i,tri in enumerate(plan['roof_triangles']):
    cx=sum(q[0]for q in tri)/3;cz=sum(q[1]for q in tri)/3
    prism('G7C3_Roof_'+str(i),tri,106.5,106.78,'roof','solid_roof','Roof_'+str(int((cz+510)//120)).zfill(2))
# Raised terminal necks preserve the retained D18 floor and 4 m occupied clear air.
for term in plan['terminals']:
    name=term['id'];cell=name+'_Closure';s=term['sign'];z0,z1=sorted([s*510,s*531.5]);nx=6.8
    for side in [-1,1]:
        q=[[side*nx,106.5,z0],[side*nx,106.5,z1],[side*nx,110.5,z1],[side*nx,110.5,z0]]
        quad(name+'_RaisedNeck_'+str(side),q,0,.18,'glass','solid_skin',cell,False)
        quad(name+'_RaisedNeckHead_'+str(side),subfield(q,0,1,.95,1),.18,.4,'metal','solid_frame',cell,False)
    q=[[-nx,106.5,s*531.5],[nx,106.5,s*531.5],[nx,110.5,s*531.5],[-nx,110.5,s*531.5]]
    quad(name+'_RaisedEnd',q,0,.18,'glass','solid_skin',cell,False)
    # Flat underside meets the wall heads; shallow faceted crown ribs rise above it.
    rect(name+'_NeckRoof',-nx,nx,z0,z1,110.5,110.78,'shell','solid_roof',cell)
    for j,z in enumerate([s*v for v in [510,517.5,524.5,531.5]]):
        rect(name+'_RoofBeam_'+str(j),-nx,nx,z-.07,z+.07,110.30,110.5,'metal','solid_frame',cell)
    rect(name+'_BodyHeader',-nx,nx,s*510-.07,s*510+.07,110.30,110.5,'metal','solid_frame',cell)
    # Framed low glare lights mount at actual high neck receiver points.
    for j,z in enumerate([s*517.5,s*525]):
        rect(name+'_LampHousing_'+str(j),-.16,.16,z-.19,z+.19,110.14,110.3,'metal','solid_frame',cell)
        rect(name+'_LampLens_'+str(j),-.13,.13,z-.16,z+.16,110.12,110.14,'opal','visual_lens',cell)
        lights.append({'id':name+'_Lamp_'+str(j),'position':[0,110.10,z],'direction':[0,-1,0],'range':7,'energy':1.3,'angle':62,'color':[1,.93,.79],'source_hardware':name+'_LampHousing_'+str(j)})
# Compact courts vary by principal band and use retained botanical/furniture families.
for pocket in plan['botanical_pockets']:
    x,y,z=pocket['origin'];cell=pocket['id'];deck=pocket['deck'];name=cell
    # Shaped planter against the outer edge; open inner route and two approaches remain.
    side=-1 if x<0 else 1;px=x+side*.66
    poly=[(px-.55,z-1.6),(px+.55,z-1.6),(px+.67,z-1.28),(px+.67,z+1.28),(px+.55,z+1.6),(px-.55,z+1.6),(px-.67,z+1.28),(px-.67,z-1.28)]
    prism(name+'_PlanterFoot',poly,y,y+.12,'metal','solid_frame',cell)
    prism(name+'_Planter',poly,y+.12,y+.5,'stone','solid_furniture',cell)
    prism(name+'_Soil',[(px+(a-px)*.86,z+(b-z)*.94)for a,b in poly],y+.5,y+.53,'soil','solid_furniture',cell)
    for index,(file,at,yaw)in enumerate([('AST-BOT-002.glb',[px,y+.53,z-.8],.5),('AST-BOT-003.glb',[px,y+.53,z+.8],1.4),('AST-FUR-001_day_window_bench.glb',[x-side*.65,y,z],math.pi/2)]):
        before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(R/'Game/assets/models'/file));added=list(set(bpy.data.objects)-before)
        root=bpy.data.objects.new(name+'_Original_'+str(index),None);bpy.context.collection.objects.link(root);root.location=(at[0],-at[2],at[1]);root.rotation_euler.z=yaw
        for ob in added:
            if ob.parent is None:ob.parent=root
            ob['group7_cell']=cell;ob['contact_category']='solid_furniture'if index==2 else'visual_foliage';ob['retained_original_family']=file
        bpy.context.view_layer.update()
        families.append({'cell':cell,'file':file,'sha256':hashlib.sha256((R/'Game/assets/models'/file).read_bytes()).hexdigest(),'rigid_origin':at,'yaw':yaw,'scale':[1,1,1],'mesh_nodes':[ob.name for ob in added if ob.type=='MESH']})
    lx=x-side*.5;lz=z+2.3
    rect(name+'_LampFoot',lx-.07,lx+.07,lz-.07,lz+.07,y,y+.1,'metal','solid_frame',cell)
    rect(name+'_LampPost',lx-.035,lx+.035,lz-.035,lz+.035,y+.1,y+1.95,'metal','solid_frame',cell)
    rect(name+'_LampHead',lx-.15,lx+.15,lz-.15,lz+.15,y+1.95,y+2.15,'metal','solid_frame',cell)
    rect(name+'_Opal',lx-.12,lx+.12,lz-.12,lz+.12,y+1.96,y+2.1,'opal','visual_lens',cell)
    lights.append({'id':name+'_Light','position':[lx,y+1.94,lz],'direction':[0,-1,0],'range':5,'energy':1.1,'angle':65,'color':[1,.93,.79],'source_hardware':name+'_LampHead'})
for row in lights:
    data=bpy.data.lights.new(row['id'],'SPOT');data.energy=220;data.color=row['color'];data.spot_size=math.radians(row['angle']*2);data.use_custom_distance=True;data.cutoff_distance=row['range']
    ob=bpy.data.objects.new(row['id'],data);bpy.context.collection.objects.link(ob);ob.location=(row['position'][0],-row['position'][2],row['position'][1]);ob['fixture_source']=row['source_hardware']
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
bpy.ops.file.pack_all();native=P/'source/natives/G7_Completion_r001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native))
(P/'qa/SOURCE_GEOMETRY.json').write_text(json.dumps(records,separators=(',',':'))+'\n')
(P/'qa/OMITTED_SOURCE_FIELDS.json').write_text(json.dumps(omitted,indent=2)+'\n')
(P/'docs/ORIGINAL_FAMILY_BINDINGS.json').write_text(json.dumps(families,indent=2)+'\n')
(P/'docs/LIGHT_INTERFACES.json').write_text(json.dumps(lights,indent=2)+'\n')
print('GROUP7_SOURCE_AUTHORED',len(records),'parts',len(omitted),'held fields',len(families),'rigid families')
