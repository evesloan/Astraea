"""Editable Sunset architecture, linked authored interiors and compact GLB."""
from pathlib import Path
import bpy,json,hashlib,math,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[1];S=R.parent;OUT=R/'outputs/house_r002';PLAN=OUT/'PLAN.json';CAT=Path('/workspace/shared/astraea-catalogue-continuation-20261002');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not(OUT/'house.blend').exists(),'Use a fresh revision, preserve existing work'
plan=json.loads(PLAN.read_text());interiors=R/'outputs/interiors_r002';batch=json.loads((interiors/'BATCH_RECEIPT.json').read_text());proto={r['prototype']:r for r in batch['prototypes']};pins={str(p):sha(p)for p in[PLAN,S/'source/retained_court_primitives.py',interiors/'BATCH_RECEIPT.json']}
ns={'__file__':str(OUT/'source_helpers.py')};exec(compile((S/'source/retained_court_primitives.py').read_text(),'retained_court_primitives.py','exec'),ns)
scene=bpy.context.scene;mesh=ns['mesh'];beam=ns['beam'];mat=ns['mat'];xyz=ns['xyz'];arch=[]
for i,p in enumerate(plan['parts']):
 o=mesh(p['name'],p['verts'],p['faces'],p['role'],'02',p['category'])if p['kind']=='mesh'else beam(p['name'],p['a'],p['b'],p['width'],p['depth'],p['role'],'02',p['category'])
 o['court_owner']=plan['house_id'];o['source_part_id']=p['name'];o['source_plan_sha256']=sha(PLAN);o['functional_status']='Sunset source construction unadopted';arch.append(o)
 if i%2000==0:print('SUNSET_ARCHITECTURE_PARTS',i,flush=True)
roomcol=bpy.data.collections.new('10_AuthoredSunsetInteriors_83');scene.collection.children.link(roomcol);assetcol=bpy.data.collections.new('11_RootedPlantingAndFurniture');scene.collection.children.link(assetcol);shared={};sourcepins={}
def linked(source,key):
 source=Path(source)
 if key in shared:return shared[key]
 sourcepins[str(source)]=sha(source)
 with bpy.data.libraries.load(str(source),link=True)as(src,dst):dst.objects=list(src.objects)
 col=bpy.data.collections.new('SHARED_'+key)
 for o in dst.objects:
  if o is not None and o.type in['MESH','EMPTY','CURVE']:col.objects.link(o)
 shared[key]=col;return col
for r in plan['rooms']:
 key=r['source_recipe_key'];source=interiors/key/'assembly.blend';assert sha(source)==proto[key]['files']['assembly.blend']
 o=bpy.data.objects.new(r['rebuild_identity'],None);o.instance_type='COLLECTION';o.instance_collection=linked(source,key);x,y,z=r['source_origin_world_xyz'];o.location=(x,-z,y);o.rotation_euler.z=r['source_yaw_godot'];roomcol.objects.link(o);o['census_source_index']=r['census_source_index'];o['rest_slot_ids']=json.dumps([a['unit_slot_key']for a in r['anchor_bindings']]);o['hotel_variant']=key;o['runtime_installed']=False
manifest=json.loads((CAT/'catalogue_manifest.json').read_text());assets={a['catalogue_id']:a for a in manifest['assets']}
for r in plan['asset_instances']:
 a=assets[r['catalogue_id']];source=CAT/a['source'];assert sha(source)==a['source_sha256'];o=bpy.data.objects.new(r['name'],None);o.instance_type='COLLECTION';o.instance_collection=linked(source,r['catalogue_id']);o.location=xyz(r['world_xyz']);o.rotation_euler.z=math.radians(r['yaw']);o.scale=(r['scale'],)*3;assetcol.objects.link(o);o['purpose']=r['purpose'];o['catalogue_id']=r['catalogue_id']
for r in plan['lights']:
 d=bpy.data.lights.new(r['name'],'AREA');d.energy=r['energy'];d.color=(1,.88,.73);d.shape='DISK';d.size=r['size'];o=bpy.data.objects.new(r['name'],d);ns['collections']['08'].objects.link(o);o.location=xyz(r['world_xyz']);o.rotation_euler=(Vector(xyz(r['target']))-o.location).to_track_quat('-Z','Y').to_euler();o['source_fixture']=r['name'];o['runtime_light_budget_changed']=False
reserved=bpy.data.collections.new('12_UnbuiltSpecialtyVIP_64_NotRoomModels');scene.collection.children.link(reserved)
cross=json.loads((S.parent/'residential-neighborhood-audit-20261007/ALL_1000_NEIGHBORHOOD_CROSSWALK.json').read_text())['records'];roomids={r['census_source_index']for r in plan['rooms']};vips={r['source_envelope_index']:r for r in plan['D17_replacement_reservations']}
for r in cross:
 if r['house']!=plan['house_id']or r['source_envelope_index']in roomids:continue
 rr=vips.get(r['source_envelope_index'],r);o=bpy.data.objects.new('UNBUILT_RESERVATION_'+str(r['source_envelope_index']),None);o.empty_display_type='CUBE';o.empty_display_size=1;o['reservation']=json.dumps(rr);o['geometry_status']='UNBUILT_RESERVATION_NOT_ACCEPTED_INTERIOR';reserved.objects.link(o)
for lib in bpy.data.libraries:lib.filepath=bpy.path.relpath(lib.filepath,start=str(OUT))
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.06,.07,.08,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.20
scene['scope']='Full147-unit Sunset Conservatory source:83 authored linked interiors,47 specialty+17 VIP explicitly unbuilt';scene['receiving_limit']='All base receiving support held; D12 Vesper protected; no structural load acceptance';scene['plan_sha256']=sha(PLAN);scene.render.threads_mode='FIXED';scene.render.threads=2;scene.cycles.use_denoising=False
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'house.blend'))
exportcol=bpy.data.collections.new('EXPORT_COMPACT_ARCHITECTURE');scene.collection.children.link(exportcol);groups={}
for ob,p in zip(arch,plan['parts']):
 coords=[ob.matrix_world@v.co for v in ob.data.vertices];cy=sum(v.y for v in coords)/len(coords);cz=sum(v.z for v in coords)/len(coords);key=(p['role'],p['category'],int(cy//25),int((cz-78)//4.5));g=groups.setdefault(key,{'verts':[],'faces':[],'uv':[],'parts':[]});off=len(g['verts']);foff=len(g['faces']);g['verts'].extend(tuple(v)for v in coords);g['faces'].extend(tuple(off+j for j in f.vertices)for f in ob.data.polygons);g['uv'].extend(tuple(u.uv)for u in ob.data.uv_layers.active.data);g['parts'].append({'source_part_id':p['name'],'vertex_start':off,'vertex_count':len(coords),'face_start':foff,'face_count':len(ob.data.polygons)})
bpy.ops.object.select_all(action='DESELECT');exports=[]
for i,(key,g)in enumerate(groups.items()):
 me=bpy.data.meshes.new('SC_Batch_'+str(i));me.from_pydata(g['verts'],[],g['faces']);me.materials.append(mat(key[0]));uv=me.uv_layers.new(name='MetreScaled');assert len(uv.data)==len(g['uv'])
 for a,b in zip(uv.data,g['uv']):a.uv=b
 ob=bpy.data.objects.new('SC_Batch_'+str(i),me);exportcol.objects.link(ob);ob.select_set(True);ob['source_part_ranges']=g['parts'];ob['role']=key[0];ob['category']=key[1];ob['source_plan_sha256']=sha(PLAN);ob['runtime_collision']=key[1]not in['soil','fixture','water'];exports.append({'name':ob.name,'role':key[0],'category':key[1],'source_parts':len(g['parts']),'vertices':len(g['verts']),'triangles':sum(len(f)-2 for f in g['faces'])})
bpy.ops.export_scene.gltf(filepath=str(OUT/'architecture.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
assert all(sha(p)==h for p,h in{**sourcepins,**pins}.items())
report={'status':'FULL_HOUSE_SOURCE_BUILT_NOT_INSTALLED','house_units':147,'authored_Sunset_room_instances':83,'unbuilt_specialty_vip':64,'architecture_source_parts':len(arch),'compact_batches':len(groups),'catalogue_asset_instances':len(plan['asset_instances']),'shared_source_libraries':len(shared),'shared_source_sha256':sourcepins,'plan_sha256':sha(PLAN),'house_blend_sha256':sha(OUT/'house.blend'),'architecture_glb_sha256':sha(OUT/'architecture.glb'),'architecture_bytes':(OUT/'architecture.glb').stat().st_size,'export_batches':exports,'source_inputs_unchanged':True,'Game_or_Catalogue_writes':False,'limits':plan['limits']}
(OUT/'SOURCE_RECEIPT.json').write_text(json.dumps(report,indent=2)+'\n');print('SUNSET_FULL_HOUSE_SOURCE_COMPLETE',len(arch),len(groups),flush=True)
