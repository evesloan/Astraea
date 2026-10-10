"""Place the reviewed core plus fitted24x10 private gallery Deluxe family in one exact existing-unit reservation.
No scaling/mirroring, root slabs, exterior windows, neighbour edits or live adoption.
Run only through heavy.py. Input876 native must have matching reviewed hashes.
"""
import bpy,bmesh,pathlib,json,hashlib,math,sys,copy,runpy
from mathutils import Matrix,Vector
R=pathlib.Path(__file__).resolve().parent;I=R/'inputs';unit=int(sys.argv[sys.argv.index('--')+1]);O=R/'sections'/f'{unit}_deluxe';O.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(R));from editable_label import repair_label
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base_dir=R/'sections/876_deluxe';base_path=base_dir/'876_deluxe.blend';base=json.loads((base_dir/'SECTION_CONTRACT.json').read_text());review=json.loads((base_dir/'PIXEL_REVIEW.json').read_text());assert review['actual_views_inspected']==6;assert base['native_sha256']==sha(base_path)==review['native_sha256'];assert unit!=876
inventory=json.loads((R/'LUXURY_81_INVENTORY.json').read_text());row=next(x for x in inventory['records'] if x['identity']['source_envelope_index']==unit);rsv=row['reservation'];assert rsv['tier']=='deluxe' and rsv['nominal_depth_m']==24 and rsv['floor_y']==102
assert row['identity']['existing_partial_construction'] is None and not row['D18_dependencies'];assert unit not in inventory['protected_Group1_standard_D17_indices'];poly=rsv['proposed_floor_boundary'];xmin=min(x[0] for x in poly);xmax=max(x[0] for x in poly);zmin=min(x[1] for x in poly);zmax=max(x[1] for x in poly);assert abs(xmax-xmin-24)<.0001 and abs(zmax-zmin-10)<.0001
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
# The central family retains the reviewed household core and extends it
# with its own usable private planted gallery. No asset is stretched.
new_objects=[]
def made(name,points,role):
 me=bpy.data.meshes.new(name);n=len(points)//2
 me.from_pydata([source(*p) for p in points],[],[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]);me.update()
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 uv=me.uv_layers.new(name='MetrePlanar')
 for face in me.polygons:
  axes=([1,2] if abs(face.normal.x)>.6 else [0,2] if abs(face.normal.y)>.6 else [0,1])
  for li in face.loop_indices:
   pt=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(pt[axes[0]],pt[axes[1]])
 me.materials.append(bpy.data.materials['G2_WarmFixtureLens' if role=='lens' else 'ASTRAEA_'+role]);ob=bpy.data.objects.new(name,me);scene.collection.objects.link(ob);ob['source_scope']=f'Group2/{unit}';ob['source_envelope_index']=unit;new_objects.append(ob);return ob

def box_local(name,u0,u1,v0,v1,h0,h1,role):
 return made(name,[(u,v,h) for h in [h0,h1] for u,v in [(u0,v0),(u1,v0),(u1,v1),(u0,v1)]],role)

for name in ['CourtSealedPane1','CourtSill']:
 ob=scene.objects[name];objects.remove(ob);bpy.data.objects.remove(ob,do_unlink=True)
box_local('GalleryForeInternalSill',17.54,17.93,.9,3.5,0,.45,'warm_stone')
box_local('GalleryAftInternalSill',17.54,17.93,5.9,9.1,0,.45,'warm_stone')
# A broad portal links the salon to the gallery; side glass remains present.
box_local('GalleryForeEndWall',17.93,23.70,.30,.60,0,4.28,'ivory_enamel')
box_local('GalleryAftEndWall',17.93,23.70,9.40,9.70,0,4.28,'ivory_enamel')
box_local('HeldGalleryOutwardWall',23.70,23.94,.30,9.70,0,4.28,'ivory_enamel')
box_local('GalleryCover',17.54,23.70,.30,9.70,4.10,4.28,'ivory_enamel')
box_local('GalleryPressureClosure',17.54,23.94,.30,9.70,4.28,4.45,'ivory_enamel')
for j,v in enumerate([.60,9.40]):box_local(f'GalleryRoofBearing{j}',17.54,23.70,v-.09,v+.09,3.95,4.12,'warm_walnut')
box_local('GalleryRestBenchFoot',22.85,23.55,1.10,3.85,0,.34,'warm_walnut')
box_local('GalleryRestBenchCushion',22.78,23.55,1.10,3.85,.34,.50,'teal_weave')
box_local('GalleryRestBenchBack',23.36,23.55,1.10,3.85,.50,1.18,'oatmeal_weave')
box_local('GalleryReadingConsole',22.66,23.55,5.80,7.00,0,.77,'warm_walnut')
box_local('GalleryReadingSurface',22.58,23.55,5.76,7.04,.77,.83,'warm_stone')
box_local('GalleryCornerPlanter',21.76,22.85,8.17,8.95,0,.14,'warm_stone')
# Move the actual retained plant out of the new portal; update its recorded
# import placement later. Its scale, materials and parent hierarchy stay exact.
plant_delta=source(22.30,8.65,.14)-source(16.65,4.90,.14)
plant_imp=next(i for i in base['imports'] if i['catalogue_id']=='AST-BOT-002')
for name in plant_imp['part_names']:
 ob=scene.objects.get(name)
 if ob and ob.parent not in [scene.objects.get(n) for n in plant_imp['part_names']]:ob.matrix_world=Matrix.Translation(plant_delta)@ob.matrix_world
ob=scene.objects['PlantPlinth'];objects.remove(ob);bpy.data.objects.remove(ob,do_unlink=True)
# A retained side table completes the resting pocket. Copy hierarchy roots
# with a proper translation; the pinned source family remains unchanged.
table_imp=next(i for i in base['imports'] if i['catalogue_id']=='AST-FUR-003' and 'ConversationTable' in next(iter(i.get('part_names',[])),''))
source_table=moved_world(table_imp['world_xyz']);delta=source(21.60,2.40,0)-Vector((source_table[0],-source_table[2],source_table[1]));copies={}
for name in table_imp['part_names']:
 ob=scene.objects.get(name)
 if ob:
  cp=ob.copy();cp.name='Gallery_'+ob.name;scene.collection.objects.link(cp);copies[ob]=cp;new_objects.append(cp)
cloned_originals={ob:ob.matrix_world.copy() for ob in copies}
for ob,cp in copies.items():
 cp.parent=copies.get(ob.parent);cp.matrix_parent_inverse=ob.matrix_parent_inverse.copy();cp.matrix_basis=ob.matrix_basis.copy();cp['source_scope']=f'Group2/{unit}';cp['source_envelope_index']=unit
bpy.context.view_layer.update()
for ob,cp in copies.items():
 if ob.parent not in copies:cp.matrix_world=Matrix.Translation(delta)@cloned_originals[ob]
bpy.context.view_layer.update()
for ob,cp in copies.items():
 assert max(abs(cp.matrix_world[a][b]-(Matrix.Translation(delta)@cloned_originals[ob])[a][b]) for a in range(4) for b in range(4))<.0001,(cp.name,'clone hierarchy placement')
light=box_local('GalleryOpal_Bracket',20.91,21.09,4.61,4.79,3.90,4.125,'champagne_metal');light['source_mount_target']='GalleryCover'
box_local('GalleryOpal_Lens',20.78,21.22,4.48,4.92,3.86,3.915,'lens')
d=bpy.data.lights.new('GalleryOpal','AREA');d.energy=200;d.color=(1,.78,.53);d.shape='DISK';d.size=1.1;ob=bpy.data.objects.new('GalleryOpal',d);scene.collection.objects.link(ob);ob.location=source(21,4.70,3.83);new_objects.append(ob)
# Unit814 is adjacent to retained790. Its exact allocation stays24x10;
# only this new room's end architecture takes a declared20cm setback.
# Retained790 roof/trim and Root receiver floors are never cut or moved.
setback=[]
if unit==814:
 imported={n for imp in base['imports'] for n in imp.get('part_names',[])}
 for ob in objects+new_objects:
  if ob.type!='MESH' or ob.name in imported:continue
  inv=ob.matrix_world.inverted();changed=0
  for vertex in ob.data.vertices:
   pt=ob.matrix_world@vertex.co;v=( -pt.y-origin[2])*v_axis[2]
   if v>9.80:
    pt.y=-(origin[2]+9.80*v_axis[2]);vertex.co=inv@pt;changed+=1
  if changed:setback.append({'part':ob.name,'vertices':changed,'protected_adjoining_z_max':51.08000183105469,'new_source_end_z_min':51.20})
objects+=new_objects;bpy.context.view_layer.update()

scene.render.engine='CYCLES';scene.cycles.samples=4;scene.cycles.device='CPU';scene.cycles.use_denoising=True;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=800;scene.render.resolution_y=450;scene.render.resolution_percentage=100
# A rendering-only proposed compiler slab; never saved or exported.
me=bpy.data.meshes.new('PREVIEW_COMPILER_FLOOR');verts=[(x,-z,h) for h in [101.82,102] for x,z in poly];n=len(poly);me.from_pydata(verts,[],[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.materials.append(bpy.data.materials['ASTRAEA_warm_stone']);preview=bpy.data.objects.new('PREVIEW_COMPILER_FLOOR',me);scene.collection.objects.link(preview)
context_path=I/'Game/assets/models/AST-RES-TIDAL_floor_winding_r002.glb';before=set(scene.objects);bpy.ops.import_scene.gltf(filepath=str(context_path));context=set(scene.objects)-before
camera=bpy.data.objects.new('QA_EyeLevelCamera',bpy.data.cameras.new('QA_EyeLevelCamera'));scene.collection.objects.link(camera);scene.camera=camera;camera.data.lens=20;camera.data.clip_start=.05;camera.data.clip_end=100
receipts=[]
for view in base['source_views']:
 position=moved_world(view['camera_world_xyz']);target=moved_world(view['target_world_xyz']);
 if view['name']=='main_programme':
  a=source(19.20,4.80,1.65);b=source(23.10,2.70,1.15);position=[a.x,a.z,-a.y];target=[b.x,b.z,-b.y]
 camera.location=(position[0],-position[2],position[1]);look=Vector((target[0],-target[2],target[1]));camera.rotation_euler=(look-camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(O/view['file']);bpy.ops.render.render(write_still=True);receipts.append({'name':view['name'],'file':view['file'],'camera_world_xyz':position,'target_world_xyz':target,'height_above_local_floor':1.65,'sha256':sha(O/view['file']),'render_samples':4,'scope':'Actual placed unit source plus exact retained world context; no adopted floor or final court/outlook claimed'})
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
contract['architecture_family']='central_deluxe_private_gallery'
contract['architecture']='Retained two-rest-branch household core with a broad portal into a planted private gallery, long fitted resting bench, reading console and side table; actual24m depth is composed without scaling fixtures'
contract['private_frontage_status']='Private gallery is inside this existing unit. Side glass faces its planting; opaque outward wall held for Root/Group7 genuine frontage and opening adoption. No exterior view claimed.'
contract['geometry_rebuild_dependencies']={'build_deluxe_central.py':sha(pathlib.Path(__file__)),'editable_label.py':sha(R/'editable_label.py')}
contract['protected_790_end_setback']=setback
plant=next(i for i in contract['imports'] if i['catalogue_id']=='AST-BOT-002');p=source(22.30,8.65,.14);plant['world_xyz']=[p.x,p.z,-p.y]
new_imp=copy.deepcopy(table_imp);new_imp['part_names']=[copies[scene.objects[n]].name for n in table_imp['part_names'] if n in scene.objects];p=source(21.60,2.40,0);new_imp['world_xyz']=[p.x,p.z,-p.y];new_imp['source_yaw']+=angle;contract['imports'].append(new_imp)
def world_route(points):
 a=[]
 for u,v in points:
  p=source(u,v,0);a.append([p.x,p.z,-p.y])
 return a
contract['source_routes_world']=[(name,world_route(points),radius) for name,points,radius in [('main_loaded_cart',[(2.65,5.30),(5.90,5.30),(5.90,5.00),(10.5,5.00),(10.5,7.25),(13,7.25)],.82),('kitchen_loaded_cart',[(2.65,5.30),(2.65,7.0),(3.50,7.0)],.82),('restA_body',[(6.2,4.6),(7.55,4.65)],.38),('restB_body',[(10.5,4.6),(13.1,4.65)],.38),('bath_body',[(2.65,5.3),(3.45,4.6)],.38),('private_gallery_body',[(10.5,5.0),(10.5,4.65),(16.9,4.65),(19.20,4.65),(21.60,4.8),(21.60,3.9)],.38)]]

(O/'SECTION_CONTRACT.json').write_text(json.dumps(contract,indent=2))
# Independently reopen the saved native, then parse the actual export. Both
# scripts write failures before raising; no pixel-approval claim is made here.
sys.path.insert(0,str(R));runpy.run_path(str(R/'verify_first_native.py'),run_name='__main__');runpy.run_path(str(R/'verify_first_export.py'),run_name='__main__');print('PLACED DELUXE SOURCE QA PASS',unit,flush=True)
