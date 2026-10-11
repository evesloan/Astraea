from pathlib import Path
import json,copy,math
from shapely.geometry import box as rect,mapping
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
W=Path('/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/d04_port_aft_court_routes_20261011');R=W.parents[2];P=json.load(open(W/'AUDIT_INPUT_PLAN.json'));S=json.load(open(W/'SITE_PREFLIGHT002.json'));P['runtime_preimages']=S['meshes'];P['support_preimages']=[];P['ledger_preimages']=S['ledgers'];assert len(S['meshes'])==35;assert all(not q['blockers']for q in S['roof_rows']);assert all(len(q['corners'])==4 and all(not c.get('missing')and c['source_mesh']==q['site']['source_mesh']for c in q['corners'])for q in S['ledgers'])
P['source_planter_clearance_predictions']=[]
for q in S['stances']:
 if not q['blockers']:continue
 assert q.get('gate')in ['PortAftCourtGate2','PortAftCourtGate6'],q
 for owner in q['blockers']:
  name=owner.split('/')[-2];row=next(row for row in P['moves']if row['name']==name);pre=next(row for row in S['meshes']if row['name']==name);at=q['at'];lo=[pre['bounds'][0][i]+row['delta'][i]for i in range(3)];hi=[pre['bounds'][1][i]+row['delta'][i]for i in range(3)];assert max(lo[0]-at[0],at[0]-hi[0])>.302;P['source_planter_clearance_predictions'].append({'source_owner':owner,'gate':q['gate'],'rigid_delta':row['delta'],'post_translation_bounds':[lo,hi]})
P['parts']=[];P['lights']=[];faces=[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
def box(name,lo,hi,role='staff_bluegrey_paint',cat='wall'):
 x,y,z=lo;X,Y,Z=hi;assert X>x and Y>y and Z>z;P['parts'].append({'name':name,'verts':[[a,b,c]for b in[y,Y]for a,c in[(x,z),(X,z),(X,Z),(x,Z)]],'faces':faces,'role':role,'category':cat,'runtime_collision':True})
def slab(poly,name,y,Y,role,cat):
 pts=list(poly.exterior.coords)[:-1];idx={tuple(v):j for j,v in enumerate(pts)};n=len(pts);fs=[]
 for t in constrained_delaunay_triangles(poly).geoms:
  ids=[idx[tuple(v)]for v in list(t.exterior.coords)[:-1]];fs.extend([list(reversed(ids)),[j+n for j in ids]])
 fs += [[j,(j+1)%n,(j+1)%n+n,j+n]for j in range(n)];P['parts'].append({'name':name,'verts':[[x,h,z]for h in[y,Y]for x,z in pts],'faces':fs,'role':role,'category':cat,'runtime_collision':True})
floor=unary_union([rect(*q['lo'],*q['hi'])for q in P['floor_rectangles']]);P['floor_geometry']=mapping(floor);P['new_floor_m2']=floor.area;polys=list(floor.geoms);P['wall_ceiling_junctions']=[]
for i,poly in enumerate(polys):
 slab(poly,'PAR_Floor'+str(i),16.26,16.5,'staff_rubber','floor');slab(poly,'PAR_Roof'+str(i),19.7,19.82,'staff_white_paint','roof')
 for j,(a,b)in enumerate(zip(poly.exterior.coords,list(poly.exterior.coords)[1:])):
  x,z=a;X,Z=b;vertical=abs(x-X)<1e-6;lo,hi=(min(z,Z),max(z,Z))if vertical else(min(x,X),max(x,X));spans=[(lo,hi)]
  # Private-court collars are exact source wall-width; retained upper glazing plus new stepped portal header closes to20.46.
  if vertical and any(abs(x-g['wall_x'])<.001 and lo>=g['z']-.851 and hi<=g['z']+.851 for g in P['gates'][:9]):continue
  opening=None
  if vertical and abs(x+59)<.001:opening=(290.65,292.15)
  if not vertical and abs(z-290.8)<.001:opening=(-23.95,-22.45)
  if not vertical and abs(z-445.4)<.001:opening=(-44.75,-43.25)
  if opening:spans=[(u,v)for A,B in spans for u,v in[(A,min(B,opening[0])),(max(A,opening[1]),B)]if v-u>.0001]
  for k,(A,B)in enumerate(spans):
   name='PAR_Wall'+str(i)+'_'+str(j)+'_'+str(k)
   if vertical:box(name,(x-.06,16.5,A),(x+.06,19.7,B))
   else:box(name,(A,16.5,z-.06),(B,19.7,z+.06))
   P['wall_ceiling_junctions'].append({'wall':name,'roof':'PAR_Roof'+str(i),'wall_top_y':19.7,'roof_underside_y':19.7})
source=json.load(open(R/'BlenderCatalogue/assets/d04_staff_court_physical_connections_20261011/PLAN.json'));sg=P['source_gate_template'];parts={q['name']:q for q in source['parts']};P['gate_source']={'native':P['source_gate_native'],'source_pivot':sg['pivot'],'members':sg['members'],'control_members':sg['control_members']}
for i,g in enumerate(P['gates']):
 a=math.radians(g['source_rotation_y_degrees']);c,s=math.cos(a),math.sin(a)
 def tr(v):dx=v[0]-sg['pivot'][0];dz=v[2]-sg['pivot'][2];return[g['pivot'][0]+c*dx+s*dz,g['pivot'][1]+v[1]-sg['pivot'][1],g['pivot'][2]-s*dx+c*dz]
 for name in sg['members']+sg['control_members']:
  q=copy.deepcopy(parts[name]);q['name']='PAR_G'+str(i)+'_'+name;q['verts']=[tr(v)for v in q['verts']]
  if name.endswith('_Control')and i>=9:q['verts']=[[v[k]+g['fixed_control_delta'][k]for k in range(3)]for v in q['verts']]
  P['copied_gate_parts'].append(q);g['members'if name in sg['members']else'control_members'].append(q['name'])
 g['control_at']=tr(sg['control_at'])
 if i>=9:g['control_at']=[g['control_at'][k]+g['fixed_control_delta'][k]for k in range(3)]
 if i<9:
  x=g['wall_x'];z=g['z'];box('PAR_CourtHeader'+str(i),(x-.1,19.2,z-.75),(x+.1,20.46,z+.75),'champagne_metal','header');P['wall_ceiling_junctions'].append({'wall':'PAR_CourtHeader'+str(i),'retained_roof':g['court_prefix']+'_Roof','wall_top_y':20.46,'roof_underside_y':20.46})
 elif i in [10,11]:
  x=g['closed_center'][0];z=g['closed_center'][2];box('PAR_ReceivingHeader'+str(i),(x-.75,19.2,z-.12),(x+.75,20.48,z+.12),'champagne_metal','header')
  for k,(a,b)in enumerate([(x-1.2,x-.75),(x+.75,x+1.2)]):box('PAR_ReceivingUpperWing'+str(i)+'_'+str(k),(a,19.7,z-.06),(b,20.48,z+.06),'staff_bluegrey_paint','wall')
  P['wall_ceiling_junctions'].append({'wall':'PAR_ReceivingHeader'+str(i),'retained_roof':'PA_ReceivingRoof','wall_top_y':20.48,'roof_underside_y':20.48})
 else:P['wall_ceiling_junctions'].append({'retained_wall':'PANR_D04SF_ServiceEastWall','retained_roof':'PA_ReceivingRoof','wall_top_y':20.48,'roof_underside_y':20.48})
for i,q in enumerate(S['ledgers']):
 x=q['site']['x'];z=q['site']['z'];outer=-66.18 if x<-40 else -22.02;box('PAR_Ledger'+str(i),(x-.08,16.27,z-.18),(x+.08,16.49,z+.18),'champagne_metal','frame');box('PAR_WingBeam'+str(i),(min(x,outer),16.30,z-.12),(max(x,outer),16.45,z+.12),'champagne_metal','frame')
P['end_ledger_sites']=[]
for x,name in[(-27.2,'PASH_D04SFH_D04HC3_east_Floor'),(-60.9,'PASH_D04SFH_D04HC3_west_Floor'),(-44,'PA_ReceivingFloor')]:P['end_ledger_sites'].append({'x':x,'z':445.2 if x!=-44 else 445.4,'source_mesh':name,'source_root':'D04PortAftHabitatNeighborhood','half_x':.16})
for room in json.load(open(R/'Game/data/architecture/D04_PORT_AFT_NEIGHBORHOOD.json'))['rooms']:
 if room['allocation']['source_envelope_index']not in[984,996]:continue
 q=next(q for q in room['parts']if q['category']=='floor');a=room['allocation']['allocation_x'];P['end_ledger_sites'].append({'x':sum(a)/2,'z':445.2,'source_mesh':q['name'],'source_root':'D04PortAftHabitatNeighborhood','half_x':.16})
box('PAR_CrossRingBeamSouth',(-66.18,16.3,446.48),(-22.02,16.45,446.72),'champagne_metal','frame')
for i,site in enumerate(P['end_ledger_sites']):
 x,z=site['x'],site['z'];box('PAR_EndLedger'+str(i),(x-.18,16.27,z-.08),(x+.18,16.49,z+.08),'champagne_metal','frame');box('PAR_EndWingBeam'+str(i),(x-.12,16.30,z),(x+.12,16.45,447.7),'champagne_metal','frame')
# North entry edge joints use actual distinct source platform faces, no duplicate walking floor.
P['north_entry_floor_joints']=[{'point':[-59,16.38,291.4],'normal':[-1,0,0],'source_mesh':'PA_ReceivingFloor'},{'point':[-23.2,16.38,290.8],'normal':[0,0,1],'source_mesh':'PA_ReceivingFloor'}]
box('PAR_NorthWestEntryLedger',(-59.08,16.27,291.22),(-58.92,16.49,291.58),'champagne_metal','frame');box('PAR_NorthWestEntryBeam',(-66.18,16.30,291.28),(-59,16.45,291.52),'champagne_metal','frame');box('PAR_NorthEastEntryLedger',(-23.38,16.27,290.72),(-23.02,16.49,290.88),'champagne_metal','frame');box('PAR_NorthEastEntryBeam',(-23.32,16.30,290.8),(-23.08,16.45,294.5),'champagne_metal','frame')
for i,(x,z)in enumerate([(x,z)for x in[-65,-23.2]for z in[297,304,311,318,325,330,410,417,424,431,438,445]]+[(x,446.6)for x in[-58,-51,-44,-37,-30]]+[(-61,291.4),(-23.2,291.4)]):
 box('PAR_LampHousing'+str(i),(x-.3,19.37,z-.22),(x+.3,19.52,z+.22),'champagne_metal','fixture');box('PAR_LampLens'+str(i),(x-.26,19.35,z-.18),(x+.26,19.37,z+.18),'opal_glow','fixture');P['lights'].append({'name':'PAR_LampLens'+str(i),'at':[x,19.33,z]})
P['patch_file']='D04_PORT_AFT_COURT_PATCH_r002.glb';P['structure_file']='D04_PORT_AFT_COURT_ROUTES_r002.glb';P['closed_staging_translation']=[0,0,0]
for f in [W/'PLAN.json',W/'NATIVE_AUTHORING_INPUT_PLAN.json']:f.write_text(json.dumps(P,indent=2)+'\n')
print(json.dumps({'floor_m2':floor.area,'parts':len(P['parts']),'junctions':len(P['wall_ceiling_junctions'])}))
