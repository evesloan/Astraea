"""A Court-A-specific PURE geometry candidate using the reviewed pool METHOD.
Never appends or exports any pool prototype. No Blender and no source writes.
"""
from pathlib import Path
import sys,json,math,hashlib
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent
M=Path('/workspace/scratch/375c2e438292/pool-architectural-composition/plant_mass_prototype')
sys.path.insert(0,str(M))
from retained_geometry import Geometry,add,mul,sub
from geometry_plan import fit_reach,along,LEVELS,ANGLES
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
base=json.loads((R/'COURT_A_GEOMETRY_CONTRACT.json').read_text())
soil=next(s for s in base['soil_receivers']if s.get('retained'))
origin=[-69.5,soil['top_y']-.003,-143.0]
poly=[[x-origin[0],-(z-origin[2])]for x,z in soil['polygon_xz']]
poly.sort(key=lambda p:math.atan2(p[1],p[0]))
g=Geometry('AST-CUL-005_court_A_middle_mass_004','AST-BOT-002',origin,soil['id'],'theater_middle_mass_candidate',0)
chosen=[]
for j,(x,y,h)in enumerate([[-1.4,.08,1.19],[0,.10,1.43],[1.4,.06,1.09]]):
 root=f'CA4_crown{j}_root';stem=f'CA4_crown{j}_stem';g.root(root,x,y,.045)
 points=[[x,y,.035],[x+.018,y-.012,h*.32],[x-.025,y+.020,h*.67],[x+.02,y-.014,h]]
 g.tube(stem,points,[.031,.026,.019,.009]);g.joint(stem,root,points[0])
 for k,t in enumerate(LEVELS):
  at=along(points,t);angle=ANGLES[k]+[11,-9,23][j];width=[.41,.445,.40][j];want=[.58,.65,.56][j]
  options=[]
  for change in[0,12,-12,26,-26,45,-45,70,-70,100,-100,150,180]:
   a=angle+change;r=math.radians(a);leafbase=add(at,[.042*math.cos(r),.042*math.sin(r),.025]);length=fit_reach(leafbase,a,want,width,poly,.02)
   if length is not None:options.append((abs(change)+max(0,.35-length)*450,a,length,leafbase))
  assert options,(j,k)
  _,a,length,leafbase=min(options,key=lambda x:x[0]);pet=f'CA4_crown{j}_pet{k:02}';leaf=f'CA4_crown{j}_leaf{k:02}'
  g.tube(pet,[at,add(at,mul(sub(leafbase,at),.52)),leafbase],[.01,.007,.005],'botanical_leaf_olive',6);g.joint(pet,stem,at)
  role=['sage','jade','olive'][j]if k%4 else'jade'
  g.blade(leaf,leafbase,a,length,width,[.11,.15,.18,.12][k%4],.155,.062,'botanical_leaf_'+role,.018 if k%2 else-.018,'broad',pet)
  chosen.append({'part':leaf,'angle_degrees':a,'authored_reach_m':want,'fitted_reach_m':length,'width_m':width})
asset=g.finish();asset.update(soil_polygon_local_xy=poly,soil_surface_local_z=.003,authored_leaf_fit=chosen,status='COURT_A_PURE_GEOMETRY_ONLY_SOURCE_UNBUILT',source_method_parent='BOT-002; reviewed pool half-plane fit method, not pool source asset reuse',retention_gate='No candidate export/adoption until this Court A source is built, independently reopened, visually reviewed and independently retained')
from shapely.geometry import Polygon,Point
sp=Polygon(poly);outside=[];roots=[];maximum=0
for part in asset['parts']:
 for v in part['vertices']:
  if not sp.buffer(1e-7).covers(Point(v[0],v[1])):outside.append(part['name'])
  maximum=max(maximum,v[2]-.003)
 if part['name'].endswith('_root'):
  pp=part['shape_controls']['centerline'][0];radius=part['shape_controls']['radii'][0]
  roots.append({'part':part['name'],'world':[origin[0]+pp[0],origin[1]+pp[2],origin[2]-pp[1]],'embed_m':.003,'root_radius_m':radius,'root_disk_outside_m2':Point(pp[0],pp[1]).buffer(radius).difference(sp).area,'soil_depth_m':soil['top_y']-soil['bottom_y'],'minimum_proposed_soil_depth_m':.22})
assert not outside and all(r['root_disk_outside_m2']<1e-10 for r in roots)
record={'status':'PASS_PURE_SOIL_FIT_ONLY_UNBUILT_UNRETAINED','asset':asset,'source_method_pins':{str(p):sha(p)for p in[M/'geometry_plan.py',M/'retained_geometry.py',M/'CURRENT_STATUS.md',M/'SOURCE_JOB001.json',M/'candidate_v001/qa/SOURCE_QA.json']},'fit':{'all_emitted_vertices_inside_actual_soil_projection':True,'soil_polygon_world_xz':soil['polygon_xz'],'roots':roots,'maximum_height_above_soil_m':maximum,'closed_root_stem_petiole_and_open_full_blades':True,'whole_plant_scale':[1,1,1],'clipped_blades':0,'pool_route_or_collision_acceptance_inherited':False},'material_policy':'Append exact botanical material roles from retained BOT-002 source; preserve leaf across/root-to-tip UVs and packed bytes. No source graph reconstruction or recolouring. Runtime consolidate by material, not one node per leaf.','gates':['Parent-coordinated Court A source build','Independent source reopen and exact joint/UV/material checks','Court A composed pixels including retained fans and lower bank','Independent retention before any export','Actual Godot contact/light-budget/composition review']}
(R/'FULLER_REAR_MASS_CANDIDATE.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'status':record['status'],'parts':asset['part_count'],'triangles':asset['planned_triangle_count'],'roots':roots,'height_m':maximum},indent=2))
