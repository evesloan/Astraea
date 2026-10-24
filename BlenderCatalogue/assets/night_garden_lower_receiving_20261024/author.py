from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector
N=Path(__file__).resolve().parent;R=N.parents[2];P=R/'Game/night_garden_lower_receiving_20261024'
plan=json.loads((P/'RECEIVING.json').read_text());out=N/'NightGardenLowerReceiving_r001.blend';assert not out.exists()
bpy.ops.wm.read_factory_settings(use_empty=True)
roles={}
for name,color in [('warm_stone',(.65,.60,.49,1)),('champagne_metal',(.65,.68,.68,1))]:
 m=bpy.data.materials.new(name);m.diffuse_color=color;m['runtime_owner']='existing ship.surface('+name+')';roles[name]=m
C=lambda p:Vector((p[0],-p[2],p[1]))
def box(name,lo,hi):
 vs=[C((x,y,z))for x,y,z in [(lo[0],lo[1],lo[2]),(hi[0],lo[1],lo[2]),(hi[0],lo[1],hi[2]),(lo[0],lo[1],hi[2]),(lo[0],hi[1],lo[2]),(hi[0],hi[1],lo[2]),(hi[0],hi[1],hi[2]),(lo[0],hi[1],hi[2])]]
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(roles['warm_stone']);return o
def beam(name,a,b,radius):
 av=C(a);bv=C(b);delta=bv-av;bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=radius,depth=delta.length,location=(av+bv)*.5);o=bpy.context.object;o.name=name;o.rotation_euler=delta.to_track_quat('Z','Y').to_euler();o.data.materials.append(roles['champagne_metal']);return o
for row in plan['regions']:
 xs=[p[0]for p in row['rings'][0]];zs=[p[1]for p in row['rings'][0]];o=box(row['id'],[min(xs),row['floor_y']-.24,min(zs)],[max(xs),row['floor_y'],max(zs)]);o['receiving_role']='missing-only public street slab; no private slab duplication'
for row in plan['new_guards']:
 a=row['a'];b=row['b'];beam(row['id']+'_Rail',[a[0],a[1]+1.1,a[2]],[b[0],b[1]+1.1,b[2]],.04);steps=max(1,math.ceil((C(b)-C(a)).length/2))
 for i in range(steps+1):
  p=[a[k]+(b[k]-a[k])*i/steps for k in range(3)];beam(row['id']+'_Post_'+str(i),p,[p[0],p[1]+1.1,p[2]],.035)
# Link the exact previously authored17-room native. Do not duplicate meshes.
source=R/'BlenderCatalogue/assets/night_garden_lower_bank_20261022/NightGardenLower17Native_r001.blend'
with bpy.data.libraries.load(str(source),link=True)as(a,b):b.objects=[name for name in a.objects if name.startswith('NightGardenLower_')]
assert len(b.objects)==17
for o in b.objects:bpy.context.collection.objects.link(o)
bpy.context.scene['status']='INTEGRATION WIP; four streets, exact guard successors;17 existing room floors reused; no final visual/primary-structure acceptance'
bpy.context.scene['receiving_plan_sha256']=hashlib.sha256((P/'RECEIVING.json').read_bytes()).hexdigest();bpy.context.scene['source_native_sha256']=hashlib.sha256(source.read_bytes()).hexdigest();bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True,relative_remap=True)
receipt={'status':'NATIVE_RECEIVING_AUTHORED','path':str(out.relative_to(R)),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bytes':out.stat().st_size,'retained_linked_rooms':17,'new_street_slabs':4,'new_or_replacement_guard_segments':len(plan['new_guards']),'new_private_floors':0,'new_room_meshes':0,'plan_sha256':bpy.context.scene['receiving_plan_sha256'],'source_native_sha256':bpy.context.scene['source_native_sha256'],'runtime_geometry':'Existing structural_floor_builder and central_house_connections consume the same pinned RECEIVING.json; native presentation colors only reference shared runtime material roles','accepted_art':False}
(P/'evidence/NATIVE.json').write_text(json.dumps(receipt,indent=2)+'\n');print('NIGHT_GARDEN_RECEIVING_NATIVE',json.dumps(receipt))
