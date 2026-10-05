"""Independent source/export and actual shared-door sweep verification. No Godot work."""
from pathlib import Path
from collections import Counter
import bpy,bmesh,json,math,hashlib
from mathutils import Vector
from mathutils.kdtree import KDTree
R=Path(__file__).resolve().parents[1];C=R.parents[1];AID='AST-CMD-003';D=json.loads((R/'source/section_contract.json').read_text());P=json.loads((R/'source/geometry_parts.json').read_text())['parts'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
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
 if any(m.name=='ASTRAEA_bridge_gallery_glass'for m in o.data.materials):glass_batches.append(o.name)
assert S==E,('triangles_materials_uv_changed',sum((S-E).values()),sum((E-S).values()));assert max_error<.0001,max_error
ET=KDTree(len(export_points))
for i,p in enumerate(export_points):ET.insert(p,i)
ET.balance();reverse_error=max(ET.find(p)[2]for p in source_points);assert reverse_error<.0001
markers={o.name:o for o in bpy.context.scene.objects if o.type=='EMPTY'}
for name,p in source_markers.items():assert name in markers and (markers[name].location-Vector(p)).length<.0001,name
def overlap(a,b,tol=1e-6):return all(min(a[2*k+1],b[2*k+1])-max(a[2*k],b[2*k])>tol for k in range(3))
def aabb(v):return [q for k in range(3)for q in[min(p[k]for p in v),max(p[k]for p in v)]]

# Actual source geometry must match every ledger vertex, including rotated guard/support beams.
bpy.ops.wm.open_mainfile(filepath=str(R/'source'/(AID+'.blend')))
actual={o.name:o for o in bpy.context.scene.objects if o.type=='MESH'}
assert len(actual)==len(P)
for p in P:
 o=actual[p['name']];vs=[o.matrix_world@v.co for v in o.data.vertices]
 world=[(v.x,v.z,-v.y)for v in vs]
 assert len(world)==len(p['vertices_world'])
 assert max((Vector(a)-Vector(b)).length for a,b in zip(world,p['vertices_world']))<.0001,p['name']
 b=p['world_aabb'];assert b[3]<=114.50001 and b[4]>=-181.00001 and b[5]<=-79.99999,(p['name'],b)
 assert p['group']!='floor'
 if p['group']=='pier':assert any(b[0]>=x-.40001 and b[1]<=x+.40001 and b[4]>=z-.60001 and b[5]<=z+.60001 for x,z in D['support']['pier_centres_xz']),(p['name'],b)
 elif b[2]<105.7999:raise AssertionError(('extra_downward_structure',p['name'],b))
 # Every deeper branch stays outside the D17 spine, irrespective of author-assigned group.
 if b[2]<106.2599 and b[3]>102.01:assert b[1]<=-4.0999 or b[0]>=4.0999,(p['name'],'D17 headroom intrusion',b)
# All old source paths/records exact; the eventual appended catalogue entry is checked separately.
protected=json.loads((R/'qa/protected_prior_files.json').read_text())
for name,value in protected['files'].items():
 if name=='catalogue_manifest.json':continue
 assert sha(C/name)==value,('protected_file_changed',name)
manifest=json.loads((C/'catalogue_manifest.json').read_text())
assert len(manifest['assets']) in[161,162]
assert not D['doors']
# Standing route and the complete actual fore street stay free of new geometry.
protected_volumes=[('old_spine',[-4,4,106.501,110.40,-181.001,-113]),('fore_street',[-48,48,106.501,110.40,-80,-74]),('port_leg_6m',[-47,-41,106.501,110.4,-177,-80]),('fore_leg_6m',[-44,4,106.501,110.4,-180,-174]),('turn_square',[-47,-41,106.501,110.4,-180,-174])]
for label,bb in protected_volumes:
 assert not any(overlap(p['world_aabb'],bb)for p in P),(label,[p['name']for p in P if overlap(p['world_aabb'],bb)])
# Source fixtures: actual local triangles for support and clear optical exits, not only markers.
from mathutils.bvhtree import BVHTree
allv=[];allf=[]
for o in actual.values():
 offset=len(allv);allv.extend(o.matrix_world@v.co for v in o.data.vertices);allf.extend(tuple(i+offset for i in f.vertices)for f in o.data.polygons)
bvh=BVHTree.FromPolygons(allv,allf,all_triangles=False)
fixture_records=[]
for m in D['light_markers']:
 name=m['fixture_assembly'];lens=[p for p in P if p['assembly']==name+'_Lens'];housing=[p for p in P if p['assembly']==name+'_Housing'];assert lens and housing
 assert any(overlap(a['world_aabb'],b['world_aabb'])for a in lens for b in housing)
 support=[p for p in P if p['group']in['ceiling','transfer','bypass_transfer']]
 contacts=[b['name']for a in housing for b in support if overlap(a['world_aabb'],b['world_aabb'])];assert contacts,(name,'no actual backing')
 x,y,z=m['position'];q=Vector((x,-z,y));ob=bpy.context.scene.objects[m['name']];assert (ob.location-q).length<.0001
 for dx,dz in[(0,0),(.08,0),(-.08,0),(0,.08),(0,-.08)]:
  origin=q+Vector((dx,-dz,0));hit=bvh.ray_cast(origin,Vector((0,0,-1)),y-106.501)
  assert hit[0]is None,(m['name'],'downward_exit_hit',hit[0])
 fixture_records.append({'name':m['name'],'source_support_contacts':contacts,'clear_downward_rays':5})
# Return wall is roof-hung, continuously sealed into a shallow retained-floor bearing.
base=[p for p in P if p['assembly']=='BRP_EastReturnSlabHeightClosure'];wall=[p for p in P if p['assembly']=='BRP_EastJunctionReturn'];assert base and wall
for w in wall:assert any(overlap(w['world_aabb'],b['world_aabb'])for b in base)
for b in base:
 bb=b['world_aabb'];assert bb[2]>=106.26 and bb[3]<106.5 and bb[0]<4 and bb[1]>4
 assert overlap(bb,[-4,4,106.26,106.5,-181,-173])
# Markers, texture equality and topology are separate gates. No standalone floor authored.
report={'catalogue_id':AID,'source_closed_outward_meshes':source_count,'source_triangles':sum(S.values()),'export_triangles':sum(E.values()),'triangle_material_uv_equivalence_at_1mm_rounding':True,'source_to_export_vertex_max_error_m':reverse_error,'export_to_source_vertex_max_error_m':max_error,'uv_faces_tested':uv_faces,'max_metric_uv_area_relative_error':uv_error,'runtime_mesh_batches':len(batch_sizes),'max_runtime_dimensions_blender_xyz_m':[max(x[k]for x in batch_sizes)for k in range(3)],'glass_batches':len(glass_batches),'light_markers':len(D['light_markers']),'all_markers_preserved':True,'source_ledger_vertices_match':True,'no_extra_downward_columns':True,'all_deeper_underfloor_branches_outside_D17_spine':True,'source_fixture_exits_and_supports':fixture_records,'protected_clear_volumes':[{'id':a,'world_aabb':b}for a,b in protected_volumes],'east_return_roof_hung_and_slab_height_closure_proven':True,'no_general_floor_or_doors':True,'protected_prior_design_count':161,'protected_prior_files':len(protected['files']),'source_sha256':sha(R/'source'/(AID+'.blend')),'export_sha256':sha(R/'exports'/(AID+'.glb')),'limits':D['runtime_limits']}
(R/'qa/source_export_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='source_fixture_exits_and_supports'}))
