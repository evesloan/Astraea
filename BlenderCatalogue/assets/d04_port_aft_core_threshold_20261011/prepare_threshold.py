from pathlib import Path
import json,hashlib,subprocess,shutil
W=Path(__file__).resolve().parent;R=W.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
scope=json.load(open(W/'PINNED_SCOPE_INPUT.json'));assert all(sha(R/f)==h for f,h in scope['source_pins'].items());pre=json.load(open(W/'INTERFACE_PREFLIGHT.json'))
for x in [-8.3,-7.5]:
 for row in pre['rows']:
  if row['x']==x:assert abs(row['floor']['point'][1]-16.5)<.002 and abs(row['underside']['point'][1]-16.26)<.002
pa=json.load(open(R/'BlenderCatalogue/assets/d04_port_aft_neighborhood_20261011/PLAN.json'));guards=[q for v in pa['assemblies'].values()for q in v if q['name'].startswith('PA_NorthClosedCoreEndGuard')];assert len(guards)==3
parts=[]
def box(name,lo,hi,role,category,group='collar'):
 x0,y0,z0=lo;x1,y1,z1=hi;parts.append({'name':name,'verts':[[x,y,z]for y in [y0,y1]for x,z in [(x0,z0),(x1,z0),(x1,z1),(x0,z1)]],'faces':[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],'role':role,'category':category,'runtime_collision':True,'group':group})
box('D04PA_CollarFloor',[-8,16.26,286.6],[-7.8,16.5,290.8],'warm_stone','floor')
# Beams bear below both original slabs; no duplicated public floor top.
for i,z in enumerate([287.03,290.37]):
 box(f'D04PA_CollarBearingBeam_{i}',[-8.36,16.06,z-.10],[-7.45,16.26,z+.10],'champagne_metal','frame')
for i,(z0,z1) in enumerate([(286.96,287.1),(290.3,290.44)]):
 box(f'D04PA_ThresholdJamb_{i}',[-8.16,16.5,z0],[-7.5,19.7,z1],'ivory_enamel','frame','core')
 box(f'D04PA_JambFoot_{i}',[-8.2,16.5,z0-.04 if i==0 else z0],[-7.45,16.66,z1 if i==0 else z1+.04],'warm_walnut','frame','core')
 box(f'D04PA_RevealMetal_{i}',[-8.17,16.66,z0],[-8.11,19.7,z1],'champagne_metal','frame','core')
box('D04PA_ThresholdHeader',[-8.16,19.7,286.96],[-7.5,19.98,290.44],'warm_walnut','frame','core')
box('D04PA_HeaderMetalCap',[-8.18,19.98,286.94],[-7.48,20.04,290.46],'champagne_metal','frame','core')
box('D04PA_CollarRoof',[-8,20.48,286.6],[-7.72,20.7,290.8],'ivory_enamel','roof')
# Guard only the two closed returns; aperture remains3.2m wide.
for original in guards:
 v=original['verts'];lo=[min(a[i]for a in v)for i in range(3)];hi=[max(a[i]for a in v)for i in range(3)]
 for suffix,z0,z1 in [('ForeReturn',286.6,286.96),('AftReturn',290.44,290.8)]:box(original['name']+'_'+suffix,[lo[0],lo[1],z0],[hi[0],hi[1],z1],original['role'],'guard')
for i,z in enumerate([286.6,290.8]):
 box(f'D04PA_CollarSideGuard_{i}',[-8,16.62,z-.035],[-7.8,17.62,z+.035],'hospitality_glass','guard')
 box(f'D04PA_CollarSideGuardBase_{i}',[-8,16.5,z-.04],[-7.8,16.64,z+.04],'champagne_metal','guard')
 box(f'D04PA_CollarSideGuardCap_{i}',[-8,17.6,z-.04],[-7.8,17.68,z+.04],'champagne_metal','guard')
box('D04PA_ThresholdLampHousing',[-8.35,19.98,288.25],[-8.03,20.35,289.15],'warm_walnut','fitting')
box('D04PA_ThresholdLampLens',[-8.33,19.95,288.29],[-8.05,19.98,289.11],'opal_glow','light_fixture')
pins=dict(scope['source_pins']);pins.update({f:sha(R/f)for f in ['Game/scripts/ship.gd','BlenderCatalogue/catalogue_manifest.json','Game/assets/models/D04_PORT_AFT_COMBINEDSTRUCTURE_r002.glb','Game/data/architecture/D04_PORT_AFT_NEIGHBORHOOD.json','Game/scripts/primary_atrium_core.gd']})
P={'schema':'astraea.d04.port_aft_core_threshold.v1','base_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'active':False,'core_root':'AftMidshipPublicCore_WIP','original_core_file':'AST-CIR-005_spine_core.glb','core_origin':[0,0,272],'core_derivative_file':'AST-CIR-005_aft_midship_d04_port_threshold_r001.glb','collar_file':'D04_PORT_AFT_CORE_COLLAR_r001.glb','source_pins':pins,'exact_removed_source_meshes':['CORE_OuterWall_03_-1','CORE_WallDado_03_-1'],'original_runtime_guards':guards,'parts':parts,'clear_aperture_world':{'x':[-8.16,-7.5],'z':[287.1,290.3],'y':[16.5,19.7]},'new_floor_m2':.84,'existing_public_floor_top_duplicated_m2':0,'beam_support_note':'Two short collar beams join exact retained PANR_D04SF_ArrivalCross_8.5 east faceX-8.36 overY16.06..16.26 and bear beneath unchanged PA/core slabs. This is geometric connection, not engineering/load certification.','beam_bearings':[[[-8.3,16.26,287.03],[-7.5,16.26,287.03]],[[-8.3,16.26,290.37],[-7.5,16.26,290.37]]],'lights':[{'name':'D04PA_ThresholdLampLens','at':[-8.19,19.93,288.7]}],'new_units':0,'new_rests':0,'phase_evidence':{},'limits':['Dedicated lower staff-network links/crossings and central service verticals remain physical construction backlog.','Source bearing and supported aperture geometry do not certify loads or engineering.','No cart/tool/gameplay/loaded vertical operation changes or acceptance.','Partial native source visuals are separate from ordinary game/CRT/hardware/final acceptance.','Two historical unpublished r004 native byte versions remain unavailable.']}
for f in ['PLAN.json','NATIVE_AUTHORING_INPUT_PLAN.json']: (W/f).write_text(json.dumps(P,indent=2)+'\n')
shutil.copy2('/tmp/port_aft_core_interface001.log',W/'interface001.log');shutil.copy2('/tmp/port_aft_core_native_audit002.log',W/'native_audit002.log');print('Threshold input prepared; gap floor0.84m2; two slab-bearing beams')
