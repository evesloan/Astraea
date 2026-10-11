from pathlib import Path
import json,copy,hashlib,shutil
R=Path('/workspace/astraea-recovered-532087b9-20261010T083844Z');W=R/'BlenderCatalogue/assets/d04_port_central_west_staff_circuit_20261011';P=json.load(open(W/'AUDIT_INPUT_PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();src=json.load(open(R/'BlenderCatalogue/assets/d04_staff_court_physical_connections_20261011/PLAN.json'));gate=next(q for q in src['gates']if q['name']=='D04PC_CourtSouth');names=gate['members']+gate['control_members'];sourceparts={q['name']:q for q in src['parts']}
P['gate_source']={'native':'BlenderCatalogue/assets/d04_staff_court_physical_connections_20261011/D04PhysicalFittings_r009.blend','source_pivot':gate['pivot'],'members':gate['members'],'control_members':gate['control_members']};P['source_pins'][P['gate_source']['native']]=sha(R/P['gate_source']['native']);P['source_pins']['Game/assets/models/D04_PHYSICAL_FITTINGS_r009.glb']=sha(R/'Game/assets/models/D04_PHYSICAL_FITTINGS_r009.glb');P['copied_gate_parts']=[];P['lights']=[];P['support_sites']=[]
faces=[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
def box(name,lo,hi,role='ivory_enamel',cat='frame'):
 x,y,z=lo;X,Y,Z=hi;assert X>x and Y>y and Z>z;P['parts'].append({'name':name,'verts':[[a,b,c]for b in[y,Y]for a,c in[(x,z),(X,z),(X,Z),(x,Z)]],'faces':faces,'role':role,'category':cat,'runtime_collision':True})
for i,g in enumerate(P['gates']):
 z=g['z'];x=g['wall_x']
 for n in names:
  q=copy.deepcopy(sourceparts[n]);q['name']='PCW_G'+str(i)+'_'+n;q['verts']=[[g['pivot'][0]-(Z-gate['pivot'][2]),g['pivot'][1]+y-gate['pivot'][1],g['pivot'][2]+X-gate['pivot'][0]]for X,y,Z in q['verts']];P['copied_gate_parts'].append(q);g['members'if n in gate['members']else'control_members'].append(q['name'])
 g['control_at']=[g['pivot'][0]-(gate['control_at'][2]-gate['pivot'][2]),gate['control_at'][1],g['pivot'][2]+gate['control_at'][0]-gate['pivot'][0]]
 box('PCW_CollarFloor'+str(i),(-103,16.26,z-.7),(x,16.5,z+.7),'warm_stone','floor')
 for side,dz in [('S',-.65),('N',.65)]:box('PCW_CollarWall'+str(i)+side,(-103,16.5,z+dz-.05),(x,19.7,z+dz+.05),'ivory_enamel','wall')
 verts=[[X,Y+(.12 if upper else 0),Z]for upper in[False,True]for X,Y,Z in[(-103,19.7,z-.7),(x,20.46,z-.7),(x,20.46,z+.7),(-103,19.7,z+.7)]];P['parts'].append({'name':'PCW_CollarRoof'+str(i),'verts':verts,'faces':faces,'role':'ivory_enamel','category':'roof','runtime_collision':True})
 box('PCW_CourtHeader'+str(i),(x-.04,19.2,z-.7),(x+.22,19.45,z+.7),'champagne_metal','header')
 # Narrow-court gate sits back in its own collar; it never sweeps into the home wall or long artery.
 if i==1:box('PCW_SetbackHeader'+str(i),(-101.24,19.2,z-.7),(-101.16,19.7,z+.7),'champagne_metal','header')
box('PCW_PerimeterFloor',(-105,16.26,-101.4),(-103,16.5,79),'warm_stone','floor');box('PCW_CrossFloor',(-103,16.26,-101.4),(-64.6,16.5,-99.8),'warm_stone','floor')
box('PCW_PerimeterRoof',(-105,19.7,-101.4),(-103,19.82,79),'ivory_enamel','roof');box('PCW_CrossRoof',(-103,19.7,-101.4),(-64.6,19.82,-99.8),'ivory_enamel','roof')
box('PCW_WestEnclosure',(-105.06,16.5,-101.4),(-104.94,19.7,79),'ivory_enamel','wall')
segments=[(-101.4,-99.8)]+[(g['z']-.7,g['z']+.7)for g in P['gates']];segments.sort();last=-101.4
for i,(a,b)in enumerate(segments):
 if a>last:box('PCW_EastEnclosure'+str(i),(-103.06,16.5,last),(-102.94,19.7,a),'ivory_enamel','wall')
 last=max(last,b)
if last<79:box('PCW_EastEnclosureEnd',(-103.06,16.5,last),(-102.94,19.7,79),'ivory_enamel','wall')
box('PCW_NorthEnd',(-105,16.5,-101.46),(-103,19.7,-101.34),'ivory_enamel','wall');box('PCW_SouthEnd',(-105,16.5,78.94),(-103,19.7,79.06),'ivory_enamel','wall')
for z in [-101.4,-99.8]:box('PCW_CrossWall'+str(z),(-103,16.5,z-.06),(-64.6,19.7,z+.06),'ivory_enamel','wall')
box('PCW_ExistingHeader',(-64.72,19.2,-101.3),(-64.48,19.7,-99.9),'champagne_metal','header')
# Supports are pin-query candidates; author only after exact four-corner source contact and empty column-volume evidence.
for z in [-100.6]+list(range(-94,79,8)):
 for x in [-104.75,-103.25]:P['support_sites'].append({'x':x,'z':z,'half':.18})
for x in range(-100,-64,6):
 for z in [-101.15,-100.05]:P['support_sites'].append({'x':x,'z':z,'half':.18})
for i,g in enumerate(P['gates']):
 P['support_sites'].append({'x':(-103+g['wall_x'])/2,'z':g['z'],'half':.18})
for i,z in enumerate(range(-96,79,8)):
 box('PCW_LightHousing'+str(i),(-104.35,19.35,z-.2),(-103.65,19.52,z+.2),'champagne_metal','fixture');box('PCW_LightLens'+str(i),(-104.3,19.33,z-.15),(-103.7,19.35,z+.15),'opal_glow','fixture');P['lights'].append({'name':'PCW_LightLens'+str(i),'at':[-104,19.3,z]})
for i,x in enumerate(range(-100,-65,8)):
 box('PCW_CrossLightHousing'+str(i),(x-.3,19.35,-100.8),(x+.3,19.52,-100.4),'champagne_metal','fixture');box('PCW_CrossLightLens'+str(i),(x-.25,19.33,-100.75),(x+.25,19.35,-100.45),'opal_glow','fixture');P['lights'].append({'name':'PCW_CrossLightLens'+str(i),'at':[x,19.3,-100.6]})
P['new_floor_m2']=430.22;P['patch_file']='D04_PORT_CENTRAL_WEST_STAFF_PATCH_r001.glb';P['structure_file']='D04_PORT_CENTRAL_WEST_STAFF_CIRCUIT_r001.glb';P['phase_evidence']={'authored':[],'connected':[]};P['public_branch_unchanged']='All public receiving floors/guards/roofs and house streets unchanged; new circuit westX<=-99.7, north connectorZ<-99.8.'
(W/'CANDIDATE_PLAN.json').write_text(json.dumps(P,indent=2)+'\n');(W/'prepare_plan001.py').write_bytes(Path(__file__).read_bytes());print('Candidate5courts',P['new_floor_m2'],'m2',len(P['parts']),'fixed parts',len(P['support_sites']),'support columns')
