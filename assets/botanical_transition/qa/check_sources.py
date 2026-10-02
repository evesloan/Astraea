"""Actual editable-source checks for BOT-010, including finite void volumes and contact graph."""
import bpy,bmesh,json,hashlib,itertools,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]
meta=json.loads((ROOT/'AST-BOT-010.manifest.json').read_text());source=ROOT/meta['source_blend'];bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.view_layer.update()
obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];trees={};bounds={};samples={};source_parts=[]
for o in obs:
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();vs=[o.matrix_world@v.co for v in me.vertices];polys=[list(p.vertices) for p in me.polygons]
 trees[o.name]=BVHTree.FromPolygons(vs,polys);bounds[o.name]=([min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)])
 samples[o.name]=vs+[sum((vs[i]for i in f),Vector())/len(f) for f in polys]
 bm=bmesh.new();bm.from_mesh(o.data);bad=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);bm.free()
 source_parts.append({'name':o.name,'role':o['material_role'],'source_nonmanifold_edges':bad,'source_signed_volume_m3':volume,'evaluated_min_m':bounds[o.name][0],'evaluated_max_m':bounds[o.name][1],'editable_modifiers':[m.type for m in o.modifiers],'passed':bad==0 and volume>0 and all(math.isfinite(c)for v in vs for c in v)})
 ev.to_mesh_clear()
def inside(name,p):
 t=trees[name];p=Vector(p);near=t.find_nearest(p)
 if near[3] is not None and near[3]<.00003:return True
 d=Vector((.937,.287,.199)).normalized();count=0;start=p.copy()
 for _ in range(100):
  co,no,ix,dist=t.ray_cast(start,d,100)
  if co is None:break
  count+=1;start=co+d*.000001
 return count%2==1
contacts=[]
for m in meta['markers']:
 ob=bpy.data.objects[m['name']];p=ob.matrix_world.translation;row={'name':m['name'],'position_error_m':(p-Vector(m['source_m'])).length,'passed':(p-Vector(m['source_m'])).length<1e-6}
 if m['physical_target'] in trees:
  near=trees[m['physical_target']].find_nearest(p);row.update(target=m['physical_target'],surface_distance_m=near[3],physical_normal=list(near[1]));row['passed'] &= near[3]<.00015
  if m['physical_normal_source']:
   row['normal_dot']=near[1].dot(Vector(m['physical_normal_source']));row['passed'] &=row['normal_dot']>.99
 contacts.append(row)
# Selected joins have witnesses on actual surfaces or inside an explicit bearing overlap.
joins=[]
def join(name,parts,p):
 ds=[trees[k].find_nearest(Vector(p))[3] for k in parts];ins=[inside(k,p) for k in parts];joins.append({'name':name,'parts':parts,'witness_source_m':p,'surface_distances_m':ds,'on_or_inside_each':ins,'passed':all(ins)})
for i,x in enumerate([.220,.900,1.580],1):
 join('shoe_to_bracket_'+str(i),['floor_contact_bracket_shoe_'+str(i),'seat_load_bracket_'+str(i)],[x,-.1,.065])
 join('bracket_to_seat_'+str(i),['seat_load_bracket_'+str(i),'timber_sitting_ribbon_2'],[x,-.24,.415])
 for r,y in [(1,-.1),(2,-.37)]:join('bracket_to_rail_'+str(i)+'_'+str(r),['seat_load_bracket_'+str(i),'timber_underseat_bearing_rail_'+str(r)],[x,y,.400])
for i,x in enumerate([.780,1.570],1):join('upper_pier_to_floor_'+str(i),['upper_cell_floor_pier_'+str(i),'upper_cell_floor'],[x,.515,.335])
join('upper_soil_on_base',['upper_usable_soil_volume','upper_cell_floor'],[1.10,.515,.365]);join('lower_soil_on_base',['lower_usable_soil_volume','lower_basin_floor'],[.28,.515,.105])
join('upper_soil_to_riser',['upper_usable_soil_volume','transverse_riser_retaining_wall'],[.680,.515,.50]);join('upper_soil_to_end',['upper_usable_soil_volume','closed_end_retaining_return'],[1.680,.515,.50])
# Whole-volume grids supplemented by bidirectional rays along all three axes.
voids=[]
void_specs=[('seated_above_ribbon',[.010,-.485,.471],[1.790,-.025,1.350]),('underseat_bay_1',[.280,-.420,.090],[.840,-.120,.340]),('underseat_bay_2',[.960,-.420,.090],[1.520,-.120,.340]),('lower_planting_opening',[.020,.200,.435],[.290,.830,1.30]),('upper_planting_opening',[.710,.200,.835],[1.650,.830,1.30]),('front_approach',[.010,-1.690,.005],[1.790,-.500,1.90]),('rear_maintenance_unplanted',[.010,1.080,.005],[1.790,1.880,1.90]),('under_upper_floor_void',[.850,.240,.115],[1.500,.790,.320])]
for name,lo,hi in void_specs:
 hits=[];rays=0
 for p in itertools.product(*[[lo[i]+(hi[i]-lo[i])*k/6 for k in range(7)]for i in range(3)]):
  for n in trees:
   b0,b1=bounds[n]
   if all(b0[i]<=p[i]<=b1[i] for i in range(3))and inside(n,p):hits.append({'part':n,'point':list(p),'kind':'volume grid'})
 for axis in range(3):
  others=[i for i in range(3)if i!=axis]
  for aa,bb in itertools.product(range(7),repeat=2):
   p=Vector(lo);p[others[0]]=lo[others[0]]+(hi[others[0]]-lo[others[0]])*aa/6;p[others[1]]=lo[others[1]]+(hi[others[1]]-lo[others[1]])*bb/6;d=Vector([int(i==axis)for i in range(3)]);rays+=1
   for n,t in trees.items():
    co,no,idx,dist=t.ray_cast(p,d,hi[axis]-lo[axis])
    if co is not None:hits.append({'part':n,'point':list(co),'kind':'full-volume ray'})
 voids.append({'name':name,'min_source_m':lo,'max_source_m':hi,'grid_points':343,'rays':rays,'hits':hits[:12],'hit_count':len(hits),'passed':not hits})
# Each part must reach a floor-contacting source part through actual surface
# distances or buried union contacts. Report the graph, not a declared list.
edges=[]
for a,b in itertools.combinations([o.name for o in obs],2):
 al,ah=bounds[a];bl,bh=bounds[b]
 if any(ah[i]+.0015<bl[i]or bh[i]+.0015<al[i]for i in range(3)):continue
 hit=None
 for left,right in [(a,b),(b,a)]:
  for p in samples[left]:
   near=trees[right].find_nearest(p)
   if near[3]<.0015 or (all(bounds[right][0][i]<=p[i]<=bounds[right][1][i]for i in range(3))and inside(right,p)):
    hit={'parts':[a,b],'witness_source_m':list(p),'surface_distance_m':near[3],'kind':'touch/overlap' if near[3]<.0015 else 'buried overlap'};break
  if hit:break
 if hit:edges.append(hit)
floor_nodes=[o.name for o in obs if abs(bounds[o.name][0][2])<1e-6];reachable=set(floor_nodes)
for _ in obs:
 for e in edges:
  if any(n in reachable for n in e['parts']):reachable.update(e['parts'])
isolated=sorted(set(trees)-reachable)
materials=[]
for mat in {s.material for o in obs for s in o.material_slots}:
 imgs=[n.image for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]
 materials.append({'name':mat.name,'images_packed':bool(imgs)and all(i.packed_file for i in imgs),'passed':bool(imgs)and all(i.packed_file for i in imgs)})
result={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'editable_parts':source_parts,'physical_markers':contacts,'support_witnesses':joins,'finite_void_volume_checks':voids,'contact_graph':{'floor_nodes':floor_nodes,'edges':edges,'isolated_parts':isolated,'all_parts_reach_floor':not isolated},'material_checks':materials,'scope':'Geometric contact and finite component void evidence; no strength, species, actor or host acceptance','passed':all(r['passed']for r in source_parts+contacts+joins+voids+materials)and not isolated}
(ROOT/'qa/source_reload_checks.json').write_text(json.dumps(result,indent=2)+'\n');print('SOURCE_PASS',result['passed']);print('ISSUES',[(r.get('name'),r)for r in contacts+joins+voids if not r['passed']],isolated)
assert result['passed']
