"""Immutable native successors: sixteen private outlook bays, no hull/gallery edits."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1];G=P.parent;R=G.parent
N=R/'BlenderCatalogue/assets/night_garden_panoramic_suites_20261022'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for p,h in json.loads((P/'evidence/INPUT_PINS.json').read_text()).items():assert sha(R/p)==h,p
package=json.loads((G/'data/architecture/night_garden_specialty_d15_20261020/PACKAGE_R003.json').read_text())
index=json.loads((G/'data/architecture/night_garden_partition_20261021/index.json').read_text())['rooms']
receipt={'rooms':[],'original_inner_shells_preserved':14,'hull_changes':0,'new_units':0,'accepted':False}
def xyz(v):return Vector((v[0],-v[2],v[1]))
def bounds(objects):
 bpy.context.view_layer.update()
 points=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box]
 points=[(v.x,v.z,-v.y)for v in points]
 return [[min(p[k]for p in points)for k in range(3)],[max(p[k]for p in points)for k in range(3)]]
def fingerprint(o):return hashlib.sha256(repr(([list(r)for r in o.matrix_world],[list(v.co)for v in o.data.vertices],[list(p.vertices)for p in o.data.polygons])).encode()).hexdigest()
def material(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=color;m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=color;bs.inputs['Roughness'].default_value=.38;bs.inputs['Alpha'].default_value=color[3]
 if color[3]<1:m.surface_render_method='DITHERED'
 return m
def box(name,lo,hi,mat=None):
 bpy.ops.mesh.primitive_cube_add(size=1,location=xyz([(a+b)/2 for a,b in zip(lo,hi)]));o=bpy.context.object;o.name=name
 o.dimensions=(hi[0]-lo[0],hi[2]-lo[2],hi[1]-lo[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if mat:o.data.materials.append(mat)
 o['runtime_collision']=True
 return o
for row in package['rooms']:
 a=row['allocation'];i=int(a['source_envelope_index'])
 if a['allocation_x'][0]<84:continue
 source=R/'BlenderCatalogue'/row['native_source'];assert sha(source)==row['native_source_sha256']
 native=N/f'NG{i}_PanoramicSuite_r001.blend';out=P/'runtime'/f'NG{i}_PanoramicSuite_r001.glb'
 assert not native.exists() and not out.exists()
 bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.preferences.filepaths.save_version=0
 original=[o for o in bpy.context.scene.objects if o.type=='MESH'];before={o.name:fingerprint(o)for o in original}
 cz=sum(a['allocation_z'])/2;rear=next(o for o in original if o.name==f'NG{i}_OpaqueRearBoundary')
 moved=[o for o in original if o.name.startswith(f'NG{i}_Cocoon') or o.name.startswith(f'NG{i}_ReservedRestSupport_')]
 assert moved
 for o in moved:o.location.x-=2.7
 rest_bounds=bounds(moved);assert rest_bounds[0][0]>91.65 and rest_bounds[1][0]<95.9
 study=[o for o in original if any(o.name.startswith(f'NG{i}_{part}__')for part in ['LibraryStudyEdge','SupportedOpenFolio','HousedStudyTaskFixture','DayReadingChair'])]
 assert study
 study_before=bounds(study)
 study_z=cz+(1.4 if i in [404,572] or cz<0 else -1.4)
 center=[(a+b)/2 for a,b in zip(*study_before)]
 target=[97.25,center[1],study_z]
 pose=Matrix.Translation(xyz(target))@Matrix.Rotation(math.pi/2,4,'Z')@Matrix.Translation(-xyz(center))
 for o in study:o.matrix_world=pose@o.matrix_world
 delta=Vector((target[0]-center[0],0,target[2]-center[2]))
 study_after=bounds(study)
 assert study_after[0][0]>95.9 and study_after[1][0]<98.7,study_after
 assert study_after[0][2]>a['allocation_z'][0]+.12 and study_after[1][2]<a['allocation_z'][1]-.12,study_after
 cutter=box('PanoramicOpeningCut',[98.5,93.4,cz-3.05],[99.2,96.45,cz+3.05])
 bpy.context.view_layer.objects.active=rear;mod=rear.modifiers.new('PanoramicPrivateOutlook','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
 wood=material('NGP_WarmWalnut',(.17,.085,.037,1));ivory=material('NGP_SoftIvory',(.66,.59,.46,1));glass=material('NGP_PrivateOutlook',(.23,.39,.34,.12));cushion=material('NGP_QuietWeave',(.30,.38,.35,1))
 extra=[]
 for suffix,lo,hi in [('Sill',[98.72,93.28,cz-3.17],[98.95,93.4,cz+3.17]),('Head',[98.72,96.45,cz-3.17],[98.95,96.57,cz+3.17]),('Left',[98.72,93.4,cz-3.17],[98.95,96.45,cz-3.05]),('Right',[98.72,93.4,cz+3.05],[98.95,96.45,cz+3.17])]:extra.append(box(f'NGP_{i}_Frame_{suffix}',lo,hi,wood))
 pane=box(f'NGP_{i}_PrivateViewPane',[98.85,93.4,cz-3.05],[98.87,96.45,cz+3.05],glass);pane['private_view_plane_x']=98.86;pane['private_view_sign']=-1;extra.append(pane)
 # Seat is oriented outward, with clear view above its low back. Hull metal stays intact.
 seat_z=cz+(-1.5 if study_z>cz else 1.5)
 for suffix,lo,hi,mat in [('Base',[96.0,93,seat_z-.75],[96.85,93.32,seat_z+.75],wood),('Cushion',[96.05,93.32,seat_z-.72],[96.87,93.48,seat_z+.72],cushion),('Back',[95.95,93.32,seat_z-.78],[96.1,93.95,seat_z+.78],ivory)]:extra.append(box(f'NGP_{i}_ViewSeat_{suffix}',lo,hi,mat))
 if i in [404,410]:extra.append(box(f'NGP_{i}_RetainedFrameAlignment',[98.72,93.4,cz-.08],[98.95,96.45,cz+.08],wood))
 changed={o.name for o in moved+study+[rear]}
 assert all(fingerprint(o)==before[o.name]for o in original if o.name not in changed)
 for o in moved+study+extra:
  lo,hi=bounds([o]);assert lo[0]>=a['allocation_x'][0]-.001 and hi[0]<=a['allocation_x'][1]+.001
  assert lo[2]>=a['allocation_z'][0]-.001 and hi[2]<=a['allocation_z'][1]+.001
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
 # Preserve each original shell/detail batch identity while changing only its named members.
 batches=index[row['model_file']]['always_resident_meshes']+index[row['model_file']]['immutable_private_detail_meshes']
 exports=[]
 for batch in batches:
  members=[bpy.data.objects[n]for n in batch['source_names']]
  bpy.ops.object.select_all(action='DESELECT')
  for o in members:o.select_set(True)
  bpy.context.view_layer.objects.active=members[0]
  if len(members)>1:bpy.ops.object.join()
  combined=bpy.context.object;combined.name=batch['node'];exports.append(combined)
 bpy.ops.object.select_all(action='DESELECT')
 for o in exports+extra:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_extras=True,export_yup=True,export_cameras=False,export_lights=False)
 record={'index':i,'model_file':row['model_file'],'room_id':a['proposed_runtime_id'],'rest_slot_ids':a['proposed_rest_slot_ids'],'rest_delta':[-2.7,0,0],'rest_bounds':rest_bounds,'study_delta':list(delta),'study_yaw_delta':math.pi/2,'study_bounds':study_after,'view_stance':[97.2,94.65,seat_z],'seated_eye':[96.5,94.15,seat_z],'window_bounds':[[98.79,93.4,cz-3.05],[98.95,96.45,cz+3.05]],'new_meshes':[o.name for o in extra],'source_native':str(source.relative_to(R)),'source_sha256':sha(source),'native':str(native.relative_to(R)),'native_sha256':sha(native),'export':str(out.relative_to(G)),'export_sha256':sha(out),'changed_members':sorted(changed),'unchanged_members':len(original)-len(changed)}
 receipt['rooms'].append(record)
 (P/'evidence/BUILD.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print('PANORAMIC_SUITE',i,'native and complete batched geometry saved',flush=True)
assert len(receipt['rooms'])==16
print('PANORAMIC_PACKAGE_COMPLETE 16 suites; 14 inner untouched; zero hull cuts',flush=True)
