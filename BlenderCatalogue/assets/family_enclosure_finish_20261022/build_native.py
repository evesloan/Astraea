from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Matrix
R=Path('/workspace/Astraea-recovered-e6274e77-20261021');P=R/'Game/family_enclosure_finish_20261022';N=R/'BlenderCatalogue/assets/family_enclosure_finish_20261022';d=json.loads((P/'PLAN.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(R/d['source_plan'])==d['source_plan_sha256'];assert sha(R/d['native_source'])==d['native_sha256']
bpy.ops.wm.read_factory_settings(use_empty=True);mats={}
for role,row in d['materials'].items():
 m=bpy.data.materials.new('FamilyCourt_'+role);m.diffuse_color=row['color'];m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=row['color'];bs.inputs['Roughness'].default_value=row['roughness'];bs.inputs['Metallic'].default_value=row['metallic'];mats[role]=m
for row in d['parts']:
 mesh=bpy.data.meshes.new(row['name']);mesh.from_pydata([(x,-z,y)for x,y,z in row['verts']],[],row['faces']);mesh.update();o=bpy.data.objects.new(row['name'],mesh);bpy.context.collection.objects.link(o);mesh.materials.append(mats[row['role']]);o['retained_owner']=row['owner'];o['role']=row['role']
# Editable source-family collection instances, kept separate from runtime export.
collections={}
for source in d['sources']:
 path=R/'BlenderCatalogue'/source['source'];assert sha(path)==source['source_sha256']
 with bpy.data.libraries.load(str(path),link=True)as(a,b):b.objects=a.objects
 objects=[o for o in b.objects if o and o.type in ['MESH','CURVE'] and 'previewground' not in o.name.lower() and not o.get('preview_only',False)];assert objects
 holder=bpy.data.collections.new(source['catalogue_id']+'_NativeSource');collections[source['catalogue_id']]=holder
 # Link source collections only to the instanced holder, not scene collection.
 for o in objects:holder.objects.link(o)
for row in d['placements']:
 o=bpy.data.objects.new(row['name'],None);o.instance_type='COLLECTION';o.instance_collection=collections[row['catalogue_id']];bpy.context.collection.objects.link(o);x,y,z=row['position'];o.location=(x,-z,y);o.rotation_euler.z=row['yaw'];o.scale=(row['scale'],)*3;o['receiving_bed']=row['receiving_bed']
for row in d['lights']:
 data=bpy.data.lights.new(row['name'],'SPOT');data.energy=140;data.color=row['color'];o=bpy.data.objects.new(row['name'],data);bpy.context.collection.objects.link(o);x,y,z=row['position'];o.location=(x,-z,y);o['runtime_budget']=8
bpy.context.scene['status']='UNFINISHED additive successor; retained house is external unchanged owner';bpy.context.scene['source_plan_sha256']=d['source_plan_sha256'];bpy.context.preferences.filepaths.save_version=0
out=N/'FamilyEnclosure_r001.blend';assert not out.exists();bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True,relative_remap=True)
(P/'evidence/NATIVE.json').write_text(json.dumps(dict(status='PASS',native=str(out.relative_to(R)),sha256=sha(out),parts=len(d['parts']),native_collection_instances=len(d['placements']),source_families=len(d['sources']),lights=len(d['lights']),editable_linked_sources=[s['source']for s in d['sources']]),indent=2)+'\n');print('NATIVE_PASS',out.stat().st_size)
