"""Bounded public court entrance successor; four façade parts only, no floor or hull cuts."""
from pathlib import Path
s=Path(__file__).with_name('build.py').read_text();exec(s.split('pre=json.loads',1)[0])
package=json.loads((G/'data/architecture/night_garden_specialty_d15_20261020/PACKAGE_R003.json').read_text())['receiving']
source=R/'BlenderCatalogue'/package['native_source'];assert sha(source)==package['native_source_sha256']
bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.preferences.filepaths.save_version=0
before={o.name:geometry(o)for o in bpy.context.scene.objects if o.type=='MESH'};changed=[];added=[]
for sign in [-1,1]:
 z0,z1=sorted([sign*34.65,sign*36.35]);cutter=box('TemporaryBoundedPublicPortal',[81.7,92.95,z0],[82.2,95.8,z1],bpy.data.materials[0])
 for suffix in ['CourtWallSill_4','CourtGlass_4']:
  o=bpy.data.objects[f'NG_{sign}_{suffix}'];bpy.context.view_layer.objects.active=o
  mod=o.modifiers.new('BoundedGardenEntrance','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name);changed.append(o.name)
 bpy.data.objects.remove(cutter,do_unlink=True)
 wood=bpy.data.objects[f'NG_{sign}_CourtWallSill_4'].data.materials[0]
 for label,a,b in [('JambA',z0,z0+.10),('JambB',z1-.10,z1)]:added.append(box(f'NGRC_{sign}_{label}',[81.78,93,a],[82.10,95.82,b],wood,.018))
 added.append(box(f'NGRC_{sign}_EntranceHead',[81.78,95.8,z0],[82.10,95.98,z1],wood,.018))
for name,digest in before.items():
 if name not in changed:assert geometry(bpy.data.objects[name])==digest,name
native=N/'NightGardenD15CourtEntrances_r004.blend';runtime=P/'runtime/NightGardenD15CourtEntrances_r004.glb';assert not native.exists() and not runtime.exists()
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(runtime),export_format='GLB',use_selection=True,export_extras=True,export_yup=True,export_cameras=False,export_lights=False)
receipt={'native':str(native.relative_to(R)),'native_sha256':sha(native),'runtime':str(runtime.relative_to(G)),'runtime_sha256':sha(runtime),'source_native':str(source.relative_to(R)),'source_native_sha256':sha(source),'source_model':package['model_file'],'source_model_sha256':package['model_sha256'],'changed_source_meshes':changed,'unchanged_source_meshes':len(before)-len(changed),'unchanged_geometry_sha256':{k:v for k,v in before.items()if k not in changed},'new_parts':[o.name for o in added],'floor_cuts':0,'hull_cuts':0,'portal_clear_height_m':2.8,'portal_clear_width_m':1.5,'scope':'Two public avenue to receiving-court entrances, bounded to existing sill/glass; all other source geometry unchanged','visual_accepted':False}
(P/'evidence/ENTRANCES.json').write_text(json.dumps(receipt,indent=2)+'\n');print('BOUNDED_PUBLIC_ENTRANCES',len(changed),len(before)-len(changed))
