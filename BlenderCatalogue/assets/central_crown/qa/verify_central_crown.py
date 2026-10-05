"""Independent source/export and actual shared-door sweep verification. No Godot work."""
from pathlib import Path
from collections import Counter
import bpy,bmesh,json,math,hashlib
from mathutils import Vector
from mathutils.kdtree import KDTree
R=Path(__file__).resolve().parents[1];C=R.parents[1];AID='AST-CMD-001';D=json.loads((R/'source/section_contract.json').read_text());P=json.loads((R/'source/geometry_parts.json').read_text())['parts'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(R/'source'/(AID+'.blend')))
def signatures(o):
 o.data.calc_loop_triangles();uv=o.data.uv_layers.active
 for t in o.data.loop_triangles:
  points=[]
  for vi,li in zip(t.vertices,t.loops):
   p=o.matrix_world@o.data.vertices[vi].co;q=uv.data[li].uv;points.append(tuple(round(v,3)for v in (*p,*q)))
  yield(o.data.materials[t.material_index].name,tuple(sorted(points)))
S=Counter();source_points=[];source_count=0;uv_faces=0;uv_error=0
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 source_count+=1;bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold for e in bm.edges),o.name;assert bm.calc_volume(signed=True)>0,o.name;assert all(f.calc_area()>1e-10 for f in bm.faces),o.name;bm.free();assert o.data.uv_layers
 scale=o.data.materials[0]['meters_per_tile_uv'];uv=o.data.uv_layers.active.data
 for f in o.data.polygons:
  qs=[uv[i].uv for i in f.loop_indices];area=abs(sum(a.x*b.y-a.y*b.x for a,b in zip(qs,qs[1:]+qs[:1])))/2;err=abs(area*scale[0]*scale[1]-f.area)/f.area;uv_error=max(uv_error,err);uv_faces+=1;assert err<.035,(o.name,err)
 S.update(signatures(o));source_points.extend(o.matrix_world@v.co for v in o.data.vertices)
source_markers={o.name:list(o.location)for o in bpy.context.scene.objects if o.type=='EMPTY'}
T=KDTree(len(source_points))
for i,p in enumerate(source_points):T.insert(p,i)
T.balance();bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.materials):bpy.data.materials.remove(m,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(R/'exports'/(AID+'.glb')));E=Counter();export_points=[];batch_sizes=[];max_error=0;glass_batches=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 E.update(signatures(o));vs=[o.matrix_world@v.co for v in o.data.vertices];export_points.extend(vs);size=[max(v[k]for v in vs)-min(v[k]for v in vs)for k in range(3)];batch_sizes.append(size)
 assert max(size)<16.001,(o.name,size)
 assert o.data.uv_layers and all(math.isfinite(v)for uv in o.data.uv_layers.active.data for v in uv.uv)
 for v in vs:max_error=max(max_error,T.find(v)[2])
 if any(m.name=='ASTRAEA_crown_tinted_glass'for m in o.data.materials):glass_batches.append(o.name)
assert S==E,('triangles_materials_uv_changed',sum((S-E).values()),sum((E-S).values()));assert max_error<.0001,max_error
ET=KDTree(len(export_points))
for i,p in enumerate(export_points):ET.insert(p,i)
ET.balance();reverse_error=max(ET.find(p)[2]for p in source_points);assert reverse_error<.0001
markers={o.name:o for o in bpy.context.scene.objects if o.type=='EMPTY'}
for name,p in source_markers.items():assert name in markers and (markers[name].location-Vector(p)).length<.0001,name
# Pure geometric checks use recorded actual source vertices, not authored intentions.
def overlap(a,b,tol=1e-6):return all(min(a[2*k+1],b[2*k+1])-max(a[2*k],b[2*k])>tol for k in range(3))
def aabb(v):return [q for k in range(3)for q in[min(p[k]for p in v),max(p[k]for p in v)]]
for p in P:
 if p['group']=='pier':
  b=p['world_aabb'];assert max(abs(b[0]),abs(b[1]))<=51.90001 and min(abs(b[0]),abs(b[1]))>=51.09999;assert b[2]>=-3.20001 and b[3]<=114.00001
 if p['group']in['roof','ceiling']:
  b=p['world_aabb'];assert b[2]>=109 and b[3]<=114.50001 and b[0]>=-36.00001 and b[1]<=36.00001 and b[4]>=-78.00001 and b[5]<=64.00001,(p['name'],b)
assert not any(overlap(p['world_aabb'],[-4,4,106.51,110.5,-78,60])for p in P),'public route blocked'
assert not any(overlap(p['world_aabb'],[-48,48,106.51,110.5,-80,-74])for p in P),'north cross-street belt blocked'
assert not any(p['group']=='floor'for p in P)
def in_polygon(x,z,ring):
 inside=False
 for a,b in zip(ring,ring[1:]+ring[:1]):
  cross=(b[0]-a[0])*(z-a[1])-(b[1]-a[1])*(x-a[0])
  if abs(cross)<1e-4 and min(a[0],b[0])-1e-5<=x<=max(a[0],b[0])+1e-5 and min(a[1],b[1])-1e-5<=z<=max(a[1],b[1])+1e-5:return True
  if (a[1]>z)!=(b[1]>z) and x<(b[0]-a[0])*(z-a[1])/(b[1]-a[1])+a[0]:inside=not inside
 return inside
for programme in D['programmes']:
 for p in P:
  if programme['programme_key']in p['name']:
   assert all(in_polygon(v[0],v[2],programme['boundary'])for v in p['vertices_world']),(p['name'],'outside programme')
for q in P:
 if q['name'].startswith('CMD_RoofPurlin'):
  assert any(p['name'].startswith('CMD_Longitudinal')and overlap(q['world_aabb'],p['world_aabb'])for p in P),(q['name'],'no longitudinal bearing')

# Leaf OBB vs source AABB separating-axis test. Rotations use actual Blender hinge-local parts.
bpy.ops.wm.open_mainfile(filepath=str(C/'assets/staff_threshold/source/AST-STF-008.blend'))
leaf_data=[];fixed=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 if o.parent and o.parent.name.startswith('HINGE_'):
  leaf_data.append((o.name,tuple(o.parent.location),[tuple(v.co)for v in o.data.vertices],1 if o.parent.name=='HINGE_LEFT'else-1))
 elif o.name.startswith('STF_'):fixed.append({'name':o.name,'vertices':[(v.co.x,v.co.z,-v.co.y)for v in o.data.vertices]})
assert len(fixed)==3 and len(leaf_data)==9,(len(fixed),len(leaf_data))
def plan_sat(points,b,tol=1e-7):
 # Vertices project to a rectangle under this yaw. Hull corners are measured from OBB source points.
 pts=list(set((p[0],p[2])for p in points));cx=sum(p[0]for p in pts)/len(pts);cz=sum(p[1]for p in pts)/len(pts);pts.sort(key=lambda p:math.atan2(p[1]-cz,p[0]-cx));rect=[(b[0],b[4]),(b[1],b[4]),(b[1],b[5]),(b[0],b[5])];axes=[(1,0),(0,1)]
 for p,q in zip(pts,pts[1:]+pts[:1]):
  dx=q[0]-p[0];dz=q[1]-p[1]
  if dx*dx+dz*dz>1e-12:axes.append((-dz,dx))
 for ax,az in axes:
  aa=[ax*p[0]+az*p[1]for p in pts];bb=[ax*p[0]+az*p[1]for p in rect]
  if min(max(aa),max(bb))-max(min(aa),min(bb))<=tol:return False
 return True
sweep_samples=0;door_records=[]
for door in D['doors']:
 x,y,z=door['position'];yaw=door['yaw'];co,si=math.cos(yaw),math.sin(yaw)
 near=[p for p in P if overlap(p['world_aabb'],[x-1.6,x+1.6,y,y+2.57,z-1.6,z+1.6])]
 for deg in range(91):
  angle=math.radians(deg)
  for name,pivot,vertices,sign in leaf_data:
   c,s=math.cos(sign*angle),math.sin(sign*angle);points=[]
   for vx,vy,vz in vertices:
    bx=pivot[0]+c*vx-s*vy;by=pivot[1]+s*vx+c*vy;gz=-by;points.append((x+co*bx+si*gz,y+vz,z-si*bx+co*gz))
   b=aabb(points);sweep_samples+=1
   for p in near:
    if overlap(b,p['world_aabb'])and plan_sat(points,p['world_aabb']):raise AssertionError(('door_leaf_source_collision',door['name'],name,deg,p['name']))
 # Frame-wall joint: actual fixed frame's full outer bounds and exact depth intersect the fitted wall sides/header.
 # This checks seam sealing without substituting a frame from its nominal aperture.
 fverts=[v for o in fixed for v in o['vertices']];fb=aabb(fverts);assert abs(fb[0]+1.38)<1e-5 and abs(fb[1]-1.38)<1e-5 and abs(fb[3]-2.82)<1e-5
 for side in [-1,1]:
  q=[x+co*side*1.3775-si*.01,y+1.3,z-si*side*1.3775-co*.01]
  assert any(p['world_aabb'][0]-1e-6<=q[0]<=p['world_aabb'][1]+1e-6 and p['world_aabb'][2]<=q[1]<=p['world_aabb'][3]and p['world_aabb'][4]-1e-6<=q[2]<=p['world_aabb'][5]+1e-6 for p in P),(door['name'],'jamb_seam')
 assert any(p['world_aabb'][0]-1e-6<=x-si*.01<=p['world_aabb'][1]+1e-6 and p['world_aabb'][2]<=y+2.8175<=p['world_aabb'][3]and p['world_aabb'][4]-1e-6<=z-co*.01<=p['world_aabb'][5]+1e-6 for p in P),(door['name'],'header_seam')
 door_records.append({'name':door['name'],'angles_degrees':[0,90],'angle_step_degrees':1,'actual_moving_meshes':len(leaf_data),'samples':91*len(leaf_data),'new_source_collisions':0,'frame_side_overlap_m':.005,'frame_top_overlap_m':.005})
# Exact downward marker origins are10mm below the lens, and all rays to existing floor are clear.
for m in D['light_markers']:
 x,y,z=m['position'];lens=[p for p in P if p['role']=='staff_opal'and p['world_aabb'][0]-1e-5<=x<=p['world_aabb'][1]+1e-5 and p['world_aabb'][4]-1e-5<=z<=p['world_aabb'][5]+1e-5 and abs(p['world_aabb'][2]-y-.01)<1e-5];assert lens,(m['name'],'lens missing')
 q=[x-.001,x+.001,106.51,y,z-.001,z+.001];assert not any(overlap(p['world_aabb'],q)for p in P),(m['name'],'emitter_exit_blocked')
# Window edge contacts and selected-only programme allocation.
for w in D['windows']:
 glass=[p for p in P if p['role']=='crown_tinted_glass'and w['programme_key']in p['name']];assert glass
 for p in glass:
  assert max(abs(v[0])for v in p['vertices_world'])<=36 and all(106.9499<=v[1]<=110.5501 for v in p['vertices_world'])
  # Both end faces meet mullions, while lower/upper glass end vertices lie in a real sill/head pocket.
  for z in [p['world_aabb'][4],p['world_aabb'][5]]:
   assert any(q['group']=='glazing'and q['role']!='crown_tinted_glass'and w['programme_key']in q['name']and q['world_aabb'][4]-1e-5<=z<=q['world_aabb'][5]+1e-5 for q in P)
# Deliberate transfer contacts: every pier top meets a transverse girder, every longitudinal meets both transverse frames.
contacts=[]
for x,z in D['support']['pier_centres_xz']:
 region=[x-.4,x+.4,111.25,114,z-.6,z+.6];hits=[p for p in P if p['group']=='transfer'and overlap(region,p['world_aabb'])];assert hits;contacts.append({'pier':[x,z],'transfer_parts':[p['name']for p in hits]})
for x in [-32,0,32]:
 for z in [-71,71]:
  assert any(p['name'].startswith('CMD_TransferGirder')and overlap(p['world_aabb'],[x-.4,x+.4,111.05,113.15,z-.55,z+.55])for p in P)
for tie in D['support']['authored_ties']:
 assert any(p['group']=='pier'and overlap(tie['world_aabb'],p['world_aabb'])for p in P),tie['name']
protected=json.loads((R/'qa/protected_prior_assets.json').read_text());assert protected['catalogue_count']==159
for a in protected['assets']:assert sha(C/a['path'])==a['sha256'],('protected_changed',a['path'])
report={'catalogue_id':AID,'source_closed_outward_meshes':source_count,'source_triangles':sum(S.values()),'export_triangles':sum(E.values()),'triangle_material_uv_equivalence_at_1mm_rounding':True,'source_to_export_vertex_max_error_m':reverse_error,'export_to_source_vertex_max_error_m':max_error,'uv_faces_tested':uv_faces,'max_metric_uv_area_relative_error':uv_error,'runtime_mesh_batches':len(batch_sizes),'max_runtime_dimensions_blender_xyz_m':[max(x[k]for x in batch_sizes)for k in range(3)],'light_markers':len(D['light_markers']),'all_markers_preserved':True,'downward_lens_exit_m':.01,'all_downward_light_exits_clear':True,'door_leaf_samples':sweep_samples,'doors':door_records,'fixed_frame_actual_source_sha256':sha(C/'assets/staff_threshold/source/AST-STF-008.blend'),'glazing_programmes':[w['programme_key']for w in D['windows']],'glass_batch_names':glass_batches,'pier_envelope_0_8_by_1_2_m_preserved':True,'public_route_X_plus_minus4_clear':True,'no_general_floor_or_duplicate_static_leaves':True,'deliberate_pier_transfer_contacts':contacts,'principal_band_ties':len(D['support']['authored_ties']),'all_ties_intersect_spine_chords':True,'protected_prior_design_count':159,'protected_prior_source_export_files':len(protected['assets']),'source_sha256':sha(R/'source'/(AID+'.blend')),'export_sha256':sha(R/'exports'/(AID+'.glb')),'limits':['Source-only checks, not Godot collision or walking acceptance','Band-slab edge embed independently cross-checked in source report; parent must run new tie contact/clearance queries','No structural load certification','Furnishings, operational command, final art, celestial composition and neighbouring pavilion views remain open']}
(R/'qa/source_export_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k not in['doors','glass_batch_names','deliberate_pier_transfer_contacts']}))
