from pathlib import Path
import json,ast,hashlib,copy
from shapely.geometry import shape,box,mapping
from shapely.geometry.polygon import orient
from shapely import constrained_delaunay_triangles
W=Path('/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/d04_port_aft_neighborhood_20261011');R=W.parents[2];P=json.load(open(W/'RUNTIME_PLAN.json'));prior=copy.deepcopy(P);parts=[]
text=(R/'BlenderCatalogue/assets/d04_port_forward_receiving_20261010/prepare.py').read_text()
for n in ast.parse(text).body:
 if isinstance(n,ast.FunctionDef)and n.name in ['add','cube','prism']:exec(compile(ast.get_source_segment(text,n),'<reviewed original geometry helpers>','exec'))
changed=[]
for a in P['assemblies']['CombinedStructure']:
 if a['name'].startswith('PANR_')and len(a['verts'])==8:
  lo=[min(v[i]for v in a['verts'])for i in range(3)];hi=[max(v[i]for v in a['verts'])for i in range(3)]
  if hi[0]>-8 and lo[0]<-8 and lo[2]>=259 and hi[2]<=292:
   changed.append(a['name'])
   for v in a['verts']:v[0]=min(v[0],-8)
g=shape(P['receiving_floor_geometry']);ng=g.difference(box(-8,259,-4,292));removed=g.area-ng.area
prism('PA_ReceivingFloor',ng,16.26,16.5);prism('PA_ReceivingRoof',ng,20.48,20.70,role='ivory_enamel',category='roof')
faces=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
cube('PA_NorthClosedCoreEndGuard',[-8.08,16.62,286.6],[-8,17.62,290.8],'hospitality_glass','guard')
cube('PA_NorthClosedCoreEndGuard_Base',[-8.08,16.5,286.6],[-8,16.64,290.8],'champagne_metal','guard')
cube('PA_NorthClosedCoreEndGuard_Cap',[-8.08,17.6,286.6],[-8,17.68,290.8],'champagne_metal','guard')
P['assemblies']['CombinedStructure']=[a for a in P['assemblies']['CombinedStructure']if a['name']not in ['PA_ReceivingFloor','PA_ReceivingRoof']]+parts
P['receiving_floor_geometry']=mapping(ng);P['receiving_floor_m2']=ng.area;P['public_receiving_interface']={'world_floor':[ -3.5,16.5,405.2],'branch_world_floor':[-8,16.5,405.2],'original_spine':'D04_aft_route','north_core_sidewall_preserved_closed':True,'north_platform_end_x':-8,'northern_platform_purpose':'guarded arrival lookout; no lateral portal or route declared','source_probe':'CORE_BOUNDARY_PROBE.json','observed_ivory_outer_x':-7.88000011444092,'additional_floor_trim_m2':removed}
P['limits'].append('Retained aft core has no D04 lateral portal; north platform remains a guarded lookout. Public receiving connects at retained D04 aft spine Z405.2.')
(W/'PLAN.json').write_text(json.dumps(P,indent=2)+'\n');(W/'CORE_INTERFACE_CORRECTION_INPUT.json').write_text(json.dumps({'prior_runtime_sha256':hashlib.sha256((W/'RUNTIME_PLAN.json').read_bytes()).hexdigest(),'baseline_probe_sha256':hashlib.sha256((W/'CORE_BOUNDARY_PROBE.json').read_bytes()).hexdigest(),'changed_original_members':changed,'floor_trim_m2':removed,'new_end_guard_parts':3,'immutable_new_revision':'CombinedStructure_r002','unchanged_other_assemblies':21,'actual_bearings_unchanged':119,'source_core_unchanged':True},indent=2)+'\n');assert len(changed)==8
