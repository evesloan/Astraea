from pathlib import Path
import json,copy,hashlib,struct
R=Path('/workspace/astraea-recovered-532087b9-20261010T083844Z');W=R/'BlenderCatalogue/assets/d04_port_central_west_staff_circuit_20261011';P=json.load(open(W/'PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();hold=W/'candidate_r001_narrow_swing_hold';hold.mkdir();
for name in ['PLAN.json','RUNTIME_PLAN.json','NATIVE_EXPORT_CHECK.json','EXACT_NATIVE_SOURCE_AUDIT.json','SOURCE_VIEW_RUN001.json','SITE_PREFLIGHT.json']:(hold/name).write_bytes((W/name).read_bytes())
(hold/'geometry.json').write_bytes((R/'Game/artifacts/d04_port_central_west_staff_circuit_geometry.json').read_bytes());(hold/'geometry001.log').write_bytes((W/'geometry001.log').read_bytes())
P['retained_candidate_r001']={str(f.relative_to(R)):sha(f)for f in [W/'D04PortCentralWestStaffPatch_r001.blend',W/'D04PortCentralWestStaffCircuit_r001.blend',W/'D04_PORT_CENTRAL_WEST_STAFF_PATCH_r001.glb',W/'D04_PORT_CENTRAL_WEST_STAFF_CIRCUIT_r001.glb',R/'Game/assets/models/D04_PORT_CENTRAL_WEST_STAFF_PATCH_r001.glb',R/'Game/assets/models/D04_PORT_CENTRAL_WEST_STAFF_CIRCUIT_r001.glb']};P['source_protected_native_exports'].update(P['retained_candidate_r001']);assert len(P['source_protected_native_exports'])==4327
P['patch_file']='D04_PORT_CENTRAL_WEST_STAFF_PATCH_r002.glb';P['structure_file']='D04_PORT_CENTRAL_WEST_STAFF_CIRCUIT_r002.glb'
for key in ['patch','structure','native_export_records','model_pins']:P.pop(key,None)
faces=[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
def box(name,lo,hi,role='ivory_enamel',cat='frame'):
 x,y,z=lo;X,Y,Z=hi;P['parts'].append({'name':name,'verts':[[a,b,c]for b in[y,Y]for a,c in[(x,z),(X,z),(X,Z),(x,Z)]],'faces':faces,'role':role,'category':cat,'runtime_collision':True})
# Remove r001 derived piers for a fresh complete support plan; originals remain immutable.
P['parts']=[q for q in P['parts']if not q['name'].startswith(('PCW_Foot','PCW_Column','PCW_BearingCap'))]
P['parts']=[q for q in P['parts']if q['name']not in ['PCW_CollarWall1S','PCW_EastEnclosureEnd']]
z=P['gates'][1]['z'];box('PCW_RecessWall1S',(-103,16.5,z-.8),(-100.8,19.7,z-.7),'ivory_enamel','wall');box('PCW_CollarWall1S',(-100.8,16.5,z-.7),(-99.7,19.7,z-.6),'ivory_enamel','wall');box('PCW_RecessReturn1',(-100.85,16.5,z-.8),(-100.75,19.7,z-.6),'ivory_enamel','wall');box('PCW_RecessFloor1',(-103,16.26,z-.8),(-100.8,16.5,z-.7),'warm_stone','floor');box('PCW_RecessRoof1',(-103,19.7,z-.8),(-100.8,20.46,z-.7),'ivory_enamel','roof')
box('PCW_EastEnclosureEndA',(-103.06,16.5,58.3),(-102.94,19.7,77.2),'ivory_enamel','wall');box('PCW_EastEnclosureEndB',(-103.06,16.5,78.8),(-102.94,19.7,79),'ivory_enamel','wall')
# Southern cross-route lies beyond both unchanged75.2m court ends and75.4m public street end.
box('PCW_SouthCrossFloor',(-103,16.26,77.2),(-64.2,16.5,78.8),'warm_stone','floor');box('PCW_SouthCrossRoof',(-103,19.7,77.2),(-64.2,19.82,78.8),'ivory_enamel','roof')
for z in [77.2,78.8]:box('PCW_SouthCrossWall'+str(z),(-103,16.5,z-.06),(-64.2,19.7,z+.06),'ivory_enamel','wall')
box('PCW_SouthEastFloor',(-64.2,16.26,56.6),(-62.2,16.5,78.8),'warm_stone','floor');box('PCW_SouthEastRoof',(-64.2,19.7,56.6),(-62.2,19.82,78.8),'ivory_enamel','roof')
# Eastern long edge never intersects a public spur; north terminus remains closed atZ42.2 after lower extension.
P['parts']=[q for q in P['parts']if q['name']not in['PCW_SouthEastFloor','PCW_SouthEastRoof']]
box('PCW_SouthEastFloor',(-64.2,16.26,42.2),(-62.2,16.5,78.8),'warm_stone','floor');box('PCW_SouthEastRoof',(-64.2,19.7,42.2),(-62.2,19.82,78.8),'ivory_enamel','roof');box('PCW_SouthEastOuterWall',(-62.26,16.5,42.2),(-62.14,19.7,78.8),'ivory_enamel','wall');box('PCW_SouthEastNorthEnd',(-64.2,16.5,42.14),(-62.2,19.7,42.26),'ivory_enamel','wall');box('PCW_SouthEastSouthEnd',(-64.2,16.5,78.74),(-62.2,19.7,78.86),'ivory_enamel','wall')
pc=json.load(open(R/'BlenderCatalogue/assets/d04_port_central_neighborhood_20261011/PLAN.json'));by={q['name']:q for q in pc['assemblies']['CombinedStructure']};orig=json.load(open(R/'BlenderCatalogue/assets/d04_staff_court_physical_connections_20261011/PLAN.json'));gate=next(q for q in orig['gates']if q['name']=='D04PC_CourtSouth');gp={q['name']:q for q in orig['parts']};names=gate['members']+gate['control_members']
for i,(prefix,z)in enumerate([('PCK_D04HC4_east',43.2),('PCK_D04HC5_east',57.6)],5):
 g={'name':'PortCentralSouthEastCourtGate'+str(i-5),'id':'D04_port_central_southern_east_court_work_gate_'+str(i-5),'z':z,'wall_x':-66.2,'pivot':[-66.08,16.5,z-.574],'closed_center':[-66.08,17.85,z],'private_side_normal':[-1,0,0],'candidate_open_degrees':90,'requires_visit':True,'sweep_min':[-66.18,16.5,z-.7],'sweep_max':[-64.75,19.25,z+.72],'members':[],'control_members':[],'court_prefix':prefix,'court_stance':[-68.1,16.5,z]};P['gates'].append(g)
 for suffix in ['_PrivacyScreen','_GlassUpper']:
  q=by[prefix+suffix];P['cuts'].append({'source_root':'D04PortCentralHabitatNeighborhood','source_model':'D04_PORT_CENTRAL_COMBINEDSTRUCTURE_r002.glb','name':q['name'],'preimage':q,'boxes':[{'min':[-66.45,16.495,z-.7],'max':[-66.15,19.2,z+.7]}]})
 for n in names:
  q=copy.deepcopy(gp[n]);q['name']='PCW_G'+str(i)+'_'+n;q['verts']=[[g['pivot'][0]-(Z-gate['pivot'][2]),g['pivot'][1]+y-gate['pivot'][1],g['pivot'][2]+X-gate['pivot'][0]]for X,y,Z in q['verts']];P['copied_gate_parts'].append(q);g['members'if n in gate['members']else'control_members'].append(q['name'])
 g['control_at']=[g['pivot'][0]-(gate['control_at'][2]-gate['pivot'][2]),gate['control_at'][1],g['pivot'][2]+gate['control_at'][0]-gate['pivot'][0]]
 box('PCW_CollarFloor'+str(i),(-66.2,16.26,z-.7),(-64.2,16.5,z+.7),'warm_stone','floor')
 # Swing side widened0.1m only across own gap so the unscaled original profile/handle clear.
 box('PCW_CollarWall'+str(i)+'S',(-66.2,16.5,z-.8),(-64.2,19.7,z-.7),'ivory_enamel','wall');box('PCW_CollarWall'+str(i)+'N',(-66.2,16.5,z+.6),(-64.2,19.7,z+.7),'ivory_enamel','wall');box('PCW_CollarRecessFloor'+str(i),(-66.2,16.26,z-.8),(-64.2,16.5,z-.7),'warm_stone','floor')
 verts=[[X,Y+(.12 if upper else 0),Z]for upper in[False,True]for X,Y,Z in[(-66.2,20.46,z-.8),(-64.2,19.7,z-.8),(-64.2,19.7,z+.7),(-66.2,20.46,z+.7)]];P['parts'].append({'name':'PCW_CollarRoof'+str(i),'verts':verts,'faces':faces,'role':'ivory_enamel','category':'roof','runtime_collision':True});box('PCW_CourtHeader'+str(i),(-66.45,19.2,z-.7),(-66.15,19.45,z+.7),'champagne_metal','header')
for i,(a,b)in enumerate([(42.2,42.4),(43.9,56.8),(58.3,77.2)]):box('PCW_SouthEastInnerWall'+str(i),(-64.26,16.5,a),(-64.14,19.7,b),'ivory_enamel','wall')
for x in range(-100,-64,6):
 for z in [77.45,78.55]:P['support_sites'].append({'x':x,'z':z,'half':.18})
for z in [43.2,50,57.6,65,73,78]:
 for x in [-63.95,-62.45]:P['support_sites'].append({'x':x,'z':z,'half':.18})
for g in P['gates'][5:]:P['support_sites'].append({'x':-65.2,'z':g['z'],'half':.18})
for i,x in enumerate(range(-100,-65,8)):
 box('PCW_SouthLightHousing'+str(i),(x-.3,19.35,77.8),(x+.3,19.52,78.2),'champagne_metal','fixture');box('PCW_SouthLightLens'+str(i),(x-.25,19.33,77.85),(x+.25,19.35,78.15),'opal_glow','fixture');P['lights'].append({'name':'PCW_SouthLightLens'+str(i),'at':[x,19.3,78]})
for i,z in enumerate([44,52,60,68,76]):
 box('PCW_SELightHousing'+str(i),(-63.55,19.35,z-.2),(-62.85,19.52,z+.2),'champagne_metal','fixture');box('PCW_SELightLens'+str(i),(-63.5,19.33,z-.15),(-62.9,19.35,z+.15),'opal_glow','fixture');P['lights'].append({'name':'PCW_SELightLens'+str(i),'at':[-63.2,19.3,z]})
P['new_floor_m2']=430.22+.22+38.8*1.6+36.6*2+2*2*1.5;P['limits'][0]='Seven remaining private-court work thresholds in an enclosed western/southern perimeter staff circuit; commons physical staff links remain held by public circulation/vertical-allocation interface constraints.';P['public_branch_unchanged']='All original receiving floors/guards/roofs and public house streets unchanged. South bypassZ77.2..78.8 lies beyond75.4 public street end; eastern staff legZ42.2..78.8 stays beyond southern receiving spurZ30.3..33.7.'
(W/'CANDIDATE_PLAN_r002.json').write_text(json.dumps(P,indent=2)+'\n');(W/'extend_plan002.py').write_bytes(Path(__file__).read_bytes())
s=(W/'probe_site002.gd').read_text().replace('CANDIDATE_PLAN.json','CANDIDATE_PLAN_r002.json').replace('SITE_PREFLIGHT.json','SITE_PREFLIGHT_r002.json').replace('FRESH_IMPORT_FACES.json','FRESH_IMPORT_FACES_r002.json');s=s.replace('Vector3(-80,19.5,-100.6)','Vector3(-80,19.5,-100.6),Vector3(-80,19.5,78),Vector3(-63.2,19.5,50)');(W/'probe_site003.gd').write_text(s);print('Extended7courts',P['new_floor_m2'],'m2',len(P['support_sites']),'supports')
