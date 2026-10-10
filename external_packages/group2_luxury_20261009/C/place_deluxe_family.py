"""Place the reviewed18x10 Deluxe fixture family in one exact existing-unit reservation.
No scaling/mirroring, root slabs, exterior windows, neighbour edits or live adoption.
Run only through heavy.py. Input876 native must have matching reviewed hashes.
"""
import bpy,bmesh,pathlib,json,hashlib,math,sys,copy,runpy
from mathutils import Matrix,Vector
R=pathlib.Path(__file__).resolve().parent;I=R/'inputs';unit=int(sys.argv[sys.argv.index('--')+1]);O=R/'sections'/f'{unit}_deluxe';O.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(R));from editable_label import repair_label
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base_dir=R/'sections/876_deluxe';base_path=base_dir/'876_deluxe.blend';base=json.loads((base_dir/'SECTION_CONTRACT.json').read_text());review=json.loads((base_dir/'PIXEL_REVIEW.json').read_text());assert review['actual_views_inspected']==6;assert base['native_sha256']==sha(base_path)==review['native_sha256'];assert unit!=876
inventory=json.loads((R/'LUXURY_81_INVENTORY.json').read_text());row=next(x for x in inventory['records'] if x['identity']['source_envelope_index']==unit);rsv=row['reservation'];assert rsv['tier']=='deluxe' and rsv['nominal_depth_m']==18 and rsv['floor_y']==102
assert row['identity']['existing_partial_construction'] is None and not row['D18_dependencies'];assert unit not in inventory['protected_Group1_standard_D17_indices'];poly=rsv['proposed_floor_boundary'];xmin=min(x[0] for x in poly);xmax=max(x[0] for x in poly);zmin=min(x[1] for x in poly);zmax=max(x[1] for x in poly);assert abs(xmax-xmin-18)<.0001 and abs(zmax-zmin-10)<.0001
screen=json.loads((R/'ALL_81_NEIGHBOUR_SCREEN.json').read_text());sr=next(x for x in screen['records'] if x['source_envelope_index']==unit)
if sr['screen_status']!='NO_AABB_INTERSECTIONS':
 precise=json.loads((R/'PRECISE_RETAINED_TIDAL_INTERSECTIONS.json').read_text());pr=next(x for x in precise['records'] if x['source_envelope_index']==unit);assert pr['status']=='AABB_CANDIDATE_CLEARED_BY_ACTUAL_TRIANGLES';assert not sr['structural_mesh_aabb_contacts']
starboard=xmin>0;angle=math.pi if starboard else 0
if starboard:
 origin=[xmin,102,zmax];u_axis=[1,0,0];v_axis=[0,0,-1];transform=Matrix.Translation(Vector((xmin-43,459-zmax,0)))@Matrix.Rotation(math.pi,4,'Z')
else:
 origin=[xmax,102,zmin];u_axis=[-1,0,0];v_axis=[0,0,1];transform=Matrix.Translation(Vector((xmax+43,-zmin-459,0)))
def source(u,v,h):return Vector((origin[0]+u*u_axis[0]+v*v_axis[0],-(origin[2]+u*u_axis[2]+v*v_axis[2]),origin[1]+h))
def moved_world(w):
 p=transform@Vector((w[0],-w[2],w[1]));return [p.x,p.z,-p.y]
bpy.ops.wm.open_mainfile(filepath=str(base_path));scene=bpy.context.scene;objects=list(scene.objects);original={ob:ob.matrix_world.copy() for ob in objects}
for ob in objects:
 if ob.parent not in objects:ob.matrix_world=transform@original[ob]
 ob['source_scope']=f'Group2/{unit}';ob['source_envelope_index']=unit
 if ob.name.startswith('DATUM_rest_'):
  ix=int(ob.name.rsplit('_',1)[1])-1;ob['reservation_id']=row['identity']['proposed_rest_slot_ids'][ix]
 if ob.type=='FONT':
  ob.data.body=f'DELUXE {unit}'
  repair_label(ob)
bpy.context.view_layer.update()
for ob in objects:assert max(abs(ob.matrix_world[a][b]-(transform@original[ob])[a][b]) for a in range(4) for b in range(4))<.0001
scene.render.engine='CYCLES';scene.cycles.samples=4;scene.cycles.device='CPU';scene.cycles.use_denoising=True;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=800;scene.render.resolution_y=450;scene.render.resolution_percentage=100
# A rendering-only proposed compiler slab; never saved or exported.
me=bpy.data.meshes.new('PREVIEW_COMPILER_FLOOR');verts=[(x,-z,h) for h in [101.82,102] for x,z in poly];n=len(poly);me.from_pydata(verts,[],[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.materials.append(bpy.data.materials['ASTRAEA_warm_stone']);preview=bpy.data.objects.new('PREVIEW_COMPILER_FLOOR',me);scene.collection.objects.link(preview)
context_path=I/'Game/assets/models/AST-RES-TIDAL_floor_winding_r002.glb';before=set(scene.objects);bpy.ops.import_scene.gltf(filepath=str(context_path));context=set(scene.objects)-before
camera=bpy.data.objects.new('QA_EyeLevelCamera',bpy.data.cameras.new('QA_EyeLevelCamera'));scene.collection.objects.link(camera);scene.camera=camera;camera.data.lens=20;camera.data.clip_start=.05;camera.data.clip_end=100
receipts=[]
for view in base['source_views']:
 position=moved_world(view['camera_world_xyz']);target=moved_world(view['target_world_xyz']);camera.location=(position[0],-position[2],position[1]);look=Vector((target[0],-target[2],target[1]));camera.rotation_euler=(look-camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(O/view['file']);bpy.ops.render.render(write_still=True);receipts.append({'name':view['name'],'file':view['file'],'camera_world_xyz':position,'target_world_xyz':target,'height_above_local_floor':1.65,'sha256':sha(O/view['file']),'render_samples':4,'scope':'Actual placed unit source plus exact retained world context; no adopted floor or final court/outlook claimed'})
for ob in context:bpy.data.objects.remove(ob,do_unlink=True)
bpy.data.objects.remove(preview,do_unlink=True);bpy.data.objects.remove(camera,do_unlink=True);scene.camera=None
bpy.ops.file.pack_all();bpy.ops.object.select_all(action='DESELECT')
for ob in objects:
 if ob.type not in {'LIGHT','CAMERA'}:ob.select_set(True)
native=O/f'{unit}_deluxe.blend';export=O/f'{unit}_deluxe.glb';bpy.ops.wm.save_as_mainfile(filepath=str(native));bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False,export_apply=True)
contract=copy.deepcopy(base);contract['identity']=row['identity'];contract['reservation']=rsv;contract['status']='BUILT_CANDIDATE_PENDING_INDEPENDENT_QA_AND_ACTUAL_PIXEL_REVIEW';contract['local_frame']={'origin_xyz':origin,'u_axis':u_axis,'v_axis':v_axis,'h_axis':[0,1,0],'rigid_transform_only':True};contract['native_sha256']=sha(native);contract['export_sha256']=sha(export);contract['rebuild_source_sha256']=sha(pathlib.Path(__file__));contract['derivative_source']={'reviewed_template':'sections/876_deluxe/876_deluxe.blend','template_sha256':sha(base_path),'native_root_transform':[list(transform[i]) for i in range(4)],'scale':1,'reflection':False,'scope':'Same Deluxe fixture family in independently reconciled exact source reservations; species/habitat mix remains unassigned'};contract['source_views']=receipts;contract['floor_proposal']['boundary']=poly;contract['render_only_context']['objects_removed_before_native_and_export']=len(context)
for imp in contract['imports']:
 if 'world_xyz' in imp:imp['world_xyz']=moved_world(imp['world_xyz']);imp['source_yaw']+=angle
for marker in contract['markers']:
 marker['world_xyz']=moved_world(marker['world_xyz'])
 if marker['kind']=='proposed_rest_anchor':marker['reservation_id']=row['identity']['proposed_rest_slot_ids'][int(marker['name'].rsplit('_',1)[1])-1]
(O/'SECTION_CONTRACT.json').write_text(json.dumps(contract,indent=2))
# Independently reopen the saved native, then parse the actual export. Both
# scripts write failures before raising; no pixel-approval claim is made here.
sys.path.insert(0,str(R));runpy.run_path(str(R/'verify_first_native.py'),run_name='__main__');runpy.run_path(str(R/'verify_first_export.py'),run_name='__main__');print('PLACED DELUXE SOURCE QA PASS',unit,flush=True)
