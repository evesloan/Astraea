"""Component source/export, geometric and protected-catalogue verification.
Run with Blender, before runtime integration. No Godot launch or production writes.
"""
from pathlib import Path
from collections import Counter
import bpy,bmesh,json,math,hashlib,subprocess
from mathutils import Vector
from mathutils.kdtree import KDTree
R=Path(__file__).resolve().parents[1];C=R.parents[1];AID='AST-STF-009'
D=json.loads((R/'source/section_contract.json').read_text());B=json.loads((R/'source/geometry_parts.json').read_text())['boxes']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(R/'source'/(AID+'.blend')))
source_points=[];source_tri=Counter();uv_faces=0;max_uv_area_error=0;source_count=0
# Rounded point+UV signatures preserve every material triangle across optimization.
def signatures(o):
 o.data.calc_loop_triangles();uv=o.data.uv_layers.active
 for t in o.data.loop_triangles:
  pts=[]
  for vi,li in zip(t.vertices,t.loops):
   p=o.matrix_world@o.data.vertices[vi].co;q=uv.data[li].uv
   pts.append(tuple(round(v,3)for v in (*p,*q)))
  yield (o.data.materials[t.material_index].name,tuple(sorted(pts)))
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 source_count+=1;bm=bmesh.new();bm.from_mesh(o.data)
 assert all(e.is_manifold for e in bm.edges),o.name
 assert bm.calc_volume(signed=True)>0,o.name
 assert all(f.calc_area()>1e-10 for f in bm.faces),o.name
 bm.free();assert o.data.uv_layers
 scale=o.data.materials[0]['meters_per_tile_uv'];uv=o.data.uv_layers.active.data
 for f in o.data.polygons:
  qs=[uv[i].uv for i in f.loop_indices];area=abs(sum(a.x*b.y-a.y*b.x for a,b in zip(qs,qs[1:]+qs[:1])))/2
  err=abs(area*scale[0]*scale[1]-f.area)/f.area;max_uv_area_error=max(max_uv_area_error,err);uv_faces+=1
  assert err<.03,(o.name,err)
 for v in o.data.vertices:source_points.append(o.matrix_world@v.co)
 source_tri.update(signatures(o))
source_marker={o.name:list(o.location)for o in bpy.context.scene.objects if o.type=='EMPTY'}
tree=KDTree(len(source_points))
for i,p in enumerate(source_points):tree.insert(p,i)
tree.balance()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.materials):bpy.data.materials.remove(m,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(R/'exports'/(AID+'.glb')))
export_tri=Counter();max_error=0;batch_sizes=[];export_points=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 export_tri.update(signatures(o));p=[o.matrix_world@v.co for v in o.data.vertices];export_points.extend(p)
 for q in p:max_error=max(max_error,tree.find(q)[2])
 lo=[min(q[k]for q in p)for k in range(3)];hi=[max(q[k]for q in p)for k in range(3)];size=[hi[k]-lo[k]for k in range(3)];batch_sizes.append(size)
 assert size[0]<=20.0001 and size[1]<=20.0001,(o.name,size)
 assert all(f.area>1e-10 for f in o.data.polygons),o.name
 assert o.data.uv_layers and all(math.isfinite(v)for uv in o.data.uv_layers.active.data for v in uv.uv)
assert source_tri==export_tri,('triangle_or_uv_mismatch',sum((source_tri-export_tri).values()),sum((export_tri-source_tri).values()))
assert max_error<.0001,max_error
export_tree=KDTree(len(export_points))
for i,p in enumerate(export_points):export_tree.insert(p,i)
export_tree.balance();reverse_error=max(export_tree.find(p)[2]for p in source_points);assert reverse_error<.0001
markers={o.name:o for o in bpy.context.scene.objects if o.type=='EMPTY'}
for name,p in source_marker.items():assert name in markers and (markers[name].location-Vector(p)).length<.0001,name
# Exact axis-aligned authored boxes support robust aperture and footprint tests.
def overlap(a,b):return all(min(a[2*k+1],b[2*k+1])-max(a[2*k],b[2*k])>1e-5 for k in range(3))
# Conservative complete cabin sweep, with positive clearance required on every face.
cabin_sweep_inflation=.005
cabin_sweep=[-26.8-.005,-23.2+.005,-.18-.005,14.94+.005,-492-.005,-488+.005]
assert not any(overlap(b['world_aabb'],cabin_sweep)for b in B),[(b['name'],b['world_aabb'])for b in B if overlap(b['world_aabb'],cabin_sweep)]
for deck in D['decks']:
 n=deck['deck'];y=deck['floor_y'];rects=deck['floor_union_rectangles_x0_x1_z0_z1']
 for b in B:
  if b['deck']!=n:continue
  x0,x1,y0,y1,z0,z1=b['world_aabb']
  # General containment remains strict; only explicitly named collar parts use its bounded extension.
  permitted=rects
  if b['name'].startswith('STF_D02_FusionCollar_'):
   ext=deck['interface_extensions'][0];assert b['name'] in ext['permitted_parts'],b['name']
   assert y0>=ext['height_y'][0] and y1<=ext['height_y'][1]
   permitted=[ext['supported_plan_rectangle']]
  for x in [x0+1e-5,(x0+x1)/2,x1-1e-5]:
   for z in [z0+1e-5,(z0+z1)/2,z1-1e-5]:assert any(r[0]-1e-5<=x<=r[1]+1e-5 and r[2]-1e-5<=z<=r[3]+1e-5 for r in permitted),(b['name'],'outside_owned_or_explicit_supported_interface',x,z)
 # Through portal is fully clear for the real gate aperture plus small tolerance.
 query=[-23.4,-22.6,y+.025,y+2.64,-491.195,-488.805]
 assert not any(overlap(b['world_aabb'],query)for b in B),(n,'portal_blocked')
 # Entire dynamic leaf sweep (all four leaves) remains away from authored architecture.
 for x in [-23.08,-23.32]:
  sweep=[x-.04,x+.04,y+.03,y+2.63,-491.83,-488.17]
  assert not any(overlap(b['world_aabb'],sweep)for b in B),(n,'leaf_channel_blocked')
 for ap in deck['boundary_apertures']:
  if ap['name']=='lift_shaft_connection':continue
  a0,a1=ap['range'];p=ap['plane'];q=[p-.02,p+.02,y+.03,y+3.19,a0+.15,a1-.15]if ap['plane_axis']=='x'else[a0+.15,a1-.15,y+.03,y+3.19,p-.02,p+.02]
  assert not any(overlap(b['world_aabb'],q)for b in B),(ap['name'],'interface_blocked')
# Light emission origins are 10 mm below lens underside; no housing or wall occludes the exit.
light_clearances=[]
for mark in D['light_markers']:
 x,y,z=mark['position'];base=(mark['deck']-1)*6
 lenses=[b for b in B if b['role']=='staff_opal' and b['world_aabb'][0]<=x<=b['world_aabb'][1] and b['world_aabb'][4]<=z<=b['world_aabb'][5] and 0<b['world_aabb'][2]-y<.03]
 assert len(lenses)>=1,(mark['name'],'missing_exact_lens') # A cell-boundary fixture may have two exact lens halves.
 clearance=lenses[0]['world_aabb'][2]-y;assert abs(clearance-.01)<1e-5
 ray=[x-.001,x+.001,base+.05,y,z-.001,z+.001]
 assert not any(overlap(b['world_aabb'],ray)for b in B),(mark['name'],'downward_exit_blocked')
 light_clearances.append(clearance)
# Independent fit in the actual authored lower-hull convex ring lofts.
hull=json.loads((C/'assets/lower_hull_body/source/body_contract.json').read_text());planes=[]
for lo,hi in zip(hull['rings'],hull['rings'][1:]):
 bm=bmesh.new()
 for r in [lo,hi]:
  for x,z in r['inner']:bm.verts.new((x,-z,r['y']))
 bmesh.ops.convex_hull(bm,input=list(bm.verts));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 faces=[(f.normal.copy(),f.verts[0].co.copy())for f in bm.faces]
 planes.append((lo['y'],hi['y'],faces));bm.free()
min_hull_distance=1e10;hull_points=0
for box in B:
 x0,x1,y0,y1,z0,z1=box['world_aabb']
 for y in [y0,y1]:
  _,_,faces=next(r for r in planes if r[0]-1e-6<=y<=r[1]+1e-6)
  for x in [x0,x1]:
   for z in [z0,z1]:
    p=Vector((x,-z,y));hull_points+=1
    for n,q in faces:
     distance=-n.dot(p-q);assert distance>-.0001,(box['name'],'outside_lower_hull',distance)
     if abs(n.z)<.98:min_hull_distance=min(min_hull_distance,distance)
# Preserve every previously registered source/export byte relative to the existing manifest.
protected=[]
for a in json.loads((C/'catalogue_manifest.json').read_text())['assets']:
 if a['catalogue_id']==AID:continue
 for key in ['source','export']:
  if key not in a:continue
  p=C/a[key]
  if not p.exists():continue
  # HEAD comparison is independent of possibly historical per-entry manifest hashes.
  result=subprocess.run(['git','-C',str(C),'diff','--quiet','HEAD','--',a[key]],check=False)
  assert result.returncode==0,('protected_asset_changed',a['catalogue_id'],key)
  protected.append({'catalogue_id':a['catalogue_id'],'kind':key,'path':a[key],'sha256':sha(p)})
report={'catalogue_id':AID,'source_closed_outward_meshes':source_count,'source_triangles':sum(source_tri.values()),'export_triangles':sum(export_tri.values()),'exact_triangle_material_uv_equivalence_at_1mm_rounding':True,'source_to_export_vertex_max_error_m':reverse_error,'export_to_source_vertex_max_error_m':max_error,'uv_faces_tested':uv_faces,'max_metric_uv_area_relative_error':max_uv_area_error,'runtime_mesh_batches':len(batch_sizes),'max_runtime_plan_dimensions_m':[max(x[k]for x in batch_sizes)for k in [0,1]],'light_markers':len(D['light_markers']),'all_markers_preserved':True,'all_downward_light_exits_clear':True,'lens_underside_to_light_origin_m':[min(light_clearances),max(light_clearances)],'floor_union_wall_fixture_containment':True,'strict_general_floor_union_check':True,'explicit_supported_interface_extensions':D['decks'][1].get('interface_extensions',[]),'floor_contact_tolerance_east_m':D['lift']['floor_contact_tolerance_east_m'],'lower_hull_corner_points_checked':hull_points,'minimum_oblique_inner_hull_face_distance_m':min_hull_distance,'lift_apertures_and_dynamic_leaf_sweeps_clear':True,'complete_moving_cabin_swept_aabb_clear':True,'cabin_sweep_inflation_m':cabin_sweep_inflation,'ceiling_shaft_reservation_east_x':D['lift']['ceiling_shaft_exclusion'][1],'D01_D02_existing_interface_apertures_clear':True,'D01_existing_spine_sidewalls_omitted_x_range':[-48,-46],'protected_prior_assets':protected,'limitations':['Static source/export geometry checks, not Godot physics or normal-play acceptance','Physical loaded-cart boarding/turning, shell fit and in-engine lighting owned by integration task','Reference-informed construction kit; D03 home and depot are bounded thresholds, not finished rooms','Source uses opaque shaft and shared pre-existing dynamic glazed gate/cabin; no crew assignments added']}
report['protected_reused_derived_assets']=[]
for rel in ['assets/commons_lift_cabin/source/AST-CIR-003_three_stop.blend','assets/commons_lift_cabin/exports/AST-CIR-003_three_stop.glb']:
 assert subprocess.run(['git','-C',str(C),'diff','--quiet','HEAD','--',rel]).returncode==0
 report['protected_reused_derived_assets'].append({'path':rel,'sha256':sha(C/rel)})
(R/'qa/source_export_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='protected_prior_assets'}))
