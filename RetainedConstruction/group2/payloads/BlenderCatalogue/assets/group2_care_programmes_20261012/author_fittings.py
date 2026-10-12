"""Six counter-mounted care/hydration sets; immutable source adjuncts remain intact."""
import bpy,bmesh,gzip,json,pathlib,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[3];P=pathlib.Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
materials={}
for role,color in [('ivory',(.73,.72,.63,1)),('metal',(.56,.49,.33,1)),('teal',(.13,.32,.33,1)),('walnut',(.33,.20,.11,1))]:
 m=bpy.data.materials.new('G2C_'+role);m.diffuse_color=color;materials[role]=m
rows=[];metrics=[]
keys=['port_forward_upper_house','starboard_forward_upper_house','port_central_upper_house','starboard_central_upper_house','port_aft_upper_house','starboard_aft_upper_house']
for key in keys:
 cpath=ROOT/f'Game/data/group2_completion/contracts/{key}.json';c=json.loads(cpath.read_text())
 vpath=ROOT/f'BlenderCatalogue/assets/group2_completion_20261011/retained_evidence/{key}/SAVED_NATIVE_VERTICES.json.gz'
 verts=json.loads(gzip.decompress(vpath.read_bytes()))['CareStoneSurface']
 bounds=[[min(q[i]for q in verts),max(q[i]for q in verts)]for i in range(3)]
 assert abs(bounds[0][1]-bounds[0][0]-1)<.001 and abs(bounds[2][1]-bounds[2][0]-1.85)<.001
 top=bounds[1][1];port=key.startswith('port_');objects=[];feet=[]
 def world(u,h,v):return(bounds[0][1]-u if port else bounds[0][0]+u,top+h,bounds[2][0]+v if port else bounds[2][1]-v)
 def box(name,u0,u1,h0,h1,v0,v1,role):
  points=[world(u,h,v)for h in [h0,h1]for v in [v0,v1]for u in [u0,u1]]
  mesh=bpy.data.meshes.new('G2C_'+key+'_'+name);mesh.from_pydata([(x,-z,y)for x,y,z in points],[],[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)])
  bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);assert volume>1e-7;bm.to_mesh(mesh);bm.free()
  o=bpy.data.objects.new(mesh.name,mesh);bpy.context.collection.objects.link(o);mesh.materials.append(materials[role]);objects.append(o)
  metrics.append({'name':o.name,'closed_manifold':True,'positive_volume_m3':volume})
  if h0==0:feet.append({'name':o.name,'foot_uv':[u0,u1,v0,v1]})
  return o
 # Raised watertight vessel on the existing full stone surface; no countertop cut.
 box('WashBottom',.13,.87,0,.03,.85,1.65,'ivory')
 box('WashSideA',.13,.17,.03,.20,.85,1.65,'ivory');box('WashSideB',.83,.87,.03,.20,.85,1.65,'ivory')
 box('WashFront',.17,.83,.03,.20,.85,.89,'ivory');box('WashRear',.17,.83,.03,.20,1.61,1.65,'ivory')
 box('FaucetFoot',.20,.34,0,.04,1.68,1.81,'metal')
 box('FaucetStem',.24,.30,.04,.48,1.70,1.76,'metal')
 box('FaucetArm',.24,.30,.42,.48,1.42,1.76,'metal')
 box('FaucetOutlet',.24,.30,.34,.42,1.42,1.48,'metal')
 box('ValvePlate',.40,.58,0,.035,1.68,1.81,'teal');box('ValveLever',.46,.50,.035,.16,1.70,1.78,'metal')
 box('PreparationTray',.08,.92,0,.035,.40,.77,'teal')
 # Closed clean cup/feed-preparation case; not a medical bed or infant berth.
 box('CleanCaseBottom',.15,.85,0,.025,.07,.35,'walnut')
 box('CleanCaseRear',.15,.85,.025,.25,.31,.35,'walnut')
 box('CleanCaseLeft',.15,.19,.025,.25,.07,.31,'walnut');box('CleanCaseRight',.81,.85,.025,.25,.07,.31,'walnut')
 box('CleanCaseLid',.15,.85,.25,.28,.07,.35,'ivory')
 box('ClosedCleanFront',.19,.81,.025,.25,.07,.095,'ivory')
 box('CleanHandle',.46,.54,.10,.15,.045,.07,'metal')
 for i in range(3):
  u=.24+i*.17
  box('CupBottom'+str(i),u,u+.12,.025,.04,.15,.27,'ivory')
  for n,(a,b,z0,z1)in enumerate([(u,u+.015,.15,.27),(u+.105,u+.12,.15,.27),(u+.015,u+.105,.15,.165),(u+.015,u+.105,.255,.27)]):box('CupWall'+str(i)+'_'+str(n),a,b,.04,.19,z0,z1,'ivory')
 ports=[]
 for name,u,h,v in [('clean_supply',.27,.02,1.80),('contained_used_return',.74,.02,1.60)]:
  o=bpy.data.objects.new('G2C_'+key+'_PORT_'+name,None);bpy.context.collection.objects.link(o);x,y,z=world(u,h,v);o.location=(x,-z,y);o.empty_display_type='PLAIN_AXES';objects.append(o)
  ports.append({'name':name,'world_xyz':[x,y,z],'capped_unconnected':True,'existing_surface_or_wall_cut':False})
 path=ROOT/f'Game/assets/group2_care_programmes/CARE_{key}_r001.glb';path.parent.mkdir(parents=True,exist_ok=True);assert not path.exists()
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
 view=next(v for v in c['source_views']if v['name']=='care_threshold')
 # A bounded original-player approach from the retained source review eye position.
 front_z=bounds[2][0]-.70 if port else bounds[2][1]+.70
 target=[sum(bounds[0])/2,102,front_z]
 rows.append({'key':key,'source_native_sha256':c['native_sha256'],'source_runtime_sha256':c['export_sha256'],
  'contract_sha256':hashlib.sha256(cpath.read_bytes()).hexdigest(),'saved_vertices_sha256':hashlib.sha256(vpath.read_bytes()).hexdigest(),
  'existing_counter':'CareStoneSurface','counter_bounds_xyz':bounds,'support_y':top,'counter_not_cut':True,'floor_roof_or_original_mesh_changed':False,
  'contact_feet':feet,'service_ports':ports,'light_owner':'Existing retained CareTaskLens and source selector; no new budget',
  'approach_walk':[ [view['camera_world_xyz'][0],102,view['camera_world_xyz'][2]],target],
  'export_path':str(path.relative_to(ROOT)),'export_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
  'new_rooms_beds_capacity':0,'water_hygiene_food_simulation_accepted':False,'production_adoption':False})
native=P/'source/CARE_FITTINGS_r001.blend';native.parent.mkdir(exist_ok=True);assert not native.exists();bpy.ops.wm.save_as_mainfile(filepath=str(native))
data={'schema':'astraea.group2_existing_adjunct_care_fittings.v1','parent_checkpoint':'d6bf9c755357b07d185a88119574d1cc06d791f6',
 'rows':rows,'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'790_excluded':True,'shared_root_registry_unchanged':True,
 'counts_as_complete_nursery_or_medical_facility':False}
out=ROOT/'Game/data/group2_care_programmes/FITTINGS_r001.json';out.parent.mkdir(parents=True,exist_ok=True);assert not out.exists();out.write_text(json.dumps(data,indent=2)+'\n')
(P/'evidence/NATIVE_r001.json').write_text(json.dumps({'pass':True,'native_sha256':data['native_sha256'],'metrics':metrics,'original_sources_modified':False},indent=2)+'\n')
print('PASS six counter-mounted washing/hydration/preparation sets')
