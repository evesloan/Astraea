"""Author a new, unselected aquatic station; never rewrite retained sources."""
from pathlib import Path
import json, math, hashlib, importlib.util, sys, copy
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[2];D=R/'Game/aquatic_tram_interior_20261026/r002'
assert not D.exists()
spec=importlib.util.spec_from_file_location('author',R/'recovery/tram_section_successor_20261023/author_section_r002.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
prior=json.loads((R/'Game/aquatic_tram_interior_20261026/r001/RECEIVING_PLAN.json').read_text(encoding='utf-8'))
for p,h in prior['source_pins'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
base=json.loads((R/'Game/orchard_tram_interior_20261025/r006/PLAN.json').read_text(encoding='utf-8'))
points=np.array(prior['route']['route_points_xz']);fit=a.PathFit(points)
compiled=json.loads((R/'Game/data/generated/structural_meshes.json').read_text(encoding='utf-8'))
floor=next(f for f in compiled['regions'] if f['id']=='D09_living_gifts_floor')
upper=[f for f in compiled['regions'] if f['floor_y']==61]
stops=[]
for st in base['stops']:
 target=np.array([18.5,192] if st['station']=='AFT_MIDSHIP' else base['central']['path_point_xz'] if st['station']=='CENTRAL' else [st['world_xyz'][0],st['world_xyz'][2]])
 at=fit.nearest(target);pose=fit.fit(at);stops.append(dict(st,distance_m=at,world_xyz=[pose[1],56.1,pose[2]],body_yaw=pose[3]))
knots=sorted(set([4.,float(fit.s[-1]-4)]+list(np.arange(4,fit.s[-1]-4,.1))+[s['distance_m'] for s in stops]))
poses=[fit.fit(float(at))+[.25] for at in knots]
assert max(abs(p[i]) for p in poses for i in [4,7])<.2
central=next(p for p in poses if p[0]==next(s['distance_m'] for s in stops if s['station']=='CENTRAL'))
assert np.max(np.abs(np.array(central[1:4])-base['central']['new_pose'][1:4]))<1e-7
interval=[fit.nearest(np.array([-5.6,140])),fit.nearest(np.array([-5.6,300]))]
# Exact transformed original recess: half turn around the relocated root.
# X23.3 keeps the complete 4.4m recess outside the X20.5 vehicle reservation.
station=copy.deepcopy(next(s for s in json.loads((R/'Game/data/architecture/GROUP4_COMPLETION_CANDIDATE.json').read_text(encoding='utf-8'))['stations'] if s['label']=='AFT_MIDSHIP'))
station.update(lift_root=[23.3,0,187.7],lift_yaw_rad=math.pi/2,
 boarding_edge_x=20.7,physical_docking_z=192,track_x=18.5,
 platform_xz=[20.7,187.9,28.5,198],lower_lift_recess_xz=[21.1,25.5,183.9,187.9],
 retained_lower_floor_owners=['D09_living_gifts_floor'])
rect=station['lower_lift_recess_xz']
def area(poly):return abs(sum(p[0]*q[1]-q[0]*p[1] for p,q in zip(poly,poly[1:]+poly[:1])))/2
def subtract(triangle):
 inside=triangle;outside=[]
 for axis,value,above in [(0,rect[0],True),(0,rect[1],False),(1,rect[2],True),(1,rect[3],False)]:
  if not inside:break
  piece=a.screen.clip(inside,axis,value,not above)
  if len(piece)>2 and area(piece)>1e-10:outside += [[piece[0],piece[i],piece[i+1]] for i in range(1,len(piece)-1) if area([piece[0],piece[i],piece[i+1]])>1e-10]
  inside=a.screen.clip(inside,axis,value,above)
 removed=area(inside) if len(inside)>2 else 0
 return (outside,removed) if removed>1e-10 else ([triangle],0)
after=copy.deepcopy(floor);triangles=[];removed=0
for t in floor['triangles']:
 ps,amount=subtract(t);triangles+=ps;removed+=amount
assert abs(removed-17.6)<1e-7
after['triangles']=triangles;after['structural_area_m2']-=removed
hole=[[rect[0],rect[2]],[rect[1],rect[2]],[rect[1],rect[3]],[rect[0],rect[3]]]
outer=floor['rings'][0]
if sum(p[0]*q[1]-q[0]*p[1] for p,q in zip(outer,outer[1:]+outer[:1]))>0:hole.reverse()
after['rings'].append(hole)
for chunk in after.get('render_chunks',[]):chunk['triangles']=[p for t in chunk['triangles'] for p in subtract(t)[0]]
# Public balcony, real depth/recess borders and separately supported east refuge.
a.prism('AquaticArrivalSlab',[[20.7,187.9],[26.1,187.9],[26.1,190.6],[28.5,190.6],[28.5,198],[20.7,198]],55.82,56.1,'warm_stone')
a.box('ArrivalWalnutWestEdge',[20.8,55.94,192.95],[.12,.24,10.1],'warm_walnut')
a.box('ArrivalWalnutEastEdge',[28.4,55.94,194.3],[.12,.24,7.4],'warm_walnut')
for z,w,x in [(188,5.4,23.4),(197.9,7.8,24.6)]:a.box('ArrivalTerracottaFascia_'+str(z),[x,55.88,z],[w,.28,.12],'AquaticTerracottaEnamel')
# Clear boarding aperture stays exactly 2.22m; original bridge/controller reused.
for z0,z1 in [(187.9,190.89),(193.11,198)]:
 a.beam('TrackGuardRail_'+str(z0),[20.76,57.23,z0],[20.76,57.23,z1],.10,.10)
 a.box('TrackGuardGlass_'+str(z0),[20.76,56.71,(z0+z1)/2],[.035,1.1,z1-z0],'AquaticGuardGlass')
for z in [190.8,193.2]:a.box('OriginalPortalReceiver_'+str(z),[20.76,57.45,z],[.16,2.7,.16])
a.box('PortalHeader',[20.76,58.88,192],[.16,.16,2.56],'warm_walnut')
# East-facing stair descends to the intact north D09 gallery. Twenty 180mm rises.
for i in range(20):
 x=26.1+.3*i;top=56.1-.18*i
 a.box('PublicStairTread_%02d'%i,[x+.15,top-.10,189.3],[.30,.20,2.4],'warm_stone')
 a.box('PublicStairGrip_%02d'%i,[x+.025,top+.004,189.3],[.045,.008,2.22],'dark_rubber')
for z in [188.12,190.48]:
 a.beam('PublicStairStringer_'+str(z),[26.1,55.84,z],[32.1,52.24,z],.16,.28)
 a.beam('PublicStairHandrail_'+str(z),[26.1,57.23,z],[32.1,53.63,z],.10,.10)
 for i in range(5):
  x=26.1+1.5*i;y=56.1-.6*(x-26.1)
  a.box('PublicStairPost_%s_%s'%(z,i),[x,y+.52,z],[.08,1.12,.08])
# Intact lower floor is reused, never covered by a duplicate slab.
# Four hanger frames have exact D10 pad footprint ownership; unresolved pads
# are a real selection hold, not suppressed to claim structural readiness.
receivers=[];unresolved=[]
for i,(x,z) in enumerate([(21.1,188.25),(25.7,188.25),(21.1,195.6),(25.7,195.6)]):
 owners=a.screen.footprint_owners(np.array([x,z]),upper)
 if len(owners)!=1 or abs(owners[0]['overlap_m2']-.0864)>1e-6:unresolved.append({'part':'ArrivalHanger_'+str(i),'owners':owners})
 else:receivers.append({'part':'ArrivalHanger_'+str(i),'pad':[x,z],'owner':owners[0]})
 a.box('ArrivalHanger_'+str(i),[x,58.33,z],[.12,4.94,.12])
 a.box('ArrivalHangerBearing_'+str(i),[x,60.79,z],[.24,.08,.36])
for z,end in [(188.25,26.1),(195.6,28.5)]:a.beam('ArrivalUnderbeam_'+str(z),[20.7,55.74,z],[end,55.74,z],.20,.24)
# Guard the new balcony's free edges. North lift threshold and east stair are open.
for x0,x1 in [(20.7,21.1),(25.5,26.1)]:
 a.beam('NorthGuard_'+str(x0),[x0,57.23,187.95],[x1,57.23,187.95],.1,.1)
for z0,z1 in [(190.6,198)]:
 a.beam('EastGuard',[28.45,57.23,z0],[28.45,57.23,z1],.1,.1)
 a.box('EastGuardGlass',[28.45,56.71,(z0+z1)/2],[.035,1.1,z1-z0],'AquaticGuardGlass')
a.beam('SouthGuard',[20.7,57.23,197.95],[28.5,57.23,197.95],.1,.1)
a.box('SouthGuardGlass',[24.6,56.71,197.95],[7.8,1.1,.035],'AquaticGuardGlass')
# Planted lower arrival plus an upper water-view conversation refuge.
plants=[];furniture=[]
def bed(name,lo,hi,y):
 x=(lo[0]+hi[0])/2;z=(lo[1]+hi[1])/2;w=hi[0]-lo[0];l=hi[1]-lo[1]
 a.box(name+'_Base',[x,y+.12,z],[w,.24,l],'AquaticTerracottaEnamel')
 a.box(name+'_Soil',[x,y+.27,z],[w-.16,.08,l-.16],'botanical_soil')
 for xx in [lo[0]+.04,hi[0]-.04]:a.box(name+'_RimX_'+str(xx),[xx,y+.30,z],[.08,.16,l],'warm_walnut')
 for zz in [lo[1]+.04,hi[1]-.04]:a.box(name+'_RimZ_'+str(zz),[x,y+.30,zz],[w,.16,.08],'warm_walnut')
 return y+.31
y=bed('NorthGalleryGarden',[27,182.5],[35,184.7],52.5)
for i,x in enumerate([28.2,31,33.8]):plants.append({'file':'AST-BOT-001.glb','name':'NorthCanopy_'+str(i),'xyz':[x,y,183.6],'yaw':i*.8})
for i,x in enumerate(np.linspace(27.6,34.4,9)):plants.append({'file':'AST-BOT-009.glb','name':'NorthShrub_'+str(i),'xyz':[float(x),y,184.15],'yaw':i*.6})
for i,x in enumerate(np.linspace(27.4,34.6,14)):plants.append({'file':'AST-BOT-003.glb','name':'NorthGroundcover_'+str(i),'xyz':[float(x),y,183.0],'yaw':i*.4})
y=bed('UpperRefugeGarden',[26.9,194.5],[28.3,197.7],56.1)
for i,z in enumerate([195.1,196.1,197.1]):plants.append({'file':'AST-BOT-009.glb','name':'RefugeShrub_'+str(i),'xyz':[27.6,y,z],'yaw':i*.7})
for i,z in enumerate(np.linspace(194.9,197.3,6)):plants.append({'file':'AST-BOT-003.glb','name':'RefugeGroundcover_'+str(i),'xyz':[27.2,y,float(z)],'yaw':i*.7})
for i,(x,y,z,yaw) in enumerate([(29,52.5,185.6,0),(33,52.5,185.6,0),(25.8,56.1,196.7,math.pi/2)]):
 furniture.append({'file':'AST-FUR-001.glb','name':'WaterGardenBench_'+str(i),'xyz':[x,y,z],'yaw':yaw})
# No fictional extra light sources: original station fittings will be relocated
# with their immutable source, unchanged energy and the existing light selector.
plan=dict(base,schema='astraea.aquatic.interior.r002',active=False,status='UNSELECTED_AUTHORED_RECEIVING',route_points_xz=points.tolist(),stops=stops)
plan['central']=dict(base['central'],new_pose=central[:-1]);plan['aquatic_interval_m']=interval
plan['safe_body_cursor_range_m']=[4,float(fit.s[-1]-4)]
plan['aftmid_receiving']=station;plan['unresolved_receivers']=unresolved
plan['remaining']=['Full route supports and exact retired guideway receiver reconciliation','Original shaft enclosure relocation and fixture bindings','Original vehicle/cart/door sweep against new receiving and preserved world','Native/runtime comparison','Installed lift, boarding, stair and rider sightlines','Visual guest completion review','Moving resource/performance and matching Windows delivery']
pins=dict(prior['source_pins'])
for f in ['AST-AQU-012.glb','AST-AQU-013.glb','AST-AQU-014.glb','AST-RTL-006.glb','AST-BOT-001.glb','AST-BOT-003.glb','AST-BOT-009.glb','AST-FUR-001.glb']:
 p='Game/assets/models/'+f;pins[p]=hashlib.sha256((R/p).read_bytes()).hexdigest()
D.mkdir()
for name,data in [('PLAN.json',plan),('PARTS.json',a.parts),('POSE_KNOTS.json',poses),('SOURCE_PINS.json',pins),('PLANTING_AND_SEATING.json',{'plants':plants,'furniture':furniture}),('PIT_AND_BINDING.json',{'before':floor,'after':after,'removed_m2':removed,'station':station,'selected':False}),('RECEIVERS.json',{'bindings':receivers,'unresolved':unresolved})]:
 (D/name).write_bytes((json.dumps(data,separators=(',',':'))+'\n').encode())
print(json.dumps({'parts':len(a.parts),'plants':len(plants),'benches':len(furniture),'pit_cut_m2':removed,'hanger_receivers':len(receivers),'unresolved':unresolved,'selected':False}))
