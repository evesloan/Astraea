"""Pure authored connected-gallery geometry. No engine or shared writes."""
from pathlib import Path
import ast,json,math,copy,hashlib,struct
import numpy as np
S=Path('/workspace/scratch/375c2e438292');B=Path(__file__).parent;C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');FLOOR=52.5
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
old=json.loads((S/'pool-east-gallery-canopy-correction001/revision001/CORE_PLAN.json').read_text());parts=copy.deepcopy(old['parts']);old_names={p['name']for p in parts};changed=set()
# Reuse only the retained pure geometry constructors, never their top-level writer.
method=S/'pool-opposite-gallery-proposal001/source_blockin001/plan_core.py';tree=ast.parse(method.read_text());names={'scalar','add','box','extrude_plan','loft_closed','ellipse'}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names],type_ignores=[]),str(method),'exec'))
FACES=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
def replace(name):
 global parts
 p=next(x for x in parts if x['name']==name);parts.remove(p);changed.add(name);return p
# Each piecewise-linear roof is evaluated at the very same knots used by its mesh.
def roof(x,z,a,b,rise):
 n=24;i=max(0,min(n-1,int((z-a)/(b-a)*n)));t=((z-a)/(b-a)*n-i);s0=math.sin(math.pi*i/n);s1=math.sin(math.pi*(i+1)/n);s=s0*(1-t)+s1*t
 return 56.02+.17*(x+10.85)+rise*s
bay_a,bay_b=-454.,-445.
bayheight=lambda x,z:roof(x,z,bay_a,bay_b,1.22)
for name in ['EAST_Bay_WarmRearCanopy','EAST_Bay_PaleFrontCanopy']:
 p=next(x for x in parts if x['name']==name);changed.add(name)
 for v in p['vertices_xyz']:v[1]=scalar(v[1]+bayheight(v[0],v[2])-(56.02+.17*(v[0]+10.85)))
 p['semantic']='Continuous rising curved full-width canopy; new integrated revision, original curvature retained as design guidance';p['source_group']='connected_gallery'
# Rear closure rises with the actual roof, keeping the clay back untouched.
name='EAST_Bay_RearHeader';p=replace(name);v=np.array(p['vertices_xyz']);xmin,xmax=v[:,0].min(),v[:,0].max();ymin=v[:,1].min();rings=[]
for i in range(25):
 z=bay_a+(bay_b-bay_a)*i/24;rings.append([[xmin,ymin,z],[xmax,ymin,z],[xmax,bayheight(xmax,z),z],[xmin,bayheight(xmin,z),z]])
loft_closed(name,'bay','retail_terracotta_enamel',rings,['EAST_Bay_CurvedClayBack','EAST_Bay_WarmRearCanopy'],semantic='Continuous curved rear closure into retained enclosure')
# Follow the exact new canopy at every existing mount vertex; keep image and lower hangers exact.
for name in ['EAST_Bay_FixtureCup_0','EAST_Bay_FixtureCup_1','EAST_Bay_OpalLens_0','EAST_Bay_OpalLens_1','EAST_Display_CommonMountRail']:
 p=next(x for x in parts if x['name']==name);changed.add(name)
 for v in p['vertices_xyz']:v[1]=scalar(v[1]+bayheight(v[0],v[2])-(56.02+.17*(v[0]+10.85)))
for name in ['EAST_Display_Hanger_Fore','EAST_Display_Hanger_Aft']:
 p=next(x for x in parts if x['name']==name);changed.add(name);ys=[v[1]for v in p['vertices_xyz']];threshold=(min(ys)+max(ys))/2
 for v in p['vertices_xyz']:
  if v[1]>threshold:v[1]=scalar(v[1]+bayheight(v[0],v[2])-(56.02+.17*(v[0]+10.85)))
fixtures=copy.deepcopy(old['fixture_reservations'])
for r in fixtures:
 x,y,z=r['position_xyz'];r['position_xyz'][1]=scalar(y+bayheight(x,z)-(56.02+.17*(x+10.85)))
 dz=.001;slope=(bayheight(x,z+dz)-bayheight(x,z-dz))/(2*dz);n=np.array([.17,-1,slope]);r['direction_xyz']=(n/np.linalg.norm(n)).tolist();r['native_acceptance_pending']=True
# Convex difference builds exact cutouts around retained octagonal pier profiles.
contract=json.loads((C/'assets/grand_pool_orchard_section/source/connected_contract.json').read_text())
def ring(name,y):
 p=next(p for p in contract['source_parts']if p['name']==name);r=[[v[0],v[2]]for v in p['world_vertices']if abs(v[1]-y)<1e-7]
 if sum(r[i][0]*r[(i+1)%len(r)][1]-r[(i+1)%len(r)][0]*r[i][1]for i in range(len(r)))<0:r.reverse()
 return r
pier4=ring('GP_UpperPier_4',53.05);cap4=ring('GP_UpperPier_4',59.35);cap3=ring('GP_UpperPier_3',59.35)
def clip(poly,a,b,inside):
 def d(p):return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
 out=[]
 for p,q in zip(poly,poly[1:]+poly[:1]):
  dp,dq=d(p),d(q);ip=dp>=-1e-10 if inside else dp<=1e-10;iq=dq>=-1e-10 if inside else dq<=1e-10
  if ip:out.append(p)
  if ip!=iq:
   t=dp/(dp-dq);out.append([p[k]+t*(q[k]-p[k])for k in range(2)])
 clean=[]
 for p in out:
  if not clean or math.dist(p,clean[-1])>1e-7:clean.append(p)
 if len(clean)>1 and math.dist(clean[0],clean[-1])<1e-7:clean.pop()
 if len(clean)<3:return []
 area=abs(sum(clean[i][0]*clean[(i+1)%len(clean)][1]-clean[(i+1)%len(clean)][0]*clean[i][1]for i in range(len(clean))))/2
 return clean if area>1e-8 else []
def difference(poly,hole):
 remain=poly;out=[]
 for a,b in zip(hole,hole[1:]+hole[:1]):
  if not remain:break
  piece=clip(remain,a,b,False)
  if piece:out.append(piece)
  remain=clip(remain,a,b,True)
 return out

def variable(name,role,poly,y0,y1,support,group='gallery_roof',**kw):
 n=len(poly);vs=[[x,fn(x,z),z]for fn in [y0,y1]for x,z in poly];fs=[list(range(n-1,-1,-1)),list(range(n,n*2))]+[[i,(i+1)%n,(i+1)%n+n,i+n]for i in range(n)]
 return add(name,group,role,vs,fs,support,grain_axis_xyz=[1,0,0],**kw)
for label,a,b,rise,holes in [('Fore',-461.1,-454.,1.22,[pier4]),('Market',-445.,-435.4,1.40,[])]:
 n=24;zs=[a+(b-a)*i/n for i in range(n+1)]
 for i in range(n):
  def xf(z):return -10.85-.25*math.sin(math.pi*(z-a)/(b-a))
  poly=[[xf(zs[i]),zs[i]],[-8.2,zs[i]],[-8.2,zs[i+1]],[xf(zs[i+1]),zs[i+1]]];ps=[poly]
  for hole in holes:ps=[q for p in ps for q in difference(p,hole)]
  for j,p in enumerate(ps):
   h=lambda x,z:roof(x,z,a,b,rise)
   variable(f'CG_{label}_Vault_{i:02}_{j}_Timber','warm_walnut',p,h,lambda x,z:h(x,z)+.065,['GP_EastWall.002','GP_UpperPier_4']if label=='Fore'else['GP_EastWall.002'],semantic='Connected curved timber gallery soffit, continuous across real supports')
   variable(f'CG_{label}_Vault_{i:02}_{j}_Cap','warm_stone',p,lambda x,z:h(x,z)+.065,lambda x,z:h(x,z)+.28,[f'CG_{label}_Vault_{i:02}_{j}_Timber'],semantic='Actual finite cap and fascia, contrasting timber underside')
 # Full-height clay enclosure is supported by retained wall, roof profile closes the top.
 poly=[[-8.35,a],[-8.2,a],[-8.2,b],[-8.35,b]]
 for i in range(n):
  p=[[-8.35,zs[i]],[-8.2,zs[i]],[-8.2,zs[i+1]],[-8.35,zs[i+1]]]
  variable(f'CG_{label}_ClayWall_{i:02}','retail_terracotta_enamel',p,lambda x,z:FLOOR,lambda x,z:roof(x,z,a,b,rise),['GP_EastWall.002','COMPILER_FLOOR_D09_orchard_market_gallery'],group='gallery_wall',semantic='Real terracotta receiving wall, ceiling junction continuous')
# Bookends at outer limits: stepped plans, actual ceiling bearing. Central returns retained.
for label,z,a,b,rise in [('Fore',-461.1,-461.1,-454.,1.22),('Aft',-435.4,-445.,-435.4,1.40)]:
 lo,hi=(z,z+.15)if label=='Fore'else(z-.15,z);p=[[-10.85,lo],[-8.35,lo],[-8.35,hi],[-10.85,hi]]
 variable(f'CG_{label}_OuterBearing','warm_stone',p,lambda x,z:FLOOR,lambda x,z:roof(x,z,a,b,rise),['COMPILER_FLOOR_D09_orchard_market_gallery'],group='gallery_bearing',semantic='Full-height end bearing connecting wall to curved roof')
# Upper crown: real supports remain visible. Roof rib splits solids, capitals are exact cutouts.
xbreak=[-12.18,-11.5,-10.8,-8.2];ys=[60.4,60.4,60.0,59.95]
for seg,(z0,z1)in enumerate([(-461.1,-451.45),(-450.55,-435.4)]):
 for j,(x0,x1)in enumerate(zip(xbreak,xbreak[1:])):
  ps=[[[x0,z0],[x1,z0],[x1,z1],[x0,z1]]]
  for hole in [cap4,cap3]:ps=[q for p in ps for q in difference(p,hole)]
  for k,p in enumerate(ps):
   low=lambda x,z,j=j:ys[j]+(ys[j+1]-ys[j])*(x-xbreak[j])/(xbreak[j+1]-xbreak[j])
   variable(f'CG_UpperCrown_{seg}_{j}_{k}','warm_walnut',p,low,lambda x,z:low(x,z)+.18,['GP_LongCeilingReturn_-12.5','GP_EastWall.002','GP_RoofRib_-451','GP_UpperPier_4','GP_UpperPier_3'],semantic='Stepped continuous upper crown, connected to real perimeter return and wall')
# Supported corbel between long return and pier4, with explicit shared bearing faces.
xy=[[-12.18,59.8],[-11.90,59.70],[-11.30,59.48],[-10.0765,59.35],[-10.0765,60.40],[-12.18,60.40]]
n=len(xy);vs=[[x,y,z]for z in [-458.55,-457.45]for x,y in xy];fs=[list(range(n-1,-1,-1)),list(range(n,n*2))]+[[i,(i+1)%n,(i+1)%n+n,i+n]for i in range(n)]
add('CG_Pier4_CurvedCapitalCorbel','gallery_bearing','warm_stone',vs,fs,['GP_LongCeilingReturn_-12.5','GP_UpperPier_4'],semantic='Real corbel linking existing offset capital to high longitudinal return')
# Narrowed shaft facings: all remain inside original wider base/capital envelope.
box('CG_Pier4_WestBearingFace','gallery_bearing','warm_walnut',[-9.9425,53.07,-458.59],[-9.9025,58.998,-457.41],'GP_UpperPier_4',semantic='Supported middle-shaft timber facing showing collar bearing',grain_axis_xyz=[0,1,0])
box('CG_Pier4_AftBearingFace','gallery_bearing','warm_walnut',[-9.59,53.07,-457.1],[-8.91,58.998,-457.06],'GP_UpperPier_4',semantic='Supported return face, existing pale shaft edges remain visible',grain_axis_xyz=[0,1,0])
# Two full planted ends, reusing the actual unscaled crown+basal family footprint.
plants=[]
for label,cz,var in [('Fore',-460.16,'00'),('Directory',-455.30,'03')]:
 cx=-9.70;N=32;rs=[(1.24,.65,52.5),(1.31,.68,52.59),(1.31,.68,53.1),(1.21,.64,53.1),(1.21,.64,52.7)]
 rings=[[[cx+rx*math.cos(2*math.pi*i/N),y,cz+rz*math.sin(2*math.pi*i/N)]for i in range(N)]for rx,rz,y in rs]
 bowl=loft_closed(f'CG_{label}Bed_Container','soilbed','warm_stone',rings,'COMPILER_FLOOR_D09_orchard_market_gallery',semantic='Full planted orientation pocket, actual finite basin')
 rings=[[[cx+1.21*math.cos(2*math.pi*i/N),y,cz+.64*math.sin(2*math.pi*i/N)]for i in range(N)]for y in [52.7,53.02]]
 soil=loft_closed(f'CG_{label}Bed_Soil','soilbed','botanical_soil',rings,bowl)
 plants.append({'name':'CG_'+label,'variant':var,'position_xyz':[cx,53.02,cz],'yaw_radians':0.,'scale_xyz':[1,1,1],'soil_object':soil,'available_soil_xy_m':[2.42,1.28]})
# Directory derivative from the retained frame/backing proportions, physically mounted to pier west face.
# Plane UV: U along +Z, V up, outward -X. Original body preserved; new bounded dimensions are explicit.
for name,role,u0,u1,y0,y1,x0,x1 in [('Directory_Back','ivory_enamel',-.55,.55,53.95,55.35,-9.9745,-9.9425),('Directory_Frame_Fore','warm_walnut',-.61,-.55,53.89,55.41,-10.0045,-9.9425),('Directory_Frame_Aft','warm_walnut',.55,.61,53.89,55.41,-10.0045,-9.9425),('Directory_Frame_Top','warm_walnut',-.55,.55,55.35,55.41,-10.0045,-9.9425),('Directory_Frame_Bottom','warm_walnut',-.55,.55,53.89,53.95,-10.0045,-9.9425)]:
 box('CG_'+name,'directory',role,[x0,y0,-458+u0],[x1,y1,-458+u1],'CG_Pier4_WestBearingFace',parent_family='AST-RES-001',semantic='Bounded physical directory derivative with real bearing; original family retained')
# Four new real source housings under the added vaults. Native optical selection/energy pending.
for i,(label,x,z,a,b,rise)in enumerate([('Fore',-10.57,-460.0,-461.1,-454.,1.22),('Directory',-10.57,-455.6,-461.1,-454.,1.22),('Service',-10.52,-443.,-445.,-435.4,1.4),('Counter',-10.52,-437.8,-445.,-435.4,1.4)]):
 h=lambda x,z:roof(x,z,a,b,rise);N=20;rs=[(.11,0),(.11,-.11),(.079,-.11),(.079,-.028)]
 rings=[[[x+r*math.cos(2*math.pi*k/N),h(x+r*math.cos(2*math.pi*k/N),z+r*math.sin(2*math.pi*k/N))+dy,z+r*math.sin(2*math.pi*k/N)]for k in range(N)]for r,dy in rs]
 cup=loft_closed(f'CG_{label}_FixtureCup','fixtures','champagne_metal',rings,'CG_'+('Fore'if i<2 else'Market')+'_Vault',semantic='Real canopy-recessed cup and visible aperture')
 rings=[[[x+.079*math.cos(2*math.pi*k/N),h(x+.079*math.cos(2*math.pi*k/N),z+.079*math.sin(2*math.pi*k/N))+dy,z+.079*math.sin(2*math.pi*k/N)]for k in range(N)]for dy in [-.067,-.055]]
 lens=loft_closed(f'CG_{label}_OpalLens','fixtures','lens',rings,cup);parts[-1]['collision']='visual_lens_no_contact';parts[-1]['cast_shadow']=False
 dz=.001;normal=np.array([.17,-1,(h(x,z+dz)-h(x,z-dz))/(2*dz)]);normal/=np.linalg.norm(normal)
 fixtures.append({'name':f'CG_{label}_LightReserve','housing':cup,'physical_lens':lens,'position_xyz':[x,h(x,z)-.103,z],'direction_xyz':normal.tolist(),'candidate_only':True,'native_range_energy_aim':'must derive from actual receiving surfaces; not accepted','maximum_active_lights_unchanged':8})
reuse=[{'name':'CG_MarketCounter','catalogue_id':'AST-LIB-012','source':str(C/'assets/library_arrival_counter/source/AST-LIB-012.blend'),'position_xyz':[-10.78,52.5,-438.70],'yaw_radians':-math.pi/2,'scale_xyz':[1,1,1]},{'name':'CG_ServiceWorkbench','catalogue_id':'AST-RTL-003','source':str(C/'assets/retail_work/source/AST-RTL-003.blend'),'position_xyz':[-10.65,52.5,-443.0],'yaw_radians':-math.pi/2,'scale_xyz':[1,1,1]}]
new_names={p['name']for p in parts}-old_names
plan={**old,'status':'CONNECTED_CURVED_GALLERY_PURE_PLAN_PENDING_QA','source_brief_sha256':sha(B/'SOURCE_BRIEF.md'),'parts':parts,'fixture_reservations':fixtures,'additional_plants':plants,'retained_furniture':reuse,'modified_existing_parts':sorted(changed),'new_parts':sorted(new_names),'user_design_message':'Sentinel_512e57bb743881918717a87eb828ab21','restored_curvature':True,'public_scope_length_m':25.7,'programme':{'groups':['orientation_garden','rest_bay','market_receiving'],'new_furniture_instances':2,'new_botanical_instances':4,'new_directory_derivative':1,'new_light_reservations':4,'old_bay_lights':2,'active_budget':8,'candidate_budget':32},'source_base':str(C/'assets/grand_pool_first_pass/architectural_composition/east_gallery_arrival001/canopy_revision002/revision001/source001/source/AST-AQU-016_east_gallery_canopy_r02.blend'),'source_base_sha256':'7dfce55242a651af80b59199217424470ed8d951ecb81eee68ac83539ea5fe14','pending':['Pure connected geometry screening','Composed source build/reopen','Actual source context view','Independent retention/export','Runtime physical and art acceptance']}
(B/'CORE_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
print(json.dumps({'parts':len(parts),'new':len(new_names),'modified':len(changed),'fixtures':len(fixtures),'plan_sha256':sha(B/'CORE_PLAN.json')},indent=2))
