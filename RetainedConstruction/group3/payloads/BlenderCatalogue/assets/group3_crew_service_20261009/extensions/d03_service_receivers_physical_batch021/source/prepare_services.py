"""Five remaining D03 service receivers, with exact prior source preservation."""
from pathlib import Path
import json,copy,hashlib,math
import shapely
from shapely.geometry import Polygon,box,Point,MultiPoint
from shapely.ops import unary_union
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[4];EXT=HERE.parent
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
write=lambda f,q:f.write_text(json.dumps(q,indent=2)+'\n')
rows=[('breakroom','breakroom_receiving_batch008',['BREAKROOM_COLLAR.json','BREAKROOM_REUSED_BRANCH.json'],'CREW_STREET_BREAKROOM_PATCH.json','BREAKROOM_MISSING_SUPPORT_PROPOSAL.json','D03_directory_02',[54,12,-420],math.pi/2),('dining','dining_receiving_batch009',['DINING_COLLAR.json','DINING_REUSED_BRANCH.json'],'CREW_STREET_DINING_PATCH.json','DINING_MISSING_SUPPORT_PROPOSAL.json','D03_directory_04',[54,12,-216],math.pi/2),('care','care_dogleg_batch010',['CARE_DOGLEG.json','CARE_REUSED_BRANCH.json'],'CREW_STREET_CARE_PATCH.json','CARE_MISSING_SUPPORT_PROPOSAL.json','D03_directory_09',[-54,12,422],-math.pi/2),('recreation','recreation_receiving_batch011',['RECREATION_RECEIVER.json'],'CREW_STREET_RECREATION_PATCH.json','RECREATION_MISSING_SUPPORT_PROPOSAL.json','D03_directory_07',[-54.5,12,216],-math.pi/2),('briefing','briefing_receiving_batch012',['BRIEFING_RECEIVER.json'],'CREW_STREET_BRIEFING_PATCH.json','BRIEFING_MISSING_SUPPORT_PROPOSAL.json','D03_directory_10',[54.5,12,216],math.pi/2)]
for _,folder,*_ in rows:
 for line in(EXT/folder/'SHA256SUMS.txt').read_text().splitlines():h,f=line.split('  ',1);assert sha(EXT/folder/f)==h,f
paths=[]
for _,folder,files,patch,floor,*_ in rows:paths.extend([EXT/folder/'source'/f for f in files+[patch,floor]]);paths.append(EXT/folder/'SHA256SUMS.txt')
paths.extend([ROOT/'BlenderCatalogue/assets/group3_crew_service_20261009/source/CREW_STREETS.json',ROOT/'Game/data/generated/structural_meshes.json',ROOT/'Game/data/generated/received_structural_meshes.json',ROOT/'Game/data/architecture/REMAINING_BATCH_FLOORS.json',ROOT/'Game/data/architecture/received_sections.json',ROOT/'Game/data/architecture/crew_batch/runtime_manifest.json',ROOT/'Game/scripts/service_door.gd',ROOT/'Game/assets/models/AST-STF-008.glb'])
pins={str(f.relative_to(ROOT)):sha(f)for f in paths};base=dict(schema=1,family='group3_crew_service_20261009',material_contract='retained_lower_staff_network',source_pins=pins,automatic_runtime_adoption=False,authoritative_identity_map=None,registered_berths_added=0)
for i in range(48,52):assert not any(q['catalogue_id']==f'AST-STF-G3-{i:03d}'for q in json.load(open(ROOT/'BlenderCatalogue/catalogue_manifest.json'))['assets'])
def shape(q):
 if'boundary'in q:return Polygon(q['boundary'],q['holes'])
 if'vertices_godot'in q:return MultiPoint([(v[0],v[2])for v in q['vertices_godot']]).convex_hull
 a=q['aabb'];return box(a[0],a[4],a[1],a[5])
def yr(q):
 if'y'in q:return q['y']
 if'vertices_godot'in q:return[min(v[1]for v in q['vertices_godot']),max(v[1]for v in q['vertices_godot'])]
 return q['aabb'][2:4]
def prism(out,name,g,lo,hi,role,category,cell):
 lo=round(lo,6);hi=round(hi,6)
 if hi-lo<.000001:return
 g=shapely.set_precision(g,grid_size=.000001)
 for i,p in enumerate(shapely.get_parts(g)):
  if p.geom_type!='Polygon'or p.area<1e-10:continue
  out.append(dict(name=name+'_'+str(i),boundary=list(p.exterior.coords)[:-1],holes=[list(r.coords)[:-1]for r in p.interiors],triangles=[list(t.exterior.coords)[:3]for t in shapely.constrained_delaunay_triangles(p).geoms],y=[lo,hi],role=role,category=category,batch_cell=cell))
receivers=[];fixtures=[];gates=[];selections=[];requests=[];patches=[]
for name,folder,files,patch,floor,programme,at,yaw in rows:
 for f in files:
  p=json.load(open(EXT/folder/'source'/f));receivers.extend(p['parts']);fixtures.extend(p['fixtures'])
 patches.extend(json.load(open(EXT/folder/'source'/patch))['parts'])
 f=json.load(open(EXT/folder/'source'/floor));requests.extend(Polygon(q['boundary'],q['holes'])for q in f['polygons'])
 x,z=(-57 if at[0]<0 else 57),at[2];selections.append(box(x-2,z-12,x+2,z+12))
 gates.append(dict(name=name+'_service_entry',programme_key=programme,position=at,yaw=yaw,persistent_id=None,original_room_or_header_modified=False,frame_outside_original_2650mm_header=name in['recreation','briefing']))
selection=unary_union(selections);old=json.load(open(ROOT/'BlenderCatalogue/assets/group3_crew_service_20261009/source/CREW_STREETS.json'));street=[]
# Exact patch semantics replace their old cell only inside the selected source;
# all other first-street source geometry remains unchanged and uninstalled.
omitted_names={q['name']for _,folder,_,patch,*_ in rows for q in json.load(open(EXT/folder/'source'/patch))['original_semantic_parts']}
for q in old['parts']:
 if q['name']in omitted_names:continue
 g=shape(q).intersection(selection)
 if g.is_empty:continue
 for name,folder,files,patch,floor,programme,at,yaw in rows:
  p=json.load(open(EXT/folder/'source'/patch));opening=p['opening'];a=opening['wall_x'];z=opening['clear_z'];y=opening['clear_y']
  if yr(q)[0]<y[1]and yr(q)[1]>y[0] and 'wall'in q['category']:g=g.difference(box(a[0]-.001,z[0],a[1]+.001,z[1]))
 prism(street,q['name']+'_Selected',g,*yr(q),q['role'],q['category'],q['batch_cell'])
for q in patches:
 g=shape(q).intersection(selection)
 if not g.is_empty:prism(street,q['name']+'_RetainedPatch',g,*yr(q),q['role'],q['category'],q['batch_cell'])
fixtures.extend(q for q in old['fixtures']if selection.covers(Point(q['position'][0],q['position'][2])))
requests.extend(Polygon(q['boundary'],q['holes']).intersection(selection)for q in old['route_shape'])
def gate_rect(q,x0,x1,z0,z1):
 x,y,z=q['position'];c=math.cos(q['yaw']);s=math.sin(q['yaw']);return Polygon([(x+c*a+s*b,z-s*a+c*b)for a,b in[(x0,z0),(x1,z0),(x1,z1),(x0,z1)]])
# New frame cuts apply only to new receiver/street derivatives, never rooms.
cut=unary_union([gate_rect(q,-1.382,1.382,-.182,.182)for q in gates]);fitted=[]
for q in receivers+street:
 if'vertices_godot'in q:
  assert shape(q).intersection(cut).area<1e-10,q['name'];fitted.append(copy.deepcopy(q));continue
 lo,hi=yr(q);levels=sorted({round(v,6)for v in[lo,hi,*[v for v in[14.822]if lo<v<hi]]})
 for a,b in zip(levels,levels[1:]):prism(fitted,q['name']+'_FrameFit_'+str(a),shape(q).difference(cut)if a<14.822 else shape(q),a,b,q['role'],q['category'],q.get('batch_cell','receiver'))
receivers=[q for q in fitted if q['category']!='street_selection_only'];infills=[]
for q in gates:
 for suffix,x0,x1,lo in [('Left',-1.8,-1.38,12),('Right',1.38,1.8,12),('Head',-1.38,1.38,14.82)]:
  g=gate_rect(q,x0,x1,-.18,.18);hi=15.2;levels=sorted({round(v,6)for v in[lo,hi,*[v for p in fitted for v in yr(p)if lo<v<hi]]})
  for a,b in zip(levels,levels[1:]):
   fixed=unary_union([shape(p)for p in fitted if yr(p)[0]<b and yr(p)[1]>a]);prism(infills,q['name']+suffix+str(a),g.difference(fixed),a,b,'staff_white_paint','door_receiver',q['name'])
for q in fixtures:q.update(color=[.78,.88,1],energy=.9,range_m=8,runtime_calibration='Same first-pass supported staff-task profile as batch013/018; not final photometry')
write(HERE/'source/D03_SERVICE_ARCHITECTURE.json',dict(base,catalogue_id='AST-STF-G3-048',parts=fitted,fixtures=fixtures,selected_source_bounds=[list(q.bounds)for q in selections],existing_room_sources_unchanged=True))
write(HERE/'source/D03_SERVICE_FRAME_INFILLS.json',dict(base,catalogue_id='AST-STF-G3-049',parts=infills,fixtures=[],door_bindings=gates))
existing=[]
for f in ['Game/data/generated/structural_meshes.json','Game/data/generated/received_structural_meshes.json','Game/data/architecture/REMAINING_BATCH_FLOORS.json']:existing.extend(json.load(open(ROOT/f))['regions'])
previous=unary_union([Polygon(t)for q in existing if q['deck']=='D03'for t in q['triangles']]);prior=[]
for folder,file in [('d03_remaining_receivers_batch013','MISSING_ONLY_FLOOR_PATCH.json'),('labelled_crew_bank_batch014','BANK_MISSING_ONLY_FLOOR.json'),('fore_starboard_clinical_batch018','FORE_MISSING_ONLY_FLOORS.json'),('port2_clinical_physical_batch016','PORT2_MISSING_ONLY_FLOORS.json'),('starboard3_private_landings_batch019','STARBOARD3_MISSING_FLOORS.json')]:
 f=EXT/folder/'source'/file;p=json.load(open(f));pins[str(f.relative_to(ROOT))]=sha(f)
 for q in p['parts']:
  if yr(q)[1]==12:prior.append(shape(q))
request=unary_union(requests).buffer(.14,join_style=2);missing=request.difference(previous).difference(unary_union(prior));floors=[]
prism(floors,'D03FiveServicesMissingFloor',missing,11.76,12,'staff_floor','floor','D03')
write(HERE/'source/D03_SERVICE_MISSING_FLOOR.json',dict(base,catalogue_id='AST-STF-G3-050',parts=floors,fixtures=[],new_floor_m2=missing.area,original_or_prior_floor_overlaid=False))
contract=dict(base,parent_handoff_commit='b707db9ba47d42185c2f9b2c1373f800a8264de1',door_bindings=gates,fixtures=fixtures,programmes=[r[5]for r in rows],new_floor_m2=missing.area,source_room_header_and_furniture_unchanged=True,all_source_originals_and_D01_D04_preserved=True,full_400_berth_roster_or_species_loaded_cart_primary_engineering_or_final_acceptance=False)
write(HERE/'source/D03_SERVICE_CONTRACT.json',contract);print(json.dumps(dict(receivers=5,parts=len(fitted),infills=len(infills),fixture_profiles=len(fixtures),new_floor_m2=missing.area)))
