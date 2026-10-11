from pathlib import Path
import json,hashlib,copy,math
from shapely.geometry import box as rect,mapping,shape
from shapely.ops import unary_union,triangulate
W=Path('/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/d04_starboard_forward_work_branches_20261011');R=W.parents[2];P=json.load(open(W/'AUDIT_INPUT_PLAN.json'));S=json.load(open(W/'SITE_PREFLIGHT001.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert len(S['meshes'])==15 and all(not q.get('missing')and not q['blockers']for q in S['supports'])and all(not q['blockers']for q in S['roof_rows']);P['runtime_preimages']=S['meshes'];P['support_preimages']=S['supports']
for f in ['Game/data/reference/D04_guest_envelopes.json','Game/data/spatial_layout.json','Game/data/hull_envelope.json']:P['source_pins'][f]=sha(R/f)
for row in P['cuts']+P['moves']:
 q=next(q for q in S['meshes']if q['name']==row['name']);v=row['preimage']['verts'];lo=[min(p[i]for p in v)for i in range(3)];hi=[max(p[i]for p in v)for i in range(3)];assert max(abs(a-b)for a,b in zip(lo+hi,q['bounds'][0]+q['bounds'][1]))<.00015,row['name']
source_approaches=[q for q in S['stances']if q['at']in P['source_approach_samples']];assert len(source_approaches)==10 and all(not q['blockers']and q.get('floor')and abs(q['floor']['y']-16.5)<.001 for q in source_approaches)
P['parts']=[];P['lights']=[];faces=[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
def box(name,lo,hi,role='staff_bluegrey_paint',cat='wall'):
 x,y,z=lo;X,Y,Z=hi;assert X>x and Y>y and Z>z;P['parts'].append({'name':name,'verts':[[a,b,c]for b in[y,Y]for a,c in[(x,z),(X,z),(X,Z),(x,Z)]],'faces':faces,'role':role,'category':cat,'runtime_collision':True})
floor=unary_union([rect(*q['lo'],*q['hi'])for q in []])if False else unary_union([rect(q['lo'][0],q['lo'][1],q['hi'][0],q['hi'][1])for q in P['floor_rectangles']]);P['floor_geometry']=mapping(floor);P['new_floor_m2']=floor.area;polys=list(floor.geoms)if floor.geom_type=='MultiPolygon'else[floor]
for i,poly in enumerate(polys):
 # Watertight triangulated slabs with only the true union boundary sides.
 points=list(poly.exterior.coords)[:-1];index={tuple(p):j for j,p in enumerate(points)};n=len(points);fs=[]
 for tri in triangulate(poly):
  if not poly.covers(tri.representative_point()):continue
  ids=[index[tuple(p)]for p in list(tri.exterior.coords)[:-1]];fs.extend([list(reversed(ids)),[j+n for j in ids]])
 fs += [[j,(j+1)%n,(j+1)%n+n,j+n]for j in range(n)]
 for label,Y,H,role,category in [('Floor',16.26,16.5,'staff_rubber','floor')]:P['parts'].append({'name':'SFW_'+label+str(i),'verts':[[x,y,z]for y in[Y,H]for x,z in points],'faces':fs,'role':role,'category':category,'runtime_collision':True})
 for j,(a,b)in enumerate(zip(poly.exterior.coords,list(poly.exterior.coords)[1:])):
  x,z=a;X,Z=b
  # Leave source portal joins and private court-side edges open; exact source successor fills those boundaries.
  if abs(z-Z)<1e-6 and ((abs(z+384)<1e-6)or(abs(z+356.2)<1e-6)):continue
  if abs(x-X)<1e-6 and any(abs(x-g['wall_x'])<.0001 and min(z,Z)>=g['z']-.851 and max(z,Z)<=g['z']+.851 for g in P['gates'][:4]):continue
  collar=next((g for g in P['gates'][:4] if abs(z-Z)<1e-6 and abs(abs(z-g['z'])-.85)<1e-6 and min(x,X)>=g['wall_x']-.001 and max(x,X)<=(64 if g['branch']=='south' else 63.3)+.001),None)
  if collar:
   low=min(x,X);high=max(x,X);verts=[[low,16.5,z-.06],[high,16.5,z-.06],[high,16.5,z+.06],[low,16.5,z+.06],[low,20.46,z-.06],[high,19.7,z-.06],[high,19.7,z+.06],[low,20.46,z+.06]]
   P['parts'].append({'name':'SFW_CollarWall'+str(i)+'_'+str(j),'verts':verts,'faces':faces,'role':'staff_bluegrey_paint','category':'wall','runtime_collision':True})
  elif abs(x-X)<1e-6:box('SFW_Wall'+str(i)+'_'+str(j),(x-.06,16.5,min(z,Z)),(x+.06,19.7,max(z,Z)))
  else:box('SFW_Wall'+str(i)+'_'+str(j),(min(x,X),16.5,z-.06),(max(x,X),19.7,z+.06))
# Flat roofs cover main halls only; sloped collars are separately sealed.
roof=unary_union([rect(q['lo'][0],q['lo'][1],q['hi'][0],q['hi'][1]) for q in P['floor_rectangles'][:3]])
for i,poly in enumerate(roof.geoms):
 points=list(poly.exterior.coords)[:-1];index={tuple(p):j for j,p in enumerate(points)};n=len(points);fs=[]
 for tri in triangulate(poly):
  if poly.covers(tri.representative_point()):
   ids=[index[tuple(p)]for p in list(tri.exterior.coords)[:-1]];fs.extend([list(reversed(ids)),[j+n for j in ids]])
 fs += [[j,(j+1)%n,(j+1)%n+n,j+n]for j in range(n)]
 P['parts'].append({'name':'SFW_Roof'+str(i),'verts':[[x,y,z]for y in[19.7,19.82]for x,z in points],'faces':fs,'role':'staff_white_paint','category':'roof','runtime_collision':True})
# Close the south boundary join except the actual staff portal.
box('SFW_SouthJoinWest',(64,16.5,-384.06),(71.326,19.7,-383.94));box('SFW_SouthJoinEast',(72.826,16.5,-384.06),(73.2,19.7,-383.94))
source=json.load(open(R/'BlenderCatalogue/assets/d04_staff_court_physical_connections_20261011/PLAN.json'));sg=P['source_gate_template'];parts={q['name']:q for q in source['parts']};P['gate_source']={'native':P['source_gate_native'],'source_pivot':sg['pivot'],'members':sg['members'],'control_members':sg['control_members']};P['copied_gate_parts']=[]
for i,g in enumerate(P['gates']):
 g['source_rotation_y_degrees']=-90 if i<4 else 0
 def transform(v):
  x,y,z=v;dx=x-sg['pivot'][0];dz=z-sg['pivot'][2];return [g['pivot'][0]-dz if i<4 else g['pivot'][0]+dx,g['pivot'][1]+y-sg['pivot'][1],g['pivot'][2]+dx if i<4 else g['pivot'][2]+dz]
 for name in sg['members']+sg['control_members']:
  q=copy.deepcopy(parts[name]);q['name']='SFW_G'+str(i)+'_'+name;q['verts']=[transform(v)for v in q['verts']]
  if name.endswith('_Control')and i>=4:q['verts']=[[v[k]+g['fixed_control_delta'][k]for k in range(3)]for v in q['verts']]
  P['copied_gate_parts'].append(q);g['members'if name in sg['members']else'control_members'].append(q['name'])
 g['control_at']=transform(sg['control_at'])
 if i>=4:g['control_at']=[g['control_at'][k]+g['fixed_control_delta'][k]for k in range(3)]
 if i<4:
  z=g['z'];x=g['wall_x'];end=64 if g['branch']=='south'else 63.3
  # Sloped local collar roof reaches the unchanged original court canopy; lower hall roof remains an independent slab.
  verts=[[X,Y+(.12 if upper else 0),Z]for upper in[False,True]for X,Y,Z in[(x,20.46,z-.85),(end,19.7,z-.85),(end,19.7,z+.85),(x,20.46,z+.85)]];P['parts'].append({'name':'SFW_CollarRoof'+str(i),'verts':verts,'faces':faces,'role':'staff_white_paint','category':'roof','runtime_collision':True});box('SFW_CourtHeader'+str(i),(x+.01,19.2,z-.75),(x+.19,19.45,z+.75),'champagne_metal','header')
 else:box('SFW_StaffHeader'+str(i),(g['pivot'][0]-.1,19.2,g['pivot'][2]-.12),(g['pivot'][0]+1.4,19.7,g['pivot'][2]+.12),'champagne_metal','header')
# Support geometry is authored only from the exact existing keel samples and empty column-volume proof.
for i,q in enumerate(S['supports']):
 x,z,h=q['x'],q['z'],q['half'];base=[]
 for X,Z in[(x-h,z-h),(x+h,z-h),(x+h,z+h),(x-h,z+h)]:base.append([X,min(q['corners'],key=lambda c:(c['point'][0]-X)**2+(c['point'][2]-Z)**2)['point'][1],Z])
 P['parts'].append({'name':'SFW_Foot'+str(i),'verts':base+[[X,q['column_bottom'],Z]for X,Y,Z in base],'faces':faces,'role':'champagne_metal','category':'frame','runtime_collision':True});box('SFW_Column'+str(i),(x-h+.04,q['column_bottom'],z-h+.04),(x+h-.04,16.14,z+h-.04),'champagne_metal','frame');box('SFW_Cap'+str(i),(x-h-.06,16.14,z-h-.06),(x+h+.06,16.26,z+h+.06),'champagne_metal','frame')
for i,(x,z)in enumerate([(65.2,z)for z in range(-440,-386,8)]+[(64.5,z)for z in range(-352,-310,8)]+[(69,-386.4),(72,-386.4)]):
 box('SFW_FixtureHousing'+str(i),(x-.3,19.37,z-.22),(x+.3,19.52,z+.22),'champagne_metal','fixture');box('SFW_FixtureLens'+str(i),(x-.26,19.35,z-.18),(x+.26,19.37,z+.18),'opal_glow','fixture');P['lights'].append({'name':'SFW_FixtureLens'+str(i),'at':[x,19.33,z]})
# The four static source meshes form one intact closed used-return dock in the wide receiving junction.
P['closed_staging_source_members']=[n for n in parts if n.startswith('D04PC_ClosedUsed_0_')];P['closed_staging_translation']=[107.5,4.5,63.5];P['closed_staging_parts']=[]
for n in P['closed_staging_source_members']:
 q=copy.deepcopy(parts[n]);q['name']='SFW_ClosedDock_'+n;q['verts']=[[v[k]+P['closed_staging_translation'][k]for k in range(3)]for v in q['verts']];P['closed_staging_parts'].append(q)
P['patch_file']='D04_STARBOARD_FORWARD_WORK_PATCH_r001.glb';P['structure_file']='D04_STARBOARD_FORWARD_WORK_BRANCHES_r001.glb';P['pending_port_central_commons_untouched']=True;P['source_side_name_note']='Historical west names in mirrored source nodes are retained; actual world-positiveX geometry identifies the eastern courts.'
P['north_end_condition_threshold_m2']=floor.intersection(rect(63,-356.2,85,-356)).area;P['outer_floor_free_perimeter_m2_unchanged']=336;P['stair_headroom_void_m2_unchanged']=68.04
for f in[W/'PLAN.json',W/'NATIVE_AUTHORING_INPUT_PLAN.json']:f.write_text(json.dumps(P,indent=2)+'\n')
(W/'build_plan001.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({'new_floor_m2':floor.area,'fixed_parts':len(P['parts']),'gate_source_parts':len(P['copied_gate_parts']),'closed_staging_source_meshes':len(P['closed_staging_parts']),'north_end_condition_threshold_m2':P['north_end_condition_threshold_m2']}))
