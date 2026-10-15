from pathlib import Path
import bpy,json,hashlib
D=Path(__file__).resolve().parent;original=json.loads((D/'NATIVE_VERIFICATION.json').read_text());(D/'NATIVE_VERIFICATION_r001.json').write_text(json.dumps(original,indent=2)+'\n');assert hashlib.sha256((D/'native/THEATER_SECONDARY_APPROACHES_r001.blend').read_bytes()).hexdigest()==original['native_sha256'];bpy.ops.wm.open_mainfile(filepath=str(D/'native/THEATER_SECONDARY_APPROACHES_r001.blend'));bpy.context.preferences.filepaths.save_version=0
metal=bpy.data.materials['ASTRAEA_champagne_metal'];glass=next(m for m in bpy.data.materials if 'glass' in m.name.lower());stone=bpy.data.materials['warm_stone']
def box(col,name,lo,hi,mat):
 vs=[(x,-z,y)for y in[lo[1],hi[1]]for z in[lo[2],hi[2]]for x in[lo[0],hi[0]]];faces=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)];mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],faces);mesh.update();obj=bpy.data.objects.new(name,mesh);col.objects.link(obj);obj.data.materials.append(mat);obj['new_bounded_secondary_receiving_component']=True
for row in original['models']:
 col=bpy.data.collections['SECONDARY_'+row['deck']];y=row['y'];prefix=row['deck']+'_SECONDARY_'
 for side,a,b in[('SOUTH',-174.3,-172.7),('NORTH',-169.3,-169.1)]:
  for kind,low,high,width,mat in [('Foot',.02,.12,.09,metal),('Glass',.12,1.00,.018,glass),('Handrail',1.00,1.10,.09,metal)]:box(col,prefix+'ApertureReturn_'+side+'_'+kind,[-34-width/2,y+low,a],[-34+width/2,y+high,b],mat)
 for i,z in enumerate([-172.5,-171.,-169.5]):box(col,prefix+'SourceFloorUnderlap_'+str(i),[-35.4,y-.18,z-.20],[-33.7,y-.04,z+.20],metal)
 row['file']=row['file'].replace('r001','r002');row['meshes']=96;row['source_door_aperture_z']=[-172.7,-169.3];row['new_return_guards']=2;row['below_floor_west_receiving_laps']=3
 bpy.ops.object.select_all(action='DESELECT')
 for o in col.objects:o.select_set(True)
 f=D/'import/Game/assets/theater_secondary_receiving_20261015'/row['file'];bpy.ops.export_scene.gltf(filepath=str(f),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False);row['sha256']=hashlib.sha256(f.read_bytes()).hexdigest()
native=D/'native/THEATER_SECONDARY_APPROACHES_r002.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);bpy.ops.wm.open_mainfile(filepath=str(native))
for row in original['models']:
 bpy.ops.object.select_all(action='DESELECT')
 for o in bpy.data.collections['SECONDARY_'+row['deck']].objects:o.select_set(True)
 f=D/'fresh_reexport'/row['file'];bpy.ops.export_scene.gltf(filepath=str(f),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False);assert hashlib.sha256(f.read_bytes()).hexdigest()==row['sha256']
original.update(native_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),native_file=native.name,revision='r002_after_failed217',new_guards=6,new_below_floor_receiving_laps=9);(D/'NATIVE_VERIFICATION.json').write_text(json.dumps(original,indent=2)+'\n');print('PASS_NATIVE_R002_FRESH_REEXPORT_EXACT')
