"""Author only the paired end additions; link exact retained architecture/plant sources."""
from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector,Matrix
N=Path(__file__).resolve().parent;R=N.parents[2];P=R/'Game/night_garden_lower_courts_20261024';plan=json.loads((P/'PLAN.json').read_text());out=N/'NightGardenLowerCourtEnds_r001.blend'
assert not out.exists()
for path,digest in plan['source_pins'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,path
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
C=lambda v:Vector((v[0],-v[2],v[1]))
source=R/'BlenderCatalogue/assets/night_garden_court_completion_20261022/NightGardenResortCourts_r003.blend'
with bpy.data.libraries.load(str(source),link=True)as(a,b):b.objects=list(a.objects)
originals=[o for o in b.objects if o is not None]
context=bpy.data.collections.new('Retained paired courts — unchanged except connected ground terminals');bpy.context.scene.collection.children.link(context)
def bounds(o):
 vs=[o.matrix_world@Vector(c)for c in o.bound_box];vs=[(v.x,v.z,-v.y)for v in vs];return [[min(v[k]for v in vs)for k in range(3)],[max(v[k]for v in vs)for k in range(3)]]
removed=[]
for o in originals:
 name=o.name
 remove=any(name.startswith(pre+'_')or name.startswith('Resort_'+pre+'_')for pre in plan['remove_guard_prefixes'])
 if not remove and '_Baluster_'in name and o.type=='MESH':
  lo,hi=bounds(o)
  remove=lo[0]>=54.99 and hi[0]<=68.76 and lo[1]>=83.99 and hi[1]<=85.09 and any(lo[2]>=sgn*90.24-.0125 and hi[2]<=sgn*90.24+.0125 for sgn in [-1,1])
 if remove:removed.append(name)
 else:context.objects.link(o)
mat_names={'stone':'NGRC_WarmLimestone','ivory':'NGRC_PorcelainStructure','wood':'NGRC_HoneyWalnut','metal':'NGRC_BrushedChampagne','soil':'NGRC_PlantingBed','opal':'NGRC_OpalFixture'}
materials={role:next(m for m in bpy.data.materials if m.name==name)for role,name in mat_names.items()}
new=bpy.data.collections.new('Lower court end architecture r001');bpy.context.scene.collection.children.link(new)
def own(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 new.objects.link(o)
def cube(name,lo,hi,role):
 bpy.ops.mesh.primitive_cube_add(size=1,location=C([(lo[k]+hi[k])/2 for k in range(3)]));o=bpy.context.object;o.name=name;o.dimensions=(hi[0]-lo[0],hi[2]-lo[2],hi[1]-lo[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(materials[role]);own(o);return o
for region in plan['regions']:
 ring=region['rings'][0];cube(region['id'],[min(v[0]for v in ring),83.76,min(v[1]for v in ring)],[max(v[0]for v in ring),84,max(v[1]for v in ring)],'stone')
for row in plan['parts']:
 lo=row['min'];hi=row['max']
 if row['shape']=='box':o=cube(row['name'],lo,hi,row['role'])
 else:
  bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=(hi[0]-lo[0])/2,depth=hi[1]-lo[1],location=C([(lo[k]+hi[k])/2 for k in range(3)]));o=bpy.context.object;o.name=row['name'];o.data.materials.append(materials[row['role']]);own(o)
 o['runtime_part']=row['name'];o['contact']=row['contact']
plant_meshes=0
for row in plan['plants']:
 transform=Matrix.Translation(C(row['target_center']))@Matrix.Scale(row['uniform_scale'],4)@Matrix.Translation(-C(row['source_center']))
 parts=[o for o in originals if o.type=='MESH'and o.name.startswith(row['source_prefix'])];assert parts
 for i,old in enumerate(parts):
  obj=bpy.data.objects.new(row['name']+'_'+str(i),old.data);new.objects.link(obj);obj.matrix_world=transform@old.matrix_world;obj['linked_source_object']=old.name;plant_meshes+=1
for row in plan['furniture']:
 name={'AST-FUR-002.glb':'AST-FUR-002_day_reading_chair.blend','AST-FUR-003.glb':'AST-FUR-003_day_table.blend'}[row['model_file']]
 with bpy.data.libraries.load(str(R/'BlenderCatalogue/assets/furniture'/name),link=True)as(a,b):b.objects=list(a.objects)
 transform=Matrix.Translation(C(row['position']))@Matrix.Rotation(row['yaw'],4,'Z')
 for i,old in enumerate(b.objects):
  if old is None or old.type!='MESH':continue
  obj=bpy.data.objects.new(row['name']+'_'+str(i),old.data);new.objects.link(obj);obj.matrix_world=transform@old.matrix_world;obj['catalogue_source']=row['model_file']
for row in plan['lights']:
 data=bpy.data.lights.new(row['name'],'SPOT');obj=bpy.data.objects.new(row['name'],data);new.objects.link(obj);obj.location=C(row['position']);obj.rotation_euler=(C(row['target'])-obj.location).to_track_quat('-Z','Y').to_euler();data.energy=300*row['energy'];data.color=(1,.78,.51);data.spot_size=math.radians(row['angle']*2);obj['runtime_light_budget']='existing eight-source selector; native light watts are preview only'
bpy.context.scene['status']='Integrated-source candidate; retained exact native links; final visual/engineering/gameplay acceptance open'
bpy.context.scene['plan_sha256']=hashlib.sha256((P/'PLAN.json').read_bytes()).hexdigest()
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True,relative_remap=True)
receipt={'status':'NATIVE_AUTHORED','path':str(out.relative_to(R)),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bytes':out.stat().st_size,'plan_sha256':bpy.context.scene['plan_sha256'],'new_floor_regions':2,'new_floor_area_m2':610.5,'new_architectural_parts':len(plan['parts']),'linked_canopy_parts':plant_meshes,'canopy_groups':4,'retained_catalogue_placements':6,'native_excluded_connected_terminal_parts':removed,'native_originals_unchanged':True,'new_capacity':0,'new_upper_decks':0,'runtime_plant_meshes_shared':True,'visual_accepted':False}
(P/'evidence/NATIVE.json').write_text(json.dumps(receipt,indent=2)+'\n');print('LOWER_COURTS_NATIVE',len(plan['parts']),plant_meshes,len(removed),receipt['bytes'])
