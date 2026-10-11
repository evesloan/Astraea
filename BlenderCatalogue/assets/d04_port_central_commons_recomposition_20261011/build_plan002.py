from pathlib import Path
import json,copy,math
R=Path('/workspace/astraea-recovered-532087b9-20261010T083844Z');W=R/'BlenderCatalogue/assets/d04_port_central_commons_recomposition_20261011';P=json.load(open(W/'AUDIT_INPUT_PLAN_r002.json'));P['runtime_preimages']=json.load(open(W/'SITE_PREFLIGHT001.json'))['meshes'];assert len(P['runtime_preimages'])==len(P['cuts'])+len(P['moves']);P['parts']=[];F=[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
def box(name,lo,hi,role='staff_bluegrey_paint',category='wall'):
 x,y,z=lo;X,Y,Z=hi;assert X>x and Y>y and Z>z;P['parts'].append({'name':name,'verts':[[a,b,c]for b in [y,Y]for a,c in[(x,z),(X,z),(X,Z),(x,Z)]],'faces':F,'role':role,'category':category,'runtime_collision':True})
box('PCR_BridgeFloor',[-103,16.26,-1],[-96,16.5,1],'staff_rubber','floor');box('PCR_BridgeRoof',[-103,19.7,-1],[-96,19.82,1],'staff_white_paint','roof')
for z in [-1,1]:box('PCR_BridgeWall'+str(z),[-103,16.5,z-.06],[-96,19.7,z+.06])
# All new structure above the retained Training/D03 occupied volume.
for z in [-.8,.8]:box('PCR_BridgeEdgeBeam'+str(z),[-103.02,16.30,z-.1],[-95.98,16.45,z+.1],'champagne_metal','frame')
for x in [-103,-96]:
 for z in [-.8,.8]:box('PCR_SourceFloorLedger'+str(x)+'_'+str(z),[x-.025,16.27,z-.15],[x+.025,16.49,z+.15],'champagne_metal','frame')
box('PCR_RearQuietBoundary',[-93.15,16.5,2.6],[-92.99,19.7,8]);box('PCR_RearSouthEnd',[-96,16.5,-8.05],[-93,19.7,-7.89]);box('PCR_RearNorthEnd',[-96,16.5,7.89],[-92.99,19.7,8.05]);box('PCR_FrontGuestBoundary',[-93.15,16.5,2.6],[-83.79,19.7,2.76]);box('PCR_EastGuestBoundary',[-83.95,16.5,-.4],[-83.79,19.7,2.76])
# Seal the enlarged original stock opening around an unchanged full-size staff fitting.
box('PCR_StockFrontFillWest',[-88.5,16.5,-.56],[-88.2,19.35,-.4]);box('PCR_StockFrontFillEast',[-86.7,16.5,-.56],[-85.1,19.35,-.4]);box('PCR_StockNewHeader',[-88.2,19.2,-.56],[-86.7,19.35,-.4],'champagne_metal','header');box('PCR_ReturnNewHeader',[-90.7,19.2,-.56],[-89.2,19.35,-.4],'champagne_metal','header')
box('PCR_RearPortalHeader',[-96.16,19.2,-.8],[-95.98,19.7,.8],'champagne_metal','header')
source=json.load(open(R/'BlenderCatalogue/assets/d04_staff_court_physical_connections_20261011/PLAN.json'));sg=next(g for g in source['gates']if g['name']=='D04PC_CourtSouth');parts={q['name']:q for q in source['parts']}
for i,g in enumerate(P['gates']):
 yaw=math.radians(g['source_rotation_y_degrees']);cs=math.cos(yaw);sn=math.sin(yaw)
 def tr(v):
  x=v[0]-sg['pivot'][0];z=v[2]-sg['pivot'][2];return[g['pivot'][0]+cs*x+sn*z,g['pivot'][1]+v[1]-sg['pivot'][1],g['pivot'][2]-sn*x+cs*z]
 for name in sg['members']+sg['control_members']:
  q=copy.deepcopy(parts[name]);q['name']='PCR_G'+str(i)+'_'+name;q['verts']=[tr(v)for v in q['verts']];P['copied_gate_parts'].append(q);g['members'if name in sg['members']else'control_members'].append(q['name'])
 g['control_at']=tr(sg['control_at'])
for i,(x,z)in enumerate([(-100,0),(-94.5,4),(-94.5,-5),(-89.5,0)]):
 box('PCR_LightHousing'+str(i),[x-.3,19.37,z-.2],[x+.3,19.52,z+.2],'champagne_metal','fixture');box('PCR_LightLens'+str(i),[x-.26,19.35,z-.16],[x+.26,19.37,z+.16],'opal_glow','fixture');P['lights'].append({'name':'PCR_LightLens'+str(i),'at':[x,19.33,z]})
P['route_samples']=[[-104,16.5,0],[-102,16.5,0],[-100,16.5,0],[-98,16.5,0],[-93.8,16.5,0],[-94.5,16.5,4],[-94.5,16.5,-5],[-89.976,16.5,1.5],[-87.476,16.5,1.5],[-89.976,16.5,-2.1],[-87.476,16.5,-2.1]];P['low_service_canopy_lift_m']=.2;P['service_group_translation']=[-15,0,3];P['quiet_group_translation']=[4,0,0];P['moved_light_nodes']=[{'name':q['name']+'_Light','delta':q['delta']}for q in P['moves']if q['name'].startswith(('PCC_Lamp2_Lens','PCC_Lamp4_Lens','PCC_Lamp5_Lens'))];P['front_clip_boxes']={'PCC_ReturnFrontL':{'min':[-90.7,16.495,-.7],'max':[-89.2,19.2,-.2]},'PCC_ReturnFrontR':{'min':[-90.7,16.495,-.7],'max':[-89.2,19.2,-.2]},'PCC_ReturnHead':{'min':[-90.7,16.495,-.7],'max':[-89.2,19.2,-.2]},'PCC_StockHead':{'min':[-88.2,16.495,-.7],'max':[-86.7,19.2,-.2]}}
for f in [W/'PLAN.json',W/'NATIVE_AUTHORING_INPUT_PLAN.json']:f.write_text(json.dumps(P,indent=2)+'\n')
(W/'build_plan.py').write_bytes(Path(__file__).read_bytes());print('parts',len(P['parts']),'copies',len(P['copied_gate_parts']))
