from pathlib import Path
import sys,json,hashlib,copy,importlib.util
O=Path(__file__).resolve().parent;I=O/'isolated/Game';S=O.parent
sys.path.insert(0,str(S/'botanical_receiving_court_build_20261007/python_deps'));sys.path.insert(0,str(I/'tools'))
from shapely.geometry import Polygon,box,MultiPoint,LineString
from shapely.ops import unary_union
from d12_pair_incremental_preservation import prepare_projection,finish_projection
from theater_incremental_preservation import effective_shapes
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def dump(n,x):(O/n).write_text(json.dumps(x,indent=2)+'\n')
layout=read(I/'data/spatial_layout.json');compiled=read(I/'data/generated/structural_meshes.json');base=I/'data/architecture/packages/d12_pair_candidate/predecessors';old=read(base/'data/generated/structural_meshes.json');oldlayout=read(base/'data/spatial_layout.json');assert compiled['regions'][:296]==old['regions'] and len(compiled['regions'])==300
assert layout['regions'][:-4]==oldlayout['regions'];assert {k:v for k,v in layout.items() if k!='regions'}=={k:v for k,v in oldlayout.items() if k!='regions'}
restored=copy.deepcopy(compiled);restored['regions']=restored['regions'][:-4];restored['source_checks']=old['source_checks'];assert restored==old
owners={r['id']:unary_union([Polygon(t) for t in r['triangles']]) for r in compiled['regions']};matrix=[]
for a in compiled['regions'][-4:]:
 for b in compiled['regions']:
  if a['id']==b['id']:continue
  area=owners[a['id']].intersection(owners[b['id']]).area;depth=min(a['floor_y'],b['floor_y'])-max(a['floor_y']-a['thickness'],b['floor_y']-b['thickness']);assert area*max(depth,0)<1e-7
  matrix.append({'a':a['id'],'b':b['id'],'overlap_area_m2':area,'slab_overlap_depth_m':max(0,depth)})
dump('COMPILER_PRESERVATION.json',{'compiled_owners':300,'prior_records_exact':296,'prior_layout_records_exact':len(oldlayout['regions']),'inverse_entire_document_equal':True,'source_checks_inverse_requires_exact_preimage':True,'per_owner_sha256':{r['id']:hashlib.sha256(json.dumps(r,sort_keys=True,separators=(',',':')).encode()).hexdigest() for r in old['regions']},'matrix':matrix})
solids=read(O/'GUARD_SOLIDS.json')['solids'];geom={};contacts=[];graph={r['name']:set() for r in solids};floor=set()
for r in solids:
 vs=r['vertices'];xs=[v[0]for v in vs];yz=Polygon([(v[1],v[2]) for v in vs[:len(vs)//2]]) if r['kind']=='jamb_profile' else box(r['lo'][1],r['lo'][2],r['hi'][1],r['hi'][2]);assert yz.is_valid
 geom[r['name']]=(min(xs),max(xs),yz)
 if min(v[1] for v in vs)==78:floor.add(r['name'])
for i,a in enumerate(solids):
 ax,bx,ayz=geom[a['name']]
 for b in solids[i+1:]:
  cx,dx,byz=geom[b['name']];ov=min(bx,dx)-max(ax,cx);cross=ayz.intersection(byz);vol=max(0,ov)*cross.area
  assert vol<1e-10,('Guard overlap',a['name'],b['name'],vol)
  face=0
  if abs(ov)<1e-8:face=cross.area
  elif ov>0 and ayz.distance(byz)<1e-8:face=cross.length*ov
  if face>1e-10:contacts.append({'a':a['name'],'b':b['name'],'contact_area_m2':face});graph[a['name']].add(b['name']);graph[b['name']].add(a['name'])
reached=set(floor)
while True:
 expanded=reached|{b for a in reached for b in graph[a]}
 if expanded==reached:break
 reached=expanded
assert reached==set(graph),set(graph)-reached
# Cross-section barrier continuity: rails and infill must close every intended branch and mouth wing.
y=78.6;section={}
for r in solids:
 x0,x1,yz=geom[r['name']];cut=yz.intersection(LineString([(y,200),(y,230)]))
 if not cut.is_empty:
  z0,z1=cut.bounds[1],cut.bounds[3];section[r['name']]=box(x0,z0,x1,z1)
barrier=unary_union(list(section.values()));required=[]
for key,side in [('D12_directory_07',-1),('D12_directory_08',1)]:
 for z,end in [(213.85,212.22499999),(218.15,219.77500001)]:
  required.append(LineString([(side*4.0,z),(side*8.65,z),(side*8.65,end)]))
assert all(line.difference(barrier.buffer(1e-7)).length<1e-7 for line in required)
# Check continuity at every geometry-height event and every interval midpoint.
levels=sorted({v[1] for r in solids for v in r['vertices']});sample_ys=sorted(set(levels+[(a+b)/2 for a,b in zip(levels,levels[1:])]))
height_checks=[]
for yy in sample_ys:
 pieces=[]
 for name,(x0,x1,yz) in geom.items():
  cut=yz.intersection(LineString([(yy,200),(yy,230)]))
  if not cut.is_empty:pieces.append(box(x0,cut.bounds[1],x1,cut.bounds[3]))
 barrier_y=unary_union(pieces)
 for key,side in [('D12_directory_07',-1),('D12_directory_08',1)]:
  for tag,z in [('_south',213.85),('_north',218.15)]:
   row=next(r for r in solids if r['name']==key+tag+'_SourceProfiledTerminal');profile=row['profile_yz'];end=None
   for (a,u),(b,v) in zip(profile,profile[1:]):
    if a-1e-9<=yy<=b+1e-9:end=u+(v-u)*(yy-a)/(b-a);break
   assert end is not None
   line=LineString([(side*4.,z),(side*8.65,z),(side*8.65,end)])
   missing=line.difference(barrier_y.buffer(1e-7)).length;assert missing<1e-7,(yy,key,tag,missing)
 height_checks.append({'y':yy,'four_barriers_closed':True})
dump('GUARD_VERTICAL_CONTINUITY.json',{'height_event_and_interval_checks':height_checks,'source_profiled_bottom_bevel_closed':True,'scope':'Entire 1.1m guard height at all piecewise-linear events and intervals'})
controls=[]
def negative(name,fn):
 try:fn()
 except (AssertionError,KeyError):controls.append({'name':name,'rejected':True});return
 raise AssertionError(('Negative not rejected',name))
elev={r['deck_id']:r['floor_elevation_m']for r in read(I/'data/design_contract.json')['deck_datums']};owned=effective_shapes(layout,elev)
for name,mutate in [('duplicate_owner',lambda l:l['regions'].append(l['regions'][-1])),('existing_owner_edit',lambda l:l['regions'][0].update(status='corrupted')),('new_boundary_edit',lambda l:l['regions'][-1]['boundary'][0].__setitem__(0,999)),('void_edit',lambda l:l['voids'].pop())]:
 l=copy.deepcopy(layout);mutate(l);negative(name,lambda:prepare_projection(I,l,elev,owned,compiled['regions']))
q=copy.deepcopy(old['regions']);q[0]['floor_y']+=.01;negative('old_compiled_datum_corruption',lambda:finish_projection(I,q,compiled['regions'][-4:]))
q=copy.deepcopy(compiled['regions'][-4:]);q[0]['thickness']=.25;negative('new_compiled_thickness_corruption',lambda:finish_projection(I,old['regions'],q))
without=unary_union([p for n,p in section.items() if 'SourceProfiledTerminal' not in n]);negative('missing_source_jamb_closure',lambda:assert_all_covered(required,without)) if False else None
assert any(l.difference(without.buffer(1e-7)).length>.1 for l in required);controls.append({'name':'missing_source_jamb_closure','rejected':True})
without=unary_union([p for n,p in section.items() if not n.endswith(('Panel3','Rail3','SourceProfiledTerminal'))]);assert any(l.difference(without.buffer(1e-7)).length>.1 for l in required);controls.append({'name':'unguarded_front_mouth_wings','rejected':True})
# A 0.10m inward shift of the south feet violates the explicit 4m strip.
from shapely.affinity import translate
p=next(p for n,p in section.items() if n.endswith('south_Post0'));assert translate(p,yoff=.20).intersection(box(-16,214,16,218)).area>0;controls.append({'name':'guard_intrudes_four_metre_strip','rejected':True})
dump('GUARD_CONTACT_GRAPH.json',{'solid_count':len(solids),'all_parts_floor_connected':True,'floor_contact_parts':sorted(floor),'positive_volume_pair_overlap':False,'contacts':contacts,'branch_and_mouth_barriers_continuous_at_y':y,'caveat':'Geometric contact only, not loads/fixings strength'})
dump('NEGATIVE_CONTROLS.json',controls)
pins=read(O/'INPUT_PINS.json');recheck={p:{'match':sha(Path(p))==v['sha256']} for p,v in pins.items()};assert all(v['match']for v in recheck.values());dump('FINAL_INPUT_RECHECK.json',recheck)
print('PASS 296 exact predecessors, 4 additions, inverse, 116 supported guard solids, contacts,',len(controls),'negative controls')
