"""Full house source builder. Linked rooms/plants, editable architecture, compact export."""
from pathlib import Path
import bpy,json,hashlib,math,sys,collections as pycollections
from mathutils import Matrix,Vector
S=Path(__file__).resolve().parents[1];OUT=S/'outputs/sf_house_r002';PLAN=OUT/'PLAN.json';B=S.parent/'residential-batch-neighborhood-20261006/scale_domestic_r011';CAT=next(q for q in Path(__file__).resolve().parents if (q/'catalogue_manifest.json').is_file())
assert not (OUT/'house.blend').exists(),'Fresh source revision required'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();plan=json.loads(PLAN.read_text());pins={str(p):sha(p)for p in [PLAN,S/'source/retained_court_primitives.py']}
ns={'__file__':str(OUT/'source_helpers.py')};exec(compile((S/'source/retained_court_primitives.py').read_text(),'retained_court_primitives.py','exec'),ns)
scene=bpy.context.scene;mesh=ns['mesh'];beam=ns['beam'];mat=ns['mat'];xyz=ns['xyz'];arch=[]
for i,p in enumerate(plan['parts']):
 if p['kind']=='mesh':o=mesh(p['name'],p['verts'],p['faces'],p['role'],'02',p['category'])
 else:o=beam(p['name'],p['a'],p['b'],p['width'],p['depth'],p['role'],'02',p['category'])
 o['court_owner']=plan['house_id'];o['source_part_id']=p['name'];o['source_plan_sha256']=pins[str(PLAN)];o['functional_status']='source_construction_unadopted';arch.append(o)
 if i%2000==0:print('ARCHITECTURE_PARTS',i,flush=True)
# Collections link the original evaluated sources; no repeated heavyweight mesh export.
room_col=bpy.data.collections.new('10_ActualRegularFamilyInteriors_83');scene.collection.children.link(room_col)
asset_col=bpy.data.collections.new('11_ActualCataloguePlantingAndFurniture');scene.collection.children.link(asset_col)
shared={};linked_source_pins={}
def linked(source,key):
 source=Path(source)
 if key in shared:return shared[key]
 linked_source_pins[str(source)]=sha(source)
 with bpy.data.libraries.load(str(source),link=True)as(src,dst):dst.objects=list(src.objects)
 col=bpy.data.collections.new('SHARED_'+key)
 for o in dst.objects:
  if o is not None and o.type in ['MESH','EMPTY','CURVE']:col.objects.link(o)
 shared[key]=col;return col
for r in plan['rooms']:
 proto=plan['room_prototypes'][r['source_recipe_key']];source=B/proto['source_blend'];assert sha(source)==proto['source_blend_sha256']
 o=bpy.data.objects.new(r['rebuild_identity'],None);o.instance_type='COLLECTION';o.instance_collection=linked(source,r['source_recipe_key']);x,y,z=r['source_origin_world_xyz'];o.location=(x,-z,y);o.rotation_euler.z=r['source_yaw_godot'];room_col.objects.link(o)
 o['census_source_index']=r['census_source_index'];o['rest_slot_ids']=json.dumps([a['unit_slot_key']for a in r['anchor_bindings']]);o['hotel_variant_status']='Corrected shared family construction input; Quiet Grove-specific interior successor still being authored';o['runtime_installed']=False
manifest=json.loads((CAT/'catalogue_manifest.json').read_text());assets={a['catalogue_id']:a for a in manifest['assets']}
for r in plan['asset_instances']:
 a=assets[r['catalogue_id']];source=CAT/a['source'];assert sha(source)==a['source_sha256']
 o=bpy.data.objects.new(r['name'],None);o.instance_type='COLLECTION';o.instance_collection=linked(source,r['catalogue_id']);o.location=xyz(r['world_xyz']);o.rotation_euler.z=math.radians(r['yaw']);o.scale=(r['scale'],)*3;asset_col.objects.link(o);o['purpose']=r['purpose'];o['catalogue_id']=r['catalogue_id']
for r in plan['lights']:
 d=bpy.data.lights.new(r['name'],'AREA');d.energy=r['energy'];d.color=(1,.88,.73);d.shape='DISK';d.size=r['size'];o=bpy.data.objects.new(r['name'],d);ns['collections']['08'].objects.link(o);o.location=xyz(r['world_xyz']);o.rotation_euler=(Vector(xyz(r['target']))-o.location).to_track_quat('-Z','Y').to_euler();o['source_fixture']=r['name'];o['runtime_light_budget_changed']=False
# Explicit planning datums are hidden from beauty images; no false specialty/VIP facades.
reserved=bpy.data.collections.new('12_UnbuiltSpecialtyVIPReservations_NotRoomModels');scene.collection.children.link(reserved)
for r in plan['D17_replacement_reservations']:
 p=r['proposed_floor_boundary'];o=bpy.data.objects.new('RESERVED_VIP_'+str(r['source_envelope_index']),None);o.empty_display_type='CUBE';o.empty_display_size=1;o.location=xyz((sum(x for x,z in p)/len(p),104,sum(z for x,z in p)/len(p)));o['reservation']=json.dumps(r);reserved.objects.link(o)
# No dependency pointer is allowed to change the linked originals.
for lib in bpy.data.libraries:lib.filepath=bpy.path.relpath(lib.filepath,start=str(OUT))
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.06,.07,.08,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.20
scene['scope']='147-unit five-level Quiet Grove house source:83actual linked regular/family interiors,64specialty/VIP reserved. No standalone pilot adoption.'
scene['receiving_limit']='Two transfer rows and affected longitudinal spans withheld pending verified WP06 Long Library envelope. No final support or load acceptance.'
scene['theme_status']='Quiet Grove lobby/gallery architecture authored; linked room recipes remain inputs pending specific hotel-room successor.'
scene['plan_sha256']=sha(PLAN);scene.render.threads_mode='FIXED';scene.render.threads=2
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'house.blend'))
# Export compact static architecture by source role/category/25m cell. Linked components stay separate.
export_col=bpy.data.collections.new('EXPORT_COMPACT_ARCHITECTURE');scene.collection.children.link(export_col);groups={}
for ob,p in zip(arch,plan['parts']):
 coords=[ob.matrix_world@v.co for v in ob.data.vertices];cy=sum(v.y for v in coords)/len(coords);cz=sum(v.z for v in coords)/len(coords)
 key=(p['role'],p['category'],int(cy//25),int((cz-78)//4.5));g=groups.setdefault(key,{'verts':[],'faces':[],'uv':[],'parts':[]});offset=len(g['verts']);faceoff=len(g['faces']);g['verts'].extend(tuple(v)for v in coords);g['faces'].extend(tuple(offset+j for j in face.vertices)for face in ob.data.polygons);g['uv'].extend(tuple(u.uv)for u in ob.data.uv_layers.active.data);g['parts'].append({'source_part_id':p['name'],'vertex_start':offset,'vertex_count':len(coords),'face_start':faceoff,'face_count':len(ob.data.polygons)})
bpy.ops.object.select_all(action='DESELECT');export_rows=[]
for i,(key,g)in enumerate(groups.items()):
 me=bpy.data.meshes.new('QG_Batch_'+str(i));me.from_pydata(g['verts'],[],g['faces']);me.materials.append(mat(key[0]));uv=me.uv_layers.new(name='MetreScaled');assert len(uv.data)==len(g['uv'])
 for a,b in zip(uv.data,g['uv']):a.uv=b
 ob=bpy.data.objects.new('QG_Batch_'+str(i),me);export_col.objects.link(ob);ob.select_set(True);ob['source_part_ranges']=g['parts'];ob['role']=key[0];ob['category']=key[1];ob['source_plan_sha256']=sha(PLAN);ob['runtime_collision']=key[1]not in ['soil','fixture'];export_rows.append({'name':ob.name,'role':key[0],'category':key[1],'source_parts':len(g['parts']),'vertices':len(g['verts']),'triangles':sum(len(f)-2 for f in g['faces'])})
bpy.ops.export_scene.gltf(filepath=str(OUT/'architecture.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
for source,h in linked_source_pins.items():assert sha(source)==h
assert sha(PLAN)==pins[str(PLAN)]
report={'status':'FULL_HOUSE_SOURCE_BUILT_NOT_INSTALLED','house_units':147,'actual_regular_family_room_instances':83,'unbuilt_specialty_vip':64,'architecture_source_parts':len(arch),'compact_batches':len(groups),'catalogue_asset_instances':len(plan['asset_instances']),'shared_source_libraries':len(shared),'shared_source_sha256':linked_source_pins,'plan_sha256':sha(PLAN),'house_blend_sha256':sha(OUT/'house.blend'),'architecture_glb_sha256':sha(OUT/'architecture.glb'),'architecture_bytes':(OUT/'architecture.glb').stat().st_size,'export_batches':export_rows,'source_inputs_unchanged':True,'Game_or_Catalogue_writes':False,'limits':plan['limits']+['Source-room hotel-specific revisions pending; current83are genuine generic corrected inputs','Receiving library interface explicitly unresolved; no full support claim']}
(OUT/'SOURCE_RECEIPT.json').write_text(json.dumps(report,indent=2)+'\n');print('FULL_HOUSE_SOURCE_COMPLETE',len(arch),len(groups),flush=True)
