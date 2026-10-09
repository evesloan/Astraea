from pathlib import Path
import json,hashlib,math,sys
sys.path.insert(0,'/workspace/shared/astraea_python_deps')
from shapely.geometry import box,shape,Polygon
R=Path(__file__).resolve().parents[4];O=R/'BlenderCatalogue/assets/sunset_receiving_frame_20261009';(O/'source').mkdir(parents=True,exist_ok=True)
source=R/'BlenderCatalogue/assets/residential_hotels/aft_houses_20261007_r001/residential-neighborhood-courts-20261007/sunset_conservatory_house/outputs/house_r002/PLAN.json';old=json.load(open(source));parts=[];joints=[]
def cube(name,lo,hi,role):
 assert all(b>a for a,b in zip(lo,hi));parts.append({'name':name,'kind':'box','min':lo,'max':hi,'role':role});return name
def beam(name,a,b,width,depth,role):
 parts.append({'name':name,'kind':'beam','a':a,'b':b,'width':width,'depth':depth,'role':role});return name
def edge(z):return -100 if z<=423.164 else -100+(z-423.164)*37/67.959
stations=[251,310,350,386,397.2,466.8,480]
for i,z in enumerate(stations):
 x=edge(z)-.1
 cube(f'SC_Frame_{i}_LowerEmbeddedFlange',[-4.8,77.80,z-.45],[-3.7,77.98,z+.45],'axial_contact')
 cube(f'SC_Frame_{i}_LowerCheek',[-4.8,77.80,z-.45],[-4.05,78.70,z+.45],'axial_contact')
 cube(f'SC_Frame_{i}_UpperEmbeddedFlange',[-4.8,83.74,z-.45],[-3.7,83.98,z+.45],'axial_contact')
 cube(f'SC_Frame_{i}_UpperCheek',[-4.8,82.95,z-.45],[-4.05,83.98,z+.45],'axial_contact')
 cube(f'SC_Frame_{i}_UpperChord',[x,83.06,z-.45],[-4.05,83.76,z+.45],'transfer_chord')
 beam(f'SC_Frame_{i}_Diagonal',[-4.45,78.5,z],[x+.25,83.25,z],.50,.60,'transfer_diagonal')
 for k,u in enumerate([.2,.4,.6,.8]):
  xx=-4.45+(x+.25+4.45)*u;yy=78.5+(83.25-78.5)*u
  cube(f'SC_Frame_{i}_Web_{k}',[xx-.15,yy-.1,z-.18],[xx+.15,83.35,z+.18],'transfer_web')
 joints.append({'station_z':z,'source_receivers':['D12_aft_route','D13_aft_route'],'lower_contact_volume':[-4,77.8,z-.45,-3.7,77.98,z+.45],'upper_contact_volume':[-4,83.76,z-.45,-3.7,83.98,z+.45]})
# Outboard longitudinal trusses do not cross the Vesper allocation.
zs=sorted(set([250.5,491.0,423.164]+stations))
for line in ['outer','inner','verge']:
 def xx(z):return edge(z)+.4 if line=='outer' else (-63.45 if line=='inner' else -59.6)
 for i,(a,b)in enumerate(zip(zs,zs[1:])):
  # The taper leaves no full-width court at the last point; centre follows its edge.
  wa=1.0 if line=='outer'else .7
  beam(f'SC_Long_{line}_{i}_Top',[xx(a),83.41,a],[xx(b),83.41,b],wa,.70,'longitudinal_chord')
  beam(f'SC_Long_{line}_{i}_Bottom',[xx(a),78.65,a],[xx(b),78.65,b],wa,.70,'longitudinal_chord')
  count=max(1,math.ceil((b-a)/12))
  for k in range(count):
   z0=a+(b-a)*k/count;z1=a+(b-a)*(k+1)/count
   beam(f'SC_Long_{line}_{i}_Diagonal_{k}',[xx(z0),78.65,z0],[xx(z1),83.41,z1],.32,.36,'longitudinal_web')
   cube(f'SC_Long_{line}_{i}_Web_{k}',[xx(z0)-.17,78.30,z0-.17],[xx(z0)+.17,83.76,z0+.17],'longitudinal_web')
# Real source reaction rows, distributed court loads and the retained stair foot.
rows=[260,262,288,291,316,320,344,349,361.4,379,381.9,389,396,417,421,451,475,377.25,382.15]
for i,z in enumerate(rows):cube(f'SC_CourtCollector_{i}',[edge(z)-.1,82.96,z-.35],[-59.05,83.76,z+.35],'court_collector')
# Four inner reactions can be connected without entering Vesper.
for x in [-28,-15]:
 for i,(a,b)in enumerate([(251,310),(310,350),(350,397.5)]):
  beam(f'SC_Inner_{x}_{i}_Top',[x,83.41,a],[x,83.41,b],.6,.7,'inner_collector')
  beam(f'SC_Inner_{x}_{i}_Bottom',[x,79,a],[x,79,b],.6,.6,'inner_collector')
  count=math.ceil((b-a)/12)
  for k in range(count):
   z0=a+(b-a)*k/count;z1=a+(b-a)*(k+1)/count
   beam(f'SC_Inner_{x}_{i}_Diagonal_{k}',[x,79,z0],[x,83.41,z1],.3,.34,'inner_collector')
   cube(f'SC_Inner_{x}_{i}_Web_{k}',[x-.15,78.7,z0-.15],[x+.15,83.76,z0+.15],'inner_collector')
reactions=[];held=[]
for q in old['parts']:
 if q['category']!='pier' or q['kind']!='mesh':continue
 lo=[min(v[i]for v in q['verts'])for i in range(3)];hi=[max(v[i]for v in q['verts'])for i in range(3)]
 if abs(lo[1]-84)>.001:continue
 x=(lo[0]+hi[0])/2;z=(lo[2]+hi[2])/2
 if -54<x<-8 and 398<z<466:held.append(q['name']);continue
 cube(q['name']+'_UnderSlabBearing',[lo[0]-.12,83.48,lo[2]-.12],[hi[0]+.12,83.76,hi[2]+.12],'bearing_shoe')
 reactions.append({'source_part':q['name'],'footprint_xz':[lo[0],lo[2],hi[0],hi[2]],'source_foot_y':84,'existing_source_slab_interval':[83.76,84]})
assert len(reactions)==40 and len(held)==2
# Conservative bounds: exact boxes, endpoint-expanded beam bounds. Reject any programme intrusion.
def bounds(p):
 if p['kind']=='box':return p['min'],p['max']
 # Beam cross sections can extend no further than the larger half diagonal.
 t=[p['b'][i]-p['a'][i]for i in range(3)];n=math.sqrt(sum(v*v for v in t));t=[v/n for v in t];ref=[0,0,1]if abs(t[2])<.95 else [1,0,0];d=sum(t[i]*ref[i]for i in range(3));s=[ref[i]-t[i]*d for i in range(3)];n=math.sqrt(sum(v*v for v in s));s=[v/n for v in s];u=[t[1]*s[2]-t[2]*s[1],t[2]*s[0]-t[0]*s[2],t[0]*s[1]-t[1]*s[0]]
 ext=[abs(s[i])*p['width']/2+abs(u[i])*p['depth']/2 for i in range(3)];return [min(p['a'][i],p['b'][i])-ext[i]for i in range(3)],[max(p['a'][i],p['b'][i])+ext[i]for i in range(3)]
for p in parts:
 lo,hi=bounds(p);p['bounds_min']=lo;p['bounds_max']=hi
 assert not (hi[0]>-54 and lo[0]<-8 and hi[2]>398 and lo[2]<466 and hi[1]>78 and lo[1]<84),p['name']
 # No newly added above-floor geometry in the axial walking surface.
 assert not (hi[0]>-4 and lo[0]<4 and hi[1]>78.001 and lo[1]<83.739),p['name']
# Exact member footprints, rather than axis-aligned bounds of oblique trusses.
def vertices(q):
 if q['kind']=='box':
  lo,hi=q['min'],q['max'];a=[(lo[0]+hi[0])/2,lo[1],(lo[2]+hi[2])/2];b=[a[0],hi[1],a[2]];width=hi[2]-lo[2];depth=hi[0]-lo[0]
 else:a,b,width,depth=q['a'],q['b'],q['width'],q['depth']
 t=[b[i]-a[i]for i in range(3)];n=math.sqrt(sum(v*v for v in t));t=[v/n for v in t];ref=[0,0,1]if abs(t[2])<.95 else[1,0,0];d=sum(t[i]*ref[i]for i in range(3));sv=[ref[i]-t[i]*d for i in range(3)];n=math.sqrt(sum(v*v for v in sv));sv=[v/n for v in sv];u=[t[1]*sv[2]-t[2]*sv[1],t[2]*sv[0]-t[0]*sv[2],t[0]*sv[1]-t[1]*sv[0]]
 return [[pt[i]+sv[i]*w+u[i]*h for i in range(3)]for pt in[a,b]for w,h in[(-width/2,-depth/2),(width/2,-depth/2),(width/2,depth/2),(-width/2,depth/2)]]
from shapely.geometry import MultiPoint
hull=Polygon(json.load(open(R/'Game/data/hull_envelope.json'))['plan_xz_m'])
for q in parts:
 q['verts']=vertices(q);q['faces']=[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
 footprint=MultiPoint([(v[0],v[2])for v in q['verts']]).convex_hull
 assert footprint.difference(hull).area<.0001,(q['name'],footprint.difference(hull).area)
plan={'schema':'astraea.sunset_receiving_frame.v1','status':'COURT_AND_OUTER_VERGE_FRAME_CANDIDATE','parts':parts,'contact_interfaces':joints,'source_reactions_connected_via_retained_slab':reactions,'held_source_reactions':held,'retained_source_plan_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_pins':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [R/'Game/assets/models/SOL_D12_directory_09_entry001.glb',R/'Game/assets/models/SUNSET_ARCHITECTURE_lift_r003.glb',R/'Game/data/generated/structural_meshes.json']},'open_construction_hold':'SUNSET_INNER_VESPER_RECEIVING_HOLD','full_base_hold_closed':False,'scope':'Additive court/verge frame and four unconflicted inner reactions. Source slab contacts are geometric evidence, not primary hull-frame or structural capacity certification. Inner Vesper-band garden/street and two trellis reactions remain held.'}
(O/'RECEIVING_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print(json.dumps({'parts':len(parts),'reaction_feet':len(reactions),'held':held,'axial_stations':len(joints),'programme_intrusions':0}))
