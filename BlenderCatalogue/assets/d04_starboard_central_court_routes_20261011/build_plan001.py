from pathlib import Path
import json,copy,math
from shapely.geometry import box as rect,mapping
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'AUDIT_INPUT_PLAN.json'));S=json.load(open(W/'RETAINED_SITE_ATTEMPT002.json'));revised=json.load(open(W/'SITE_CHANGED_STANCES003.json'));S['meshes']=revised['meshes'];S['stances']=[q for q in S['stances']if 'gate'not in q]+revised['stances'];S['ledgers']=json.load(open(W/'SITE_LEDGER_FACING004.json'))['ledgers'];P['runtime_preimages']=S['meshes'];P['support_preimages']=[];P['ledger_preimages']=S['ledgers'];assert len(S['meshes'])==30
predicted=[]
for q in S['stances']:
 if not q['blockers']:continue
 assert q.get('gate')in ['StarboardCentralCourtGate2','StarboardCentralCourtGate6'],q
 for owner in q['blockers']:
  name=owner.split('/')[-2];row=next(row for row in P['moves']if row['name']==name);pre=next(row for row in S['meshes']if row['name']==name);at=q['at'];lo=[pre['bounds'][0][i]+row['delta'][i]for i in range(3)];hi=[pre['bounds'][1][i]+row['delta'][i]for i in range(3)];assert max(lo[0]-at[0],at[0]-hi[0])>.302
  predicted.append({'source_owner':owner,'gate':q['gate'],'rigid_delta':row['delta'],'post_translation_bounds':[lo,hi],'conservative_capsule_x_clearance_m':max(lo[0]-at[0],at[0]-hi[0])-.302,'actual_candidate_capsule_check_required':True})
P['source_planter_clearance_predictions']=predicted
assert all(len(q['corners'])==4 and all(not c.get('missing')and c['source_mesh']==q['site']['source_mesh']for c in q['corners'])for q in S['ledgers']);assert all(not q['blockers']for q in S['roof_rows'])
P['parts']=[];P['lights']=[];faces=[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
def box(name,lo,hi,role='staff_bluegrey_paint',cat='wall'):
 x,y,z=lo;X,Y,Z=hi;assert X>x and Y>y and Z>z;P['parts'].append({'name':name,'verts':[[a,b,c]for b in[y,Y]for a,c in[(x,z),(X,z),(X,Z),(x,Z)]],'faces':faces,'role':role,'category':cat,'runtime_collision':True})
def slab(poly,name,y,Y,role,cat):
 pts=list(poly.exterior.coords)[:-1];idx={tuple(v):j for j,v in enumerate(pts)};n=len(pts);fs=[]
 for t in constrained_delaunay_triangles(poly).geoms:
  ids=[idx[tuple(v)]for v in list(t.exterior.coords)[:-1]];fs.extend([list(reversed(ids)),[j+n for j in ids]])
 fs += [[j,(j+1)%n,(j+1)%n+n,j+n]for j in range(n)];P['parts'].append({'name':name,'verts':[[x,h,z]for h in[y,Y]for x,z in pts],'faces':fs,'role':role,'category':cat,'runtime_collision':True})
floor=unary_union([rect(*q['lo'],*q['hi'])for q in P['floor_rectangles']]);P['floor_geometry']=mapping(floor);P['new_floor_m2']=floor.area
for i,poly in enumerate(floor.geoms):
 slab(poly,'SCR_Floor'+str(i),16.26,16.5,'staff_rubber','floor');slab(poly,'SCR_Roof'+str(i),19.7,19.82,'staff_white_paint','roof')
 for j,(a,b)in enumerate(zip(poly.exterior.coords,list(poly.exterior.coords)[1:])):
  x,z=a;X,Z=b
  if abs(x-X)<1e-6 and any(abs(x-g['wall_x'])<.001 and min(z,Z)>=g['z']-.851 and max(z,Z)<=g['z']+.851 for g in P['gates'][:9]):continue
  if abs(x-X)<1e-6:box('SCR_Wall'+str(i)+'_'+str(j),(x-.06,16.5,min(z,Z)),(x+.06,19.7,max(z,Z)));continue
  spans=[(min(x,X),max(x,X))]
  if abs(abs(z)-75.4)<.001:
   spans=[(u,v)for lo,hi in spans for u,v in[(lo,min(hi,83.25)),(max(lo,84.75),hi)]if v-u>.0001]
  for k,(lo,hi)in enumerate(spans):box('SCR_Wall'+str(i)+'_'+str(j)+'_'+str(k),(lo,16.5,z-.06),(hi,19.7,z+.06))
source=json.load(open(R/'BlenderCatalogue/assets/d04_staff_court_physical_connections_20261011/PLAN.json'));sg=P['source_gate_template'];parts={q['name']:q for q in source['parts']};P['gate_source']={'native':P['source_gate_native'],'source_pivot':sg['pivot'],'members':sg['members'],'control_members':sg['control_members']}
for i,g in enumerate(P['gates']):
 a=math.radians(g['source_rotation_y_degrees']);c,s=math.cos(a),math.sin(a)
 def tr(v):
  dx=v[0]-sg['pivot'][0];dz=v[2]-sg['pivot'][2];return[g['pivot'][0]+c*dx+s*dz,g['pivot'][1]+v[1]-sg['pivot'][1],g['pivot'][2]-s*dx+c*dz]
 for name in sg['members']+sg['control_members']:
  q=copy.deepcopy(parts[name]);q['name']='SCR_G'+str(i)+'_'+name;q['verts']=[tr(v)for v in q['verts']]
  if name.endswith('_Control')and i>=9:q['verts']=[[v[k]+g['fixed_control_delta'][k]for k in range(3)]for v in q['verts']]
  P['copied_gate_parts'].append(q);g['members'if name in sg['members']else'control_members'].append(q['name'])
 g['control_at']=tr(sg['control_at'])
 if i>=9:
  g['control_at']=[g['control_at'][k]+g['fixed_control_delta'][k]for k in range(3)];z=g['pivot'][2];box('SCR_ReceivingHeader'+str(i),(83.25,19.2,z-.12),(84.75,19.7,z+.12),'champagne_metal','header')
 else:
  x=g['wall_x'];z=g['z'];box('SCR_CourtHeader'+str(i),(x-.1,19.2,z-.75),(x+.1,19.7,z+.75),'champagne_metal','header')
for i,q in enumerate(S['ledgers']):
 x=q['site']['x'];z=q['site']['z'];west=x<70;outer=62.02 if west else 106.18;box('SCR_Ledger'+str(i),(x-.08,16.27,z-.18),(x+.08,16.49,z+.18),'champagne_metal','frame');box('SCR_WingBeam'+str(i),(min(x,outer),16.30,z-.12),(max(x,outer),16.45,z+.12),'champagne_metal','frame')
# Cross-passages couple to original end-floor faces; no lower columns.
P['end_ledger_sites']=[]
source=json.load(open(R/'Game/data/architecture/D04_STARBOARD_CENTRAL_NEIGHBORHOOD.json'))
for sign in [-1,1]:
 for x,name,z in [(67.2,'SCK_D04HC5_east_Floor'if sign<0 else'SCK_D04HC3_east_Floor',75.2),(100.9,'SCK_D04HC5_west_Floor'if sign<0 else'SCK_D04HC3_west_Floor',75.2),(84,'SC_ReceivingFloor_0'if sign<0 else'SC_ReceivingFloor_1',75.4)]:
  P['end_ledger_sites'].append({'x':x,'z':sign*z,'source_mesh':name,'half_x':.16})
 for room in source['rooms']:
  if room['allocation']['source_envelope_index']not in ([980,992]if sign<0 else[986,998]):continue
  q=next(q for q in room['parts']if q['category']=='floor');a=room['allocation']['allocation_x'];P['end_ledger_sites'].append({'x':sum(a)/2,'z':sign*75.2,'source_mesh':q['name'],'half_x':.16})
 box('SCR_CrossRingBeam'+str(sign),(62.02,16.30,sign*76.6-.12),(106.18,16.45,sign*76.6+.12),'champagne_metal','frame')
for i,site in enumerate(P['end_ledger_sites']):
 x,z=site['x'],site['z'];outer=77.7 if z>0 else-77.7;box('SCR_EndLedger'+str(i),(x-.18,16.27,z-.08),(x+.18,16.49,z+.08),'champagne_metal','frame');box('SCR_EndWingBeam'+str(i),(x-.12,16.30,min(z,outer)),(x+.12,16.45,max(z,outer)),'champagne_metal','frame')
for i,(x,z)in enumerate([(x,s*z)for s in[-1,1]for x in[63.2,105]for z in[41,48,55,62,69,76]]+[(x,s*76.6)for s in[-1,1]for x in[70,77,84,91,98]]):
 box('SCR_LampHousing'+str(i),(x-.3,19.37,z-.22),(x+.3,19.52,z+.22),'champagne_metal','fixture');box('SCR_LampLens'+str(i),(x-.26,19.35,z-.18),(x+.26,19.37,z+.18),'opal_glow','fixture');P['lights'].append({'name':'SCR_LampLens'+str(i),'at':[x,19.33,z]})
P['patch_file']='D04_STARBOARD_CENTRAL_COURT_PATCH_r001.glb';P['structure_file']='D04_STARBOARD_CENTRAL_COURT_ROUTES_r001.glb';P['closed_staging_translation']=[0,0,0]
for f in[W/'PLAN.json',W/'NATIVE_AUTHORING_INPUT_PLAN.json']:f.write_text(json.dumps(P,indent=2)+'\n')
print(json.dumps({'floor_m2':floor.area,'parts':len(P['parts']),'fitting_members':len(P['copied_gate_parts'])}))
