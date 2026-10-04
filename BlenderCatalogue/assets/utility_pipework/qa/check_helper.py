"""Read-only geometric smoke checks for new shared arbitrary-axis helper."""
import bpy,importlib.util,json,math
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
def load(name):
 s=importlib.util.spec_from_file_location(name,CAT/'standards'/f'{name}.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
p=load('utility_ports');m=load('staff_materials').materials();records=[]
for axis in [(1,0,0),(-1,0,0),(0,1,0),(0,0,1),(1,2,3)]:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 point=Vector((.17,-.33,.51));normal=Vector(axis).normalized();row=p.add_flange('smoke',point,axis,m);tri=0;pts=[];closed=True
 for ob in row['objects']:
  ob.data.calc_loop_triangles();tri+=len(ob.data.loop_triangles);pts.extend(Vector(v.co)-point for v in ob.data.vertices)
  counts={}
  for f in ob.data.polygons:
   for k,a in enumerate(f.vertices):
    edge=tuple(sorted((a,f.vertices[(k+1)%len(f.vertices)])));counts[edge]=counts.get(edge,0)+1
  closed=closed and all(n==2 for n in counts.values())
 axial=[v.dot(normal)for v in pts];rad=[(v-normal*v.dot(normal)).length for v in pts]
 rec={'outward':axis,'face':list(point),'triangles_one_flange_neck_and_twelve_hardware_parts':tri,'axial_minmax_m':[min(axial),max(axial)],'radial_minmax_m':[min(rad),max(rad)],'every_individual_mesh_closed':closed,'passes':abs(min(axial)+.095)<2e-6 and abs(max(axial))<2e-6 and abs(min(rad)-.08)<2e-6 and abs(max(rad)-.16)<2e-6 and closed};records.append(rec)
bad=[]
for axis in [(0,0,0),(math.nan,1,0),(0,math.inf,1)]:
 try:p.basis(axis);bad.append(False)
 except ValueError:bad.append(True)
namespace={'__name__':'cost_comparison_helper'}
exec(compile((CAT/'standards/utility_ports.py').read_text().replace('RING_SEGMENTS=48','RING_SEGMENTS=96'),str(CAT/'standards/utility_ports.py'),'exec'),namespace)
comparison=namespace['add_flange']('comparison96',(0,0,0),(1,0,0),m);comparison_tri=0
for ob in comparison['objects']:
 ob.data.calc_loop_triangles();comparison_tri+=len(ob.data.loop_triangles)
report={'tessellation_cost_comparison':{'96_segment_same_dimensions_and_cleanup_triangles':comparison_tri,'48_segment_same_dimensions_and_cleanup_triangles':records[0]['triangles_one_flange_neck_and_twelve_hardware_parts'],'scope':'Single entire flange, hollow neck and twelve hardware parts; same Boolean tolerance and unchanged nominal interface'},'interface_revision':p.REVISION,'nominal_dimensions_unchanged':True,'ring_radial_segments':p.RING_SEGMENTS,'nominal_flange_radius_m':.16,'maximum_outer_flange_polygon_sagitta_m':.16*(1-math.cos(math.pi/p.RING_SEGMENTS)),'nominal_bore_radius_m':.08,'minimum_polygon_bore_inradius_m':.08*math.cos(math.pi/p.RING_SEGMENTS),'boolean_cleanup_tolerance_m':.000001,'cases':records,'invalid_axis_rejected':bad,'all_passed':all(r['passes']for r in records)and all(bad),'scope':'Geometric helper smoke checks; no operating rating, fluid solve or target engine'}
(BASE/'qa/helper_smoke.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
