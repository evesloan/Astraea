"""Move the new entrance portal frame off the supported bridge approach; originals unchanged."""
from pathlib import Path
s=Path(__file__).with_name('build.py').read_text();exec(s.split('pre=json.loads',1)[0].replace('bpy.context.view_layer.update();v=', 'v='))
original=json.loads((P/'evidence/BUILD_R002.json').read_text());parent_hash=original['native_sha256'];assert sha(R/original['native'])==parent_hash
bpy.ops.wm.open_mainfile(filepath=str(R/original['native']));bpy.context.preferences.filepaths.save_version=0
moved=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH' and o.name.endswith('_35.25'):
  sign=-1 if o.name.startswith('Fore_') else 1;o.location+=xyz([0,0,sign*2.1]);moved.append(o.name)
assert len(moved)==14,len(moved)
bpy.context.view_layer.update()
for row in original['objects']:
 if row['name']in moved:row['bounds']=bounds(bpy.data.objects[row['name']])
native=N/'NightGardenReceivingCourts_r003.blend';out=P/'runtime/NightGardenReceivingCourts_r003.glb';assert not native.exists() and not out.exists()
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
export='for side in [\'Fore\',\'Aft\']:'+Path(__file__).with_name('refine_r002.py').read_text().split("for side in ['Fore','Aft']:",1)[1].split('original.update',1)[0]
exec(export)
original.update(native=str(native.relative_to(R)),native_sha256=sha(native),runtime=str(out.relative_to(G)),runtime_sha256=sha(out),predecessor_native_sha256=parent_hash,moved_new_portal_parts=moved,new_portal_z_abs=37.35)
(P/'evidence/BUILD_R003.json').write_text(json.dumps(original,indent=2)+'\n');print('RECEIVING_PORTAL_APPROACH_CORRECTED',len(moved))
