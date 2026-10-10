"""Distinct quiet/aquatic Deluxe source studies inside fixed existing reservations.
Reuse reviewed living/service core; replace the rest spatial composition and preserve
all four proposed reservation identities. No biological/capacity certification.
"""
import bpy,bmesh,pathlib,json,hashlib,math,sys,copy,runpy
from mathutils import Matrix,Vector
R=pathlib.Path(__file__).resolve().parent;I=R/'inputs';unit=int(sys.argv[sys.argv.index('--')+1]);kind=sys.argv[sys.argv.index('--')+2];assert kind in ['quiet','aquatic'];O=R/'sections'/f'{unit}_deluxe';O.mkdir(parents=True,exist_ok=True);assert not (O/f'{unit}_deluxe.blend').exists(),'Preserve existing source outputs; use an explicit revision'
sys.path.insert(0,str(R));from editable_label import repair_label
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();base_dir=R/'sections/876_deluxe';base_path=base_dir/'876_deluxe.blend';base=json.loads((base_dir/'SECTION_CONTRACT.json').read_text());assert sha(base_path)==base['native_sha256'];assert json.loads((base_dir/'PIXEL_REVIEW.json').read_text())['actual_views_inspected']==6
row=next(x for x in json.loads((R/'LUXURY_81_INVENTORY.json').read_text())['records'] if x['identity']['source_envelope_index']==unit);rsv=row['reservation'];assert rsv['tier']=='deluxe' and rsv['nominal_depth_m']==18 and row['identity']['existing_partial_construction'] is None
bpy.ops.wm.open_mainfile(filepath=str(base_path));scene=bpy.context.scene;contract=copy.deepcopy(base);contract['identity']=row['identity'];contract['reservation']=rsv
# Author the altered family in the already reviewed local frame, then place it
# rigidly. LocalU points outward; localV runs along the arrival/living edge.
def xyz(u,v,h):return Vector((-43-u,459-v,102+h))
def w(u,v,h):return [-43-u,102+h,-459+v]
imports=contract['imports'];parts=list(scene.objects);markers=[x for x in contract['markers'] if x['kind']!='proposed_rest_anchor'];removed=set()
def remove(names):
 chosen=[x for x in parts if any(x.name.startswith(n) for n in names)]
 for ob in chosen:removed.add(ob.name)
 parts[:]=[x for x in parts if x not in chosen]
 for ob in reversed(chosen):
  if ob.name in scene.objects:bpy.data.objects.remove(ob,do_unlink=True)
remove(['RestAlcove','RestHeadBacking','RestSideCheek','RestCrown','PersonalStow','RestReading','DATUM_RestReading','DATUM_rest_'])
imports[:]=[x for x in imports if not any(n in removed for n in x.get('part_names',[]))];markers[:]=[x for x in markers if x['name'] not in removed]
materials={k:bpy.data.materials['ASTRAEA_'+k] for k in ['ivory_enamel','warm_walnut','warm_stone','champagne_metal','teal_weave']};materials['lens']=bpy.data.materials['G2_WarmFixtureLens']
def mesh(name,points,faces,role,category='fitted_rest'):
 me=bpy.data.meshes.new(name);me.from_pydata([xyz(*p) for p in points],[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();uv=me.uv_layers.new(name='MetreScaled')
 for face in me.polygons:
  n=face.normal.normalized();u=(Vector((1,0,0))-n*n.x).normalized() if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u).normalized()
  for li in face.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p.dot(u),p.dot(v))
 me.materials.append(materials[role]);ob=bpy.data.objects.new(name,me);scene.collection.objects.link(ob);ob['group2_kind']=category;parts.append(ob);return ob
faces=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def box(name,u0,u1,v0,v1,h0,h1,role,category='fitted_rest'):return mesh(name,[(u,v,h) for h in [h0,h1] for u,v in [(u0,v0),(u1,v0),(u1,v1),(u0,v1)]],faces,role,category)
cat={x['catalogue_id']:x for x in json.loads((I/'BlenderCatalogue/catalogue_manifest.json').read_text())['assets']}
def asset(aid,u,v,h=0,yaw=0,label='Rest'):
 item=cat[aid];p=I/'BlenderCatalogue'/item['source'];assert sha(p)==item['source_sha256'];before=set(scene.objects)
 with bpy.data.libraries.load(str(p),link=False) as (a,b):b.objects=list(a.objects)
 loaded=[x for x in b.objects if x and 'preview' not in x.name.lower() and x.type not in ['CAMERA','LIGHT'] and not x.hide_render]
 for ob in list(b.objects):
  if ob and 'preview' in ob.name.lower():bpy.data.objects.remove(ob,do_unlink=True)
 for ob in loaded:scene.collection.objects.link(ob);ob.name=label+'_'+ob.name
 uv_repairs=[]
 for ob in loaded:
  if ob.type=='MESH' and not ob.data.uv_layers:
   me=ob.data;uv=me.uv_layers.new(name='RetainedDerivativeMetreUV')
   for face in me.polygons:
    axis=max(range(3),key=lambda k:abs(face.normal[k]));axes=[k for k in range(3) if k!=axis]
    for li in face.loop_indices:
     uvpt=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(uvpt[axes[0]],uvpt[axes[1]])
   uv_repairs.append(ob.name)
 bpy.context.view_layer.update();old={x:x.matrix_world.copy() for x in loaded};dg=bpy.context.evaluated_depsgraph_get();bottoms=[]
 for ob in loaded:
  if ob.type not in ['MESH','FONT','CURVE']:continue
  e=ob.evaluated_get(dg);me=e.to_mesh();bottoms.extend((e.matrix_world@x.co).z for x in me.vertices);e.to_mesh_clear()
 pivot_bottom=min(bottoms);matrix=Matrix.Translation(xyz(u,v,h-pivot_bottom))@Matrix.Rotation(math.pi+yaw,4,'Z')
 for ob in loaded:
  if ob.parent not in loaded:ob.parent=None;ob.matrix_world=matrix@old[ob]
  ob['retained_catalogue_id']=aid;ob['group2_kind']='retained_rest_fixture';parts.append(ob)
 bpy.context.view_layer.update();imports.append({'catalogue_id':aid,'source_path':str(p.relative_to(I)),'source_sha256':sha(p),'world_xyz':w(u,v,h),'source_yaw':math.pi+yaw,'part_names':[x.name for x in loaded],'isolated_derivative_repairs':{'missing_metre_UV_added_to':uv_repairs,'retained_pivot_bottom_m':pivot_bottom,'source_placement_vertical_offset_m':-pivot_bottom,'reason':'Measured source origin is not its physical bearing; original Catalogue bytes preserved'}});return loaded
rests=[]
def rest(index,u,v,h,token):
 name=f'DATUM_rest_{index+1:02}';ob=bpy.data.objects.new(name,None);scene.collection.objects.link(ob);ob.location=xyz(u,v,h);ob['kind']='proposed_rest_anchor';ob['reservation_id']=row['identity']['proposed_rest_slot_ids'][index];parts.append(ob);rests.append((ob,token));markers.append({'name':name,'world_xyz':w(u,v,h),'kind':'proposed_rest_anchor','reservation_id':ob['reservation_id'],'contact_source':'Actual evaluated retained support surface; no occupancy/body fit asserted'})
def lamp(name,u,v,h,target,ceiling):
 mount=box(name+'_Bracket',u-.09,u+.09,v-.09,v+.09,h,ceiling+.025,'champagne_metal','fixture');mount['source_mount_target']=target;box(name+'_Lens',u-.22,u+.22,v-.22,v+.22,h-.04,h+.015,'lens','fixture');data=bpy.data.lights.new(name,'AREA');data.energy=85;data.color=(1,.78,.53);data.shape='DISK';data.size=.8;ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob);ob.location=xyz(u,v,h-.07);parts.append(ob);marker=bpy.data.objects.new('DATUM_'+name+'_Light',None);scene.collection.objects.link(marker);marker.location=xyz(u,v,h-.07);marker['kind']='fixture_light';marker['energy_w']=85;parts.append(marker);markers.append({'name':marker.name,'world_xyz':w(u,v,h-.07),'kind':'fixture_light','energy_w':85})
if kind=='quiet':
 token='Concave stretched rest membrane'
 box('QuietRestCrown',5.43,16.08,.65,4.10,2.72,2.95,'ivory_enamel');box('QuietFittedBacking',5.43,16.08,.37,.62,0,2.86,'warm_walnut')
 for j,u in enumerate([8.02,10.70,13.38]):box(f'QuietBetweenBayPier{j}',u-.05,u+.05,.65,4.10,0,2.72,'warm_walnut')
 for j,u in enumerate([6.68,9.36,12.04,14.72]):asset('AST-RST-QC-001',u,2.30,0,0,f'QuietCocoon{j}');rest(j,u,2.30,.61,token);lamp(f'QuietReading{j}',u,2.75,2.58,'QuietRestCrown',2.72)
 description='Four individually open quiet rest fixtures under a shared lowered frieze, three fitted dividing piers, a sheltered front approach and retained private dining/library/crescent salon. Visual acoustic intent only.'
 routes=[('main_loaded_cart',[(2.65,5.30),(5.90,5.30),(5.90,5.00),(10.5,5.00),(10.5,7.25),(13,7.25)],.82)]+[(f'quiet_rest_{j+1}_approach',[(u,5.0),(u,4.35)],.38) for j,u in enumerate([6.68,9.36,12.04,14.72])]
else:
 token='Contoured broad immersed rest support'
 # Two wide retained support fixtures keep four proposed anchor reservations;
 # they do not certify two actors per cradle. Root must resolve actual bodies,
 # fluid/environment and physical rest ledger before any capacity assignment.
 remove(['ReadingChair'])
 delta=Matrix.Translation(Vector((0,-.60,0)));group=[x for x in parts if x.name.startswith(('FittedOvalDiningTop','DiningPedestal','DiningSplayed','PrivateDiningChair','PrivateDiningOpal'))]
 old={x:x.matrix_world.copy() for x in group}
 for ob in group:
  if ob.parent not in group:ob.matrix_world=delta@old[ob]
 for imp in imports:
  if any(n.startswith('PrivateDiningChair') for n in imp.get('part_names',[])):imp['world_xyz'][2]+=.60
 box('AquaticRearServiceFacing',5.65,15.75,.30,.342,.02,1.30,'ivory_enamel','aquatic_service')
 for j,u in enumerate([7.55,13.10]):
  asset('AST-RST-AQ-001',u,2.25,0,0,f'AquaticCradle{j}')
  for k,du in enumerate([-.588,.588]):rest(j*2+k,u+du,2.26,.29,token)
  lamp(f'AquaticBayLight{j}',u,2.25,3.05,'RisingLivingRoof',3.25+(u-.40)/7.60*.50 if u<=8 else 3.75+(u-8)/9.54*.53)
 description='Paired contained aquatic rest-support fixtures at the fore edge, a wider dry front loop, separate side care approaches and dining shifted toward the private library/salon. Source water is visual only; no live fluid, actor pairing or biological fit.'
 routes=[('main_loaded_cart',[(2.65,5.30),(5.90,5.30),(5.90,5.60),(10.5,5.60),(10.5,7.25),(13,7.25)],.82),('aquatic_rest_A_approach',[(7.55,5.6),(7.55,4.8)],.38),('aquatic_rest_B_approach',[(13.10,5.6),(13.10,4.8)],.38),('aquatic_care_A',[(9.6,5.6),(9.6,2.72)],.38),('aquatic_care_B',[(15.15,5.6),(15.15,2.72)],.38)]
# Actual support contacts from the retained evaluated meshes; ignore decorative
# seams and the visual water surface when selecting the rest contact target.
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
for ob,token in rests:
 hits=[]
 for other in parts:
  if other.type!='MESH' or token not in other.name:continue
  e=other.evaluated_get(dg);inv=e.matrix_world.inverted();hit,loc,norm,ix=e.ray_cast(inv@(ob.location+Vector((0,0,1))),inv.to_3x3()@Vector((0,0,-1)))
  if hit:hits.append((e.matrix_world@loc).z)
 assert hits,ob.name;ob.location.z=max(hits);next(x for x in markers if x['name']==ob.name)['world_xyz'][1]=max(hits)
bpy.context.view_layer.update()
poly=rsv['proposed_floor_boundary'];xmin=min(x[0] for x in poly);xmax=max(x[0] for x in poly);zmin=min(x[1] for x in poly);zmax=max(x[1] for x in poly);assert xmax-xmin==18 and zmax-zmin==10;starboard=xmin>0
transform=Matrix.Translation(Vector((xmin-43,459-zmax,0)))@Matrix.Rotation(math.pi,4,'Z') if starboard else Matrix.Translation(Vector((xmax+43,-zmin-459,0)))
def moved(w):
 p=transform@Vector((w[0],-w[2],w[1]));return [p.x,p.z,-p.y]
old={x:x.matrix_world.copy() for x in parts}
for ob in parts:
 if ob.parent not in parts:ob.matrix_world=transform@old[ob]
 ob['source_scope']=f'Group2/{unit}';ob['source_envelope_index']=unit
 if ob.type=='FONT':
  ob.data.body=f'DELUXE {unit}'
  repair_label(ob)
bpy.context.view_layer.update();scene.cycles.samples=4;scene.cycles.device='CPU';scene.cycles.use_denoising=True;scene.render.threads_mode='FIXED';scene.render.threads=2
# Render-only receiving slab/context; never packed as room geometry.
me=bpy.data.meshes.new('PREVIEW_COMPILER_FLOOR');me.from_pydata([(x,-z,h) for h in [101.82,102] for x,z in poly],[],faces);me.update();preview=bpy.data.objects.new('PREVIEW_COMPILER_FLOOR',me);scene.collection.objects.link(preview);me.materials.append(materials['warm_stone']);context_path=I/'Game/assets/models/AST-RES-TIDAL_floor_winding_r002.glb';before=set(scene.objects);bpy.ops.import_scene.gltf(filepath=str(context_path));context=set(scene.objects)-before
camera=bpy.data.objects.new('QA_EyeLevelCamera',bpy.data.cameras.new('QA_EyeLevelCamera'));scene.collection.objects.link(camera);scene.camera=camera;camera.data.lens=20;camera.data.clip_start=.05;camera.data.clip_end=100;views=[]
for view in base['source_views']:
 pos=moved(view['camera_world_xyz']);target=moved(view['target_world_xyz']);camera.location=(pos[0],-pos[2],pos[1]);camera.rotation_euler=(Vector((target[0],-target[2],target[1]))-camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(O/view['file']);bpy.ops.render.render(write_still=True);views.append({'name':view['name'],'file':view['file'],'sha256':sha(O/view['file']),'camera_world_xyz':pos,'target_world_xyz':target,'height_above_local_floor':1.65,'render_samples':4})
for ob in context:bpy.data.objects.remove(ob,do_unlink=True)
bpy.data.objects.remove(preview,do_unlink=True);bpy.data.objects.remove(camera,do_unlink=True);scene.camera=None;bpy.ops.file.pack_all();bpy.ops.object.select_all(action='DESELECT')
for ob in parts:
 if ob.type not in ['LIGHT','CAMERA']:ob.select_set(True)
native=O/f'{unit}_deluxe.blend';export=O/f'{unit}_deluxe.glb';bpy.ops.wm.save_as_mainfile(filepath=str(native));bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False,export_apply=True)
contract.update(status='BUILT_VARIANT_PENDING_ACTUAL_QA_AND_PIXEL_REVIEW',architecture=description,imports=imports,markers=markers,source_views=views,native_sha256=sha(native),export_sha256=sha(export),rebuild_source_sha256=sha(pathlib.Path(__file__)),rest_contact_mesh_tokens=[token],source_routes=routes,habitat_study=kind,species_assignment=None);contract['local_frame']={'origin_xyz':[xmin if starboard else xmax,102,zmax if starboard else zmin],'u_axis':[1 if starboard else -1,0,0],'v_axis':[0,0,-1 if starboard else 1],'h_axis':[0,1,0]};contract['floor_proposal']['boundary']=poly;contract['derivative_source']={'reviewed_template':'sections/876_deluxe/876_deluxe.blend','template_sha256':sha(base_path),'variant':kind,'rebuild_script':'build_deluxe_variant.py','scale':1,'reflection':False,'scope':'Distinct source capability study only; four existing proposed slot IDs preserved, no accepted actor/capacity/species assignment'}
for imp in imports:
 if 'world_xyz' in imp:imp['world_xyz']=moved(imp['world_xyz']);imp['source_yaw']+=math.pi if starboard else 0
for marker in markers:marker['world_xyz']=moved(marker['world_xyz'])
(O/'SECTION_CONTRACT.json').write_text(json.dumps(contract,indent=2));sys.path.insert(0,str(R));runpy.run_path(str(R/'verify_first_native.py'),run_name='__main__');runpy.run_path(str(R/'verify_first_export.py'),run_name='__main__');print('VARIANT SOURCE QA PASS',unit,kind,flush=True)
