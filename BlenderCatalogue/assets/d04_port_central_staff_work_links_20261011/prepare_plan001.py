from pathlib import Path
import json,copy,hashlib,shutil
R=Path('/workspace/astraea-recovered-532087b9-20261010T083844Z');W=R/'BlenderCatalogue/assets/d04_port_central_staff_work_links_20261011';P=json.load(open(W/'AUDIT_INPUT_PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();src=json.load(open(R/'BlenderCatalogue/assets/d04_staff_court_physical_connections_20261011/PLAN.json'));gate=next(q for q in src['gates']if q['name']=='D04PC_CourtSouth');names=gate['members']+gate['control_members'];parts={q['name']:q for q in src['parts']};P['gate_source']={'native':'BlenderCatalogue/assets/d04_staff_court_physical_connections_20261011/D04PhysicalFittings_r009.blend','source_pivot':gate['pivot'],'members':gate['members'],'control_members':gate['control_members']};P['source_pins'][P['gate_source']['native']]=sha(R/P['gate_source']['native']);P['source_pins']['Game/assets/models/D04_PHYSICAL_FITTINGS_r009.glb']=sha(R/'Game/assets/models/D04_PHYSICAL_FITTINGS_r009.glb');P['copied_gate_parts']=[]
faces=[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
def box(name,lo,hi,role='ivory_enamel',cat='frame'):
 x,y,z=lo;X,Y,Z=hi;P['parts'].append({'name':name,'verts':[[a,b,c]for b in[y,Y]for a,c in[(x,z),(X,z),(X,Z),(x,Z)]],'faces':faces,'role':role,'category':cat,'runtime_collision':True})
P['lights']=[]
for i,g in enumerate(P['gates']):
 z=g['z'];g['pivot']=[-65.28,16.5,z-.574]
 for n in names:
  q=copy.deepcopy(parts[n]);q['name']='PCW_G'+str(i)+'_'+n;new=[]
  for x,y,Z in q['verts']:
   dx,dy,dz=x-gate['pivot'][0],y-gate['pivot'][1],Z-gate['pivot'][2];new.append([g['pivot'][0]-dz,g['pivot'][1]+dy,g['pivot'][2]+dx])
  q['verts']=new;P['copied_gate_parts'].append(q);g['members'if n in gate['members']else'control_members'].append(q['name'])
 g['control_at']=[g['pivot'][0]-(gate['control_at'][2]-gate['pivot'][2]),gate['control_at'][1],g['pivot'][2]+gate['control_at'][0]-gate['pivot'][0]]
 box('PCW_GapFloor'+str(i),(-65.4,16.26,z-.7),(-64.6,16.5,z+.7),'warm_stone','floor')
 for side,dZ in [('South',-.65),('North',.65)]:
  box('PCW_BearingBeam'+str(i)+side,(-65.8,16.02,z+dZ-.05),(-64.2,16.26,z+dZ+.05),'champagne_metal','frame')
  box('PCW_Jamb'+str(i)+side,(-65.4,16.5,z+dZ-.05),(-64.6,19.7,z+dZ+.05),'ivory_enamel','wall')
 # Stepped ceiling bridge: original court roof stays at20.46, staff at19.7.
 verts=[[x,y+(0.12 if upper else 0),Z]for upper in[False,True]for x,y,Z in[(-65.4,20.46,z-.7),(-64.6,19.7,z-.7),(-64.6,19.7,z+.7),(-65.4,20.46,z+.7)]];P['parts'].append({'name':'PCW_SlopingCanopy'+str(i),'verts':verts,'faces':faces,'role':'ivory_enamel','category':'roof','runtime_collision':True})
 for x,X in [(-65.5,-65.3),(-64.7,-64.5)]:
  box('PCW_CollarHeader'+str(i)+str(x),(x,19.2,z-.7),(X,19.42,z+.7),'champagne_metal','header')
 box('PCW_FixtureHousing'+str(i),(-65.2,19.23,z-.15),(-64.8,19.43,z+.15),'champagne_metal','fixture');box('PCW_FixtureLens'+str(i),(-65.16,19.215,z-.1),(-64.84,19.235,z+.1),'opal_glow','fixture');P['lights'].append({'at':[-65,19.2,z],'name':'PCW_FixtureLens'+str(i)})
site=json.load(open(W/'SITE_PREFLIGHT.json'));assert all(q['hit'] for q in site['bearings']),site['bearings'];assert all(not q['hit']for q in site['floors']if q['at'][0]in[-65.2,-64.8]);P['runtime_preimages']=site['meshes'];P['bearing_preimages']=site['bearings'];P['patch_file']='D04_PORT_CENTRAL_COURT_WORK_PATCH_r001.glb';P['structure_file']='D04_PORT_CENTRAL_COURT_WORK_LINKS_r001.glb';P['phase_evidence']={'authored':[],'connected':[]};P['public_branch_unchanged']='Northern receiving floorX-81.95..-51,Z-33.7..-30.3, associated guard/roof and public street unchanged; all new works Z<=-42.5.';P['unchanged_commons_work_links_unbuilt']=True
for f in [W/'PLAN.json',W/'NATIVE_AUTHORING_INPUT_PLAN.json']:f.write_text(json.dumps(P,indent=2)+'\n')
shutil.copyfile('/tmp/prepare_port_central_court_preflight.py',W/'prepare_preflight001.py');shutil.copyfile('/tmp/prepare_port_central_court_plan.py',W/'prepare_plan001.py');print('Prepared gap links',P['new_floor_m2'],'m2',len(P['parts']),'fixed parts plus',len(P['copied_gate_parts']),'rigid source fittings')
