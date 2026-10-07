from pathlib import Path
import bpy,bmesh,math,json,hashlib,sys,runpy
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];CAT=Path('/workspace/shared/astraea-catalogue-continuation-20261002');RUN='008';PIN=json.loads((ROOT/'qa/INPUT_PINS.json').read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for p,h in PIN['inputs'].items():assert sha(p)==h,('Input changed',p)
SOURCE=ROOT/'source'/f'D05_forward_welcome_{RUN}.blend';EXPORT=ROOT/'exports'/f'D05_forward_welcome_architecture_{RUN}.glb';assert not SOURCE.exists()and not EXPORT.exists()
PRE=CAT/'assets/medical_forward_welcome_candidate_20261006';bpy.ops.wm.open_mainfile(filepath=str(PRE/'source/D05_forward_welcome_006.blend'));SCENE=bpy.context.scene
MATS={name:bpy.data.materials.get(name)for name in ['quiet_ivory','sage_acoustic','warm_sand','warm_walnut','champagne_metal','dark_rubber','ivory_enamel','clinical_ink','opal_lens']};assert all(MATS.values())
PARTS=[o for o in SCENE.objects if o.type=='MESH'and o.get('source_package')=='D05_forward_welcome_candidate'];BASE_NAMES={o.name for o in SCENE.objects};OLD=json.loads((PRE/'qa/SOURCE_MANIFEST_006.json').read_text());RETAINED=OLD['retained_component_instances'].copy();FIXTURES=OLD['fixture_sources'].copy();RECEIVERS=OLD['receiver_markers'].copy();CHANGES=[];PLANTS=[]
exec(compile((ROOT/'source/source_helpers.py').read_text(),str(ROOT/'source/source_helpers.py'),'exec'))

def remove(name):
 o=bpy.data.objects.get(name);assert o is not None,name
 if o in PARTS:PARTS.remove(o)
 bpy.data.objects.remove(o,do_unlink=True);CHANGES.append(name)

def retain_plant(id_,tag,at,yaw=0):
 row=PIN['retained_assets'][id_];src=CAT/row['source']
 with bpy.data.libraries.load(str(src),link=False)as(a,b):
  requested=tuple(a.objects);b.objects=list(requested)
 objects=[o for o in b.objects if o];assert len(objects)==len(requested)
 root=bpy.data.objects.new('INSTANCE_'+tag,None);SCENE.collection.objects.link(root);root.location=at;root.rotation_euler.z=yaw;root['retained_catalogue_id']=id_
 for o in objects:
  if not o.users_collection:SCENE.collection.objects.link(o)
  if o.parent is None:o.parent=root
  o.name=tag+'__'+o.name;o['retained_catalogue_id']=id_
 rec={'id':id_,'instance':tag,'source':str(src),'source_sha256':sha(src),'translation_source_xyz':list(at),'yaw_source_z_radians':yaw,'translation_world_xyz':world(at),'scale':[1,1,1],'objects':len(objects),'soil_receiver':('WELCOME_rear_layer_soil' if at[2]>.9 else 'WELCOME_planted_soil')if tag.startswith('Focal')else'ARRIVAL_planted_soil'};RETAINED.append(rec);PLANTS.append(rec);return root

# Put timber ribs below, into real roof receivers, rather than coplanar with panel undersides.
for o in PARTS:
 if o.name.startswith(('WAIT_fitted_rib_','SUPPORT_vault_rib_')):
  o.location.z-=.10;CHANGES.append(o.name)

# Expose the actual arrival identity on the core-facing side of the opaque bowed screen.
for name in ['ADMISSION_arrival_relief_backing','ADMISSION_original_arrival_relief']:remove(name)
box('ADMISSION_arrival_relief_backing',14.77,14.90,-15.32,-12.68,1.02,2.84,'warm_walnut',.035)
box('ARRIVAL_ivory_identity_field',14.90,14.925,-15.16,-12.84,1.20,2.67,'ivory_enamel',.025)
text('ADMISSION_original_arrival_relief','MEDICAL',(14.943,-14,2.29),.36,(math.pi/2,0,math.pi/2))
text('ARRIVAL_waiting_turn','WAITING  >',(14.945,-14,1.79),.23,(math.pi/2,0,math.pi/2))
text('ARRIVAL_quiet_care','CARE  /  ASSISTANCE',(14.945,-14,1.44),.13,(math.pi/2,0,math.pi/2))
# An opaque nested crown belongs to the same rounded return and points into the bend.
box('ARRIVAL_upper_crown_receiver',14.33,14.87,-15.45,-12.55,2.84,3.08,'sage_acoustic',.04)
box('ARRIVAL_upper_warm_reveal',14.87,14.96,-15.45,-12.55,2.87,2.96,'warm_walnut',.018)

soil=bpy.data.materials.new('botanical_soil');soil.use_nodes=True;soil['material_role']='botanical_soil';soil['metres_per_tile']=1
bs=soil.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.95;t=soil.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(CAT/'materials/botanical/botanical_soil.png'),check_existing=True);t.image.pack();t.interpolation='Closest';soil.node_tree.links.new(t.outputs['Color'],bs.inputs['Base Color']);MATS['botanical_soil']=soil

def planter(prefix,x0,x1,y0,y1,height):
 box(prefix+'_base',x0,x1,y0,y1,0,.14,'warm_walnut',.025)
 for label,a,b,c,d in [('front',x0,x1,y0,y0+.09),('back',x0,x1,y1-.09,y1),('left',x0,x0+.09,y0,y1),('right',x1-.09,x1,y0,y1)]:box(prefix+'_'+label,a,b,c,d,.10,height,'ivory_enamel',.018)
 box(prefix+'_planted_soil',x0+.09,x1-.09,y0+.09,y1-.09,height-.14,height-.06,'botanical_soil',0)
planter('ARRIVAL',14.48,15.13,-16.32,-15.12,.63)
for i,y in enumerate([-16.00,-15.47]):retain_plant('AST-BOT-003','ArrivalRosette_'+str(i),(14.81,y,.57),math.pi*i)

# The assistance ledge wraps a real planted well: counter and foliage do not share solid volume.
remove('WELCOME_crescent_supported_counter')
poly=[(4.35,3.70),(5.15,3.70),(5.15,2.60),(8.05,2.60),(8.05,3.70),(8.8,3.70),(8.8,2.70),(8.4,2.28),(7.5,2.0),(5.8,2.0),(4.85,2.25),(4.35,2.67)]
prism('WELCOME_crescent_supported_counter',poly,.90,.99,'warm_walnut',.035)
planter('WELCOME',5.16,8.04,2.65,3.76,.84)
box('WELCOME_rear_layer_soil',5.25,7.95,3.20,3.67,.77,1.00,'botanical_soil',0)
for label,x0,x1 in [('left',5.16,5.25),('right',7.95,8.04)]:box('WELCOME_rear_layer_retainer_'+label,x0,x1,3.19,3.76,.83,1.04,'ivory_enamel',.012)
box('WELCOME_rear_layer_back',5.16,8.04,3.67,3.76,.83,1.04,'ivory_enamel',.012)
retain_plant('AST-BOT-007','FocalFan',(6.60,2.95,.78),math.pi)
for i,(x,y,yaw)in enumerate([(5.67,3.25,-.18),(6.65,3.25,.18),(7.51,3.25,-.20)]):retain_plant('AST-BOT-002','FocalUnderstory_'+str(i),(x,y,1.00),yaw)
for i,(x,yaw)in enumerate([(5.75,math.pi+.02),(7.45,math.pi-.02)]):retain_plant('AST-BOT-007','FocalLayeredFan_'+str(i),(x,2.915,.78),yaw)
for i,x in enumerate([5.43,6.10,7.08,7.78]):retain_plant('AST-BOT-002','FocalRearBank_'+str(i),(x,3.25,1.00),.08 if i%2 else -.08)
for i,x in enumerate([5.41,5.98,6.38,7.00,7.76]):retain_plant('AST-BOT-002','FocalFrontBank_'+str(i),(x,2.88,.78),.13 if i%2 else -.13)
for i,(x,y)in enumerate([(5.42,2.94),(5.95,2.81),(6.42,2.81),(7.09,2.83),(7.78,2.96)]):retain_plant('AST-BOT-003','FocalRosette_'+str(i),(x,y,.78),i*.65)
# Move the former covered wall placard into the architectural canopy fascia.
for name in ['WELCOME_direction_field','WELCOME_primary_title','WELCOME_quiet_secondary','WELCOME_sign_bearing_5.38','WELCOME_sign_bearing_7.92']:remove(name)
box('WELCOME_direction_field',4.55,9.40,2.02,2.20,3.52,4.21,'sage_acoustic',.025)
text('WELCOME_primary_title','CARE & COMPANY',(6.98,2.008,3.94),.30,role='ivory_enamel')
text('WELCOME_quiet_secondary','WAITING  /  ASSISTANCE',(6.98,2.003,3.66),.15,role='ivory_enamel')
for x in [4.48,9.47]:box('WELCOME_canopy_fascia_bearing_'+str(x),x-.055,x+.055,2.01,2.25,3.49,4.22,'warm_walnut',.009)
# Two shaped overhead boundaries make a waiting group under a shared canopy, not a repeated corridor.
ys=[-3.88,-2.7,-1.7,-.3,.3,1.7,2.7,3.88]
def roof(y):return 4.66-max(0,abs(y)-.30)/3.58*.46
for i,x in enumerate([4.25,9.25]):
 profile=[(y,roof(y)-.14)for y in ys]+[(y,roof(y)+.025)for y in reversed(ys)];n=len(profile)
 mesh('WAIT_group_canopy_boundary_'+str(i),[(xx,y,z)for xx in[x-.11,x+.11]for y,z in profile],[tuple(reversed(range(n))),tuple(n+j for j in range(n))]+[(j,(j+1)%n,(j+1)%n+n,j+n)for j in range(n)],'warm_walnut',.012)
# Existing units retain identities, with two modest inward-facing gestures toward the garden.
for tag,at,yaw in [('WaitingSeat_01',(4.5,-2.88,0),math.radians(168)),('WaitingSeat_03',(9.7,-2.83,0),math.radians(195))]:
 ob=bpy.data.objects['INSTANCE_'+tag];ob.location=at;ob.rotation_euler.z=yaw;CHANGES.append(ob.name)
 for rec in RETAINED:
  if rec['instance']==tag:rec.update(translation_source_xyz=list(at),translation_world_xyz=world(at),yaw_source_z_radians=yaw)
# Re-aim existing housed sources only; no extra light or changed budget is invented.
for f in FIXTURES:
 if f['name']=='ADMISSION_lens_0':f['aim']=(14.94,-14,1.70)
 if f['name']=='WaitingSconce_0':f['aim']=(6.1,2.95,1.55)
 if f['name']=='WaitingSconce_1':f['aim']=(7.2,2.95,1.55)
SCENE['scope']='Uninstalled source008 finishing derivative of installed006 physical baseline; visual acceptance pending. No clinical/repair gameplay or production floor.'
SCENE['fixture_clearance_note']='Protected passage remains2.4m high; waiting overhead ribs>=4.06m, focal canopy fascia outside route>=3.49m; no clinical/species fit acceptance.'
SCENE['catalogue_id']='Existing unregistered medical architecture candidate; retained component identities unchanged'
bpy.context.view_layer.update();records=[]
for o in PARTS:
 verts=[o.matrix_world@v.co for v in o.data.vertices];records.append({'name':o.name,'material_role':o.get('material_role'),'bounds_source_xyz':[list(map(min,zip(*verts))),list(map(max,zip(*verts)))],'vertices':len(verts)})
REPORT=dict(OLD);REPORT.update(scope=SCENE['scope'],run=RUN,new_editable_parts=len(PARTS),retained_component_instances=RETAINED,new_part_records=records,fixture_sources=FIXTURES,receiver_markers=RECEIVERS,source_preimage=str(PRE/'source/D05_forward_welcome_006.blend'),source_preimage_sha256=PIN['inputs'][str(PRE/'source/D05_forward_welcome_006.blend')],explicit_changed_objects=sorted(set(CHANGES)),new_objects=sorted({o.name for o in SCENE.objects}-BASE_NAMES),planting_instances=PLANTS,arrival_visible_face_source_x=14.943,all_new_planting_is_retained_families=True,receiving_core_context='Installed006 core/floor connection retained unchanged; inherited aperture proposal remains source history only.')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE));bpy.ops.object.select_all(action='DESELECT')
for o in PARTS:o.select_set(True)
for o in SCENE.objects:
 if o.name.startswith('DATUM_')and o.get('source_package')=='D05_forward_welcome_candidate':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(EXPORT),export_format='GLB',export_yup=True,use_selection=True,export_extras=True,export_apply=True,export_cameras=False,export_lights=False)
REPORT.update(source=str(SOURCE),source_sha256=sha(SOURCE),architecture_export=str(EXPORT),export_sha256=sha(EXPORT),generator_sha256=sha(__file__))
(ROOT/'qa/SOURCE_MANIFEST_008.json').write_text(json.dumps(REPORT,indent=2)+'\n');runpy.run_path(str(ROOT/'source/check_loaded_source_fit.py'))
for p,h in PIN['inputs'].items():assert sha(p)==h
print('SOURCE_FINISH_008_READY',str(SOURCE),str(EXPORT),len(PARTS),len(RETAINED),flush=True)
