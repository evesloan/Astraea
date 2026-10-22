"""Bounded direct-data runtime batching from the immutable authored native scene."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];G=P.parent;R=G.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
native=R/'BlenderCatalogue/assets/atrium_terrace_inhabitation_20261022/UpperAtriumInhabitation_r001.blend';out=P/'runtime/UpperAtriumInhabitation_r001.glb';assert native.exists()and not out.exists();native_sha=sha(native)
bpy.ops.wm.open_mainfile(filepath=str(native));pre=json.loads((P/'evidence/PREREQUISITES.json').read_text());objects=[o for o in bpy.context.scene.objects if o.type=='MESH'];by_group={};batches={};instances={}
for o in objects:
 name=str(o['terrace_group']);by_group.setdefault(name,[]).append(o);mats=tuple(slot.material.name if slot.material else''for slot in o.material_slots);key=(name,mats,bool(o.get('physical_contact',False)));batches.setdefault(key,[]).append(o)
 if o.get('catalogue_source'):
  index=o.name[len(name)+1:].split('_',1)[0];instances[(name,index)]={'group':name,'index':index,'catalogue_id':str(o['catalogue_source'])}
records=[]
for row in pre['groups']:
 pts=[o.matrix_world@Vector(c)for o in by_group[row['name']]for c in o.bound_box];pts=[(v.x,v.z,-v.y)for v in pts]
 records.append({'name':row['name'],'bounds':[[min(v[k]for v in pts)for k in range(3)],[max(v[k]for v in pts)for k in range(3)]],'native_parts':len(by_group[row['name']]),'purpose':row['purpose'],'owner':row['owner']})
deps=bpy.context.evaluated_depsgraph_get();cache={};outputs=[]
for index,((group,mats,solid),obs)in enumerate(batches.items()):
 vertices=[];faces=[];uvs=[];smooth=[];material_ids=[]
 for o in obs:
  key=(o.data.as_pointer(),tuple((m.name,m.type)for m in o.modifiers))
  if key not in cache:
   evaluated=o.evaluated_get(deps);me=evaluated.to_mesh(preserve_all_data_layers=True,depsgraph=deps)
   uv=me.uv_layers.active
   cache[key]=([v.co.copy()for v in me.vertices],[tuple(p.vertices)for p in me.polygons],[p.use_smooth for p in me.polygons],[p.material_index for p in me.polygons],[tuple(x.uv)for x in uv.data]if uv else[(0,0)]*len(me.loops))
   evaluated.to_mesh_clear()
  vs,fs,ss,mi,uv=cache[key];offset=len(vertices);pose=o.matrix_world
  vertices.extend([tuple(pose@v)for v in vs]);faces.extend([tuple(offset+i for i in f)for f in fs]);smooth.extend(ss);material_ids.extend(mi);uvs.extend(uv)
 data=bpy.data.meshes.new(group+'_Batch_'+str(index));data.from_pydata(vertices,[],faces);data.update()
 for name in mats:data.materials.append(bpy.data.materials[name])
 for poly,flag,material in zip(data.polygons,smooth,material_ids):poly.use_smooth=flag;poly.material_index=material
 layer=data.uv_layers.new(name='RetainedSourceUV');assert len(layer.data)==len(uvs)
 layer.data.foreach_set('uv',[v for pair in uvs for v in pair])
 mesh=bpy.data.objects.new(group+'_Batch_'+str(index),data);mesh['physical_contact']=solid;mesh['terrace_group']=group;outputs.append(mesh)
 if index%100==0:print('DIRECT_BATCH',index,'of',len(batches),flush=True)
# Only after reading the immutable source geometry do we replace in-memory export objects.
for o in objects:
 for collection in list(o.users_collection):collection.objects.unlink(o)
for o in outputs:bpy.context.collection.objects.link(o)
bpy.context.view_layer.update()
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_extras=True,export_yup=True,export_cameras=False,export_lights=False)
assert sha(native)==native_sha
lights=[]
for row in pre['groups']:
 for i,v in enumerate([-.62,.62]):
  y=2.22-i*.14;side=row['side'];lights.append({'name':row['name']+'_Source_'+str(i),'position':[row['x']-side*.35,row['y']+y-.035,row['z']+v],'target':[row['x']-side*1.4,row['y']+.45,row['z']+v],'energy':1.25,'range':7.5,'angle':68,'group':row['name']})
result={'native':str(native.relative_to(R)),'native_sha256':native_sha,'runtime':str(out.relative_to(G)),'runtime_sha256':sha(out),'groups':records,'instances':list(instances.values()),'lights':lights,'native_mesh_parts':len(objects),'runtime_mesh_batches':len(outputs),'evaluated_source_meshes':len(cache),'new_rooms_or_rests':0,'new_catalogue_ids':0,'visual_accepted':False,'export_method':'Direct evaluated mesh/UV batching from saved native; no operator join loop'}
(P/'evidence/BUILD.json').write_text(json.dumps(result,indent=2)+'\n');print('TERRACE_COMPOSITIONS_EXPORTED',len(records),len(instances),len(lights),flush=True)
