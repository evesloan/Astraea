"""Editable additive source; original Family and catalogue files stay linked."""
from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector
R=Path(__file__).resolve().parents[3];P=R/'Game/family_aft_court_20261024';N=Path(__file__).resolve().parent
plan=json.loads((P/'PLAN.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for path,digest in plan['source_pins'].items():assert sha(R/path)==digest,path
out=N/'FamilyAftCourt_r002.blend';assert not out.exists()
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
# Link the source architecture for useful editable context. No copy of its bytes.
with bpy.data.libraries.load(str(R/plan['native_source']),link=True)as(a,b):b.objects=a.objects
context=bpy.data.collections.new('Retained Family architecture — immutable source');bpy.context.scene.collection.children.link(context)
for obj in b.objects:
 if obj is not None and obj.type in ['MESH','CURVE']:context.objects.link(obj)
mats={}
for role in set(q['role']for q in plan['parts']):
 matches=[m for m in bpy.data.materials if m.name in ['COURT_'+role,role]]
 assert matches,role
 mats[role]=matches[0]
addition=bpy.data.collections.new('Aft court architecture r001');bpy.context.scene.collection.children.link(addition)
for row in plan['parts']:
 mesh=bpy.data.meshes.new(row['name']);mesh.from_pydata([(x,-z,y)for x,y,z in row['verts']],[],row['faces']);mesh.update();mesh.materials.append(mats[row['role']]);o=bpy.data.objects.new(row['name'],mesh);addition.objects.link(o);o['retained_owner']=row['owner']
 uv=mesh.uv_layers.new(name='WorldScale_0_35')
 for poly in mesh.polygons:
  normal=poly.normal
  for loop in poly.loop_indices:
   v=mesh.vertices[mesh.loops[loop].vertex_index].co;x,y,z=v.x,v.z,-v.y
   uv.data[loop].uv=(x*.35,z*.35)if abs(normal.z)>.7 else((z*.35,y*.35)if abs(normal.x)>.7 else(x*.35,y*.35))
collections={}
for source in plan['sources']:
 with bpy.data.libraries.load(str(R/'BlenderCatalogue'/source['source']),link=True)as(a,b):b.objects=a.objects
 holder=bpy.data.collections.new(source['catalogue_id']+'_NativeSource');collections[source['catalogue_id']]=holder
 for obj in b.objects:
  if obj and obj.type in ['MESH','CURVE']and'previewground'not in obj.name.lower()and not obj.get('preview_only',False):holder.objects.link(obj)
for row in plan['plants']:
 o=bpy.data.objects.new(row['name'],None);o.instance_type='COLLECTION';o.instance_collection=collections[row['catalogue_id']];addition.objects.link(o);x,y,z=row['position'];o.location=(x,-z,y);o.rotation_euler.z=row['yaw'];o.scale=(row['scale'],)*3;o['receiving_owner']=row['owner']
for row in plan['lights']:
 light=bpy.data.lights.new(row['name'],'SPOT');light.energy=600;light.color=row['color'];light.spot_size=math.radians(row['angle']*2);o=bpy.data.objects.new(row['name'],light);addition.objects.link(o);x,y,z=row['position'];o.location=(x,-z,y);x,y,z=row['target'];o.rotation_euler=(Vector((x,-z,y))-o.location).to_track_quat('-Z','Y').to_euler();o['retained_fixture']=row['original'];o['runtime_energy_is_in_PLAN']=True
bpy.context.scene['status']='Aft court candidate; original architecture linked; no floor, hull, capacity or clerestory changes. Final visual acceptance open.'
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True,relative_remap=True)
(P/'evidence/NATIVE.json').write_text(json.dumps(dict(status='PASS',native=str(out.relative_to(R)),sha256=sha(out),bytes=out.stat().st_size,parts=len(plan['parts']),plants=len(plan['plants']),source_families=len(collections),original_native_unchanged=True,final_visual_accepted=False),indent=2)+'\n');print('FAMILY_AFT_NATIVE',out.stat().st_size)
