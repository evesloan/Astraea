from pathlib import Path
import json,copy,math,hashlib
from shapely.geometry import box as rect,mapping
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
W=Path('/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/d04_starboard_forward_remaining_courts_20261011');R=W.parents[2];P=json.load(open(W/'AUDIT_INPUT_PLAN.json'));S=json.load(open(W/'SITE_PREFLIGHT001.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();P['runtime_preimages']=S['meshes'];P['support_preimages']=S['supports'];P['ledger_preimages']=S['ledgers'];assert len(S['meshes'])==22
assert all(not q.get('missing')and not q['blockers']for q in S['supports']);assert all(len(q['corners'])==4 and all(not c.get('missing')and c['source_mesh']==q['site']['source_mesh']and abs(c['point'][0]-25.4)<.0001 for c in q['corners'])for q in S['ledgers'])
source_approaches=[q for q in S['stances']if q['at']in P['source_approach_samples']];assert len(source_approaches)==12 and all(not q['blockers']and q.get('floor')and abs(q['floor']['y']-16.5)<.001 for q in source_approaches)
P['parts']=[];P['lights']=[];faces=[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
def box(name,lo,hi,role='staff_bluegrey_paint',cat='wall'):
 x,y,z=lo;X,Y,Z=hi;assert X>x and Y>y and Z>z;P['parts'].append({'name':name,'verts':[[a,b,c]for b in[y,Y]for a,c in[(x,z),(X,z),(X,Z),(x,Z)]],'faces':faces,'role':role,'category':cat,'runtime_collision':True})
def slab(poly,name,y,Y,role,category):
 pts=list(poly.exterior.coords)[:-1];idx={tuple(p):j for j,p in enumerate(pts)};n=len(pts);fs=[]
 for t in constrained_delaunay_triangles(poly).geoms:
  ids=[idx[tuple(p)]for p in list(t.exterior.coords)[:-1]];fs.extend([list(reversed(ids)),[j+n for j in ids]])
 fs += [[j,(j+1)%n,(j+1)%n+n,j+n]for j in range(n)];P['parts'].append({'name':name,'verts':[[x,h,z]for h in[y,Y]for x,z in pts],'faces':fs,'role':role,'category':category,'runtime_collision':True})
floor=unary_union([rect(q['lo'][0],q['lo'][1],q['hi'][0],q['hi'][1])for q in P['floor_rectangles']]);P['floor_geometry']=mapping(floor);P['new_floor_m2']=floor.area
for i,poly in enumerate(floor.geoms):
 slab(poly,'SFR_Floor'+str(i),16.26,16.5,'staff_rubber','floor')
 for j,(a,b)in enumerate(zip(poly.exterior.coords,list(poly.exterior.coords)[1:])):
  x,z=a;X,Z=b
  if abs(z-Z)<1e-6 and(abs(z+406.9)<1e-6 or abs(z+290.8)<1e-6):continue
  if abs(x-X)<1e-6 and any(abs(x-g['wall_x'])<.0001 and min(z,Z)>=g['z']-.851 and max(z,Z)<=g['z']+.851 for g in P['gates'][:5]):continue
  if abs(x-X)<1e-6 and(abs(x-64)<.001 or abs(x-59.7)<.001):continue
  collar=next((g for g in P['gates'][:5]if abs(z-Z)<1e-6 and abs(abs(z-g['z'])-.85)<.001 and min(x,X)>=24.399 and max(x,X)<=g['wall_x']+.001),None)
  if collar:
   low=min(x,X);high=max(x,X);vs=[[low,16.5,z-.06],[high,16.5,z-.06],[high,16.5,z+.06],[low,16.5,z+.06],[low,19.7,z-.06],[high,20.46,z-.06],[high,20.46,z+.06],[low,19.7,z+.06]];P['parts'].append({'name':'SFR_CollarWall'+str(i)+'_'+str(j),'verts':vs,'faces':faces,'role':'staff_bluegrey_paint','category':'wall','runtime_collision':True})
  elif abs(x-X)<1e-6:box('SFR_Wall'+str(i)+'_'+str(j),(x-.06,16.5,min(z,Z)),(x+.06,19.7,max(z,Z)))
  else:box('SFR_Wall'+str(i)+'_'+str(j),(min(x,X),16.5,z-.06),(max(x,X),19.7,z+.06))
for i,q in enumerate(P['floor_rectangles'][:3]):slab(rect(q['lo'][0],q['lo'][1],q['hi'][0],q['hi'][1]),'SFR_Roof'+str(i),19.7,19.82,'staff_white_paint','roof')
source=json.load(open(R/'BlenderCatalogue/assets/d04_staff_court_physical_connections_20261011/PLAN.json'));sg=P['source_gate_template'];parts={q['name']:q for q in source['parts']};P['gate_source']={'native':P['source_gate_native'],'source_pivot':sg['pivot'],'members':sg['members'],'control_members':sg['control_members']};P['copied_gate_parts']=[]
for i,g in enumerate(P['gates']):
 def tr(v):
  dx=v[0]-sg['pivot'][0];dz=v[2]-sg['pivot'][2];return[g['pivot'][0]+dz if i<5 else g['pivot'][0]+dx,g['pivot'][1]+v[1]-sg['pivot'][1],g['pivot'][2]-dx if i<5 else g['pivot'][2]+dz]
 for name in sg['members']+sg['control_members']:
  q=copy.deepcopy(parts[name]);q['name']='SFR_G'+str(i)+'_'+name;q['verts']=[tr(v)for v in q['verts']]
  if name.endswith('_Control')and i>=5:q['verts']=[[v[k]+g['fixed_control_delta'][k]for k in range(3)]for v in q['verts']]
  P['copied_gate_parts'].append(q);g['members'if name in sg['members']else'control_members'].append(q['name'])
 g['control_at']=tr(sg['control_at'])
 if i>=5:g['control_at']=[g['control_at'][k]+g['fixed_control_delta'][k]for k in range(3)]
 if i<5:
  x=g['wall_x'];z=g['z'];vs=[[X,Y+(.12 if upper else 0),Z]for upper in[False,True]for X,Y,Z in[(24.4,19.7,z-.85),(x,20.46,z-.85),(x,20.46,z+.85),(24.4,19.7,z+.85)]];P['parts'].append({'name':'SFR_CollarRoof'+str(i),'verts':vs,'faces':faces,'role':'staff_white_paint','category':'roof','runtime_collision':True});box('SFR_CourtHeader'+str(i),(x-.19,19.2,z-.75),(x-.01,19.45,z+.75),'champagne_metal','header')
 else:
  z=g['pivot'][2];box('SFR_StaffHeader'+str(i),(22.45,19.2,z-.12),(23.95,19.7,z+.12),'champagne_metal','header');box('SFR_StaffEndWest'+str(i),(22,16.5,z-.06),(22.45,19.7,z+.06));box('SFR_StaffEndEast'+str(i),(23.95,16.5,z-.06),(24.4,19.7,z+.06))
for i,q in enumerate(S['supports']):
 x,z,h=q['x'],q['z'],q['half'];base=[]
 for X,Z in[(x-h,z-h),(x+h,z-h),(x+h,z+h),(x-h,z+h)]:base.append([X,min(q['corners'],key=lambda c:(c['point'][0]-X)**2+(c['point'][2]-Z)**2)['point'][1],Z])
 P['parts'].append({'name':'SFR_Foot'+str(i),'verts':base+[[X,q['column_bottom'],Z]for X,Y,Z in base],'faces':faces,'role':'champagne_metal','category':'frame','runtime_collision':True});box('SFR_Column'+str(i),(x-h+.04,q['column_bottom'],z-h+.04),(x+h-.04,16.14,z+h-.04),'champagne_metal','frame');box('SFR_Cap'+str(i),(x-h-.06,16.14,z-h-.06),(x+h+.06,16.26,z+h+.06),'champagne_metal','frame')
for i,q in enumerate(S['ledgers']):
 s=q['site'];z=s['z'];box('SFR_SouthLedger'+str(i),(25.38,16.27,z-.18),(25.52,16.49,z+.18),'champagne_metal','frame');box('SFR_SouthWingBeam'+str(i),(22.02,16.30,z-.12),(25.5,16.45,z+.12),'champagne_metal','frame')
P['south_floor_ledger_joint_policy']='Only named unchanged source floor-edge faces atX25.4,Y16.29/16.46 provide lateral joint proof; new ledger/frame is entirely above protected D03top16.25. Floor load sizing/cantilever acceptance held.'
for i,(x,z)in enumerate([(23.2,z)for z in range(-442,-408,7)]+[(23.2,z)for z in range(-326,-292,7)]+[(61.8,-427.7)]):
 box('SFR_FixtureHousing'+str(i),(x-.3,19.37,z-.22),(x+.3,19.52,z+.22),'champagne_metal','fixture');box('SFR_FixtureLens'+str(i),(x-.26,19.35,z-.18),(x+.26,19.37,z+.18),'opal_glow','fixture');P['lights'].append({'name':'SFR_FixtureLens'+str(i),'at':[x,19.33,z]})
P['patch_file']='D04_STARBOARD_FORWARD_REMAINING_PATCH_r001.glb';P['structure_file']='D04_STARBOARD_FORWARD_REMAINING_COURTS_r001.glb';P['normal_private_staff_control_stances']={'x':23.2,'y':16.5};P['old_four_east_gates_unchanged']=True;P['closed_staging_translation']=[0,0,0]
for f in[W/'PLAN.json',W/'NATIVE_AUTHORING_INPUT_PLAN.json']:f.write_text(json.dumps(P,indent=2)+'\n')
(W/'build_plan001.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({'new_floor_m2':floor.area,'parts':len(P['parts']),'source_gates':len(P['copied_gate_parts']),'keel_supports':len(S['supports']),'named_floor_ledgers':len(S['ledgers'])}))
