from pathlib import Path
import json,hashlib,sys,copy
sys.path.insert(0,'/workspace/shared/astraea_python_deps')
from shapely.geometry import Polygon,MultiPoint
from shapely.ops import unary_union
R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');O=R/'BlenderCatalogue/assets/family_celestial_receiving_20261009';(O/'source').mkdir(parents=True,exist_ok=True)
I=O/'ROOF_CONTACT_INPUT.json'
if not I.exists():I.write_bytes(Path('/tmp/celestial_receiver_candidate_analysis.json').read_bytes())
d=json.load(open(I));h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for p,sha in d['pins'].items():assert h(R/p)==sha
parts=[];faces=[[0,1,2,3],[7,6,5,4],[0,4,5,1],[1,5,6,2],[2,6,7,3],[3,7,4,0]]
def add(name,vs,role,source=None):
 q={'name':name,'kind':'mesh','verts':vs,'faces':faces,'role':role,'bounds_min':[min(v[i]for v in vs)for i in range(3)],'bounds_max':[max(v[i]for v in vs)for i in range(3)]}
 if source:q['source']=source
 parts.append(q)
for i,p in enumerate(d['pads']):
 tri=next(q for q in d['roof']if q['name']==p['source']);foot=Polygon([(v[0],v[2])for v in p['bottom']]);assert Polygon([(v[0],v[2])for v in tri['vertices']]).covers(foot)
 a,b,c=tri['plane_y_ax_bz_c'];assert all(abs(v[1]-(a*v[0]+b*v[2]+c))<1e-7 for v in p['bottom'])
 add('FC_RoofContact_'+str(i),p['bottom']+p['top'],'plane_matched_roof_contact',p['source'])
for p in d['grid']+[dict(d['receiver_shoe'],name='OffRoofInnerReceiverShoe')]:
 a,b=p['min'],p['max'];vs=[[a[0],a[1],a[2]],[b[0],a[1],a[2]],[b[0],a[1],b[2]],[a[0],a[1],b[2]],[a[0],b[1],a[2]],[b[0],b[1],a[2]],[b[0],b[1],b[2]],[a[0],b[1],b[2]]]
 add('FC_'+p['name'],vs,'off_roof_receiver_shoe'if p['name']=='OffRoofInnerReceiverShoe'else'overhead_grid')
assert len(parts)==43
hull=Polygon(json.load(open(R/'Game/data/hull_envelope.json'))['plan_xz_m']);slab=unary_union([Polygon([(v[0],v[2])for v in q['vertices']])for q in d['retained_slab_bottom_triangles']]);contacts=[]
for p in parts:
 foot=MultiPoint([(v[0],v[2])for v in p['verts']]).convex_hull;assert foot.difference(hull).area<1e-6
 if p['name'].startswith('FC_Long_')or p['role']=='off_roof_receiver_shoe':
  missing=foot.difference(slab.buffer(.00001)).area;assert missing<1e-6,p['name'];contacts.append(p['name'])
seen={0}
while True:
 n=len(seen)
 for i,a in enumerate(parts):
  if i in seen:continue
  if any(all(min(a['bounds_max'][k],parts[j]['bounds_max'][k])-max(a['bounds_min'][k],parts[j]['bounds_min'][k])>=-1e-7 for k in range(3))for j in list(seen)):seen.add(i)
 if n==len(seen):break
assert len(seen)==43
plan={'schema':'astraea.family_celestial_receiver.v1','status':'ADDITIVE_ABOVE_ROOF_RECEIVING_CONSTRUCTION','parts':parts,'source_pins':d['pins'],'roof_contact_count':25,'roof_wedges_contacted':8,'off_roof_receiver_shoes':1,'above_roof_grid_members':17,'source_frame_contact_count':35,'slab_contained_longitudinals_and_shoe':contacts,'allocation_exception':{'programme':'D12_directory_10','basis':'Contact pads on exact eight source upper roof faces, grid/shoe y83.46..83.76 only. Original room and interior volume unchanged. Whole room allocation is not released.','below_roof_penetration':False,'roof_clearance_m':d['clearance']['grid_to_roof_min'],'nonroof_clearance_m':d['clearance']['grid_to_nonroof_min']},'full_ship_structural_acceptance':False,'visual_acceptance':False,'scope':'43 source-pinned receiving members connect inner garden, paired street and one off-roof inner task receiver to existing frame above unchanged Celestial roof. Geometry construction only; final receiving, visual and primary hull acceptance remain open.'}
(O/'RECEIVING_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');(O/'CONTACT_REVIEW.json').write_text(json.dumps({'status':'PASS_BOUNDED_GEOMETRY','parts':43,'connected_members':len(seen),'pads':25,'roof_faces':8,'frame_intersections':d['frame_positive_volume_contacts'],'contained_slab_contact_members':contacts,'source_pins_verified':4,'clearance':d['clearance'],'capacity_and_visual_acceptance':False},indent=2)+'\n');print('FAMILY_ROOF_PLAN',len(parts),len(seen),len(contacts))
