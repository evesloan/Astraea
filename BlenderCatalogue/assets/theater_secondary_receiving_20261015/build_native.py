from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
D=Path(__file__).resolve().parent;R=Path('/workspace/astraea-protected-integration-20261012');S=R/'BlenderCatalogue/assets/group4_completion_20261011/theater_upper_approaches_016/Group4_Theater_Upper_Main_Approaches_r001.blend'
assert bpy.app.version[:3]==(4,3,2);assert hashlib.sha256(S.read_bytes()).hexdigest()=='3942d446be443ad31ebaa58cb77647929181e1ba17bd4b730f3c3832f016f483'
catalogue=json.loads((R/'BlenderCatalogue/catalogue_manifest.json').read_text());ids=[f'AST-TRM-G4-{n:03}'for n in[34,35,36]]
for identity in ids:assert all(a['catalogue_id']!=identity for a in catalogue['assets']),identity
bpy.ops.wm.open_mainfile(filepath=str(S));bpy.context.preferences.filepaths.save_version=0
original=list(bpy.data.collections['D12_UPPER_MAIN_EXTERIOR'].objects);assert len([o for o in original if o.type=='MESH'])==87
new=[];rows=[]
for deck,y,identity in [('D11',69.5,ids[0]),('D12',78.,ids[1]),('D13',84.,ids[2])]:
 col=bpy.data.collections.new('SECONDARY_'+deck);bpy.context.scene.collection.children.link(col);delta=Vector((0,45.7,y-78));selected=[];clones=[]
 for source in original:
  obj=source.copy();obj.data=source.data.copy();obj.name=deck+'_SECONDARY_'+source.name;obj.parent=None;obj.matrix_world=source.matrix_world.copy();obj.location+=delta;col.objects.link(obj);obj['retained_source_object']=source.name;obj['translation_godot']=[0,y-78,-45.7];selected.append(obj);new.append(obj);clones.append({'node':obj.name,'source':source.name,'translation':[0,y-78,-45.7]})
 bpy.ops.object.select_all(action='DESELECT')
 for o in selected:o.select_set(True)
 T=D/'import/Game/assets/theater_secondary_receiving_20261015';T.mkdir(parents=True,exist_ok=True);file=f'{identity}_{deck}_secondary_approach_r001.glb';bpy.ops.export_scene.gltf(filepath=str(T/file),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False)
 rows.append({'deck':deck,'y':y,'id':identity,'file':file,'meshes':87,'sha256':hashlib.sha256((T/file).read_bytes()).hexdigest(),'floor_m2':183,'clear_z':[-174.3,-169.1],'floor_z':[-174.75,-168.65],'clones':clones})
# Keep only newly authored instances; original source native remains unchanged at its exact retained path.
for o in list(bpy.data.objects):
 if o not in new:bpy.data.objects.remove(o,do_unlink=True)
for image in bpy.data.images:
 if image.source=='FILE'and not image.packed_file:image.pack()
N=D/'native';N.mkdir(exist_ok=True);native=N/'THEATER_SECONDARY_APPROACHES_r001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);bpy.ops.wm.open_mainfile(filepath=str(native));F=D/'fresh_reexport';F.mkdir(exist_ok=True)
for row in rows:
 bpy.ops.object.select_all(action='DESELECT')
 for o in bpy.data.collections['SECONDARY_'+row['deck']].objects:o.select_set(True)
 path=F/row['file'];bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False);assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
assert hashlib.sha256(S.read_bytes()).hexdigest()=='3942d446be443ad31ebaa58cb77647929181e1ba17bd4b730f3c3832f016f483'
source=json.loads((R/'Game/data/architecture/GROUP4_THEATER_UPPER_SOURCE_CANDIDATE.json').read_text());lights=[]
for row in rows:
 for old in source['lights']:
  if not old['id'].startswith('D12_'):continue
  item=dict(old);item['id']=row['deck']+'_SECONDARY_'+old['id'];item['fixture']=row['deck']+'_SECONDARY_'+old['fixture'];item['position_world']=[old['position_world'][0],old['position_world'][1]+row['y']-78,old['position_world'][2]-45.7];lights.append(item)
plan={'status':'NATIVE_FRESH_REEXPORT_EXACT_CANDIDATE_NOT_ADOPTED','donor_sha256':'3942d446be443ad31ebaa58cb77647929181e1ba17bd4b730f3c3832f016f483','native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'models':rows,'lights':lights,'new_floor_m2':549,'original_source_unchanged':True,'doors_operating':False,'load_capacity_accepted':False,'rim_support_connections_verified':False,'source_policy':'Rigid donor geometry/material/UV copies; secondary north edge clears retained command column by50mm. New load and primary transfer remain open. Existing route widths unchanged.'};(D/'NATIVE_VERIFICATION.json').write_text(json.dumps(plan,indent=2)+'\n');print('PASS_NATIVE_SECONDARY_DERIVATIVES',len(new))
