#!/usr/bin/env python3
"""Build and verify SOURCE-ONLY additive stock contract. Standard library only.
Reads retained catalogue/Game. Writes only beside this file. No engine/import/render.
Run: python check_stock.py
"""
from geometry import *
from pathlib import Path
import hashlib, collections, re, ast, sys
sys.dont_write_bytecode=True
VERIFY_ONLY="--verify-only" in sys.argv
HERE=Path(__file__).resolve().parent
C=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
G=Path('/workspace/shared/astraea-godot-production-20261003')
PROPOSAL=HERE.parent/'reference_proposal'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):
 if VERIFY_ONLY:assert read(HERE/n)==json.loads(json.dumps(d)), 'Generated contract/report differs: '+n
 else:(HERE/n).write_text(json.dumps(d,indent=2)+'\n')
def unique(v):return list({tuple(round(x,9)for x in p):p for p in v}.values())
def inside_box(a,b,tol=EPS):return all(a[0][i]>=b[0][i]-tol and a[1][i]<=b[1][i]+tol for i in range(3))
def samples(a,b,step=.05):
 n=max(1,math.ceil(length(sub(b,a))/step));return [add(a,mul(sub(b,a),i/n))for i in range(n+1)]
def grid(lo,hi,step=.05):n=max(1,math.ceil((hi-lo)/step));return[lo+(hi-lo)*i/n for i in range(n+1)]
def floor_has(x,z,region):return any(bary_xz((x,0,z),[(p[0],0,p[1])for p in tri])is not None for tri in region['triangles'])
def part_from(p):
 v=[(x,z,-y)for x,y,z in p['vertices']];return{'name':p['name'],'vertices':v,'triangles':[tuple(v[i]for i in t)for t in p['triangles']],'bounds':bounds(v)}
PINS=read(PROPOSAL/'SCOPE_AND_SOURCE_PINS.json'); OLD=read(G/'data/architecture/GRAND_POOL_FIRST_PASS_RUNTIME.json'); SEC=read(C/'assets/grand_pool_orchard_section/source/connected_contract.json'); RSEC=read(G/'data/architecture/GRAND_POOL_SECTION_RUNTIME.json')
assert len(OLD['placements'])==51
assert sha(G/'data/architecture/GRAND_POOL_FIRST_PASS_RUNTIME.json')==PINS['current_furnishing_contract_sha256']
assert sha(C/'assets/grand_pool_orchard_section/source/connected_contract.json')==PINS['original_source_contract_sha256']
IDS=['AST-RTL-001','AST-RTL-004','AST-CUR-001','AST-CUR-002','AST-CUR-003','AST-LIB-006','AST-BOT-012_low','AST-BOT-003']
INV={p['catalogue_id']:p for p in PINS['source_inventory']if p['catalogue_id']in IDS};ASSETS={}
for k,p in INV.items():
 assert sha(C/p['source'])==p['source_sha256'],k
 assert sha(C/p['export'])==p['export_sha256'],k
 ASSETS[k]=read_glb(C/p['export']);p['actual_glb_bounds_y_up']=bounds(ASSETS[k]['vertices']);p['actual_glb_triangle_count']=len(ASSETS[k]['triangles']);p['scale_xyz']=[1,1,1]
PARTS=[part_from(p)for p in read(C/'assets/retail_display/qa/evaluated_source_geometry.json')['AST-RTL-001']['parts']];PM={p['name']:p for p in PARTS}
assert all(check_convex(p)for p in PARTS),'Source convexity is required for envelope SAT'
key=lambda t:tuple(sorted(tuple(round(x,5)for x in v)for v in t))
assert collections.Counter(key(t)for p in PARTS for t in p['triangles'])==collections.Counter(map(key,ASSETS['AST-RTL-001']['triangles'])),'Evaluated semantic triangles differ from actual GLB'
MAN=read(C/'assets/retail_display/AST-RTL-001.manifest.json');PATCHES={p['name']:p for p in MAN['support_patches']}
FLOOR=next(f for f in SEC['floor_regions']if f['id']=='D09_orchard_market_gallery');assert FLOOR==next(f for f in RSEC['floor_regions']if f['id']==FLOOR['id'])
SOIL=next(m for m in ASSETS['AST-BOT-012_low']['meshes']if m['name']=='POT_ContainedSoil');SOIL_Y=SOIL['bounds'][1][1]
SOURCE_FILES=[C/p[k]for p in INV.values()for k in ('source','export')]+[C/'assets/retail_display/qa/evaluated_source_geometry.json',C/'assets/retail_display/AST-RTL-001.manifest.json',C/'assets/retail_work/AST-RTL-004.manifest.json',C/'assets/library_contents/AST-LIB-006_upright_book_group.manifest.json',C/'assets/botanical_understory/AST-BOT-003.manifest.json',C/'assets/grand_pool_orchard_section/source/connected_contract.json',G/'data/architecture/GRAND_POOL_FIRST_PASS_RUNTIME.json',G/'data/architecture/GRAND_POOL_SECTION_RUNTIME.json',G/'data/architecture/cleaning_cart_contacts.json',G/'tests/validate_grand_pool_access.gd',G/'tests/validate_grand_pool_service_cart.gd',G/'tests/grand_pool_cart_probe.gd',G/'scripts/grand_pool_first_pass.gd',G/'scripts/grand_pool_section.gd',C/'assets/grand_pool_first_pass/source/placement_contract.json',PROPOSAL/'SCOPE_AND_SOURCE_PINS.json',PROPOSAL/'DISPLAY_CANDIDATE_SCREEN.json']
for record in PINS['source_inventory']:
 for field in ('source','export'):
  path=C/record[field];assert sha(path)==record[field+'_sha256'];SOURCE_FILES.append(path)
BEFORE={str(p):sha(p)for p in SOURCE_FILES}
def portable_pin_name(p):
 path=Path(p)
 for label,root in [('proposal',PROPOSAL),('catalogue',C),('game',G)]:
  if path.is_relative_to(root):return label+':'+str(path.relative_to(root))
 raise AssertionError('Unclassified retained input path: '+str(path))
PORTABLE_INPUTS={portable_pin_name(p):h for p,h in BEFORE.items()}
ADDITIONS=[];REPORTS=[];DISPLAYS=[];ISSUES=[];ALL_LOCAL={};ALL_WORLD={};LIGHTS=[]
def support_y(part):return PM[part]['bounds'][1][1]
def placement(name,asset,localpos,localyaw,display,support,role):
 pos=transform(localpos,display['position_xyz'],display['yaw_radians']);yaw=display['yaw_radians']+localyaw
 v=[transform(q,localpos,localyaw)for q in ASSETS[asset]['vertices']];wv=[transform(q,display['position_xyz'],display['yaw_radians'])for q in v]
 p=dict(name=name,asset=asset,retained_export=INV[asset]['export'],model_file=Path(INV[asset]['export']).name,position_xyz=pos,yaw_radians=yaw,scale_xyz=[1,1,1],support=support,host_display=display['name'],role=role,local_position_xyz=localpos,local_yaw_radians=localyaw,envelope_min_xyz=bounds(wv)[0],envelope_max_xyz=bounds(wv)[1],local_envelope=bounds(v))
 ALL_LOCAL[name]={'vertices':v,'triangles':[tuple(transform(q,localpos,localyaw)for q in t)for t in ASSETS[asset]['triangles']]};ALL_WORLD[name]=[p['envelope_min_xyz'],p['envelope_max_xyz']];ADDITIONS.append(p);return p

def support_record(p,display):
 v=ALL_LOCAL[p['name']]['vertices'];lo,hi=bounds(v);bottom=unique(q for q in v if abs(q[1]-lo[1])<EPS)
 if p['role']=='rosette':
  pot=next(x for x in ADDITIONS if x['name']==p['support']);potpos=pot['local_position_xyz'];support_tri=[tuple(add(q,potpos)for q in t)for t in SOIL['triangles']];sname='POT_ContainedSoil';patch=None
 else:
  patch=PATCHES.get(p['support']);sname=patch['physical_part']if patch else'lower_storage_tactile_floor';support_tri=PM[sname]['triangles']
 hits=[horizontal_hits(q,support_tri)for q in bottom];matched=[[(y,i,t)for y,i,t in h if abs(y-lo[1])<=EPS]for h in hits];assert all(matched),(p['name'],'unsupported contact',bottom)
 if patch:
  pb=bounds(patch['polygon_gltf_m']);margin=min(lo[0]-pb[0][0],pb[1][0]-hi[0],lo[2]-pb[0][2],pb[1][2]-hi[2]);assert margin>=-EPS,(p['name'],'full stock footprint outside declared patch',margin)
 else:margin=None
 hosthits=[s['name']for s in PARTS if convex_box_overlap(s,[lo,hi])];assert not hosthits,(p['name'],hosthits)
 assert inside_box([lo,hi],bounds(ASSETS['AST-RTL-001']['vertices'])),(p['name'],'outside full host display envelope')
 # The entire contact convex hull is supported: support plane's convex face fan,
 # or an axis-aligned rectangular patch. Bottom vertices include every mesh foot.
 tri_records={i:t for hm in matched for _,i,t in hm}
 rec=dict(item=p['name'],physical_support=sname,declared_support_patch=p['support'],contact_local_y=lo[1],contact_world_y=lo[1]+display['position_xyz'][1],contact_bottom_vertex_count=len(bottom),contact_bottom_vertices_local_xyz=bottom,matching_upward_source_triangle_indices=sorted(tri_records),matching_upward_source_triangles_local_xyz=[tri_records[i]for i in sorted(tri_records)],full_envelope_inside_declared_patch_margin_m=margin,host_source_convex_part_overlap_hits=hosthits,full_envelope_inside_display_bounds=True,back_clearance_m=lo[2]-PM['dark_inset_display_back']['bounds'][1][2],source_only=True)
 if patch:rec['support_patch_world_xyz']=[transform(q,display['position_xyz'],display['yaw_radians'])for q in patch['polygon_gltf_m']]
 if p['role']=='lower_case':rec['overhead_clearance_m']=PM['main_display_work_slab']['bounds'][0][1]-hi[1]
 elif p['role']=='main_case':rec['overhead_clearance_m']=PM['left_supported_display_shelf']['bounds'][0][1]-hi[1]
 elif p['role']=='curio':rec['overhead_clearance_m']=PM['right_supported_display_shelf']['bounds'][0][1]-hi[1]
 else:
  xs=sorted(set([lo[0],hi[0]]+[v[0]for s in PARTS for v in s['vertices']if lo[0]<=v[0]<=hi[0]]));zs=sorted(set([lo[2],hi[2]]+[v[2]for s in PARTS for v in s['vertices']if lo[2]<=v[2]<=hi[2]]));up=[]
  for x,z in itertools.product(xs,zs):
   for s in PARTS:
    if s['name']==sname:continue
    for t in s['triangles']:
     bc=bary_xz((x,0,z),t)
     if bc is None:continue
     yy=sum(t[k][1]*bc[k]for k in range(3))
     if yy>hi[1]+EPS:up.append(yy-hi[1])
  rec['overhead_clearance_at_source_profile_breakpoints_m']=min(up)if up else None
 return rec

# Paired bays use distinct curio IDs, lower compartments and gently varied book spacing.
SCHEMES=[
 ('market_display_0','AST-CUR-001',0,[-.78,-.12],[-.80,.88],.800,297),
 ('market_display_additional_0','AST-CUR-002',5,[-.79,-.15],[-.80,.03],.785,296),
 ('market_display_1','AST-CUR-002',-7,[-.76,-.10],[.03,.88],.810,298),
 ('market_display_additional_1','AST-CUR-003',0,[-.80,-.14],[-.80,.88],.795,295),
 ('market_display_2','AST-CUR-003',5,[-.77,-.10],[-.80,.03],.815,297),
 ('market_display_additional_2','AST-CUR-001',-5,[-.79,-.13],[.03,.88],.790,296)]
for si,(dn,curio,cyaw,bookxs,lowerxs,plantx,pyaw)in enumerate(SCHEMES):
 olddisplay=next((p for p in OLD['placements']if p['name']==dn),None)
 if olddisplay:display=dict(olddisplay);display['existing_preserved']=True
 else:
  cand=next(p for p in PINS['added_display_candidates']if p['name']==dn);display=dict(cand);display.update(retained_export=INV['AST-RTL-001']['export'],model_file='AST-RTL-001.glb',scale_xyz=[1,1,1],support=FLOOR['id'],existing_preserved=False,asset='AST-RTL-001');ADDITIONS.append(display);ALL_WORLD[dn]=[display['envelope_min_xyz'],display['envelope_max_xyz']]
 DISPLAYS.append(display);prefix=dn.replace('market_display','market_finish_stock');new=[]
 if not olddisplay:new.append(placement(prefix+'_main_case','AST-RTL-004',(-.4,support_y('main_display_work_slab'),.065),0,display,'main_display_left_patch','main_case'))
 else:
  original=next(p for p in OLD['placements']if p['name']=='market_goods_'+dn[-1]);local=rotate(sub(original['position_xyz'],display['position_xyz']),-display['yaw_radians']);name=original['name'];v=[transform(q,local,0)for q in ASSETS['AST-RTL-004']['vertices']];ALL_LOCAL[name]={'vertices':v,'triangles':[tuple(transform(q,local,0)for q in t)for t in ASSETS['AST-RTL-004']['triangles']]};ALL_WORLD[name]=[original['envelope_min_xyz'],original['envelope_max_xyz']]
  main={**original,'asset':'AST-RTL-004','support':'main_display_left_patch','role':'main_case','local_position_xyz':local,'local_yaw_radians':0,'local_envelope':bounds(v),'existing_preserved':True}
 new.append(placement(prefix+'_curio',curio,(.85,support_y('main_display_work_slab'),.065),math.radians(cyaw),display,'main_display_right_patch','curio'))
 for j,x in enumerate(bookxs):new.append(placement(prefix+'_books_'+str(j),'AST-LIB-006',(x,support_y('left_supported_display_shelf'),-.065+(si%3-1)*.006),math.radians((si%3-1)*2),display,'left_shelf_patch','book_group'))
 new.append(placement(prefix+'_low_pot','AST-BOT-012_low',(plantx,support_y('right_supported_display_shelf'),-.105),0,display,'right_shelf_patch','low_pot'))
 new.append(placement(prefix+'_rosette','AST-BOT-003',(plantx,support_y('right_supported_display_shelf')+SOIL_Y,-.05),math.radians(pyaw),display,prefix+'_low_pot','rosette'))
 for j,x in enumerate(lowerxs):new.append(placement(prefix+'_lower_case_'+str(j),'AST-RTL-004',(x,support_y('lower_storage_tactile_floor'),.045 if j==0 else .005),math.pi if (si+j)%2 else 0,display,'lower_storage_'+('left'if x<-.5 else'right'if x>.5 else'middle'),'lower_case'))
 localitems=new+([main]if olddisplay else[]);supports=[support_record(p,display)for p in localitems];pairhits=[];pot_pair_checks=[]
 for i,a in enumerate(localitems):
  for b in localitems[i+1:]:
   if not overlap(a['local_envelope'],b['local_envelope']):continue
   if {a['role'],b['role']}=={'rosette','low_pot'}:
    pp=a if a['role']=='low_pot'else b;plant=b if a['role']=='low_pot'else a;tris=ALL_LOCAL[plant['name']]['triangles'];bodyhits=[]
    for mesh in ASSETS['AST-BOT-012_low']['meshes']:
     if mesh['name']=='POT_ContainedSoil':continue
     mt=[tuple(transform(q,pp['local_position_xyz'],0)for q in t)for t in mesh['triangles']];mb=bounds([q for t in mt for q in t]);candidates=[(j,t)for j,t in enumerate(tris)if overlap(bounds(t),mb,-EPS)]
     for j,t in candidates:
      for k,u in enumerate(mt):
       if triangle_intersects(t,u):bodyhits.append([mesh['name'],j,k])
    assert not bodyhits,(dn,bodyhits)
    pot_pair_checks.append(dict(pot=pp['name'],plant=plant['name'],root_forward_offset_m=.055,actual_soil_top_local_y=SOIL_Y,retained_soil_datum_local_y=ASSETS['AST-BOT-012_low']['markers']['DATUM_soil_surface'][1],full_plant_vs_shell_and_lip_triangle_hits=bodyhits,root_contact_on_actual_soil_triangles=True))
   else:pairhits.append([a['name'],b['name']])
 assert not pairhits,(dn,pairhits)
 REPORTS.append(dict(display=dn,existing_display=bool(olddisplay),existing_main_case_preserved=bool(olddisplay),new_retained_stock_count=len(new),stock_composition=[{'name':p['name'],'asset':p['asset'],'role':p['role']}for p in localitems],support_reports=supports,stock_stock_unapproved_envelope_overlaps=pairhits,plant_pair_reports=pot_pair_checks,source_only_noncollision_support_pass=True))

# All new stock/display envelopes against original section and old furnishing envelopes;
# only their explicitly named host display/pot is exempted, and was exactly checked above.
OBSTACLES=[(p['name'],bounds(p['world_vertices']))for p in SEC['source_parts']if not p.get('export_excluded')]+[(p['name'],[p['envelope_min_xyz'],p['envelope_max_xyz']])for p in OLD['placements']]
for p in ADDITIONS:
 bb=[p['envelope_min_xyz'],p['envelope_max_xyz']];exclude={p.get('host_display'),p.get('support')}
 hits=[n for n,b in OBSTACLES if n not in exclude and overlap(bb,b)];assert not hits,(p['name'],'original geometry',hits)

# New display envelopes are mutually disjoint, and every new stock item is
# entirely within its host; therefore different displays cannot collide.
for i,a in enumerate(DISPLAYS):
 for b in DISPLAYS[i+1:]:assert not overlap([a['envelope_min_xyz'],a['envelope_max_xyz']],[b['envelope_min_xyz'],b['envelope_max_xyz']])

# Existing independently authored protections are copied as geometry, never changed.
plan=read(C/'assets/grand_pool_first_pass/source/placement_contract.json');protected=plan['protected_route_rects'];route_report=[]
for name,y,r in protected:
 bb=[[r[0],y+.001,r[2]],[r[1],y+3.2,r[3]]];hits=[p['name']for p in ADDITIONS if overlap(bb,[p['envelope_min_xyz'],p['envelope_max_xyz']])];assert not hits,(name,hits);route_report.append(dict(name=name,bounds=bb,new_overlap_hits=hits))
for r in OLD['return_reserves']:
 hits=[p['name']for p in ADDITIONS if overlap([r['min_xyz'],r['max_xyz']],[p['envelope_min_xyz'],p['envelope_max_xyz']])];assert not hits;route_report.append({'name':r['name'],'bounds':[r['min_xyz'],r['max_xyz']],'new_overlap_hits':hits})
old_approach_report=[]
for path in OLD['approach_paths']:
 pts=[q for a,b in zip(path['points'],path['points'][1:])for q in samples(a,b)];hits=[]
 for q in pts:
  bb=[add(q,(-.32,.03,-.32)),add(q,(.32,1.83,.32))]
  hits.extend(p['name']for p in ADDITIONS if overlap(bb,[p['envelope_min_xyz'],p['envelope_max_xyz']]))
 assert not hits,(path['item'],hits);old_approach_report.append(dict(item=path['item'],purpose=path['purpose'],points=path['points'],samples=len(pts),new_overlap_hits=hits))
new_approaches=[];floor_reports=[]
for d in DISPLAYS:
 lo,hi=d['envelope_min_xyz'],d['envelope_max_xyz'];fp=[(x,z)for x,z in itertools.product(grid(lo[0],hi[0]),grid(lo[2],hi[2]))];assert all(floor_has(x,z,FLOOR)for x,z in fp)
 a=(-45.9,52.5,d['position_xyz'][2]);b=(-51.6,52.5,d['position_xyz'][2]);pts=samples(a,b);hits=[];unsupported=[]
 for q in pts:
  bb=[add(q,(-.32,.03,-.32)),add(q,(.32,1.83,.32))]
  hits.extend(n for n,ob in OBSTACLES if overlap(bb,ob));hits.extend(p['name']for p in ADDITIONS if overlap(bb,[p['envelope_min_xyz'],p['envelope_max_xyz']]))
  for dx,dz in itertools.product([-.32,0,.32],repeat=2):
   if not floor_has(q[0]+dx,q[2]+dz,FLOOR):unsupported.append([q[0]+dx,q[2]+dz])
 # Original displays have a pause bench directly in front; the centred path is not
 # fabricated as an approach. Use the source-supported side entry around the seat.
 if hits:
  alternatives=[]
  for side in (-1,1,-.9,.9,-1.1,1.1):
   z=d['position_xyz'][2]+side;points=[(-45.9,52.5,z),(-51.925,52.5,z),(-51.925,52.5,d['position_xyz'][2])];hh=[];bad=[];ss=[q for aa,bb in zip(points,points[1:])for q in samples(aa,bb)]
   for q in ss:
    actor=[add(q,(-.30,.03,-.30)),add(q,(.30,1.83,.30))];hh.extend(n for n,ob in OBSTACLES if overlap(actor,ob));hh.extend(p['name']for p in ADDITIONS if overlap(actor,[p['envelope_min_xyz'],p['envelope_max_xyz']]))
    for dx,dz in itertools.product([-.30,0,.30],repeat=2):
     if not floor_has(q[0]+dx,q[2]+dz,FLOOR):bad.append((q[0]+dx,q[2]+dz))
   if not hh and not bad:alternatives.append((points,ss))
  assert alternatives,(d['name'],'no existing-display approach',set(hits));points,pts=alternatives[0];radius=.30;rejected=sorted(set(hits));hits=[];unsupported=[]
 else:points=[a,b];radius=.32;rejected=[]
 floor_reports.append(dict(display=d['name'],floor_region=FLOOR['id'],floor_y=FLOOR['floor_y'],footprint_samples=len(fp),unsupported_count=0))
 new_approaches.append(dict(display=d['name'],points_xyz=points,body_radius_m=radius,body_height_m=1.8,sample_spacing_at_most=.05,samples=len(pts),overlap_hits=hits,unsupported_floor_samples=unsupported,rejected_centerline_obstacles=rejected,scope='Static conservative body-envelope sampling; not engine walking or accessibility acceptance'))

# Verify all statically specified retained cart lines/arcs with an intentionally
# oversized, yaw-independent radius. This includes return/reverse/regrip paths.
cart_text=(G/'tests/validate_grand_pool_service_cart.gd').read_text();cart=read(G/'data/architecture/cleaning_cart_contacts.json')
cart_r=max(math.hypot(v[0],v[2])for box in cart['boxes']for v in corners([sub(box['center'],mul(box['size'],.5)),add(box['center'],mul(box['size'],.5))]));assert cart_r<1.0
assert 'DRIVER_OFFSET := 1.62'in cart_text or 'DRIVER_OFFSET = 1.62'in cart_text
cart_radius=1.62+.30+.04;cart_paths=[]
def arith(s):
 node=ast.parse(s.strip(),mode='eval').body
 def go(n):
  if isinstance(n,ast.Constant)and isinstance(n.value,(int,float)):return n.value
  if isinstance(n,ast.Name)and n.id=='PI':return math.pi
  if isinstance(n,ast.UnaryOp)and isinstance(n.op,ast.USub):return-go(n.operand)
  if isinstance(n,ast.BinOp)and type(n.op)in (ast.Add,ast.Sub,ast.Mult,ast.Div):return{ast.Add:lambda a,b:a+b,ast.Sub:lambda a,b:a-b,ast.Mult:lambda a,b:a*b,ast.Div:lambda a,b:a/b}[type(n.op)](go(n.left),go(n.right))
  raise ValueError(ast.dump(n))
 return go(node)
for line in cart_text.splitlines():
 m=re.search(r'line\([^,]+,\s*Vector2\(([^,]+),([^\)]+)\),\s*Vector2\(([^,]+),([^\)]+)\)',line)
 if m:
  x,z,xx,zz=map(arith,m.groups());cart_paths.append((line.strip(),[(p[0],p[2])for p in samples((x,0,z),(xx,0,zz),.04)]));continue
 m=re.search(r'arc\([^,]+,\s*Vector2\(([^,]+),([^\)]+)\),\s*([^,]+),\s*([^,]+),\s*([^\)]+)\)',line)
 if m:
  x,z,r,a,b=map(arith,m.groups());n=math.ceil(abs(b-a)*r/.04);cart_paths.append((line.strip(),[(x+r*math.cos(a+(b-a)*i/n),z+r*math.sin(a+(b-a)*i/n))for i in range(n+1)]))
cart_report=[]
for code,pts in cart_paths:
 for y in (46.2,52.5):
  hits=[]
  for x,z in pts:
   bb=[(x-cart_radius,y,z-cart_radius),(x+cart_radius,y+1.85,z+cart_radius)];hits.extend(p['name']for p in ADDITIONS if overlap(bb,[p['envelope_min_xyz'],p['envelope_max_xyz']]))
  assert not hits,(code,y,set(hits));cart_report.append(dict(source_code=code,floor_y=y,samples=len(pts),yaw_independent_radius_m=cart_radius,new_overlap_hits=hits))

# Explicit retained access routes: source contracts plus all literal route arrays
# in the actual existing access harness. Screens only the added geometry.
access_routes=[]
def collect_routes(value,path='runtime_contract'):
 if isinstance(value,dict):
  for k,v in value.items():
   if ('route' in k or 'approach' in k) and isinstance(v,list) and len(v)>=2 and all(isinstance(q,list) and len(q)==3 and all(isinstance(n,(int,float)) for n in q) for q in v):access_routes.append((path+'.'+k,v))
   else:collect_routes(v,path+'.'+k)
 elif isinstance(value,list):
  for i,v in enumerate(value):collect_routes(v,path+'.'+str(i))
collect_routes(RSEC)
access_text=(G/'tests/validate_grand_pool_access.gd').read_text()
for name,literal in re.findall(r'var (\w+): Array = (\[\[.*?\]\])',access_text):
 points=ast.literal_eval(literal);access_routes.append(('validate_grand_pool_access.gd:'+name,points))
access_routes.append(('runtime_contract.market.adopted_dry_loop_centreline_xz',[[x,52.5,z]for x,z in RSEC['market']['adopted_dry_loop_centreline_xz']]))
access_report=[]
for name,points in access_routes:
 pts=[q for a,b in zip(points,points[1:])for q in samples(a,b)];hits=[]
 for q in pts:
  bb=[add(q,(-.32,.03,-.32)),add(q,(.32,1.83,.32))];hits.extend(p['name']for p in ADDITIONS if overlap(bb,[p['envelope_min_xyz'],p['envelope_max_xyz']]))
 assert not hits,(name,hits)
 access_report.append(dict(name=name,points_xyz=points,radius_m=.32,height_m=1.8,samples=len(pts),new_overlap_hits=hits,scope='Source-only new-obstruction screen; reverse traversals cover the same positions'))

# Low display-light MOUNT PROPOSALS only. No lamp settings or lights are authored.
HOST=PM['recessed_terracotta_return_04'];mount_y=HOST['bounds'][0][1];housing=[[-.15,mount_y-.035,.22],[.35,mount_y,.30]];lens=(.1,mount_y-.040,.26)
assert not[part['name']for part in PARTS if convex_box_overlap(part,housing)]
for d,rep in zip(DISPLAYS,REPORTS):
 contact_patch=[(x,mount_y,z)for x,z in ((-.15,.22),(.35,.22),(.35,.30),(-.15,.30))];contact=[]
 for q in contact_patch:
  hit=[(i,t)for i,t in enumerate(HOST['triangles'])if (bc:=bary_xz(q,t))is not None and abs(sum(bc[j]*t[j][1]for j in range(3))-q[1])<EPS];assert hit;contact.extend(i for i,t in hit)
 receiver_names=[s['name']for s in rep['stock_composition']if s['role']in ('main_case','book_group','curio')];rays=[]
 for name in receiver_names:
  tr=ALL_LOCAL[name]['triangles'];candidates=[]
  potential=[]
  for idx,t in enumerate(tr):
   n=cross(sub(t[1],t[0]),sub(t[2],t[0]));ln=length(n)
   if ln<EPS or n[2]/ln<.45:continue
   mid=tuple(sum(q[k]for q in t)/3 for k in range(3))
   if mid[1]<bounds(ALL_LOCAL[name]['vertices'])[0][1]+.1:continue
   potential.append((length(sub(mid,lens)),idx,mid,t))
  for dist,idx,mid,t in sorted(potential):
   obstruction=[];rb=bounds([lens,mid])
   for part in PARTS:
    if not overlap(rb,part['bounds'],-EPS):continue
    for tri in part['triangles']:
     f=segment_triangle(lens,mid,tri)
     if f is not None and EPS<f<1-EPS:obstruction.append(part['name']);break
   if obstruction:continue
   for item in rep['stock_composition']:
    if not overlap(rb,bounds(ALL_LOCAL[item['name']]['vertices']),-EPS):continue
    for tri in ALL_LOCAL[item['name']]['triangles']:
     f=segment_triangle(lens,mid,tri)
     if f is not None and EPS<f<1-EPS:obstruction.append(item['name']);break
   if not obstruction:candidates.append((dist,idx,mid,t));break
  if candidates:
   dist,idx,point,tri=min(candidates);rays.append(dict(receiver=name,receiver_triangle_index=idx,receiver_triangle_local_xyz=tri,receiver_local_xyz=point,receiver_world_xyz=transform(point,d['position_xyz'],d['yaw_radians']),distance_m=dist,source_to_receiver_obstruction_hits=[]))
 assert rays,(d['name'],'no proven receiver')
 assert not [p['name'] for p in rep['stock_composition'] if overlap(housing,bounds(ALL_LOCAL[p['name']]['vertices']))]
 exit_end=add(lens,(0,-.06,0));exit_hits=[part['name']for part in PARTS for tri in part['triangles']if(f:=segment_triangle(lens,exit_end,tri))is not None and EPS<f<1-EPS];assert not exit_hits
 LIGHTS.append(dict(host_world_position_xyz=d['position_xyz'],host_yaw_radians=d['yaw_radians'],host_scale_xyz=[1,1,1],mount_outward_normal_local_xyz=[0,-1,0],mount_outward_normal_world_xyz=[0,-1,0],housing_proposal_world_bounds=bounds([transform(q,d['position_xyz'],d['yaw_radians'])for q in corners(housing)]),exit_clearance_probe_end_world_xyz=transform(exit_end,d['position_xyz'],d['yaw_radians']),exit_clearance_probe_length_m=.06,exit_clearance_hits=exit_hits,housing_stock_overlap_hits=[],name=d['name']+'_low_display_light_proposal',status='source_mount_and_receiver_proposal_no_fixture_or_light_authored',host_display=d['name'],physical_host_part=HOST['name'],mount_local_xyz=(.1,mount_y,.26),mount_world_xyz=transform((.1,mount_y,.26),d['position_xyz'],d['yaw_radians']),attachment_patch_local_xyz=contact_patch,attachment_source_triangle_indices=sorted(set(contact)),attachment_source_triangles_local_xyz=[HOST['triangles'][i]for i in sorted(set(contact))],housing_proposal_local_bounds=housing,lens_proposal_local_xyz=lens,lens_proposal_world_xyz=transform(lens,d['position_xyz'],d['yaw_radians']),housing_host_overlap_hits=[],receiver_rays=rays,energy=None,range=None,cone_angle=None,shadow_policy='Existing shared eight-source shadow cap unchanged; engine selector and photometry untested'))

assert len(ADDITIONS)<=48 and 51+len(ADDITIONS)<=99
assert all(sha(Path(p))==h for p,h in BEFORE.items()),'A retained input changed while checking'
contract=dict(schema=1,status='source_only_additive_stock_candidate_NOT_ENGINE_ACCEPTED',coordinate_system='GLB/Godot Y-up metres; local coordinates relative to AST-RTL-001; world yaw +pi/2',original_runtime_contract_sha256=sha(G/'data/architecture/GRAND_POOL_FIRST_PASS_RUNTIME.json'),preserved_original_placement_count=51,additional_placement_count=len(ADDITIONS),prospective_total=51+len(ADDITIONS),maximum_additions=48,maximum_total=99,input_inventory=INV,preserved_original_placements=OLD['placements'],displays=DISPLAYS,placements=ADDITIONS,source_support_reports_file='PER_DISPLAY_REPORTS.json',approach_paths=new_approaches,light_mount_proposals_file='DISPLAY_LIGHT_MOUNT_PROPOSALS.json',limits=['No retained file changed; no scene, runtime, GLB or blend authored','Exact input triangle checks and conservative envelopes are source-only; no engine physics, imports, body/cart execution, lights or visual acceptance','No asset scaling; no new designs, stock operations, inventory, prices or business names','Existing 51 placements, original six architectural planters, seating and towel stations remain byte-preserved','Additive wall/ceiling/sign/fixture interaction must be retested against eventual finished geometry'])
write('stock_placement_contract.json',contract);write('PER_DISPLAY_REPORTS.json',{'status':'source_only_pass','reports':REPORTS});write('DISPLAY_LIGHT_MOUNT_PROPOSALS.json',{'status':'six_source_mount_proposals_no_lights_authored','proposals':LIGHTS})
report=dict(status='SOURCE_ONLY_PASS',additional_instances=len(ADDITIONS),prospective_total=51+len(ADDITIONS),actual_source_part_count=len(PARTS),all_source_parts_convex=True,evaluated_source_triangle_multiset_matches_actual_glb_at_m=1e-5,source_floor_top_y=support_y('lower_storage_tactile_floor'),nominal_storage_void_min_y=.235,actual_low_pot_soil_top_y=SOIL_Y,soil_marker_y=ASSETS['AST-BOT-012_low']['markers']['DATUM_soil_surface'][1],original_files_preserved=True,original_six_architectural_planters_preserved=[p['name']for p in SEC['source_parts']if p['name'].startswith('GP_PlantSoil')],original_reach_segments_preserved=OLD['reach_segments'],original_seat_contact_probes_preserved=OLD['seat_contact_probes'],original_geometry_overlap_hits=[],stock_floor_reports=floor_reports,protected_route_envelopes=route_report,preserved_original_approaches=old_approach_report,display_approaches=new_approaches,retained_cart_static_paths=cart_report,cart_path_samples=sum(p['samples']for p in cart_report),cart_scope='Read-only source screen: oversized 1.96m yaw-independent square encloses cart, four-product tray and 1.62m-offset operator along all literal line/arc paths in retained test; .04m margin covers <=.04m interpolation. Engine loaded-cart/reverse/regrip remains required.',retained_access_routes=access_report,retained_access_route_samples=sum(p['samples']for p in access_report),per_display_reports='PER_DISPLAY_REPORTS.json',light_mount_proposals='DISPLAY_LIGHT_MOUNT_PROPOSALS.json',issues=[],limits=contract['limits'])
write('SOURCE_CHECK_REPORT.json',report);write('SOURCE_HASHES.json',{'inputs':PORTABLE_INPUTS,'outputs':{p.name:sha(p)for p in sorted(HERE.glob('*'))if p.is_file()and p.name!='SOURCE_HASHES.json'},'retained_inputs_unchanged':True})
print(json.dumps({'status':report['status'],'additions':len(ADDITIONS),'total':51+len(ADDITIONS),'displays':len(DISPLAYS),'source_only':True,'cart_samples':report['cart_path_samples'],'floor_samples':sum(p['footprint_samples']for p in floor_reports),'light_proposals':len(LIGHTS)},indent=2))
