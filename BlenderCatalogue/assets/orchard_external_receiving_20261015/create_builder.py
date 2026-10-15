from pathlib import Path
D=Path(__file__).resolve().parent
s=Path('/workspace/astraea-integration-cutoff-20261013/dining_public_core_20261015/build_native.py').read_text();s=s[:s.index('for obj in list(bpy.data.objects):')]
s=s.replace("src=G/'assets/models/AST-CIR-005_forward_breakroom_d03.glb';expected='dd79daa1dc24e5524cebf6ba32778eee9f1b39ef6ad02fbd4e07336d3a0191de'","src=G/'assets/models/AST-DIN-008.glb';plan=json.loads((D/'NATIVE_PLAN.json').read_text());expected=plan['source_pins']['assets/models/AST-DIN-008.glb']")
s=s.replace("names=[f'CORE_{kind}_09_{side}'for side in[-1,1]for kind in['OuterWall','WallDado']];sources={name:bpy.data.objects[name]for name in names};donor=bpy.data.objects['CORE_LateralPortalLintel_01_-1'];made=[];rows=[]","names=plan['original_wall_names'];sources={name:bpy.data.objects[name]for name in names};made=[];rows=[]")
s=s.replace('_D10_PUBLIC_PORTAL','_ORCHARD_SERVICE_GATEWAY').replace('(0,-8.1,False),(0,8.1,True),(1,61.,False),(1,64.2,True),(2,-2.,False),(2,2.,True)','(0,45.8,False),(0,46.2,True),(1,0.,False),(1,3.2,True),(2,34.3,False),(2,37.7,True)').replace('max(61.,lo.y)','max(0.,lo.y)').replace('min(64.2,hi.y)','min(3.2,hi.y)').replace('[(-2.,Vector((0,0,1))),(2.,Vector((0,0,-1)))]','[(34.3,Vector((0,0,1))),(37.7,Vector((0,0,-1)))]').replace('lo.y<64.2<hi.y','lo.y<3.2<hi.y').replace('64.2,-2','3.2,34.3').replace('64.2,2','3.2,37.7')
s+='''
for obj in list(bpy.data.objects):
 if obj not in made:bpy.data.objects.remove(obj,do_unlink=True)
B=lambda p:Vector((p[0],-p[2],p[1]));GV=lambda p:Vector((p.x,p.z,-p.y));origin=Vector((8,61,-250))
for obj in made:obj.location=B(origin)
R=G.parent;donor=R/plan['source_native'];assert hashlib.sha256(donor.read_bytes()).hexdigest()==plan['source_native_sha256'];source=json.loads((G/'data/architecture/group8/orchard_service.json').read_text());hoodrows=[r for r in source['meshes']if r['unit']=='NorthFinish_Hood'];hoodnames=[r['name']for r in hoodrows]
with bpy.data.libraries.load(str(donor),link=False)as(data_from,data_to):data_to.objects=hoodnames
col=bpy.data.collections.new('ORCHARD_EXTERNAL_RECEIVING_AUTHORING_R001');bpy.context.scene.collection.children.link(col);parts=[];clones=[];lights=[]
'''
base=Path('/workspace/astraea-integration-cutoff-20261013/dining_service_receiving_20261015/build_native_receivers.py').read_text();functions=base[base.index('mat=lambda token:'):base.index('def clone_unit(')];s+=functions
s+='''
outline=plan['floor_outline_xz'];prism('ORX_MissingOnlyFloor',outline,60.76,61,blue);prism('ORX_SourceJoinedRoof',outline,64.8,64.98,white)
for i,(a,b)in enumerate(zip(outline,outline[1:]+outline[:1])):
 if abs(a[0]-54)<.001 and abs(b[0]-54)<.001:continue
 if abs(a[0]-4)<.001 and abs(b[0]-4)<.001:
  wall('ORX_AxialReturn0',(4,-178.15),(4,-177.7));wall('ORX_AxialReturn1',(4,-174.3),(4,-173.85));line('ORX_AxialHeader',(4,-177.7),(4,-174.3),.18,64.2,64.82,white);continue
 a,b=Vector(a),Vector(b);n=max(1,math.ceil((b-a).length/5))
 for j in range(n):wall(f'ORX_Edge{i}_{j}',a.lerp(b,j/n),a.lerp(b,(j+1)/n))
 girder(f'ORX_EdgeGirder{i}',a,b)
for j,z in enumerate([-215.1,-214.,-212.9]):box(f'ORX_EmbeddedDiningTie{j}',(53.7,60.78,z-.12),(54.3,60.86,z+.12),metal)
for j,z in enumerate([-177.3,-176.,-174.7]):box(f'ORX_EmbeddedAxialTie{j}',(3.7,60.78,z-.12),(4.3,60.86,z+.12),metal)
for j in range(16):girder(f'ORX_AxialCross{j}',(4+j*4,-178.1),(4+j*4,-173.9))
for j in range(11):girder(f'ORX_GalleryCross{j}',(60,-216+j*4),(64,-216+j*4))
for j,z in enumerate([-217.8,-214,-210.2]):girder(f'ORX_GatewayCross{j}',(54,z),(64,z))
# Four rigid source-profile task hoods light the approach without changing the original stock or kitchen fixtures.
for i,target in enumerate([(62,64.1,-214),(62,64.1,-194),(42,64.1,-176),(16,64.1,-176)]):
 transform=Matrix.Translation(B(target))@Matrix.Translation(-B((34,64.1,-228.53)));madehood=[]
 for src in data_to.objects:
  o=src.copy();o.data=src.data;o.parent=None;o.matrix_world=transform@src.matrix_world;o.name=f'ORX_Hood{i}__'+src.name;col.objects.link(o);parts.append(o);madehood.append(o);clones.append({'name':o.name,'source':src.name,'rigid_matrix_blender':[list(r)for r in transform]})
 for row in source['lights']:
  if row['name']not in ['G8O_LIGHT_NorthFinish_Hood_-1','G8O_LIGHT_NorthFinish_Hood_1']:continue
  suffix=str(row['name']).split('_')[-1];lens=next(o for o in madehood if o.name.endswith('Lens'+suffix));lights.append({'name':f'ORX_LIGHT_{i}_{suffix}','at':list(GV(transform@B(row['at']))),'colour':row['colour'],'energy':row['energy'],'range':row['range'],'lens':lens.name})
for src in data_to.objects:bpy.data.objects.remove(src,do_unlink=True)
for image in bpy.data.images:
 if image.source=='FILE'and not image.packed_file:image.pack()
bpy.data.texts.new('EXACT_SOURCE_POLICY.json').write(json.dumps(plan,indent=2));bounds=[]
for o in parts:
 o.data.calc_loop_triangles();ps=[GV(o.matrix_world@Vector(v))for v in o.bound_box];bounds.append({'name':o.name,'min':[min(p[i]for p in ps)for i in range(3)],'max':[max(p[i]for p in ps)for i in range(3)],'triangles':len(o.data.loop_triangles)})
# Retain editable components; runtime batches combine only new receiving parts by material/collision class.
runtime=bpy.data.collections.new('ORCHARD_EXTERNAL_RECEIVING_RUNTIME_R001');bpy.context.scene.collection.children.link(runtime);groups={};batchrows=[]
for o in parts:
 for polygon in o.data.polygons:
  material=o.data.materials[polygon.material_index];key=(material.name,'Lens'not in o.name);g=groups.setdefault(key,{'vs':[],'fs':[],'uvs':[],'members':set()});g['members'].add(o.name);ix=[]
  for li in polygon.loop_indices:
   ix.append(len(g['vs']));g['vs'].append(tuple(o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co));g['uvs'].append(tuple(o.data.uv_layers.active.data[li].uv))
  g['fs'].append(ix)
for i,(key,g)in enumerate(sorted(groups.items())):
 name=f'ORX_BATCH_{i:03d}';data=bpy.data.meshes.new(name);data.from_pydata(g['vs'],[],g['fs']);data.update();data.materials.append(bpy.data.materials[key[0]]);uv=data.uv_layers.new(name='UVMap')
 for li in range(len(data.loops)):uv.data[li].uv=g['uvs'][data.loops[li].vertex_index]
 o=bpy.data.objects.new(name,data);runtime.objects.link(o);ps=[GV(Vector(v))for v in o.bound_box];batchrows.append({'name':name,'material':key[0],'collide':key[1],'members':sorted(g['members']),'min':[min(p[j]for p in ps)for j in range(3)],'max':[max(p[j]for p in ps)for j in range(3)]})
for row in lights:row['lens_batch']=next(b['name']for b in batchrows if row['lens']in b['members'])
I=D/'import/Game/assets/orchard_external_receiving_20261015';I.mkdir(parents=True,exist_ok=True);model=I/'ORCHARD_SERVICE_GATEWAY_r001.glb';bpy.ops.object.select_all(action='DESELECT')
for o in list(runtime.objects)+made:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(model),export_format='GLB',use_selection=True,export_yup=True,export_extras=False,export_cameras=False,export_lights=False);col.hide_render=True;N=D/'native';N.mkdir(exist_ok=True);native=N/'ORCHARD_SERVICE_GATEWAY_r001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);bpy.ops.wm.open_mainfile(filepath=str(native));fresh=D/'FRESH_REEXPORT.glb';bpy.ops.export_scene.gltf(filepath=str(fresh),export_format='GLB',use_selection=True,export_yup=True,export_extras=False,export_cameras=False,export_lights=False);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(fresh)==sha(model)and sha(src if isinstance(src,Path)else G/'assets/models/AST-DIN-008.glb')==expected
receipt={'status':'PASS_NATIVE_EXACT_FRESH_EXPORT_CANDIDATE','file':model.name,'source_file':'AST-DIN-008.glb','source_sha256':expected,'native_sha256':sha(native),'model_sha256':sha(model),'walls':rows,'batches':batchrows,'bounds':bounds,'lights':lights,'rigid_clones':clones,'authoring_meshes':len(parts)+2,'runtime_meshes':len(batchrows)+2,'source_pins':plan['source_pins'],'new_floor_area_m2':plan['new_floor_area_m2'],'new_room_ids_capacity_or_lift_stops':0,'operational_or_final_acceptance':False};(D/'NATIVE_VERIFICATION.json').write_text(json.dumps(receipt,indent=2)+'\\n');print('PASS_ORCHARD_NATIVE',receipt['authoring_meshes'],receipt['runtime_meshes'],len(lights))
'''
s=s.replace('import bpy,json,hashlib','import bpy,json,hashlib,math');(D/'build_native.py').write_text(s);compile(s,str(D/'build_native.py'),'exec');print('BUILDER_READY')
