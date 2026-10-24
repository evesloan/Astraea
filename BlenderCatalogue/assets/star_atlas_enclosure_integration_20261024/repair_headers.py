"""Two-part correction against retained later D15 portal heads, no regeneration."""
from pathlib import Path
import bpy,json,hashlib,struct
N=Path(__file__).resolve().parent;R=N.parents[2];G=R/'Game';P=G/'star_atlas_enclosure_integration_20261024'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=R/'BlenderCatalogue/assets/star_atlas_enclosure_20261022/StarAtlasEnclosure_r001.blend'
assert sha(source)=='aa40813a9e66a2a7bc476bd5e210635028a709a39fa79a2b4827295f1196355c'
original=G/'star_atlas_enclosure_20261022/PLAN.json';assert sha(original)=='f43033ce35c13a0cff2e918a1b98616f5e892fed754037d5f1fc5d607d0c43dd'
definition=json.loads((G/'data/architecture/STAR_ATLAS_SPECIALTY_FIRST.json').read_text());patch=G/'assets/models'/definition['receiving']['commons_patch_file']
assert sha(patch)=='0c9474a99a13284e617b42ea747549e16c4f8d3604b50c9ce4851865c7f438c0'
out=N/'StarAtlasEnclosure_PortalCompatible_r002.blend';assert not out.exists()
plan=json.loads(original.read_text());names=['SA_D15_NorthWall_0_AcousticFrieze','SA_D15_SouthWall_0_AcousticFrieze']
bpy.ops.wm.open_mainfile(filepath=str(source));meshes={o.name:o for o in bpy.context.scene.objects if o.type=='MESH'};assert len(meshes)==140
def geometry(o):return [[list(v.co)for v in o.data.vertices],[list(f.vertices)for f in o.data.polygons],list(o.matrix_world)]
before={n:geometry(o)for n,o in meshes.items()};rows=[]
for name in names:
 o=meshes[name];row=next(p for p in plan['parts']if p['name']==name);row=json.loads(json.dumps(row));count=0
 for v in row['verts']:
  if abs(v[1]-95.95)<1e-7:v[1]=96.025;count+=1
 assert count>0 and min(v[1]for v in row['verts'])==96.025
 native_count=0
 for v in o.data.vertices:
  if abs(v.co.z-95.95)<.00001:v.co.z=96.025;native_count+=1
 assert native_count==count;o.data.update();o['current_receiving_portal_head_y']=96.0;o['portal_clearance_m']=.025;rows.append(row)
for name,o in meshes.items():
 if name not in names:assert geometry(o)==before[name],name
for im in bpy.data.images:
 if im.source=='FILE'and not im.packed_file:im.pack()
bpy.context.scene['scope']='Retained140-part enclosure; only two D15 acoustic frieze bottom surfaces retract75mm to clear later specialty portal heads by25mm.'
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
delta=dict(status='SOURCE_CORRECTION_PENDING_CURRENT_SHIP_GATE',source_native=str(source.relative_to(R)),source_native_sha256=sha(source),native_successor=str(out.relative_to(R)),native_successor_sha256=sha(out),base_plan_sha256=sha(original),current_patch_model='res://'+str(patch.relative_to(G)),current_patch_sha256=sha(patch),parts=rows,unchanged_parts=138,total_parts=140,actual_portal_head_y=96.0,new_frieze_min_y=96.025,clearance_m=.025,original_lower_intrusion_m=.05,floors_and_portals_changed=False)
(P/'HEADER_DELTA.json').write_text(json.dumps(delta,indent=2)+'\n');print('PORTAL_NATIVE_SUCCESSOR',len(rows),138,sha(out))
