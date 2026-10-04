"""Original script-assisted shaped botanical components; Blender 4.3.2.
Run: blender -b -t 2 --python source/build_botanical_understory.py
All surfaces are explicitly shaped meshes, all arrangements deterministic.
"""
import bpy, bmesh, math, json, hashlib, importlib.util
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1]; CAT=BASE.parents[1]
spec=importlib.util.spec_from_file_location('botanical_materials',CAT/'standards/botanical_materials.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);MATS=mod.materials()
PARTS=[];SUPPORTS=[]

def reset():
    global PARTS,SUPPORTS
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    PARTS=[];SUPPORTS=[]
    sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
    sc['scope']='Blender component QA only. Original independent botanical library, no recovered game geometry.'

def mesh(name,verts,faces,role,kind='closed_support',uvs=None):
    me=bpy.data.meshes.new(name+'_editable_mesh');me.from_pydata(verts,[],faces);me.update()
    if kind=='closed_support':
        bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(MATS[role]);ob['material_role']=role;ob['surface_kind']=kind
    ob['provenance']='Original script-assisted intentionally shaped mesh; no asset extraction'
    layer=me.uv_layers.new(name='botanical_metric_uv');scale=tuple(MATS[role].get('meters_per_tile_uv',(.4,.4)))
    for face in me.polygons:
        axis=max(range(3),key=lambda k:abs(face.normal[k]));axes=[k for k in range(3) if k!=axis]
        for li in face.loop_indices:
            vi=me.loops[li].vertex_index;v=me.vertices[vi].co
            layer.data[li].uv=uvs[vi] if uvs else(v[axes[0]]/scale[0],v[axes[1]]/scale[1])
    PARTS.append(ob);return ob

def tube(name,points,radii,role='botanical_bark',sides=7,flat_rings=False):
    pp=[Vector(p) for p in points];verts=[];faces=[]
    for i,(p,r) in enumerate(zip(pp,radii)):
        if flat_rings:u,v=Vector((1,0,0)),Vector((0,1,0))
        else:
            tangent=(pp[min(i+1,len(pp)-1)]-pp[max(i-1,0)]).normalized()
            seed=Vector((0,0,1)) if abs(tangent.z)<.85 else Vector((1,0,0));u=tangent.cross(seed).normalized();v=tangent.cross(u)
        verts.extend(tuple(p+r*(u*math.cos(2*math.pi*j/sides)+v*math.sin(2*math.pi*j/sides))) for j in range(sides))
    for k in range(len(pp)-1):faces.extend((k*sides+j,k*sides+(j+1)%sides,(k+1)*sides+(j+1)%sides,(k+1)*sides+j) for j in range(sides))
    faces.extend([tuple(reversed(range(sides))),tuple((len(pp)-1)*sides+j for j in range(sides))])
    ob=mesh(name,verts,faces,role)
    # UVs use distance round each ring and cumulative stem length, caps planar.
    me=ob.data;uv=me.uv_layers.active;scale=tuple(MATS[role].get('meters_per_tile_uv',(.4,.4)));lengths=[0]
    for a,b in zip(pp,pp[1:]):lengths.append(lengths[-1]+(b-a).length)
    side_count=(len(pp)-1)*sides
    for p in me.polygons:
        if p.index>=side_count:continue
        edge=p.index%sides
        for li in p.loop_indices:
            k,j=divmod(me.loops[li].vertex_index,sides);j=sides if edge==sides-1 and j==0 else j
            uv.data[li].uv=(2*math.pi*radii[k]*j/sides/scale[0],lengths[k]/scale[1])
    ob['centerline_m']=json.dumps(points);ob['radii_m']=json.dumps(radii);return ob

def leaf(name,base,angle,length,width,rise,arch,cup,role,twist=0,kind='broad_leaf',rib=True):
    """Ovate/strap outline with five curved cross-section lanes and single tips."""
    direction=Vector((math.cos(angle),math.sin(angle),0));side=Vector((-math.sin(angle),math.cos(angle),0));b=Vector(base)
    def center(t):return b+direction*(length*t)+Vector((0,0,rise*t+arch*math.sin(math.pi*t)-.020*t*t*t))
    def point(t,u):
        profile=math.sin(math.pi*t)**(.78 if kind=='broad_leaf' else .95)*(1.15-.38*t)
        w=width*.5*profile
        return center(t)+side*(u*w)+Vector((0,0,cup*u*u*math.sin(math.pi*t)+twist*u*t*math.sin(math.pi*t)))
    ts=[.12,.29,.49,.69,.87];us=[-1,-.55,0,.55,1]
    vertices=[tuple(b)];uvs=[(.5,0)];rows=[]
    for t in ts:
        rows.append(list(range(len(vertices),len(vertices)+5)))
        for u in us:vertices.append(tuple(point(t,u)));uvs.append((.5+u*.5,t))
    tip=len(vertices);vertices.append(tuple(center(1)));uvs.append((.5,1));faces=[]
    # Ordering gives outward/top normals across all lanes.
    for j in range(4):faces.append((0,rows[0][j+1],rows[0][j]))
    for a,c in zip(rows,rows[1:]):
        for j in range(4):faces.append((a[j],a[j+1],c[j+1],c[j]))
    for j in range(4):faces.append((rows[-1][j],rows[-1][j+1],tip))
    # Parameter order is length then lateral: direction cross side is +Z.
    faces=[tuple(reversed(f)) for f in faces]
    ob=mesh(name,vertices,faces,role,'open_thin_leaf',uvs)
    ob['leaf_base_m']=json.dumps(base);ob['leaf_length_m']=length;ob['leaf_width_m']=width;ob['double_sided_treatment']='OPAQUE two-sided material, single shaped surface; open perimeter intentionally retained'
    if rib:
        ps=[tuple(center(t)+Vector((0,0,.001))) for t in[0,.18,.4,.62,.83,.95]]
        tube(name+'_raised_midrib',ps,[.0038,.0035,.0027,.0020,.0012,.0006],'botanical_leaf_olive',5)
    return ob

def record_joint(child,parent,child_point,parent_point,radius,kind):
    SUPPORTS.append({'child':child,'parent':parent,'child_attachment_m':list(child_point),'parent_centerline_attachment_m':list(parent_point),'parent_radius_m':radius,'attachment_center_distance_m':math.dist(child_point,parent_point),'joint_type':kind,'required':'Child attachment is on parent centerline; closed overlapping caps for supports or rooted leaf surface'})

def understory():
    stems={
      'main_crown':([(0,0,0),(.004,0,.12),(.011,.004,.30),(.014,.008,.48),(.004,.015,.66),(-.005,.018,.755)],[.032,.029,.023,.018,.012,.006]),
      'left_shoot':([(.004,0,.12),(-.025,.008,.22),(-.071,.021,.37),(-.10,.03,.53),(-.105,.034,.655)],[.020,.017,.013,.010,.004]),
      'rear_shoot':([(.011,.004,.30),(.041,.052,.40),(.071,.091,.53),(.085,.103,.665)],[.015,.012,.009,.004])}
    for name,(points,radii) in stems.items():tube(name,points,radii,sides=8,flat_rings=True)
    record_joint('left_shoot','main_crown',stems['left_shoot'][0][0],stems['main_crown'][0][1],.029,'branch_overlap')
    record_joint('rear_shoot','main_crown',stems['rear_shoot'][0][0],stems['main_crown'][0][2],.023,'branch_overlap')
    # Authored azimuths alternate height, width, pitch, and cup; no procedural randomness.
    layout=[
      ('main_crown',(.011,.004,.30),-72,.405,.245,.018,.095,.030,'jade',.009),
      ('left_shoot',(-.071,.021,.37),191,.395,.252,.036,.108,.036,'jade',-.008),
      ('main_crown',(.014,.008,.48),12,.400,.228,.060,.100,.026,'sage',.014),
      ('rear_shoot',(.041,.052,.40),73,.368,.245,.095,.108,.040,'olive',-.010),
      ('left_shoot',(-.10,.03,.53),-136,.360,.225,.092,.110,.040,'jade',.009),
      ('rear_shoot',(.071,.091,.53),126,.349,.215,.088,.095,.035,'sage',-.009),
      ('main_crown',(.004,.015,.66),-45,.323,.192,.105,.094,.037,'jade',.008),
      ('left_shoot',(-.105,.034,.655),-190,.287,.176,.088,.075,.032,'sage',.010),
      ('rear_shoot',(.085,.103,.665),48,.302,.190,.114,.067,.029,'jade',-.008),
      ('main_crown',(-.005,.018,.755),127,.215,.137,.105,.055,.027,'olive',.004)]
    for i,(parent,attach,degrees,length,width,rise,arch,cup,color,twist) in enumerate(layout,1):
        a=math.radians(degrees);v=Vector((math.cos(a),math.sin(a),0));p=Vector(attach);base=p+v*.075+Vector((0,0,.035));mid=p+v*.042+Vector((0,0,.024))
        stem=f'petiole_{i:02d}';tube(stem,[tuple(p),tuple(mid),tuple(base)],[.0085,.0065,.0045],'botanical_leaf_olive',6)
        name=f'cupped_broad_leaf_{i:02d}';leaf(name,tuple(base),a,length,width,rise,arch,cup,'botanical_leaf_'+color,twist)
        record_joint(stem,parent,p,p,.008,'petiole_to_stem_overlap');record_joint(name,stem,base,base,.0045,'leaf_base_to_petiole')
    return {'suggested_soil_patch_radius_m':.13,'root_or_crown_contact_radius_m':.032,'suggested_minimum_soil_depth_m':.22,'height_intent_m':[.70,1.0],'botanical_identity':'Original broad ovate cupped-leaf understory, not a named real species'}

def rosette():
    crown=[(0,0,0),(0,0,.028),(.002,.001,.052)]
    tube('rosette_basal_crown',crown,[.035,.031,.015],'botanical_bark',9,True)
    rings=[
      ([(12,.290,.100),(66,.275,.094),(121,.286,.102),(175,.263,.100),(229,.298,.103),(283,.270,.096),(328,.279,.096)],.032,.035,.075,.018,'jade'),
      ([(40,.222,.083),(112,.215,.080),(184,.228,.087),(256,.211,.080),(320,.218,.081)],.043,.080,.080,.024,'sage'),
      ([(74,.147,.062),(194,.156,.062),(300,.149,.064)],.052,.127,.047,.021,'olive')]
    idx=0
    for layout,height,rise,arch,cup,color in rings:
        for degrees,length,width in layout:
            idx+=1;a=math.radians(degrees);base=(.002,.001,height)
            name=f'rosette_spoon_leaf_{idx:02d}';leaf(name,base,a,length,width,rise,arch,cup,'botanical_leaf_'+color,(-1 if idx%2 else 1)*.008,'rosette',rib=False)
            record_joint(name,'rosette_basal_crown',base,base,.015,'leaf_root_in_crown')
    flowers=[('A',(.079,.018,.286),24),('B',(-.068,.046,.318),57),('C',(.013,-.062,.257),-13)]
    for j,(tag,top,rot) in enumerate(flowers):
        stem=f'flower_{tag}_stem';attach=(.002,.001,.038);mid=(top[0]*.45,top[1]*.45,top[2]*.55)
        tube(stem,[attach,mid,top],[.0045,.0035,.0024],'botanical_leaf_olive',6)
        record_joint(stem,'rosette_basal_crown',attach,attach,.031,'flower_stem_in_crown')
        # Closed taper receptacle visibly carries five spoon petals; no spheres.
        recept=f'flower_{tag}_receptacle';tube(recept,[(top[0],top[1],top[2]-.008),top,(top[0],top[1],top[2]+.006)],[.003,.008,.005],'botanical_leaf_olive',7,True)
        for k in range(5):
            a=math.radians(rot+k*72);base=(top[0],top[1],top[2]+.002)
            name=f'flower_{tag}_petal_{k+1}';leaf(name,base,a,.037 if j!=1 else .042,.023 if j!=1 else .026,.018,.007,.005,'botanical_flower',0,'petal',False)
            record_joint(name,recept,base,base,.008,'petal_root_in_receptacle')
        # Short closed hexagonal center reads as a restrained pollen disk.
        tube(f'flower_{tag}_center',[(top[0],top[1],top[2]+.004),(top[0],top[1],top[2]+.013)],[.006,.004],'botanical_flower',6,True)
        record_joint(recept,stem,top,top,.0024,'receptacle_to_stem')
    return {'suggested_soil_patch_radius_m':.085,'root_or_crown_contact_radius_m':.035,'suggested_minimum_soil_depth_m':.14,'height_intent_m':[.25,.4],'botanical_identity':'Original compact spoon-leaf flowering rosette, not a named real species'}

def measure(objects):
    dg=bpy.context.evaluated_depsgraph_get();pts=[];tri=0
    for ob in objects:
        ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();tri+=len(me.loop_triangles);pts.extend(ob.matrix_world@v.co for v in me.vertices);ev.to_mesh_clear()
    lo=[min(p[k] for p in pts) for k in range(3)];hi=[max(p[k] for p in pts) for k in range(3)]
    return {'min_m':lo,'max_m':hi,'dimensions_m':[b-a for a,b in zip(lo,hi)]},tri

def export(objects,path,ident):
    groups={};dg=bpy.context.evaluated_depsgraph_get()
    for src in objects:
        me=bpy.data.meshes.new_from_object(src.evaluated_get(dg));active=me.uv_layers.active
        for other in list(me.uv_layers):
            if other!=active:me.uv_layers.remove(other)
        active.name='botanical_metric_uv';active.active_render=True
        ob=bpy.data.objects.new('EXPORT_'+src.name,me);bpy.context.collection.objects.link(ob);ob.matrix_world=src.matrix_world.copy();groups.setdefault(src['material_role'],[]).append(ob)
    runtime=[]
    for role,parts in groups.items():
        bpy.ops.object.select_all(action='DESELECT')
        for ob in parts:ob.select_set(True)
        bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();ob=parts[0];ob.name=ident+'__'+role;ob['material_role']=role;ob['semantic_parts']=json.dumps([s.name for s in objects if s['material_role']==role]);runtime.append(ob)
    bpy.ops.object.select_all(action='DESELECT')
    for ob in runtime:ob.select_set(True)
    bpy.context.view_layer.objects.active=runtime[0]
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_materials='EXPORT',export_texcoords=True,export_normals=True,export_cameras=False,export_lights=False)
    for ob in runtime:bpy.data.objects.remove(ob,do_unlink=True)

def main():
    records=[];collision={};bpy.context.preferences.filepaths.save_version=0
    for ident,title,fn in [('AST-BOT-002','Cupped broad-leaf understory',understory),('AST-BOT-003','Low flowering spoon-leaf rosette',rosette)]:
        reset();soil=fn();objects=list(PARTS)
        if ident=='AST-BOT-002':
            # Curated long-axis fan keeps broad foliage inside a 0.73 m soil strip.
            # Edit actual mesh points, never leave non-unit runtime object scales.
            for ob in objects:
                for v in ob.data.vertices:v.co.y*=.755
                for key in ('centerline_m','leaf_base_m'):
                    if key in ob:
                        data=json.loads(ob[key])
                        if key=='centerline_m':data=[[p[0],p[1]*.755,p[2]] for p in data]
                        else:data=[data[0],data[1]*.755,data[2]]
                        ob[key]=json.dumps(data)
            for joint in SUPPORTS:
                for key in ('child_attachment_m','parent_centerline_attachment_m'):joint[key][1]*=.755
                joint['attachment_center_distance_m']=math.dist(joint['child_attachment_m'],joint['parent_centerline_attachment_m'])
            soil['curated_fan_depth_scale']=.755
            soil['proposed_straight_planter_base_m']=[1.2,.51,.390]
            soil['straight_planter_soil_opening_y_m']=[.15,.88]
        else:soil['proposed_straight_planter_base_m']=[1.2,.51,.390]
        bounds,tri=measure(objects);assert abs(bounds['min_m'][2])<1e-7
        bpy.context.scene['catalogue_id']=ident;bpy.context.scene['soil_plane']='Z0, pivot at soil center; no soil geometry included'
        for im in bpy.data.images:
            if im.source=='FILE' and not im.packed_file:im.pack()
        source=BASE/'source'/f'{ident}.blend';glb=BASE/'exports'/f'{ident}.glb'
        bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True);export(objects,glb,ident)
        rec={'catalogue_id':ident,'title':title,'unique_design':True,'original_script_assisted_design':True,'units':'metres','source':str(source.relative_to(BASE)),'export':str(glb.relative_to(BASE)),'generator':'source/build_botanical_understory.py','coordinates':'Blender Z up; front -Y; exported GLB standard Y-up','pivot':{'position_m':[0,0,0],'datum':'Soil plane at root/crown center'},'bounds_blender_z_up':bounds,'evaluated_triangles':tri,'editable_semantic_parts':len(objects),'semantic_parts':[o.name for o in objects],'material_roles':sorted(set(o['material_role'] for o in objects)),'material_alpha':'All OPAQUE, no alpha cutouts or blend','thin_surfaces':'Single deliberately shaped leaf and petal surfaces have open perimeters; double-sided material. Closed stem/crown/receptacle solids. No sphere foliage or alpha cards.','soil_placement':soil,'soil_contact_z_m':bounds['min_m'][2],'support_joints':SUPPORTS,'runtime_consolidation':'One evaluated static mesh per material role. UV names normalized before join. Editable named parts retained in .blend.','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256(glb.read_bytes()).hexdigest(),'reference_manifest':'../../batches/batch04/reference_manifest.json','dependencies':['../../standards/botanical_materials.py','../../materials/botanical/'],'limitations':['Independent botanical components, not original game restoration','No native engine performance, physics, room fit or species contact claim','No biological planting/horticultural viability claim; soil depth is spatial proposal only','Placement must avoid walk and seat approach space; foliage excluded from collision proposal']}
        records.append(rec);(BASE/f'{ident}.manifest.json').write_text(json.dumps(rec,indent=2)+'\n')
        if ident=='AST-BOT-002':collision[ident]={'proposal_only':True,'type':'cylinder','center_xy_m':[0,0],'z_min_m':0,'z_max_m':.15,'radius_m':.045,'scope':'Small basal stem only. Prefer surrounding planter collider; no canopy blocker.'}
        else:collision[ident]={'proposal_only':True,'type':'cylinder','center_xy_m':[0,0],'z_min_m':0,'z_max_m':.055,'radius_m':.035,'scope':'Optional tiny crown only; foliage and flowers non-colliding. Prefer surrounding planter collider.'}
    (BASE/'manifest.json').write_text(json.dumps({'family':'Original understated botanical companions','unique_design_count':2,'assets':records},indent=2)+'\n')
    (BASE/'collision_proposals.json').write_text(json.dumps(collision,indent=2)+'\n')
    print('BOTANICAL_UNDERSTORY_COMPLETE',[(r['catalogue_id'],r['evaluated_triangles'],r['bounds_blender_z_up']) for r in records])
if __name__=='__main__':main()
