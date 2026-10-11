"""Fresh saved native integrity, source contact checks and repeat exchange."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;R=P.parents[2]
bpy.ops.wm.open_mainfile(filepath=str(P/'AquaticCompletion_r013.blend'));S=bpy.context.scene
text=(P/'author_completion.py').read_text();exec(text[text.index('def digest(o):'):text.index('before={')])
audit=json.load(open(P/'NATIVE_AUDIT.json'));fail=[]
for n,h in audit['original_mesh_hashes'].items():
 if digest(bpy.data.objects[n])!=h:fail.append('Original mesh changed: '+n)
for n,h in audit['packed_images_preserved'].items():
 if hashlib.sha256(bpy.data.images[n].packed_file.data).hexdigest()!=h:fail.append('Original packed image changed: '+n)
def world(o):return [o.matrix_world@v.co for v in o.data.vertices]
def xyz(v):return (v.x,v.z,-v.y)
floor=json.load(open(R/'Game/data/architecture/AQUATIC_ANNEX_PLAN.json'))['floor_records']
def inside(p,tri):
 x,z=p;a,b,c=tri
 cross=lambda a,b,p:(b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
 v=[cross(a,b,p),cross(b,c,p),cross(c,a,p)]
 return all(q>=-1e-6 for q in v) or all(q<=1e-6 for q in v)
supports=[]
for n in ['AQ6__rest_0_plinth','AQ6__rest_1_plinth','AQ6__rest_2_plinth','AQ6__clean_linen_cabinet','AQ6__used_linen_cabinet','AQ6__arrival_perch_bearing_57.6','AQ6__arrival_perch_bearing_59.4','AQ6__spa_5_support_base','AQ6__spa_6_support_base']:
 o=bpy.data.objects[n];vs=[xyz(v) for v in world(o)];bottom=min(v[1] for v in vs);foot=[v for v in vs if abs(v[1]-bottom)<.00002]
 for x,y,z in foot:
  hit=any(abs(f['top_y']-y)<.001 and any(inside((x,z),t) for t in f['triangles_xz']) for f in floor)
  supports.append({'part':n,'xyz':[x,y,z],'supported':hit})
  if not hit:fail.append('New unsupported floor point: '+n+' '+str((x,y,z)))
def bounds(o):
 v=[xyz(p) for p in world(o)];return ([min(p[k] for p in v) for k in range(3)],[max(p[k] for p in v) for k in range(3)])
old_bounds={n:bounds(bpy.data.objects[n]) for n in audit['original_mesh_hashes'] if n not in audit['exchange_exclusions'] and bpy.data.objects[n].get('kind') not in ['water_visual','tube_static_visual','plant_static','fixture_lens','compiler_floor_proposal']}
fitting_checks=0
for o in S.objects:
 thermal_furniture=o.name.startswith(('AQ6__spa_5_','AQ6__spa_6_')) and any(k in o.name for k in ['_support_base','_support_counter','_closed_linen','_support_handle'])
 if not (o.name.startswith(('AQ6__rest_','AQ6__clean_linen','AQ6__used_linen')) or thermal_furniture) or o.type!='MESH' or o.get('kind') in ['fixture_mount','fixture_lens']:continue
 lo,hi=bounds(o)
 for name,(old_lo,old_hi) in old_bounds.items():
  fitting_checks+=1
  if all(min(hi[k],old_hi[k])-max(lo[k],old_lo[k])>.003 for k in range(3)):fail.append('Conservative furniture overlap: '+o.name+' with '+name)
mounts=[]
for o in S.objects:
 if not o.name.startswith(('AQ6__spa_5_','AQ6__spa_6_')):continue
 if '_canopy_hanger_' not in o.name and '_backdrop_hanger_' not in o.name and '_support_task_bearing' not in o.name:continue
 vs=[xyz(v) for v in world(o)];height=max(v[1] for v in vs)
 # Check the source roof/canopy itself, never infer support from another hanger.
 i=5 if o.name.startswith('AQ6__spa_5_') else 6
 target=bpy.data.objects['AQ6__spa_'+str(i)+'_quiet_canopy'] if '_backdrop_hanger_' in o.name else bpy.data.objects['AQD__opaque_roof']
 center=[sum(v[k] for v in vs if abs(v[1]-height)<.00001)/sum(1 for v in vs if abs(v[1]-height)<.00001) for k in [0,2]]
 inv=target.matrix_world.inverted();origin=inv@Vector((center[0],-center[1],height-.01));direction=(inv.to_3x3()@Vector((0,0,1))).normalized()
 hit,point,normal,face=target.ray_cast(origin,direction,distance=.03)
 attached=hit and abs((target.matrix_world@point).z-height)<.001
 mounts.append({'part':o.name,'target':target.name,'endpoint_xyz':[center[0],height,center[1]],'attached':attached})
 if not attached:fail.append('Unsupported court fixture endpoint: '+o.name)
excluded=audit['exchange_exclusions'];out=Path('/workspace/group6-repeat-export');out.mkdir(exist_ok=True)
namespace={'bpy':bpy,'json':json,'P':out,'S':S,'excluded':excluded}
exec(text[text.index('# Exchange has explicit roles;'):text.index("print('GROUP6 SOURCE PASS")],namespace)
native_export=P/'AquaticCompletion_r013.glb';repeat=out/native_export.name
exact=native_export.read_bytes()==repeat.read_bytes()
result={'status':'PASS' if not fail and exact else 'HOLD','failures':fail,'original_saved_meshes_checked':len(audit['original_mesh_hashes']),'packed_images_checked':len(audit['packed_images_preserved']),'new_floor_support_points':supports,'conservative_furniture_old_geometry_pairs':fitting_checks,'new_mounted_endpoint_checks':mounts,'fresh_saved_native_repeat_export_identical':exact,'native_sha256':hashlib.sha256((P/'AquaticCompletion_r013.blend').read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(native_export.read_bytes()).hexdigest(),'repeat_export_sha256':hashlib.sha256(repeat.read_bytes()).hexdigest(),'scope':'Source vertex/face/UV/transform/material-name/modifier and packed-image preservation; source floor contacts, furniture/original solid AABB separation, actual roof/canopy fixture contacts and exact fresh export. Engineering and gameplay remain open.'}
(P/'SAVED_NATIVE_VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print('GROUP6 FRESH SOURCE',result['status'],fail,'REPEAT',exact)
if result['status']!='PASS':raise RuntimeError('Fresh source held')
