from pathlib import Path
import bpy,json,hashlib,sys,math
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.loads((W/'PLAN.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=lambda p:(p[0],-p[2],p[1])
for p,h in P['source_pins'].items():assert sha(R/p)==h,p
bpy.ops.wm.read_factory_settings(use_empty=True)
palette={'champagne_metal':(.46,.4,.27,1),'warm_stone':(.58,.54,.45,1),'ivory_enamel':(.78,.73,.63,1),'warm_walnut':(.25,.12,.065,1),'hospitality_glass':(.22,.4,.44,.4),'opal_glow':(1,.87,.65,1)}
materials={}
for role,color in palette.items():
    mat=bpy.data.materials.new('D04Receiving_'+role);mat.diffuse_color=color;mat.use_nodes=True
    bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=color
    bs.inputs['Roughness'].default_value=.7;bs.inputs['Metallic'].default_value=.45 if role=='champagne_metal'else 0
    tex=R/'Game/assets/models'/('AST-LIB-011_'+role+'.png')
    if tex.exists():
        image=bpy.data.images.load(str(tex),check_existing=True);image.pack();node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;mat.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color'])
    if role=='opal_glow':bs.inputs['Emission Color'].default_value=color;bs.inputs['Emission Strength'].default_value=1.2
    if role=='hospitality_glass':bs.inputs['Alpha'].default_value=.4;mat.surface_render_method='DITHERED'
    materials[role]=mat
for p in P['parts']:
    me=bpy.data.meshes.new(p['name']);me.from_pydata([B(v)for v in p['verts']],[],p['faces']);me.update();me.materials.append(materials[p['role']]);uv=me.uv_layers.new(name='MetreScaled')
    for f in me.polygons:
        n=f.normal;u=Vector((1,0,0))if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u)
        for li in f.loop_indices:co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co.dot(u),co.dot(v))
    ob=bpy.data.objects.new(p['name'],me);bpy.context.collection.objects.link(ob)
    for key in ['role','category','runtime_collision']:ob[key]=p[key]
    ob['runtime_visual']=p.get('runtime_visual',True)
    ob['source_plan_sha256']=sha(W/'PLAN.json')

from mathutils import Matrix
assert json.load(open(W/'PREIMAGE_SUPPORT.json'))['status']=='PASS'
bpy.context.preferences.filepaths.save_version=0
instances=[]
def append_source(spec,stair=False):
    src=R/spec['source'];assert sha(src)==P['source_pins'][spec['source']]
    with bpy.data.libraries.load(str(src),link=False)as(a,b):b.objects=a.objects
    objs=[o for o in b.objects if o]
    for ob in objs:bpy.context.collection.objects.link(ob)
    bpy.context.view_layer.update();worlds={o:o.matrix_world.copy()for o in objs};root=bpy.data.objects.new(spec['prefix'],None);bpy.context.collection.objects.link(root)
    T=Matrix.Translation(Vector(B(spec['origin'])))@Matrix.Rotation(spec['yaw'],4,'Z');root.matrix_world=T
    meshes=0;excluded=[]
    for ob in objs:
        oldname=ob.name
        if ob.type not in ['MESH','EMPTY'] or ('PreviewGround'in oldname) or any(ob.get(k) is True for k in ['preview_only','presentation_only','exclude_from_production']):
            excluded.append(oldname);bpy.data.objects.remove(ob,do_unlink=True);continue
        ob.parent=root;ob.matrix_world=T@worlds[ob];ob.name=spec['prefix']+'__'+oldname
        ob['source_family_file']=spec['source'];ob['source_file_sha256']=sha(src)
        if ob.type=='MESH':
            meshes+=1;ob['category']='stair_source_visual'if stair else'source_fitting';ob['runtime_collision']=oldname.startswith('CIR_Guard')if stair else True;ob['runtime_visual']=True
    instances.append({'prefix':spec['prefix'],'source':spec['source'],'source_sha256':sha(src),'origin':spec['origin'],'yaw':spec['yaw'],'mesh_count':meshes,'rigid_instance_no_rescaling':True,'excluded_presentation_objects':excluded})
append_source({**P['stair'],'prefix':'D04PF_Stair'},True)
for spec in P['source_fittings']:append_source(spec)
bpy.context.view_layer.update();bpy.ops.file.pack_all()
def save(blend,glb):
    bpy.ops.wm.save_as_mainfile(filepath=str(W/blend));bpy.ops.export_scene.gltf(filepath=str(W/glb),export_format='GLB',export_extras=True)
    h=sha(W/glb);count=sum(o.type=='MESH'for o in bpy.context.scene.objects);bpy.ops.wm.open_mainfile(filepath=str(W/blend));bpy.ops.export_scene.gltf(filepath=str(W/glb),export_format='GLB',export_extras=True);assert sha(W/glb)==h
    return {'native':blend,'native_sha256':sha(W/blend),'export':glb,'export_sha256':h,'mesh_count':count,'fresh_native_repeat_identical':True}
receiving=save('D04PortForwardReceiving.blend',P['receiving_model'])
# Bounded successor of only three original material/cell batches. The full
# original lower network, cap successor, lift and other batches stay untouched.
cut=P['staff_wall_cut'];bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/'Game/assets/models'/cut['source_model']));bpy.context.view_layer.update()
found={o.name:o for o in bpy.data.objects if o.name in cut['meshes']};assert set(found)==set(cut['meshes']),found.keys()
worlds={o:o.matrix_world.copy()for o in found.values()}
for ob in list(bpy.data.objects):
    if ob not in worlds:bpy.data.objects.remove(ob,do_unlink=True)
lo=cut['min'];hi=cut['max'];center=[(a+b)/2 for a,b in zip(lo,hi)]
bpy.ops.mesh.primitive_cube_add(size=1,location=B(center));cutter=bpy.context.object;cutter.name='ExactSourceWallPortalCutter';cutter.scale=(hi[0]-lo[0],hi[2]-lo[2],hi[1]-lo[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
changes=[]
for ob,m in worlds.items():
    ob.parent=None;ob.matrix_world=m;old=ob.data.copy();before=len(ob.data.polygons);mod=ob.modifiers.new('BoundedStaffPortalOnly','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=mod.name);ob['source_model_sha256']=sha(R/'Game/assets/models'/cut['source_model']);ob['source_wall_cut_sha256']=sha(W/'PLAN.json');assert len(ob.data.polygons)!=before,ob.name
    changes.append({'mesh':ob.name,'original_faces':before,'new_faces':len(ob.data.polygons),'cut_world_min':lo,'cut_world_max':hi})
bpy.data.objects.remove(cutter,do_unlink=True);bpy.ops.file.pack_all();patch=save('D04StaffWallPortalSuccessor.blend','D04_STAFF_WALL_PORTAL_PATCH_r001.glb')
for p,h in P['source_pins'].items():assert sha(R/p)==h,p
sys.path.insert(0,str(R/'Game/tools'));from validate_production_glb import validate_and_copy
for q in [receiving,patch]:validate_and_copy(W/q['export'],R/'Game/assets/models'/q['export'])
runtime={**P,'model_file':receiving['export'],'model_sha256':receiving['export_sha256'],'native_sha256':receiving['native_sha256'],'staff_patch_model':patch['export'],'staff_patch_sha256':patch['export_sha256'],'open_staff_gateway':False,'source_fittings':instances}
(W/'RUNTIME_RECEIVING.json').write_text(json.dumps(runtime,indent=2)+'\n')
rec={'status':'PASS','blender_version':bpy.app.version_string,'receiving':receiving,'staff_patch':patch,'source_instances':instances,'original_wall_batches':changes,'source_pins_unchanged':len(P['source_pins']),'original_models_modified':False,'rooms_adopted':0,'open_staff_gateway_at_build':False,'primary_load_accepted':False};(W/'NATIVE_EXPORT_CHECK.json').write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps({'status':'PASS','receiving_meshes':receiving['mesh_count'],'patch_batches':patch['mesh_count']}))
