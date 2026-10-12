"""Fresh native/source support, original-runtime fit and repeat-export proof."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;R=P.parents[3];T=P.parent/'thermal_targets'
code=(T/'author_entries.py').read_text();exec(code[code.index('def digest'):code.index('provenance=')])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bounds(o):
 vs=[o.matrix_world@v.co for v in o.data.vertices];return [[min(v[a] for v in vs),max(v[a] for v in vs)] for a in range(3)]
def bvh(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(f.vertices) for f in o.data.polygons])
def hit_top(o,p,y):
 v=xyz(p);hit=bvh(o).ray_cast(v+Vector((0,0,.02)),Vector((0,0,-1)),.04);return hit[0] is not None and abs(hit[0].z-y)<.0015
results=[]
for spec in json.loads((P/'THERMAL_SUPPORT_CONTRACT.json').read_text())['rooms']:
 bpy.ops.wm.open_mainfile(filepath=str(R/spec['native']));assert sha(R/spec['native'])==spec['native_sha256'];assert sha(R/spec['source_context'])==spec['source_context_sha256']
 for n,h in spec['original_context_meshes'].items():assert digest(bpy.data.objects[n])==h,n
 for n,h in spec['original_packed_images'].items():assert hashlib.sha256(bpy.data.images[n].packed_file.data).hexdigest()==h,n
 for n,h in spec['new_meshes'].items():assert digest(bpy.data.objects[n])==h,n
 old_bounds={n:bounds(bpy.data.objects[n]) for n in spec['original_context_meshes']};pairs=0;contacts=[];mounts=[];cur=spec['programme_key'];prefix='G6_SUPPORT_'+cur[-2:]+'__'
 for n in spec['new_meshes']:
  o=bpy.data.objects[n];a=bounds(o)
  for old in spec['original_context_meshes']:
   b=old_bounds[old];pairs+=1
   assert not all(min(a[k][1],b[k][1])-max(a[k][0],b[k][0])>.003 for k in range(3)),(n,old,a,b)
  if 'seat_foot_' in n or n.endswith('mast_floor_anchor'):
   station=next(t for t in spec['stations'] if n.startswith(prefix+'station_'+t['id'].split('_support_')[1].split('_')[0]+'_'));landing=bpy.data.objects[station['support_landing_mesh']];vs=[o.matrix_world@v.co for v in o.data.vertices];low=min(v.z for v in vs)
   assert abs(low-44.9)<.0015
   for v in vs:
    if abs(v.z-low)>.0001:continue
    p=[v.x,v.z,-v.y];ok=hit_top(landing,p,low);assert ok,(n,p);contacts.append({'part':n,'xyz':p,'original_landing_contact':ok})
 for station in spec['stations']:
  j=station['id'].split('_support_')[1].split('_')[0];mount=bpy.data.objects[prefix+'station_'+j+'_task_mount'];crown=bpy.data.objects[prefix+'station_'+j+'_parked_head'];a=bounds(mount);b=bounds(crown)
  assert abs(a[2][1]-b[2][0])<.002,(a,b);mounts.append({'id':station['task_light']['id'],'native_mount_crown_contact':True})
  landing=bpy.data.objects[station['support_landing_mesh']]
  center=station['turn_proposal_xyz']
  for k in range(24):
   import math
   p=[center[0]+.75*math.cos(k*math.tau/24),center[1],center[2]+.75*math.sin(k*math.tau/24)];assert hit_top(landing,p,44.9),('turn floor',p)
 # Actual original water-face and bed coverage at every future carrier corner.
 water_corners=[]
 for station in spec['stations']:
  import math
  end=station['proposed_water_seat_xyz'];mast=station['mast_anchor_xyz'];park=station['seat_top_xyz'];direction=1 if park[2]>mast[2] else -1
  yaw=math.atan2((end[0]-mast[0])*direction,(end[2]-mast[2])*direction)
  assert abs(math.hypot(end[0]-mast[0],end[2]-mast[2])-abs(park[2]-mast[2]))<.0001
  for dx in [-.475,.475]:
   for dz in [-.425,.425]:
    x=end[0]+math.cos(yaw)*dx+math.sin(yaw)*dz;z=end[2]-math.sin(yaw)*dx+math.cos(yaw)*dz
    p=xyz((x,46,z));water_hit=bvh(bpy.data.objects[station['water_visual_mesh']]).ray_cast(p,Vector((0,0,-1)),2);bed_hit=bvh(bpy.data.objects[station['bed_mesh']]).ray_cast(p,Vector((0,0,-1)),2)
    assert water_hit[0] is not None and abs(water_hit[0].z-44.92)<.003,(station['id'],'water',x,z)
    assert bed_hit[0] is not None and abs(bed_hit[0].z-44.3)<.003,(station['id'],'bed',x,z)
    water_corners.append({'id':station['id'],'xyz':[x,44.48,z],'original_water_and_bed':True})
 bpy.ops.object.select_all(action='DESELECT')
 for n in spec['new_meshes']:bpy.data.objects[n].select_set(True)
 repeat=Path('/workspace/group6-repeat-export')/Path(spec['export']).name;bpy.ops.export_scene.gltf(filepath=str(repeat),export_format='GLB',use_selection=True,export_extras=True,export_cameras=False,export_lights=False,export_materials='EXPORT');assert sha(repeat)==spec['export_sha256']
 expected=bounds(bpy.data.objects[cur+'__wet_landing']);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/spec['current_room_runtime']));assert sha(R/spec['current_room_runtime'])==spec['current_room_runtime_sha256'];actual=bounds(bpy.data.objects[cur+'__wet_landing']);assert max(abs(actual[a][k]-expected[a][k]) for a in range(3) for k in range(2))<.002
 results.append({'programme':cur,'status':'PASS','preserved_context_meshes':len(spec['original_context_meshes']),'preserved_packed_images':len(spec['original_packed_images']),'new_meshes_checked':len(spec['new_meshes']),'conservative_new_original_pairs':pairs,'actual_landing_support_points':contacts,'fixture_mount_contacts':mounts,'future_unoccupied_water_carrier_corners':water_corners,'current_runtime_original_landing_bounds_match':True,'fresh_repeat_export_identical':True,'native_sha256':spec['native_sha256'],'export_sha256':spec['export_sha256'],'occupied_hoist_water_chair_species_engineering_accepted':False})
(P/'SAVED_NATIVE_VERIFICATION.json').write_text(json.dumps({'status':'PASS','rooms':results},indent=2)+'\n');print('THERMAL SUPPORT NATIVE PASS',[(r['programme'],len(r['actual_landing_support_points']),r['conservative_new_original_pairs']) for r in results])
