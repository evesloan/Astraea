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
    mat=bpy.data.materials.new('D17Receiving_'+role);mat.diffuse_color=color;mat.use_nodes=True
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
    ob['source_plan_sha256']=sha(W/'PLAN.json')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.file.pack_all()
native=W/'StarAtlasD17ReceivingFirst.blend';out=W/P['receiving_model']
bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
def export(path):bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',export_extras=True,export_yup=True)
export(out);model_sha=sha(out)
bpy.ops.wm.open_mainfile(filepath=str(native));export(out);assert sha(out)==model_sha
sys.path.insert(0,str(R/'Game/tools'));from validate_production_glb import validate_and_copy
validate_and_copy(out,R/'Game/assets/models'/out.name)

# Editable first-room derivative: move only the complete original entry fitting
# inward, retaining every original mesh/fixture and the two existing rests.
room=P['first_room'];original=R/room['recipe']['editable_source']
bpy.ops.wm.open_mainfile(filepath=str(original))
meshes=[o for o in bpy.data.objects if o.type=='MESH']
before={o.name:[tuple(v.co)for v in o.data.vertices]for o in meshes}
original_roots=[o for o in bpy.data.objects if o.parent is None]
entry_roots=[o for o in original_roots if o.name.startswith('EntryDoor__')]
assert len([o for o in meshes if o.name.startswith('EntryDoor__')])==20
for o in entry_roots:o.location.y+=room['entry_recess_m']
root=bpy.data.objects.new('D17_823_RecordedPose',None);bpy.context.collection.objects.link(root)
root.location=B(room['origin']);root.rotation_euler.z=room['yaw']
root['allocation_sha256']=room['allocation']['allocation_sha256'];root['rest_slot_ids']=room['rest_slots_unchanged']
for o in original_roots:o.parent=root
for o in original_roots:
    if o.name.startswith('bath_shower__'):o.location.y+=room['shower_shift_west_m']
bpy.data.objects['SUI_BathEntryCornerClosure'].location.y+=room['bath_corner_shift_west_m']
def native_cube(name,lo,hi,material=None):
    x,y,z=lo;X,Y,Z=hi;vs=[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)]
    fs=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update()
    if material:me.materials.append(material)
    ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.parent=root
    ob['runtime_collision']=True;ob['source_plan_sha256']=sha(W/'PLAN.json')
    uv=me.uv_layers.new(name='MetreScaled')
    for f in me.polygons:
        for li in f.loop_indices:
            co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co.x,co.z)
    return ob
cutter=native_cube('Temporary_EntryReceiverCutter',room['entry_receiver_cut_native_box']['min'],room['entry_receiver_cut_native_box']['max'])
bpy.context.view_layer.update()
for name in room['entry_receiver_shell_meshes']:
    target=bpy.data.objects[name];bpy.context.view_layer.objects.active=target
    mod=target.modifiers.new('ContainedDoorReceiver','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    bpy.ops.object.modifier_apply(modifier=mod.name)
    assert len(target.data.vertices)>0,name
bpy.data.objects.remove(cutter,do_unlink=True)
material=bpy.data.objects['SUI_BathInnerForward'].data.materials[0]
native_cube('D17_823_BathPrivacyReturn',[-3.44,.30,0],[-.70,.42,2.6],material)
native_cube('D17_823_PocketRearLeft',[.79,.255,0],[1.75,.375,2.66],material)
native_cube('D17_823_PocketRearRight',[-1.75,.255,0],[-.79,.375,2.66],material)
# A contained five-centimetre threshold infill closes the old shell-floor reveal.
me=bpy.data.meshes.new('D17_823_ContainedThreshold')
vs=[(-1.75,-.22,0),(1.75,-.22,0),(1.75,0,0),(-1.75,0,0),(-1.75,-.22,.05),(1.75,-.22,.05),(1.75,0,.05),(-1.75,0,.05)]
fs=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
me.from_pydata([B(v)for v in vs],[],fs);me.update();uv=me.uv_layers.new(name='MetreScaled')
for f in me.polygons:
    for li in f.loop_indices:
        v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.x,v.y)
floor=bpy.data.objects['SUI_Floor'];me.materials.append(floor.data.materials[0])
threshold=bpy.data.objects.new('D17_823_ContainedThreshold',me);bpy.context.collection.objects.link(threshold);threshold.parent=root
threshold['runtime_collision']=True;threshold['source_plan_sha256']=sha(W/'PLAN.json')
bpy.context.view_layer.update()
points=[o.matrix_world@v.co for o in bpy.data.objects if o.type=='MESH'for v in o.data.vertices]
xz=[(v.x,-v.y)for v in points]
# Shapely is not installed in Blender. Retain the evaluated cloud for independent
# full convex/per-part footprint verification in the geometry environment.
(W/'FIRST_ROOM_EVALUATED_FOOTPRINT.json').write_text(json.dumps({'world_xz':xz,'original_mesh_count':len(before),'original_native_sha256':sha(original),'entry_recess_m':room['entry_recess_m'],'allocation_boundary':room['allocation']['candidate_layout']['proposed_floor_boundary']},separators=(',',':'))+'\n')
changed=[name for name,vs in before.items()if [tuple(v.co)for v in bpy.data.objects[name].data.vertices]!=vs]
assert set(changed)==set(room['entry_receiver_shell_meshes']),changed
bpy.context.preferences.filepaths.save_version=0;bpy.ops.file.pack_all()
room_native=W/'StarAtlasD17Standard823Recess.blend';bpy.ops.wm.save_as_mainfile(filepath=str(room_native),compress=True)
bpy.ops.object.select_all(action='DESELECT');threshold.select_set(True);bpy.context.view_layer.objects.active=threshold
threshold_out=W/'STAR_ATLAS_D17_823_THRESHOLD_r001.glb'
bpy.ops.export_scene.gltf(filepath=str(threshold_out),export_format='GLB',use_selection=True,export_extras=True,export_yup=True)
threshold_sha=sha(threshold_out);validate_and_copy(threshold_out,R/'Game/assets/models'/threshold_out.name)
bpy.ops.object.select_all(action='DESELECT')
for ob in bpy.data.objects:
    if ob.type=='MESH'and not ob.name.startswith(('EntryDoor__','BathroomDoor__')):ob.select_set(True)
candidate_out=W/'STAR_ATLAS_D17_823_FITTED_r001.glb'
bpy.ops.export_scene.gltf(filepath=str(candidate_out),export_format='GLB',use_selection=True,export_extras=True,export_yup=True)
candidate_sha=sha(candidate_out);validate_and_copy(candidate_out,R/'Game/assets/models'/candidate_out.name)
for p,h in P['source_pins'].items():assert sha(R/p)==h,p
runtime={**P,'model_file':P['receiving_model'],'model_sha256':model_sha,'native_sha256':sha(native),'open_gateway':False}
runtime['first_room'].update(native_sha256=sha(room_native),threshold_model=threshold_out.name,threshold_sha256=threshold_sha,original_mesh_coordinates_unchanged=len(before)-len(changed),entry_native_meshes_recessed=20,adapted_shell_mesh_names=changed,candidate_model=candidate_out.name,candidate_sha256=candidate_sha,shower_shift_west_m=.21,bath_privacy_return_added=True)
(W/'RUNTIME_RECEIVING.json').write_text(json.dumps(runtime,indent=2)+'\n')
(W/'NATIVE_EXPORT_CHECK.json').write_text(json.dumps({'status':'PASS','receiving_native_sha256':sha(native),'receiving_export_sha256':model_sha,'receiving_parts':len(P['parts']),'fresh_native_repeat_export_identical':True,'first_room_native_sha256':sha(room_native),'first_room_original_mesh_coordinates_unchanged':len(before)-len(changed),'adapted_shell_mesh_names':changed,'new_pocket_receiver_parts':3,'shower_shift_west_m':.21,'candidate_export_sha256':candidate_sha,'first_room_original_meshes_removed':0,'entry_native_meshes_recessed':20,'threshold_sha256':threshold_sha,'source_pins_unchanged':len(P['source_pins']),'runtime_adoption_at_build':False,'new_rest_places':0,'limits':P['limits']},indent=2)+'\n')
print(json.dumps({'status':'PASS','parts':len(P['parts']),'room_original_meshes':len(before),'entry_recess_m':room['entry_recess_m']}))
