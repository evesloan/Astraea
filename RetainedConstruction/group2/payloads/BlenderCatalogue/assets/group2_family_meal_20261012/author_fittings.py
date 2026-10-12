"""Meal-service fittings on three actual retained Family Terrace tables; no new seats."""
import bpy,bmesh,pathlib,json,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[3];P=pathlib.Path(__file__).resolve().parent
plan_path=ROOT/'BlenderCatalogue/assets/residential_hotels/aft_houses_20261007_r001/residential-neighborhood-courts-20261007/family_terrace_house/outputs/house_r001/PLAN.json';plan=json.loads(plan_path.read_text())
bpy.ops.wm.read_factory_settings(use_empty=True);objects=[];metrics=[];tables=[];materials={}
for role,color in [('ivory',(.73,.72,.63,1)),('walnut',(.33,.20,.11,1)),('teal',(.13,.32,.33,1)),('metal',(.56,.49,.33,1))]:
 m=bpy.data.materials.new('G2M_'+role);m.diffuse_color=color;materials[role]=m
def box(name,x0,x1,y0,y1,z0,z1,role):
 v=[(x,-z,y)for y in [y0,y1]for z in [z0,z1]for x in [x0,x1]];d=bpy.data.meshes.new('G2M_'+name);d.from_pydata(v,[],[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]);d.update();bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);assert vol>1e-7;bm.to_mesh(d);bm.free();o=bpy.data.objects.new(d.name,d);bpy.context.collection.objects.link(o);d.materials.append(materials[role]);objects.append(o);metrics.append({'name':o.name,'closed_manifold':True,'positive_volume_m3':vol});return o
for index,name in enumerate(['D16_UpperGroupTable_Top_0','D16_MeetingTable_0_Top_0','D16_MeetingTable_1_Top_0']):
 part=next(p for p in plan['parts']if p['name']==name);v=part['verts'];bounds=[[min(q[i]for q in v),max(q[i]for q in v)]for i in range(3)];x=sum(bounds[0])/2;z=sum(bounds[2])/2;y=bounds[1][1];prefix='Table'+str(index)
 box(prefix+'ClosedReadyMealReceiver',x-.30,x+.30,y,y+.22,z-.25,z+.25,'walnut');box(prefix+'ReceiverLid',x-.30,x+.30,y+.22,y+.26,z-.25,z+.25,'ivory')
 box(prefix+'ServiceFace',x-.31,x-.30,y+.05,y+.17,z-.19,z+.19,'teal')
 box(prefix+'ContainedUsedReturn',x-.22,x+.22,y,y+.14,z+.50,z+.82,'metal')
 settings=[]
 for side in [-1,1]:
  for row in [-1,1]:
   px=x+side*.73;pz=z+row*.95;label=prefix+'Place'+str(side)+str(row);box(label+'Mat',px-.23,px+.23,y,y+.008,pz-.25,pz+.25,'teal');box(label+'PlateBottom',px-.16,px+.16,y+.008,y+.022,pz-.16,pz+.16,'ivory')
   for n,(a,b)in enumerate([(px-.16,px-.145),(px+.145,px+.16)]):box(label+'PlateSide'+str(n),a,b,y+.022,y+.045,pz-.16,pz+.16,'ivory')
   box(label+'PlateFore',px-.145,px+.145,y+.022,y+.045,pz-.16,pz-.145,'ivory');box(label+'PlateRear',px-.145,px+.145,y+.022,y+.045,pz+.145,pz+.16,'ivory')
   settings.append({'world_xyz':[px,y,pz],'existing_seat_used':True,'new_seat':False})
 tables.append({'existing_table':name,'actual_source_bounds_xyz':bounds,'support_y':y,'source_pose_or_surface_modified':False,'settings':settings,'new_chairs_or_credited_dining_places':0})
native=P/'source/FAMILY_MEAL_FITTINGS_r001.blend';native.parent.mkdir(parents=True,exist_ok=True);assert not native.exists();bpy.ops.wm.save_as_mainfile(filepath=str(native))
path=ROOT/'Game/assets/group2_family_meal/FAMILY_MEAL_FITTINGS_r001.glb';path.parent.mkdir(parents=True,exist_ok=True);assert not path.exists();bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0];bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
source=ROOT/'Game/assets/models/FAMILY_TERRACE_ARCHITECTURE_lift_r003.glb';data={'schema':'astraea.group2_family_meal_source.v1','parent_checkpoint':'7fdb6e55788deac0525d12649a6cb9710bb22c93','candidate_parent':'D16_directory_06','ame_id':'AME-175','source_plan_sha256':hashlib.sha256(plan_path.read_bytes()).hexdigest(),'source_runtime_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'tables':tables,'canonical_dining_total_unchanged':2200,'new_capacity_or_seats':0,'proposal':'Existing household tables gain physical clean meal receivers, contained used returns and table settings. Group8 dining ledger and Group3 food/dirty-return joins remain required; no additional dining place credit','admission_proposal':'Inclusive household/caregiver meal use; no luxury exclusion or dietary/species policy invented','food_stock_staff_hygiene_simulation_accepted':False,'production_adoption':False,'original_floor_roof_table_chair_ID_or_capacity_modified':False}
out=ROOT/'Game/data/group2_family_meal/COMPONENT_r001.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(data,indent=2)+'\n');(P/'evidence').mkdir(exist_ok=True);(P/'evidence/NATIVE_r001.json').write_text(json.dumps({'pass':True,'native_sha256':data['native_sha256'],'metrics':metrics,'original_sources_modified':False},indent=2)+'\n');print('PASS three actual family table service fittings, zero new seats or ledger places')
