"""Check the exact imported fusion portal, supported collar, clear aperture and leak rays."""
from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];C=R.parents[1];G=C.parent/'astraea-godot-production-20261003'
D=json.loads((R/'source/section_contract.json').read_text());E=D['decks'][1]['interface_extensions'][0]
B=json.loads((R/'source/geometry_parts.json').read_text())['boxes'];prior=json.loads((R/'qa/pre_fusion_collar_geometry.json').read_text())['boxes']
collar=[b for b in B if b['name'].startswith(E['mesh_name_prefix'])]
assert len(collar)==5 and {b['name']for b in collar}==set(E['permitted_parts'])
assert [b for b in B if b not in collar]==prior,'A prior architectural or fixture piece changed'
def overlap(a,b):return all(min(a[2*k+1],b[2*k+1])-max(a[2*k],b[2*k])>1e-6 for k in range(3))
q=[-53.9999,-53.7501,6.0001,9.1999,-433.7999,-430.2001]
assert not any(overlap(b['world_aabb'],q)for b in B),'New collar reduces the full transition opening'
# Retained compiled floor, read-only: prove support without changing floor ownership.
floor_path=G/'data/generated/structural_meshes.json';floor_data=json.loads(floor_path.read_text());floor=next(r for r in floor_data['regions']if r['id']==E['existing_floor_owner'])
assert floor['floor_y']==6
tris=floor['triangles']
def in_tri(p,t):
 cross=lambda a,b,c:(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 s=[cross(a,b,p)for a,b in zip(t,t[1:]+t[:1])];return min(s)>=-1e-7 or max(s)<=1e-7
supported_points=0
for b in collar:
 x0,x1,y0,y1,z0,z1=b['world_aabb']
 for x in [x0,(x0+x1)/2,x1]:
  for z in [z0,(z0+z1)/2,z1]:assert any(in_tri((x,z),t)for t in tris),(b['name'],'unsupported',x,z);supported_points+=1
# Import actual GLBs, never infer geometry only from builder values.
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
verts=[];faces=[];arrivals_bounds=[]
for path,anchor,is_arrivals in [(R/'exports/AST-STF-009.glb',(0,0,0),False),(C/E['measured_existing_asset'],(-31,0,-432),True)]:
 before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(path));new=set(bpy.context.scene.objects)-before
 for o in new:
  if o.type!='MESH':continue
  if is_arrivals and not any(s in o.name for s in ['WestServiceEnclosure','ServiceEntryHeader']):continue
  v=[o.matrix_world@v.co for v in o.data.vertices];world=[(p.x+anchor[0],p.z+anchor[1],-p.y+anchor[2])for p in v]
  if is_arrivals:
   bounds=[min(p[0]for p in world),max(p[0]for p in world),min(p[1]for p in world),max(p[1]for p in world),min(p[2]for p in world),max(p[2]for p in world)]
   arrivals_bounds.append({'name':o.name,'world_aabb':bounds})
  base=len(verts);verts.extend(world);o.data.calc_loop_triangles();faces.extend(tuple(base+v for v in t.vertices)for t in o.data.loop_triangles)
expected={r['name']:r['world_aabb']for r in E['measured_existing_mesh_aabbs']}
for row in arrivals_bounds:
 assert row['name']in expected and max(abs(a-b)for a,b in zip(row['world_aabb'],expected[row['name']]))<1e-6,row
assert len(arrivals_bounds)==3
bvh=BVHTree.FromPolygons(verts,faces,all_triangles=True)
def hit(a,b):
 a,b=Vector(a),Vector(b);delta=b-a;return bvh.ray_cast(a,delta.normalized(),delta.length)[0] is not None
# Side-slot rays across the old 200 mm vertical black slits, sampled every 10 mm.
closed_side_rays=0
for z0,z1 in [(-434,-433.8),(-430.2,-430)]:
 for iz in range(1,20):
  z=z0+(z1-z0)*iz/20
  for iy in range(1,32):
   y=6+3.2*iy/32
   for sign in [-1,1]:
    a=(-54.3,y,z)if sign>0 else(-53.65,y,z);b=(-53.65,y,z)if sign>0 else(-54.3,y,z)
    assert hit(a,b),(a,b,'side_light_leak');closed_side_rays+=1
# Header closes the short axial roof gap; vertical rays cross the entire width.
closed_header_rays=0
for x in [-54.08,-54.01,-53.98,-53.96,-53.93,-53.85,-53.78]:
 for i in range(1,40):
  z=-434+4*i/40;assert hit((x,9.15,z),(x,9.4,z)),(x,z,'header_light_leak');closed_header_rays+=1
# Dense axial aperture rays within the transition itself remain open.
clear_aperture_rays=0
for iz in range(1,36):
 z=-433.8+3.6*iz/36
 for iy in range(1,32):
  y=6+3.2*iy/32;assert not hit((-53.999,y,z),(-53.70,y,z)),(z,y,'blocked_clear_transition');clear_aperture_rays+=1
out={'old_export_sha256':hashlib.sha256((C/E['measured_existing_asset']).read_bytes()).hexdigest(),'new_export_sha256':hashlib.sha256((R/'exports/AST-STF-009.glb').read_bytes()).hexdigest(),'measured_existing_meshes':arrivals_bounds,'new_closed_collar_pieces':len(collar),'prior_1600_authored_parts_unchanged':True,'full_transition_aperture_m':[3.6,3.2],'supported_existing_floor_owner':E['existing_floor_owner'],'compiled_floor_sha256':hashlib.sha256(floor_path.read_bytes()).hexdigest(),'support_points_checked':supported_points,'closed_side_seam_rays':closed_side_rays,'closed_header_seam_rays':closed_header_rays,'clear_aperture_rays':clear_aperture_rays,'general_floor_union_check_remains_strict':True,'new_floor_area_required_m2':0,'scope':'Actual GLB geometry and bounded read-only compiled-floor support checks. Parent owns final in-engine pixels and route regression.'}
(R/'qa/fusion_collar_validation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
