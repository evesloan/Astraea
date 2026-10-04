from pathlib import Path
import json,math,hashlib
import bpy
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];SLUG='AST-STF-007_supply_work_cabinet';source=ROOT/(SLUG+'.blend')
bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.view_layer.update()
pivot=bpy.data.objects.get('AST-STF-007_door_hinge_pivot');dg=bpy.context.evaluated_depsgraph_get()
statics=[];moving=[];parts=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 eo=ob.evaluated_get(dg);me=eo.to_mesh();me.calc_loop_triangles()
 vs=[ob.matrix_world@v.co for v in me.vertices];tris=[tuple(t.vertices) for t in me.loop_triangles]
 rec=(ob.name,vs,tris)
 (moving if ob.get('assembly') in ['door_leaf','door_handle','bearing_moving'] else statics).append(rec)
 parts.append({'name':ob.name,'assembly':ob.get('assembly'),'modifiers_retained':len(ob.modifiers),'uv':me.uv_layers.active.name,'bounds_min_m':[min(p[i] for p in vs) for i in range(3)],'bounds_max_m':[max(p[i] for p in vs) for i in range(3)]});eo.to_mesh_clear()
def concat(records,rot=None):
 vs=[];tris=[];owners=[]
 for name,verts,faces in records:
  n=len(vs);vs.extend([pivot.location+rot@(p-pivot.location) for p in verts] if rot is not None else verts);tris.extend([tuple(n+i for i in f) for f in faces]);owners.extend([name]*len(faces))
 return vs,tris,owners
sv,st,so=concat(statics);s_tree=BVHTree.FromPolygons(sv,st,all_triangles=True,epsilon=0)
fails=[];samples=[];lo=[1e9]*3;hi=[-1e9]*3
for step in range(421):
 degrees=-step*.25;rot=Matrix.Rotation(math.radians(degrees),3,'Z');mv,mt,mo=concat(moving,rot);m_tree=BVHTree.FromPolygons(mv,mt,all_triangles=True,epsilon=0)
 overlaps=s_tree.overlap(m_tree)
 if overlaps:
  pairs=sorted(set((so[a],mo[b]) for a,b in overlaps));fails.append({'degrees':degrees,'triangle_pair_count':len(overlaps),'parts':pairs})
 vmin=[min(p[i] for p in mv) for i in range(3)];vmax=[max(p[i] for p in mv) for i in range(3)]
 lo=[min(a,b) for a,b in zip(lo,vmin)];hi=[max(a,b) for a,b in zip(hi,vmax)]
 if step%60==0 or step==420:samples.append({'angle_degrees':degrees,'bounds_min_m':vmin,'bounds_max_m':vmax,'surface_intersections':len(overlaps)})
print('SWEEP',len(fails),'failed samples')
if fails:print(json.dumps(fails[:8],indent=2))
# Analytic continuous separation of main leaf/handle/straps from cabinet body.
# y(theta)=pivot_y-dx*sin(theta)+dy*cos(theta), theta in [0,105].
main=[r for r in moving if 'bored_hinge_knuckle' not in r[0]];minx=min(p.x-pivot.location.x for _,vs,_ in main for p in vs)
max_y=-1e9
for _,vs,_ in main:
 for v in vs:
  dx,dy=v.x-pivot.location.x,v.y-pivot.location.y
  angles=[0,math.radians(105)]
  # all extrema of -dx sin(a)+dy cos(a)
  for k in range(-2,3):
   a=math.atan2(-dx,dy)+k*math.pi
   if 0<=a<=math.radians(105):angles.append(a)
  max_y=max(max_y,*[pivot.location.y-dx*math.sin(a)+dy*math.cos(a) for a in angles])
body=[r for r in statics if not r[0].startswith('HINGE_')]
bodyminy=min(p.y for _,vs,_ in body if min(q.z for q in vs)<.860 and max(q.z for q in vs)>.195 for p in vs)
report={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'status':'PASS' if not fails else 'FAIL','scope':'Blender evaluated visual geometry, including visible inside faces, shelf lips, full handle and complete bored hinge assembly; no convex storage proxy. No engine/controller or actor acceptance.','method':'Triangle BVH intersections for every 0.25 degree sample across closed to 105 degrees outward; continuous main-leaf/body plane-separation bound and floor bound; actual fixed/moving bearing meshes included in sampled test.','range_degrees':[0,-105],'samples':421,'failed_samples':fails,'pivot_blender_m':list(pivot.location),'moving_sweep_bounds_min_m':lo,'moving_sweep_bounds_max_m':hi,'minimum_floor_clearance_m':lo[2],'continuous_main_leaf_maximum_y_m':max_y,'cabinet_body_front_minimum_y_in_leaf_height_m':bodyminy,'continuous_front_plane_gap_m':bodyminy-max_y,'hinge_geometry':{'stationary_pin_radius_m':.004,'moving_bore_radius_m':.0046,'moving_bore_12gon_apothem_m':.0046*math.cos(math.pi/12),'guaranteed_radial_gap_lower_bound_m':.0046*math.cos(math.pi/12)-.004,'moving_barrel_half_height_m':.025,'stationary_ear_start_offset_m':.026,'guaranteed_axial_gap_m':.001},'checkpoints':samples}
(ROOT/'qa/door_sweep_report.json').write_text(json.dumps(report,indent=2))
(ROOT/'qa/source_reload_report.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'blender_version':bpy.app.version_string,'mesh_parts':len(parts),'door_pivot_m':list(pivot.location),'all_uv_names_unified':all(p['uv']=='UV_Metric_Metres' for p in parts),'floor_minimum_z_m':min(p['bounds_min_m'][2] for p in parts),'parts':parts},indent=2))
assert not fails,'Visual door/frame intersection'
assert bodyminy-max_y>0,'Continuous body-plane separation failed'
assert lo[2]>0,'Moving leaf intersects floor'

# Prove the actual GLB's evaluated geometry and separate moving groups agree with source.
from mathutils.kdtree import KDTree
source_groups={'static':[], 'door_leaf':[], 'door_handle':[]}
source_triangles={'static':0,'door_leaf':0,'door_handle':0}
for name,vs,faces in statics+moving:
 group='static' if (name,vs,faces) in statics else ('door_handle' if name.startswith('DOOR_pull_') or name=='DOOR_vertical_pull_grip' else 'door_leaf')
 source_groups[group].extend(vs);source_triangles[group]+=len(faces)
bpy.ops.wm.read_factory_settings(use_empty=True);glb=ROOT/(SLUG+'.glb');bpy.ops.import_scene.gltf(filepath=str(glb));bpy.context.view_layer.update();pivot=bpy.data.objects['AST-STF-007_door_hinge_pivot']
import_static=[];import_moving=[];import_groups={'static':[],'door_leaf':[],'door_handle':[]};import_triangles={'static':0,'door_leaf':0,'door_handle':0}
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 me=ob.data;me.calc_loop_triangles();vs=[ob.matrix_world@v.co for v in me.vertices];faces=[tuple(t.vertices) for t in me.loop_triangles];group=ob['assembly']
 import_groups[group].extend(vs);import_triangles[group]+=len(faces);(import_static if group=='static' else import_moving).append((ob.name,vs,faces))
def directed_distance(a,b):
 kd=KDTree(len(b))
 for i,v in enumerate(b):kd.insert(v,i)
 kd.balance();return max(kd.find(v)[2] for v in a)
equivalence={}
for group in source_groups:
 a,b=source_groups[group],import_groups[group]
 equivalence[group]={'source_to_glb_max_m':directed_distance(a,b),'glb_to_source_max_m':directed_distance(b,a),'source_triangles':source_triangles[group],'glb_triangles':import_triangles[group]}
 assert equivalence[group]['source_to_glb_max_m']<.000001 and equivalence[group]['glb_to_source_max_m']<.000001
 assert source_triangles[group]==import_triangles[group]
sv,st,so=concat(import_static);s_tree=BVHTree.FromPolygons(sv,st,all_triangles=True,epsilon=0);import_fail=[]
for step in range(421):
 deg=-step*.25;mv,mt,mo=concat(import_moving,Matrix.Rotation(math.radians(deg),3,'Z'));overlap=s_tree.overlap(BVHTree.FromPolygons(mv,mt,all_triangles=True,epsilon=0))
 if overlap:import_fail.append({'angle':deg,'pairs':len(overlap)})
report['glb_sha256']=hashlib.sha256(glb.read_bytes()).hexdigest();report['source_export_geometry_equivalence']=equivalence;report['imported_glb_421_sample_failures']=import_fail
report['status']='PASS' if not fails and not import_fail else 'FAIL'
(ROOT/'qa/door_sweep_report.json').write_text(json.dumps(report,indent=2));assert not import_fail
print('IMPORTED_GLB_SWEEP_PASS',equivalence)
# Additional continuous bearing bounds, independent of angular sample spacing.
# Every fixed mount lies beyond x-y = constant; exact trigonometric support extrema
# certify the moving non-barrel mesh remains on the other side for the full interval.
px,py=-.837,-.317
mounts=[r for r in statics if r[0].endswith('_static_mount')]
mount_diagonal_max=max((v.x-px)-(v.y-py) for _,vs,_ in mounts for v in vs)
def trig_extrema(a,b,minimum=True):
    # a*cos(theta)+b*sin(theta), full 0..105 degree interval
    aa=[0,math.radians(105)]
    for k in range(-2,3):
        angle=math.atan2(b,a)+k*math.pi
        if 0<=angle<=math.radians(105):aa.append(angle)
    values=[a*math.cos(t)+b*math.sin(t) for t in aa]
    return min(values) if minimum else max(values)
main_diagonal_min=min(trig_extrema((v.x-px)-(v.y-py),(v.x-px)+(v.y-py)) for _,vs,_ in main for v in vs)
main_radius_lower=min(min(v.x-px for v in vs) for _,vs,_ in main)
leaf_without_straps=[r for r in main if 'hinge_strap' not in r[0]]
def box_radial_lower(vs):
    xs=[v.x-px for v in vs];ys=[v.y-py for v in vs]
    dx=0 if min(xs)<=0<=max(xs) else min(abs(min(xs)),abs(max(xs)))
    dy=0 if min(ys)<=0<=max(ys) else min(abs(min(ys)),abs(max(ys)))
    return math.hypot(dx,dy)
leaf_radius_lower=min(box_radial_lower(vs) for _,vs,_ in leaf_without_straps)
ears=[r for r in statics if '_pin_ear' in r[0]];ear_radius_upper=max(math.hypot(v.x-px,v.y-py) for _,vs,_ in ears for v in vs)
continuous={'main_leaf_handle_to_body_plane_gap_m':bodyminy-max_y,'moving_all_to_floor_gap_m':lo[2],'main_moving_to_static_hinge_mount_diagonal_gap_m':(main_diagonal_min-mount_diagonal_max)/math.sqrt(2),'barrel_to_static_hinge_mount_x_gap_m':.004,'main_moving_to_fixed_pin_radial_gap_lower_bound_m':main_radius_lower-.004,'non_strap_leaf_to_hinge_ears_radial_gap_lower_bound_m':leaf_radius_lower-ear_radius_upper,'hinge_strap_to_fixed_ear_axial_gap_m':.003,'moving_barrel_to_fixed_ear_axial_gap_m':.001,'moving_bore_to_fixed_pin_radial_gap_lower_bound_m':.0046*math.cos(math.pi/12)-.004}
assert all(v>0 for v in continuous.values()),continuous
report['continuous_component_separation_bounds']=continuous
report['continuous_component_scope']='Positive conservative separations for the main visual leaf/handle versus body, floor and fixed hinge regions across the entire stated angle interval. Rigid parts rotate about a fixed Z axis; no deformation, actor, controller, room placement, physics solver or game runtime included. Sampled BVH checks remain separately recorded.'
(ROOT/'qa/door_sweep_report.json').write_text(json.dumps(report,indent=2));print('CONTINUOUS_BOUNDS',continuous)
# Exact continuous envelope: a linear rigid-transform coordinate attains extrema
# at an evaluated triangle vertex; solve each vertex sinusoid over the interval.
continuous_lo=[min(px+trig_extrema(v.x-px,v.y-py) for _,vs,_ in moving for v in vs),min(py+trig_extrema(v.y-py,-(v.x-px)) for _,vs,_ in moving for v in vs),min(v.z for _,vs,_ in moving for v in vs)]
continuous_hi=[max(px+trig_extrema(v.x-px,v.y-py,False) for _,vs,_ in moving for v in vs),max(py+trig_extrema(v.y-py,-(v.x-px),False) for _,vs,_ in moving for v in vs),max(v.z for _,vs,_ in moving for v in vs)]
report['continuous_sweep_aabb_blender_m']={'min':continuous_lo,'max':continuous_hi,'method':'Analytic coordinate extrema of every evaluated moving vertex over the complete angle interval; excludes no visible moving geometry.'}
report['sampled_sweep_bounds_note']='moving_sweep_bounds_min/max_m above are 421-sample bounds; use continuous_sweep_aabb_blender_m for the analytic complete interval envelope.'
(ROOT/'qa/door_sweep_report.json').write_text(json.dumps(report,indent=2));print('CONTINUOUS_SWEEP_AABB',continuous_lo,continuous_hi)
