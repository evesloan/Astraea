"""Replace only batches owning the four declared changed originals.
Freeze membership from the immutable native preimage before opening r002.
The four later approach batches are categorically excluded.
"""
from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
P=Path(__file__).resolve().parents[1];R=P.parents[1]
pins=json.loads((P/'evidence/INPUT_PINS.json').read_text())
for p,h in pins.items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
out=P/'runtime/ExactBoundedBatches_r003.glb';assert not out.exists()
names=['CR_RoyaltyLowerRoof','CR_LampHousing_CourtView','CR_LampLens_CourtView','CR_LampStem_CourtView']
bpy.ops.wm.open_mainfile(filepath=str(R/'BlenderCatalogue/assets/d17_connected_royalty/source/AST-RES-006.blend'))
groups={};owner={}
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.name.startswith('PREVIEW_ONLY_'):continue
 vs=[o.matrix_world@v.co for v in o.data.vertices];c=sum(vs,Vector())/len(vs)
 zone='support' if min(v.z for v in vs)<101 else 'approach' if -c.y<21 else 'court' if -c.y<29 else 'lane_private' if c.x<100 else 'royalty'
 key='CR_Batch_'+zone+'_'+o.data.materials[0].name
 groups.setdefault(key,[]).append(o.name);owner[o.name]=key
keys=sorted({owner[n] for n in names});assert all('approach' not in k for k in keys)
members={k:groups[k] for k in keys}
bpy.ops.wm.open_mainfile(filepath=str(R/'Game/royalty_790_completion_20261020/source/ROYALTY790_upper_candidate_r002.blend'))
selected=[]
for key in keys:
 bpy.ops.object.select_all(action='DESELECT')
 for name in members[key]:bpy.data.objects[name].select_set(True)
 active=bpy.data.objects[members[key][0]];bpy.context.view_layer.objects.active=active
 bpy.ops.object.join();active.name=key;selected.append(active)
bpy.ops.object.select_all(action='DESELECT')
for o in selected:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
(P/'evidence/BOUNDED_BATCH_MEMBERSHIP.json').write_text(json.dumps({'membership_frozen_from_original_native':members,'declared_changed_originals':names,'unchanged_member_names':[n for ns in members.values() for n in ns if n not in names],'approach_batches_excluded':True,'original_source_and_r002_unchanged':True,'export_sha256':hashlib.sha256(out.read_bytes()).hexdigest()},indent=2)+'\n')
print('BOUNDED_BATCHES',keys)
