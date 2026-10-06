"""Author a bounded, source-first architectural block-in. No engine or project writes."""
import json,math,hashlib
from pathlib import Path
S=Path(__file__).resolve().parent;C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');G=Path('/workspace/shared/astraea-godot-production-20261003')
FLOOR=46.2;parts=[];plants=[];lights=[]
FACES=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
def add(name,group,role,vertices,faces,support,**extras):
 row=dict(name=name,group=group,material_role=role,vertices_xyz=vertices,faces=faces,support=support,collision='concave_static_surface',**extras);parts.append(row);return name
def box(name,group,role,lo,hi,support,**extra):
 v=[[lo[0],lo[1],lo[2]],[hi[0],lo[1],lo[2]],[hi[0],lo[1],hi[2]],[lo[0],lo[1],hi[2]],[lo[0],hi[1],lo[2]],[hi[0],hi[1],lo[2]],[hi[0],hi[1],hi[2]],[lo[0],hi[1],hi[2]]];return add(name,group,role,v,FACES,support,**extra)
def prism(name,group,role,profile,depth0,depth1,axis,support):
 # profile=(horizontal,height), depth along X(west) or Z(end); no source rescaling.
 v=[]
 for dep in [depth0,depth1]:
  v += [[dep,y,h]if axis=='x'else[h,y,dep]for h,y in profile]
 return add(name,group,role,v,[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],support)
def curved_vault(prefix,group,centre,width,spring,rise,thickness,depth0,depth1,axis,role,support,segments=16):
 half=width/2;opening=half-.42;outer=[];inner=[]
 for i in range(segments+1):
  a=math.pi*i/segments;inner.append([centre-opening*math.cos(a),spring+rise*math.sin(a)]);outer.append([centre-half*math.cos(a),spring+(rise+thickness)*math.sin(a)+.08])
 names=[]
 for i in range(segments):names.append(prism(prefix+'_Roof_%02d'%i,group,role,[inner[i],inner[i+1],outer[i+1],outer[i]],depth0,depth1,axis,[support,prefix+'_Roof_%02d'%(i-1)]if i else[support,prefix+'_LegL']))
 for side,h0,h1 in [('L',centre-half,centre-opening),('R',centre+opening,centre+half)]:
  names.append(prism(prefix+'_Leg'+side,group,role,[[h0,FLOOR],[h1,FLOOR],[h1,spring if side=='L'else spring+.08],[h0,spring+.08 if side=='L'else spring]],depth0,depth1,axis,'D08_grand_pool_wet'))
 return names

def ring_solid(name,group,role,cx,cz,rx,rz,y0,y1,support,segments=24,bottom_radii=None):
 brx,brz=bottom_radii or (rx,rz);bottom=[[cx+brx*math.cos(2*math.pi*i/segments),y0,cz+brz*math.sin(2*math.pi*i/segments)]for i in range(segments)];top=[[cx+rx*math.cos(2*math.pi*i/segments),y1,cz+rz*math.sin(2*math.pi*i/segments)]for i in range(segments)];faces=[list(range(segments-1,-1,-1)),list(range(segments,2*segments))]+[[i,(i+1)%segments,(i+1)%segments+segments,i+segments]for i in range(segments)];return add(name,group,role,bottom+top,faces,support)
def bowl(prefix,cx,cz):
 # Open earth pocket with closed profiled wall and a separate finite soil solid.
 n=28;rings=[(.61,1.16,FLOOR),(.69,1.24,FLOOR+.08),(.72,1.28,FLOOR+.60),(.62,1.18,FLOOR+.60),(.59,1.15,FLOOR+.18)];vs=[]
 for rx,rz,y in rings:vs += [[cx+rx*math.cos(2*math.pi*i/n),y,cz+rz*math.sin(2*math.pi*i/n)]for i in range(n)]
 fs=[]
 for j in range(len(rings)-1):
  for i in range(n):fs.append([j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i])
 # Close the shell's underside across its full bottom; close inner basin floor.
 fs.append(list(range(n-1,-1,-1)));fs.append(list(range((len(rings)-1)*n,len(rings)*n)))
 add(prefix+'_Bowl','loggia','warm_stone',vs,fs,'D08_grand_pool_wet',programme_role='planted_pocket')
 ring_solid(prefix+'_Soil','loggia','botanical_soil',cx,cz,.607,1.167,FLOOR+.18,FLOOR+.52,prefix+'_Bowl',segments=n,bottom_radii=(.587,1.147))
 return FLOOR+.52

def curved_seat(prefix,cz,half_angle):
 cx=-56.;n=12;angles=[math.radians(-half_angle+2*half_angle*i/n)for i in range(n+1)]
 def wedge(name,r0,r1,y0,y1,a,b,role,support):
  plan=[[cx+r0*math.cos(a),cz+r0*math.sin(a)],[cx+r1*math.cos(a),cz+r1*math.sin(a)],[cx+r1*math.cos(b),cz+r1*math.sin(b)],[cx+r0*math.cos(b),cz+r0*math.sin(b)]];v=[[x,y0,z]for x,z in plan]+[[x,y1,z]for x,z in plan];return add(name,'loggia',role,v,FACES,support)
 for i,(a,b)in enumerate(zip(angles,angles[1:])):
  base=wedge(prefix+'_StoneBase_%02d'%i,4.,4.55,FLOOR,FLOOR+.34,a,b,'warm_stone','D08_grand_pool_wet')
  seat=wedge(prefix+'_TimberSeat_%02d'%i,3.98,4.59,FLOOR+.34,FLOOR+.44,a,b,'warm_walnut',base)
  wedge(prefix+'_ClayPad_%02d'%i,4.04,4.53,FLOOR+.44,FLOOR+.49,a+.002,b-.002,'aquatic_clay_sling',seat)
  wedge(prefix+'_TimberBack_%02d'%i,3.81,3.98,FLOOR+.34,FLOOR+1.02,a,b,'warm_walnut',[base,seat])

niches=[('Fore',-442.2,12.4,50.,4.5),('Middle',-424.6,11.2,43.,3.8),('Aft',-406.7,12.4,50.,4.5)]
for index,(label,cz,width,angle,plantz)in enumerate(niches):
 prefix='LOG_'+label
 curved_vault(prefix+'_Vault','loggia',cz,width,49.65,1.26,.28,-53.38,-49.67,'x','warm_walnut','GP_WestWall.001')
 curved_vault(prefix+'_StoneFace','loggia',cz,width,49.65,1.26,.28,-49.67,-49.32,'x','warm_stone',prefix+'_Vault',segments=16)
 # A low tiled back field ends below the existing exposed wallwasher housings.
 zl,zr=cz-width/2+.45,cz+width/2-.45
 box(prefix+'_TileBeddingMid','loggia','warm_stone',[-53.63,47.08,zl],[-53.6,47.28,zr],'Finish_WetWest_PaleQuietField')
 box(prefix+'_TileBeddingTop','loggia','warm_stone',[-53.608,47.28,zl],[-53.6,48.90,zr],'Finish_WetWest_'+str(index+1)+'_RecessBacking')
 box(prefix+'_LowTileBack','loggia','aquatic_edge_tile',[-53.6,FLOOR,zl],[-53.565,48.90,zr],['Finish_WetWest_StonePlinth',prefix+'_TileBeddingMid',prefix+'_TileBeddingTop'])
 curved_seat(prefix+'_Seat',cz,angle)
 for side,offset in enumerate([-plantz,plantz]):
  pod=prefix+'_Pocket_'+str(side);y=bowl(pod,-50.70,cz+offset);variant=index*2+side
  for kind,parent,file in [('basal','AST-BOT-003','AST-BOT-003_pool_basal_%02d.glb'%variant),('middle','AST-BOT-002','AST-BOT-002_pool_middle_%02d.glb'%variant)]:
   plants.append(dict(name=pod+'_'+kind,parent_design_id=parent,model_file=file,position_xyz=[-50.70,y,cz+offset],yaw_radians=math.pi/2,scale_xyz=[1,1,1],support=pod+'_Soil',existing_checked_export=True))

# The fore-end room sits fully behind the existing gallery fascia, not through it.
curved_vault('FOCAL_Vault','focal_end',-31.,12.,49.25,1.20,.26,-465.67,-461.62,'z','warm_walnut','GP_EndEnclosure',segments=18)
curved_vault('FOCAL_StoneFace','focal_end',-31.,12.,49.25,1.20,.26,-461.62,-461.38,'z','warm_stone','FOCAL_Vault',segments=18)
arc=[[-31.-5.58*math.cos(math.pi*i/18),49.25+1.20*math.sin(math.pi*i/18)]for i in range(19)]
def roof_at_x(x):
 for a,b in zip(arc,arc[1:]):
  if a[0]<=x<=b[0]:return a[1]+(b[1]-a[1])*(x-a[0])/(b[0]-a[0])
 raise ValueError(x)
left,right=-36.45,-25.55;profile=[[left,FLOOR],[right,FLOOR],[right,roof_at_x(right)]]+[p for p in reversed(arc)if left<p[0]<right]+[[left,roof_at_x(left)]];n=len(profile);vs=[[x,y,z]for z in [-465.67,-465.58]for x,y in profile];fs=[list(range(n-1,-1,-1)),list(range(n,2*n))]+[[i,(i+1)%n,(i+1)%n+n,i+n]for i in range(n)];add('FOCAL_RecessedTerracotta','focal_end','retail_terracotta_enamel',vs,fs,'D08_grand_pool_wet')
# A large authored orbital-water relief, rooted in the end wall; no extra seat/pot.
n=40;vs=[[ -31+1.08*math.cos(2*math.pi*i/n),49.15+1.08*math.sin(2*math.pi*i/n),z]for z in [-465.58,-465.32]for i in range(n)];fs=[list(range(n-1,-1,-1)),list(range(n,2*n))]+[[i,(i+1)%n,(i+1)%n+n,i+n]for i in range(n)];add('FOCAL_OrbitalSunRelief','focal_end','champagne_metal',vs,fs,'FOCAL_RecessedTerracotta')
# The final relief is intentionally not resolved as a decorative cylinder. Three
# wide physical wave ribbons establish scale/depth before original image/artwork.
for i in range(3):
 for j in range(12):
  x0=-35.5+j*.75;x1=x0+.75;y0=47.15+i*.36+.13*math.sin(j*.48+i*.9);y1=47.15+i*.36+.13*math.sin((j+1)*.48+i*.9)
  prism('FOCAL_Wave_%d_%02d'%(i,j),'focal_end','ivory_enamel'if i!=1 else'aquatic_edge_tile',[[x0,y0],[x1,y1],[x1,y1+.10],[x0,y0+.10]],-465.58,-465.39,'z','FOCAL_RecessedTerracotta')

# Larger ceiling wings grow between retained ribs. The open centre slot exposes
# the already retained ceiling, not D10 or a new opening, and keeps all six authored
# roof-wash receiver rays at X=-31 clear.
fields=[(-460.0,-451.45),(-450.55,-433.45),(-432.55,-416.45),(-415.55,-404.0)]
for fi,(z0,z1)in enumerate(fields):
 for side in [-1,1]:
  xs=[-31+side*x for x in [1.35,3.25,5.5,8.0,10.6]];ys=[60.12,59.95,59.63,59.29,59.06]
  for j in range(4):
   q=[[xs[j],ys[j]],[xs[j+1],ys[j+1]],[xs[j+1],ys[j+1]+.16],[xs[j],ys[j]+.16]]
   label='ROOF_Wing_%d_%s_%d'%(fi,'West'if side<0 else'East',j)
   prism(label,'roof','ivory_enamel'if j<3 else'warm_walnut',q,z0+.03,z1-.03,'z',[label+'_ForeCleat',label+'_AftCleat'])
   # Actual ribs are waisted to centre +/- .22 m at these X coordinates.
   # Their .45 m bounding-box half-depth applies only outside the wing span.
   # Extend just the metal ties over that .23 m gap, keeping wing geometry fixed.
   fore=z0 if fi==0 else [-451,-451,-433,-416][fi]+.22
   aft=z1 if fi==3 else [-451,-433,-416,-416][fi]-.22
   prism(label+'_ForeCleat','roof','champagne_metal',q,fore,z0+.03,'z','GP_RoofRib_'+str([-451,-451,-433,-416][fi])if fi else label)
   prism(label+'_AftCleat','roof','champagne_metal',q,z1-.03,aft,'z','GP_RoofRib_'+str([-451,-433,-416,-416][fi])if fi<3 else label)
# End fields hang from the actual original ceiling, with explicitly recorded
# small anchor penetrations through the already retained finish skin only.
for end,zi in [('Fore',-459.15),('Aft',-405.0)]:
 for side in [-1,1]:
  xx=-31+side*9.8
  box('ROOF_'+end+'Hanger_'+str(side),'roof','champagne_metal',[xx-.065,59.05,zi-.08],[xx+.065,60.76,zi+.08],'D10_shared_table_reserved_cap_underside',intentional_anchor_through=['Finish_RoofCoffer_'+('0'if end=='Fore'else'3')+'_InnerJunction','Finish_RoofCoffer_'+('0'if end=='Fore'else'3')+'_PaleCentralField'])

# Market thresholds remain a separate fitting subpass in this first block-in:
# existing cases run behind retained upper piers. They must become asymmetric
# pier-connected recesses, not six arbitrary arches intersecting those piers.
# Budget/intent are explicit; no falsely accepted geometry is emitted here.
inputs={}
for p in [G/'data/architecture/GRAND_POOL_SECTION_RUNTIME.json',G/'data/architecture/GRAND_POOL_FIRST_PASS_RUNTIME.json',G/'data/architecture/GRAND_POOL_FINISH_RUNTIME.json',C/'assets/grand_pool_orchard_section/source/AST-AQU-016.blend',C/'assets/aquatic_lounge/source/AST-AQU-001.blend']:
 inputs[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
for part in parts:
 if 'Hanger_'in part['name']:
  field=0 if '_Fore'in part['name']else 3;side='West'if part['name'].endswith('-1')else'East';part['intentional_new_mechanical_joint']='ROOF_Wing_%d_%s_3'%(field,side)
 if part['material_role']=='warm_walnut':
  if part['name'].startswith('ROOF_')or part['group']=='focal_end':part['grain_axis_xyz']=[0,0,1]
  elif '_Seat_'in part['name']:
   vertices=part['vertices_xyz'];cx=sum(v[0]for v in vertices)/len(vertices);cz=sum(v[2]for v in vertices)/len(vertices);center_z=next(row[1]for row in niches if part['name'].startswith('LOG_'+row[0]));radius=math.hypot(cx+56,cz-center_z);part['grain_axis_xyz']=[-(cz-center_z)/radius,0,(cx+56)/radius]
  else:part['grain_axis_xyz']=[0,1,0]if part['name'].endswith(('LegL','LegR'))else[1,0,0]
plan=dict(schema=1,status='FITTED_BLOCKIN_003_PENDING_SOURCE_REOPEN_AND_VISUAL_REVIEW',parts=parts,plants=plants,fixtures=lights,input_sha256=inputs,budget={'retained_logical_furnishings':126,'new_integrated_curved_seats':3,'new_soil_pockets':6,'new_botanical_instances':12,'new_focal_room_seating_or_pots':0,'prospective_explicit_furnishings':147,'new_architectural_GLBS':3,'maximum_additional_source_lights':3,'active_shadow_limit_unchanged':8},pending=['Actual mesh support/contact/oldfixture exit and view-volume screening','Physically support new fixture reservations if needed','Fit asymmetric market recesses around actual retained upper piers','Coordinate Blender source build and early ordinary-eye composed view','No exports or runtime adoption at block-in stage'])
(S/'BLOCKIN_PLAN_003.json').write_text(json.dumps(plan,indent=2)+'\n');print(len(parts),'planned editable solid parts;',len(plants),'retained botanical instances; source/fixture/visual gates pending')
