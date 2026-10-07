"""Read-only source geometry review; writes only this independent QA directory."""
from pathlib import Path
import sys,json,hashlib,collections,datetime,math
sys.path.insert(0,'/workspace/scratch/375c2e438292/geometry-deps')
from shapely.geometry import Polygon,Point,LineString,MultiPoint,box
from shapely.ops import unary_union
Q=Path(__file__).resolve().parent; S=Q.parents[1]; W=S.parent; G=Path('/workspace/shared/astraea-godot-production-20261003'); C=next(q for q in Path(__file__).resolve().parents if (q/'catalogue_manifest.json').is_file())
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
PLANFILE=Path(sys.argv[1])if len(sys.argv)>1 else S/'SF_FULL_HOUSE_PLAN.json'
plan_bytes=(PLANFILE).read_bytes();plan_sha=hashlib.sha256(plan_bytes).hexdigest();p=json.loads(plan_bytes);w=read(G/'data/whole_ship_layout.json');cross=read(W/'residential-neighborhood-audit-20261007/ALL_1000_NEIGHBORHOOD_CROSSWALK.json')['records'];audit=read(W/'residential-neighborhood-audit-20261007/NEIGHBORHOOD_ALLOCATION_AND_COURT_AUDIT.json');geo=read(G/'data/generated/structural_meshes.json');spatial=read(G/'data/spatial_layout.json');hull=read(G/'data/architecture/HULL_BODY_SECTION_PROPOSAL.json');lux=read(G/'data/architecture/D17_LUXURY_HOUSES_PROPOSAL.json')
parts=p['parts']; name_counts=collections.Counter(r['name']for r in parts)
for i,r in enumerate(parts):r['_review_key']=r['name']+'#'+str(i)
parts_by={r['name']:r for r in parts}; eps=1e-6

def mesh_poly(r):
 v=r['verts'];yt=max(t[1] for t in v); polys=[]
 for f in r['faces']:
  if len(f)>=3 and all(abs(v[i][1]-yt)<eps for i in f):
   pp=Polygon([(v[i][0],v[i][2])for i in f]);
   if pp.area>eps:polys.append(pp)
 return unary_union(polys)
def shape(r):
 if r['kind']=='mesh':return mesh_poly(r),min(t[1]for t in r['verts']),max(t[1]for t in r['verts'])
 a=r['a'];b=r['b'];d=[b[i]-a[i]for i in range(3)];length=math.sqrt(sum(v*v for v in d));t=[v/length for v in d];ss=[0,0,1]if abs(t[2])<.95 else[1,0,0];dot=sum(ss[i]*t[i]for i in range(3));ss=[ss[i]-t[i]*dot for i in range(3)];ln=math.sqrt(sum(v*v for v in ss));ss=[v/ln for v in ss];u=[t[1]*ss[2]-t[2]*ss[1],t[2]*ss[0]-t[0]*ss[2],t[0]*ss[1]-t[1]*ss[0]]
 vs=[[p[i]+ss[i]*ww+u[i]*dd for i in range(3)]for p in[a,b]for ww,dd in[(-r['width']/2,-r['depth']/2),(r['width']/2,-r['depth']/2),(r['width']/2,r['depth']/2),(-r['width']/2,r['depth']/2)]]
 return MultiPoint([(v[0],v[2])for v in vs]).convex_hull,min(v[1]for v in vs),max(v[1]for v in vs)
shapes={r['_review_key']:shape(r)for r in parts}
floors={y:unary_union([shapes[r['_review_key']][0]for r in parts if r['kind']=='mesh'and r['category']=='floor'and abs(shapes[r['_review_key']][2]-y)<eps])for y in p['upper_datums']}
compiled={r['id']:unary_union([Polygon(t)for t in r['triangles']])for r in geo['regions']}

def pack_poly(q):return {'area_m2':round(q.area,6),'bounds_xz':list(q.bounds)if not q.is_empty else [],'components':len(q.geoms)if hasattr(q,'geoms')else (0 if q.is_empty else 1)}
# Preserve the entire actual census and membership, with old D17 replaced only for geometry tests.
allids=[i for hh in w['residential_houses']for i in hh['guest_envelope_source_indices']]; expected=[r for r in cross if r['house']==p['house_id']]; expectedids={r['source_envelope_index']for r in expected}; regular={r['source_envelope_index']for r in expected if r['production_lane']=='regular_source_supported'}; roomids={r['census_source_index']for r in p['rooms']}; luxby={r['source_envelope_index']:r for r in lux['replacements']}; standard17={r['source_envelope_index']:r for r in lux['replanned_standard_units']}; decky={r['deck']:r['floor_y']for r in w['decks']}
identity={'all_source_records':len(cross),'all_source_indices_exact':sorted(r['source_envelope_index']for r in cross)==list(range(1000)),'membership_unique_complete':len(allids)==len(set(allids))==1000,'upper_units':sum('upper_house' in r['house']for r in cross),'independent_D04_units':sum(r['deck']=='D04'for r in cross),'house_units':len(expected),'house_membership_exact':set(p['source_house_membership']['guest_envelope_source_indices'])==expectedids,'regular_source_interior_count':len(p['rooms']),'regular_source_class_counts':dict(collections.Counter(r['historical_class']for r in p['rooms'])),'regular_source_rest_bindings':sum(len(r.get('anchor_bindings',[]))for r in p['rooms']),'regular_source_interior_set_exact':regular==roomids,'reservation_count':len(expectedids-roomids),'VIP_reservation_set_exact':{r['source_envelope_index']for r in p['D17_replacement_reservations']}=={r['source_envelope_index']for r in expected if r['source_envelope_index']in luxby},'historical_front_candidates':sum(r['historical_large_court_front_candidate']=='starboard_forward_residential_court'for r in expected),'protected_installed_pilot_indices_outside_this_house':[i for i in [16,40]if i not in expectedids]}
# Exact slab footprint intersections at a datum, conservative beam volumes above the datum.
roomclashes=[]
for rr in cross:
 if rr['deck']not in ['D13','D14','D15','D16','D17']:continue
 i=rr['source_envelope_index'];y=decky[rr['deck']];poly=Polygon(luxby[i]['proposed_floor_boundary'])if i in luxby else Polygon(standard17[i]['proposed_floor_boundary'])if i in standard17 else box(rr['allocation_x'][0],rr['allocation_z'][0],rr['allocation_x'][1],rr['allocation_z'][1]);top=luxby[i]['proposed_external_roof_limit_y']if i in luxby else y+4.2
 for r in parts:
  q,a,b=shapes[r['_review_key']]
  if b<=y+eps or a>=top-eps:continue
  if q.intersects(poly):
   ar=q.intersection(poly).area
   if ar>eps:roomclashes.append({'source_index':i,'deck':rr['deck'],'part':r['name'],'category':r['category'],'plan_overlap_m2':round(ar,6),'vertical_interval':[round(a,5),round(b,5)],'test':'exact slab prism'if r['kind']=='mesh'else 'conservative beam envelope'})
temporary_sources={r['source_index']for r in p.get('temporary_unbuilt_specialty_frontage_guards',[])}
for clash in roomclashes:
 if clash['source_index']in temporary_sources and clash['part'].startswith(('StreetExposed','StreetTerminal')):clash['classification']='declared_temporary_barrier_at_unbuilt_specialty_front'
 elif clash['part'].startswith(('StreetExposedPost','StreetTerminalPost'))and clash['plan_overlap_m2']<=.001:clash['classification']='minor_boundary_post_contact_at_room_corner_not_door_marker'
 else:clash['classification']='unintended_volume_conflict'
# D12 lower programme transfer intrusions are not waived by real bearing contact.
progclashes=[]
for pp in w['programmes']:
 y=pp['floor_y'];nexty=min((r['floor_y']for r in w['decks']if r['floor_y']>y),default=118);poly=box(pp['allocation_x'][0],pp['allocation_z'][0],pp['allocation_x'][1],pp['allocation_z'][1])
 if pp['programme_key']in p['principal_court_reservation']['affected_programmes']:continue
 if y>106 or nexty<77.5:continue
 for r in parts:
  q,a,b=shapes[r['_review_key']]
  # Same-level flooring below datum is contact rather than intrusion. D18 historical allocations are relocated and excluded.
  if pp['deck']=='D18'or b<=y+eps or a>=nexty-.24-eps:continue
  ar=q.intersection(poly).area
  if ar>eps:progclashes.append({'programme':pp['programme_key'],'programme_name':pp['name'],'part':r['name'],'category':r['category'],'plan_overlap_m2':round(ar,6),'vertical_interval':[round(a,5),round(b,5)],'programme_interval':[y,nexty-.24],'test':'exact slab prism'if r['kind']=='mesh'else 'conservative beam envelope'})
contacts=[]
for c in p['contacts']:
 if 'point'not in c:continue
 x,y,z=c['point'];holders=[r['id']for r in geo['regions']if r['floor_y']==y and compiled[r['id']].covers(Point(x,z))];contacts.append({'receiver':c['receiver'],'point':c['point'],'actual_floor_owners':holders,'claimed_owner_present':c['existing_owner']in holders,'receiver_plan_contact_m2':round(sum(shapes[r['_review_key']][0].intersection(compiled[c['existing_owner']]).area for r in parts if r['name'].startswith(c['receiver']+'_')),6)})
# New top floors must not duplicate existing compiled top surfaces or fill protected voids.
floorconf=[];voidconf=[];coreconf=[]
for y,f in floors.items():
 deck=next(k for k,v in decky.items()if v==y)
 for r in geo['regions']:
  if r['floor_y']==y:
   ar=f.intersection(compiled[r['id']]).area
   if ar>eps:floorconf.append({'deck':deck,'owner':r['id'],'overlap_m2':round(ar,6)})
 for v in spatial['voids']:
  if deck in v['decks']:
   ar=f.intersection(Polygon(v['boundary'])).area
   if ar>eps:voidconf.append({'deck':deck,'void':v['id'],'overlap_m2':round(ar,6)})
 for c in w['longitudinal_vertical_core_reservations']:
  if deck in c['decks']:
   ar=f.intersection(box(c['x'][0],c['z'][0],c['x'][1],c['z'][1])).area
   if ar>eps:coreconf.append({'deck':deck,'core':c['id'],'overlap_m2':round(ar,6)})
# Internal new-floor duplication is distinct from old compiled-owner conflict.
newfloorconf=[]
newfs=[r for r in parts if r['kind']=='mesh'and r['category']=='floor']
for i,r in enumerate(newfs):
 q,a,y=shapes[r['_review_key']]
 for rr in newfs[i+1:]:
  qq,aa,yy=shapes[rr['_review_key']]
  if abs(y-yy)<eps:
   ar=q.intersection(qq).area
   if ar>eps:newfloorconf.append({'part_a':r['name'],'part_b':rr['name'],'floor_y':y,'overlap_m2':round(ar,6)})
# Body section remains constant between these datums, so current D12 inset is valid for the source frame.
hp=Polygon(next(r for r in hull['levels']if r['deck']=='D13')['inner_reservation_boundary']);hullconf=[]
for r in parts:
 q,a,b=shapes[r['_review_key']];ar=q.difference(hp).area
 if ar>eps:hullconf.append({'part':r['name'],'outside_inner_plan_m2':round(ar,6),'vertical_interval':[round(a,5),round(b,5)]})
cut=unary_union([Polygon(r['proposed_floor_boundary'])for r in p['D17_replacement_reservations']]);cutchecks=[]
for r in parts:
 if 'D17_OuterGardenGallery' in r['name'] or 'PrincipalCourtOpaqueCover' in r['name']:
  q,a,b=shapes[r['_review_key']];cutchecks.append({'part':r['name'],'VIP_overlap_m2':round(q.intersection(cut).area,6),'minimum_VIP_distance_m':round(q.distance(cut),6)})
# Source-floor component count is not path clearance; erode to expose narrow-only bridges.
connect=[]
for y,f in floors.items():
 for radius in [0,.3,.6]:
  q=f.buffer(-radius,join_style=2)if radius else f
  connect.append({'floor_y':y,'erosion_radius_m':radius,**pack_poly(q)})
# Verify exact source landing contact at first and last tread. This is geometry only, not a stair code certificate.
stairs=[]
for level,y in enumerate(p['upper_datums'][:-1]):
 for which,name,fy in [('bottom',f'Stair_{level}_0_0_0',y),('top',f'Stair_{level}_1_12_0',y+4.5)]:
  r=parts_by.get(name)
  if not r:stairs.append({'level':level,'landing':which,'status':'tread name not found'});continue
  q=shapes[r['_review_key']][0];other=[shapes[t['_review_key']][0]for t in parts if t['kind']=='mesh'and t['category']=='floor'and abs(shapes[t['_review_key']][2]-fy)<eps];land=unary_union(other);stairs.append({'level':level,'landing':which,'tread':name,'floor_y':fy,'floor_distance_m':round(q.distance(land),6),'touch_or_overlap':q.distance(land)<eps,'tread_bounds':list(q.bounds)})
# Source entry markers are point-contact evidence only, not door motion/cart turning acceptance.
entry_checks=[]
for rr in p['rooms']:
 x,z=rr['historical_door_marker_xz'];fy=rr['floor_y'];pt=Point(x,z)
 entry_checks.append({'source_index':rr['census_source_index'],'floor_y':fy,'door_marker_xz':[x,z],'new_public_floor_covers_marker':floors[fy].buffer(1e-6).covers(pt)})
# Commons outer edges: sample exact exposed source rim at0.5m intervals and look for source guards/enclosure at handrail elevation.
commons_guard=[];cp=box(63,-384,97,-356)
for y in p['upper_datums'][1:]:
 receivers=unary_union([shapes[r['_review_key']][0]for r in parts if r['category']in['guard','enclosure']and shapes[r['_review_key']][1]<=y+1.1+eps and shapes[r['_review_key']][2]>=y+1.1-eps]);rim=floors[y].boundary.intersection(cp.boundary);missing=[]
 lines=[rim]if rim.geom_type=='LineString'else list(getattr(rim,'geoms',[]));sampled=0
 for line in lines:
  if line.geom_type!='LineString':continue
  n=max(1,math.ceil(line.length/.5))
  for j in range(n):
   pt=line.interpolate((j+.5)/n,normalized=True);sampled+=1
   if receivers.distance(pt)>.06:missing.append([round(pt.x,3),round(pt.y,3)])
 commons_guard.append({'floor_y':y,'exposed_outer_rim_length_m':round(rim.length,3),'sampled_points':sampled,'unguarded_samples':len(missing),'first_unguarded_points_xz':missing[:6]})
fixture_contacts=[]
for ll in p['lights']:
 rr=next((r for r in parts if r['name']==ll['name']+'_body_0'),None)
 if not rr:continue
 q,a,b=shapes[rr['_review_key']];receivers=[]
 for r in parts:
  if r['category']not in['support','pier','transition','ceiling','ceiling_rib','enclosure','architecture','fixture_mount']:continue
  qq,aa,bb=shapes[r['_review_key']]
  if bb<a-eps or aa>b+eps:continue
  if qq.intersects(q):receivers.append(r['name'])
 fixture_contacts.append({'fixture':ll['name'],'receiving_part_candidates':receivers,'geometric_receiving_contact_found':bool(receivers),'scope':'Conservative projected prism contact; no fastening/load certification'})
# Exact reference reading/inspection record; image contents were personally inspected in this review.
refs=[C/'references/dense/image(20261002-001051).png',C/'references/botanical/atrium_reference.png',W/'reference-window-privacy-20261006/515c9925-2338-485c-866d-c5378a82acb4(2).png'];doc=G/'docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx'
inputs=[PLANFILE,S/'source/plan_house.py',G/'data/whole_ship_layout.json',G/'data/generated/structural_meshes.json',G/'data/spatial_layout.json',G/'data/architecture/D17_LUXURY_HOUSES_PROPOSAL.json',G/'data/architecture/HULL_BODY_SECTION_PROPOSAL.json',W/'residential-neighborhood-audit-20261007/ALL_1000_NEIGHBORHOOD_CROSSWALK.json']
out={'schema':1,'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Independent source-only review of full147-unit starboard-forward house; no Game/Catalogue writes or Godot/Blender jobs. Beam tests are conservative source envelopes; no load certification or engine acceptance.','source_sha256':{str(x):(plan_sha if x==PLANFILE else sha(x))for x in inputs},'design_documents':{'path':str(doc),'sha256':sha(doc),'personally_read_chapters':[5,6,32],'actual_DOCX_paragraph_ranges':[[253,284],[1356,1406]]},'references_personally_pixel_inspected':[{'path':str(x),'sha256':sha(x)}for x in refs],'identity_checks':identity,'receiving_contacts':contacts,'room_volume_conflicts':roomclashes,'other_programme_volume_conflicts':progclashes,'duplicate_part_names':[{'name':n,'count':c}for n,c in name_counts.items()if c>1],'new_floor_owner_overlaps':newfloorconf,'compiled_floor_overlaps':floorconf,'protected_void_overlaps':voidconf,'closed_core_floor_overlaps':coreconf,'inner_hull_plan_conflicts':hullconf,'D17_luxury_subtraction_checks':cutchecks,'floor_connectivity_screen':connect,'stair_floor_receiving_contact':stairs,'ordinary_room_entry_marker_contacts':entry_checks,'commons_outer_guard_screen':commons_guard,'fixture_receiving_contact_screen':fixture_contacts,'privacy_acceptance':'NOT_ESTABLISHED. Opposite/public views must never reveal suite interiors. r010 isolated128-case proof does not validate this full house; clear inward/tinted opaque outward source profile, installed full-house sightlines, seated/standing/oblique/cross-level and effects-off checks remain separate.','declared_temporary_specialty_barrier_count':len(temporary_sources),'declared_receiving_interface_blocks':p.get('receiving_interface_blocks',[]),'no_completion_claims':['83 source room instances are not 147 completed units','47 specialty plus17 VIP remain explicit geometry reservations','76 historical outward-front candidates are not current installed windows','No invented species occupancy','No standalone3-suite adoption'],'manual_findings':[{'id':'reference_interpretation','status':'reviewed','finding':'Pixel references guide deep framed outward views, inhabited multi-level planting and warm modeled thresholds. Their visible opposite-room interiors do not override the stricter current privacy requirement.'},{'id':'full_house_not_adopted','status':'open','finding':'No full147-unit completion, full-house privacy, collision, loaded-cart route, source structural load or final art acceptance is established by this review.'}]}
(Q/'GEOMETRY_REVIEW.json').write_text(json.dumps(out,indent=2)+'\n')
summary={'plan_sha256':plan_sha,'identity':identity,'actual_bearing_contacts':sum(c['claimed_owner_present']for c in contacts),'room_conflicts':len(roomclashes),'room_conflict_classification':dict(collections.Counter(r['classification']for r in roomclashes)),'programme_conflicts':len(progclashes),'floor_duplicates':len(floorconf),'new_floor_duplicates':len(newfloorconf),'duplicate_part_names':sum(c>1 for c in name_counts.values()),'protected_void_conflicts':len(voidconf),'closed_core_conflicts':len(coreconf),'hull_conflicts':len(hullconf),'stair_contact_failures':[s for s in stairs if not s.get('touch_or_overlap')],'programme_names':dict(collections.Counter(r['programme_name']for r in progclashes)),'hull_parts':hullconf[:10],'entry_marker_failures':sum(not r['new_public_floor_covers_marker']for r in entry_checks),'commons_unguarded_samples':sum(r['unguarded_samples']for r in commons_guard),'fixtures_without_source_receiver':sum(not r['geometric_receiving_contact_found']for r in fixture_contacts)}
summary.update(status='SOURCE_REVIEW_ONLY_NOT_ADOPTED',review_file=str(Q/'GEOMETRY_REVIEW.json'),declared_temporary_specialty_fronts=len(temporary_sources),declared_support_blocks=p.get('receiving_interface_blocks',[]),unexpected_room_volume_conflicts=[r for r in roomclashes if r['classification']=='unintended_volume_conflict'],privacy_acceptance='UNTESTED_FULL_HOUSE',load_certification=False,engine_or_collision_acceptance=False)
(Q/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
