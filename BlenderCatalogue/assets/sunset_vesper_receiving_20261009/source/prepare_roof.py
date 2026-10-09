from pathlib import Path
import json,hashlib,math,sys,copy
sys.path.insert(0,'/workspace/shared/astraea_python_deps')
from shapely.geometry import Polygon,MultiPoint,box
R=Path(__file__).resolve().parents[4];O=R/'BlenderCatalogue/assets/sunset_vesper_receiving_20261009';(O/'source').mkdir(parents=True,exist_ok=True)
I=O/'ROOF_CONTACT_INPUT.json'
assert I.exists(),'Retained roof-contact input required'
inp=json.load(open(I));h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for p,sha in inp['source_hashes'].items():assert h(R/p)==sha
parts=copy.deepcopy(inp['candidate_parts'])
for q in parts:q['name']=q['name'].replace('Candidate_','SV_')
def cube(name,lo,hi,role):parts.append({'name':name,'kind':'box','min':lo,'max':hi,'role':role})
def beam(name,a,b,width,depth,role):parts.append({'name':name,'kind':'beam','a':a,'b':b,'width':width,'depth':depth,'role':role})
# Complete street receiving outside Vesper; retain the previously built x−15/−28 forward collectors.
segments=[(-44,250.5,310),(-44,310,350),(-44,350,397.5)]+[(x,466.5,480)for x in[-44,-28,-15]]+[(x,480,482.2 if x==-44 else 483)for x in[-44,-28,-15]]
for i,(x,a,b)in enumerate(segments):
 beam(f'SV_InnerCollector_{i}_Top',[x,83.41,a],[x,83.41,b],.6,.7,'inner_collector')
 beam(f'SV_InnerCollector_{i}_Bottom',[x,79,a],[x,79,b],.6,.6,'inner_collector')
 count=math.ceil((b-a)/12)
 for k in range(count):
  z0=a+(b-a)*k/count;z1=a+(b-a)*(k+1)/count
  beam(f'SV_InnerCollector_{i}_Diagonal_{k}',[x,79,z0],[x,83.41,z1],.3,.34,'inner_collector')
  cube(f'SV_InnerCollector_{i}_Web_{k}',[x-.15,78.7,z0-.15],[x+.15,83.76,z0+.15],'inner_collector')
def verts(q):
 if q['kind']=='mesh':return q['verts']
 if q['kind']=='box':
  lo,hi=q['min'],q['max'];a=[(lo[0]+hi[0])/2,lo[1],(lo[2]+hi[2])/2];b=[a[0],hi[1],a[2]];w=hi[2]-lo[2];d=hi[0]-lo[0]
 else:a,b,w,d=q['a'],q['b'],q['width'],q['depth']
 t=[b[i]-a[i]for i in range(3)];n=math.sqrt(sum(v*v for v in t));t=[v/n for v in t];ref=[0,0,1]if abs(t[2])<.95 else[1,0,0];dp=sum(t[i]*ref[i]for i in range(3));s=[ref[i]-t[i]*dp for i in range(3)];n=math.sqrt(sum(v*v for v in s));s=[v/n for v in s];u=[t[1]*s[2]-t[2]*s[1],t[2]*s[0]-t[0]*s[2],t[0]*s[1]-t[1]*s[0]]
 return [[p[i]+s[i]*ww+u[i]*hh for i in range(3)]for p in[a,b]for ww,hh in[(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]]
faces=[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
hull=Polygon(json.load(open(R/'Game/data/hull_envelope.json'))['plan_xz_m']);pads=0
for q in parts:
 q['verts']=verts(q);q.setdefault('faces',faces);q['bounds_min']=[min(v[i]for v in q['verts'])for i in range(3)];q['bounds_max']=[max(v[i]for v in q['verts'])for i in range(3)]
 footprint=MultiPoint([(v[0],v[2])for v in q['verts']]).convex_hull;assert footprint.difference(hull).area<1e-6,q['name']
 if q['role']=='plane_matched_roof_contact':
  pads+=1;contact=next(p for p in inp['contacts']if p['source']==q['source']and abs(p['x']-(q['bounds_min'][0]+q['bounds_max'][0])/2)<1e-6 and abs(p['z']-(q['bounds_min'][2]+q['bounds_max'][2])/2)<1e-6)
  aa,bb,cc=contact['plane_y_ax_bz_c'];tri=next(p for p in inp['source_main_triangles']if p['name']==q['source']);assert Polygon([(v[0],v[2])for v in tri['vertices']]).covers(footprint)
  assert all(abs(v[1]-(aa*v[0]+bb*v[2]+cc))<1e-6 for v in q['verts'][:4]);assert min(v[1]for v in q['verts'][4:])==83.46
 elif q['role']=='inner_collector':
  a,b=q['bounds_min'],q['bounds_max'];assert not (b[0]>-54 and a[0]<-8 and b[2]>398 and a[2]<466 and b[1]>78 and a[1]<84),q['name']
 else:assert q['bounds_min'][1]>=83.46 and q['bounds_max'][1]<=83.76
assert pads==47
plan={'schema':'astraea.sunset_vesper_receiving.v1','status':'ADDITIVE_ROOF_INTERFACE_CONSTRUCTION','parts':parts,'source_pins':inp['source_hashes'],'roof_contact_count':47,'roof_wedges_contacted':8,'edge_connected_trellis_shoes':2,'above_roof_grid_members':20,'inner_collector_segments':segments,'scope':'Narrow source-pinned receiver above unchanged Vesper crown.47 pads conform to upper roof planes;20 grid/shoe members connect the two off-roof trellises and bridge the outer roof margins to the court frame. Additional collectors complete the unconflicted paired street and aft inner receiving. No interior piers, source movement or primary hull/capacity certification.','allocation_exception':{'programme':'D12_directory_09','basis':'Additive contact only on verified eight roof upper faces and overhead grid within83.46..83.76; old room source retained. Whole room is not released for edits.','retained_roof_glb':inp['source_glb_sha256'],'nonroof_clearance_of_grid_min_m':83.46-inp['source_nonroof_max_y'],'below_roof_penetration':False},'full_ship_structural_acceptance':False,'visual_acceptance':False}
(O/'RECEIVING_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print({'parts':len(parts),'pads':47,'roof_wedges':8,'held_trellis_interfaces_resolved_geometrically':2,'source_pins':len(plan['source_pins'])})
