#!/usr/bin/env python3
"""Source geometry only. No Blender/Godot invocation, imports or shared writes."""
import json, math, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PROJECT=Path('/workspace/shared/astraea-godot-production-20261003')
CAT=ROOT.parents[1]
P=PROJECT/'data/architecture/packages/theater'
def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d): p.write_text(json.dumps(d,indent=2)+'\n')
proposal=read(P/'THEATER_SECTION_PROPOSAL.json'); policy=read(P/'AUTHORED_SURFACE_POLICY_PROPOSAL.json')
assert not any(x['catalogue_id']=='AST-CUL-005' for x in read(CAT/'catalogue_manifest.json')['assets'])
chair=CAT/'assets/auditorium_use/source/AST-CUL-003.blend'; chair_hash=sha(chair)
objects=[]; surfaces=[]
def area(p): return abs(sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p)))/2)
def clip(p,axis,k,low):
 out=[]
 for a,b in zip(p,p[1:]+p[:1]):
  ia=(a[axis]<=k+1e-9) if low else (a[axis]>=k-1e-9)
  ib=(b[axis]<=k+1e-9) if low else (b[axis]>=k-1e-9)
  if ia: out.append(a)
  if ia!=ib:
   t=(k-a[axis])/(b[axis]-a[axis]); out.append([a[j]+t*(b[j]-a[j]) for j in range(2)])
 return out if len(out)>2 and area(out)>1e-8 else []
def subtract_rect(p,r):
 # Mutually exclusive convex fragments: left/right then bottom/top of middle
 x0,z0,x1,z1=r; pieces=[]
 for axis,k,low in [(0,x0,True),(0,x1,False)]:
  q=clip(p,axis,k,low)
  if q: pieces.append(q)
 middle=clip(clip(p,0,x0,False),0,x1,True)
 for k,low in [(z0,True),(z1,False)]:
  q=clip(middle,1,k,low) if middle else []
  if q: pieces.append(q)
 return pieces

def split_line(p,a,b,inside_sign,keep_inside):
 out=[]
 def val(v):return ((b[0]-a[0])*(v[1]-a[1])-(b[1]-a[1])*(v[0]-a[0]))*inside_sign
 for u,v in zip(p,p[1:]+p[:1]):
  du,dv=val(u),val(v); iu=du>=-1e-9 if keep_inside else du<=1e-9; iv=dv>=-1e-9 if keep_inside else dv<=1e-9
  if iu:out.append(u)
  if iu!=iv:
   t=du/(du-dv);out.append([u[j]+t*(v[j]-u[j]) for j in range(2)])
 return out if len(out)>2 and area(out)>1e-8 else []
def subtract_convex(p,c):
 signed=sum(c[i][0]*c[(i+1)%len(c)][1]-c[(i+1)%len(c)][0]*c[i][1] for i in range(len(c))); sign=1 if signed>0 else -1
 pieces=[]; remain=p
 for a,b in zip(c,c[1:]+c[:1]):
  if not remain:break
  q=split_line(remain,a,b,sign,False)
  if q:pieces.append(q)
  remain=split_line(remain,a,b,sign,True)
 return pieces

def rect(r): x0,z0,x1,z1=r; return [[x0,z0],[x1,z0],[x1,z1],[x0,z1]]
def difference(ps,rs):
 for r in rs: ps=[q for p in ps for q in subtract_rect(p,r)]
 return ps

def prism(name,p,y,h,role,material='hospitality_ivory',surface=None):
 # World XYZ polygon prisms; top convex polygons triangulated exactly once
 n=len(p); vs=[[x,y,z] for x,z in p]+[[x,y-h,z] for x,z in p]
 faces=[[0,i+1,i] for i in range(1,n-1)]+[[n,n+i,n+i+1] for i in range(1,n-1)]
 faces += [[i,(i+1)%n,n+(i+1)%n,n+i] for i in range(n)]
 objects.append(dict(name=name,vertices_world=vs,faces=faces,role=role,material_family=material,collision_owner='AST-CUL-005' if role!='preview_only' else None,surface_region=surface))
 return name

def box(name,r,y,h,role='static_structure',mat='hospitality_ivory'): return prism(name,rect(r),y,h,role,mat)

returns=policy['whitelist'][1]['shape_rule']['union_rectangles']
# Union tessellation without overlapping slabs, split at every rectangular boundary
xs=sorted(set(v for r in returns for v in (r[0],r[2]))); zs=sorted(set(v for r in returns for v in (r[1],r[3])))
return_cells=[]
for a,b in zip(xs,xs[1:]):
 for c,d in zip(zs,zs[1:]):
  if any(r[0]<(a+b)/2<r[2] and r[1]<(c+d)/2<r[3] for r in returns): return_cells.append(rect([a,c,b,d]))

def ring(r0,r1,a0,a1):
 return [[-76+r*math.sin(math.radians(a)),-238+r*math.cos(math.radians(a))] for r,a in [(r0,a0),(r1,a0),(r1,a1),(r0,a1)]]
for tier,deck,y,rows,rstart in [('stalls','D11',69.5,18,20),('first_gallery','D12',78,17,22),('crown_gallery','D13',84,17,22)]:
 sid=f'{deck}_theater_gallery_seating' if deck!='D11' else 'D11_theater_stalls_rake'; polys=[]; names=[]
 # 1 degree facets: chord departure at outer edge <=1.8mm
 radii=[18 if deck=='D11' else 19.5]+[rstart+1.5*i+0.75 for i in range(rows-1)]+[46.4]
 for row,(r0,r1) in enumerate(zip(radii,radii[1:])):
  for a in range(-54,54):
   for j,p in enumerate([ring(r0,r1,a,a+1)]):
    names.append(prism(f'{sid}_r{row+1:02}_a{a+54:03}_{j}',p,y+row*.12,.45,'walkable_authored',surface=sid)); polys.append(dict(boundary_xz=p,top_y=y+row*.12))
 if deck!='D11': surfaces.append(dict(region_id=sid,deck=deck,absolute_floor_y=y,owner='grand_lantern_theater',kind='authored_theater_surface',provided_by_asset=True,parts=polys,objects=names))
 else: stalls_polys=polys
 fan_cut=[[-76,-238]]+[[-76+46.4*math.sin(math.radians(a)),-238+46.4*math.cos(math.radians(a))] for a in range(-54,55)]
 rear_parts=[q for p in return_cells for q in subtract_convex(p,fan_cut)]
 # Replace the cart crossing with a level3.4m plateau and two graded transverse approaches.
 ramp_patches=[]
 for a in range(-3,3):
  def on_line(z,t):return [-76+(z+238)*math.tan(math.radians(t)),z]
  inner0=[-76+46.4*math.sin(math.radians(a)),-238+46.4*math.cos(math.radians(a))]
  inner1=[-76+46.4*math.sin(math.radians(a+1)),-238+46.4*math.cos(math.radians(a+1))]
  ramp_patches.append(([inner0,on_line(-180.5,a),on_line(-180.5,a+1),inner1],[1.92,1,1,1.92],'upper_run'))
  ramp_patches.append(([on_line(-180.5,a),on_line(-177.1,a),on_line(-177.1,a+1),on_line(-180.5,a+1)],[1,1,1,1],'cart_plateau'))
  ramp_patches.append(([on_line(-177.1,a),on_line(-165.1,a),on_line(-165.1,a+1),on_line(-177.1,a+1)],[1,0,0,1],'lower_run'))
 left0=on_line(-180.5,-3);left1=on_line(-177.1,-3);right0=on_line(-180.5,3);right1=on_line(-177.1,3)
 ramp_patches += [([[-92,-180.5],left0,left1,[-92,-177.1]],[0,1,1,0],'port_cart_approach'),([right0,[-60,-180.5],[-60,-177.1],right1],[1,0,0,1],'starboard_cart_approach')]
 ramp_parts=[p for p,h,k in ramp_patches]
 for rp in ramp_parts:rear_parts=[q for p in rear_parts for q in subtract_convex(p,rp)]
 for kind,ps in [('rear_public_returns',rear_parts),('foyer_landings',difference([rect([-117,-153,-35,-116])],[[-59,-146,-50,-122],[-44.5,-124,-38.5,-118]])),('stair_upper_landing',[rect([-59,-123.8,-50,-122])])]:
  if deck=='D11': continue
  sid=f'{deck}_theater_{kind}'; 
  if kind=='foyer_landings': ps=ps+[rect([-35,-128.6,-34,-123.4])]
  names=[prism(f'{sid}_{i:03}',p,y,.45,'walkable_authored',surface=sid) for i,p in enumerate(ps)]
  surfaces.append(dict(region_id=sid,deck=deck,absolute_floor_y=y,owner='grand_lantern_theater',kind='authored_theater_surface',provided_by_asset=True,parts=[dict(boundary_xz=p,top_y=y) for p in ps],objects=names))

 if deck!='D11':
  f=next(f for f in surfaces if f['region_id']==f'{deck}_theater_rear_public_returns')
  for i,(p,offsets,part_kind) in enumerate(ramp_patches):
   heights=[y+h for h in offsets]
   name=f'{deck}_rear_access_ramp_{i}'
   vs=[[x,h,z] for (x,z),h in zip(p,heights)]
   objects.append(dict(name=name,vertices_world=vs,faces=[[0,2,1],[0,3,2]],role='walkable_authored',collision_owner='AST-CUL-005',surface_region=f['region_id'],material_family='hospitality_ivory',ramp_part_kind=part_kind))
   f['parts'].append(dict(boundary_xz=p,vertex_top_y=heights,top_y=(heights[0] if len(set(heights))==1 else None),ramp_part_kind=part_kind));f['objects'].append(name)

# D11 compiler datum is deliberately not exported, solely diagnostic source preview.
box('D11_COMPILER_PREVIEW_NOT_EXPORT',[-117,-263,-35,-116],69.5,.12,'preview_only')
box('stage_36x14',[-94,-252,-58,-238],70.1,.6,'walkable_authored','dark_stage')
# True incline stage access, kept in exact reservation
objects.append(dict(name='stage_access_ramp_1_in_12',vertices_world=[[-55,69.5,-238.8],[-51,69.5,-238.8],[-51,70.1,-246],[-55,70.1,-246]],faces=[[0,2,1],[0,3,2]],role='walkable_authored',collision_owner='AST-CUL-005',material_family='hospitality_ivory'))
for name,r in [('ramp_low_landing',[-55,-238.8,-51,-237]),('ramp_high_landing',[-58,-249.4,-51,-246])]: box(name,r,69.5 if 'low' in name else 70.1,.25,'walkable_authored')
# Deep proscenium: opening exact x[-94,-58], y[70.1,86.1].
box('proscenium_port_reveal',[-96,-240,-94,-237.3],86.1,16,'static_structure','cultural_red')
box('proscenium_starboard_reveal',[-58,-240,-56,-237.3],86.1,16,'static_structure','cultural_red')
box('proscenium_head',[-96,-240,-56,-237.3],87.4,1.3,'static_structure','cultural_red')
# Inhabited columns located inward of all side/cart routes; supports pending structural certification.
for x in [-105,-47]:
 for z in [-160,-149]:
  box(f'lantern_pier_{x}_{z}',[x-.55,z-.55,x+.55,z+.55],87.1,17.6)
# Faceted elliptical canopy ring above crown crowd; no full-width roof slab/pressure hull.
for a in range(0,360,6):
 p=[[-76+rx*math.sin(math.radians(t)),-207+rz*math.cos(math.radians(t))] for rx,rz,t in [(23,14,a),(24,15,a),(24,15,a+6),(23,14,a+6)]]
 prism(f'canopy_lantern_ring_{a:03}',p,91.35,.35,'static_structure','hospitality_bronze')
fixtures=[dict(id=f'lantern_sconce_{i:02}',position_world=[x,82 if i%2 else 74,-207 if i<4 else -155],family='AST-STF-006',aim_world=[0,-1,0],runtime_light='pending_source_export_and_lighting_review') for i,x in enumerate([-104,-48,-104,-48,-104,-48])]
fixtures += [dict(id='stage_cue_worklight',position_world=[-54,71,-249],family='AST-CUL-004',aim_world=[0,-.3,-1],runtime_light='not_instantiated')]
placements=proposal['seat_proposals']
for seat in placements:
 if seat['tier']=='first_gallery' and seat['kind']=='rear_transfer_replaceable_place':
  seat['planning_original_position']=seat['position'][:]
  seat['position'][2]=-163
  seat['source_revision_reason']='Level rear viewing row relocated inside same return to avoid accessible ramp, exact IDs/capacity retained'
assert len(placements)==2200 and len({s['id'] for s in placements})==2200
assert len(surfaces)==8 and set(s['region_id'] for s in surfaces)==set(s['region_id'] for s in policy['whitelist'])
from extend_architecture import extend
extend(objects,surfaces,box,prism,write,ROOT)
geometry=dict(schema=1,catalogue_id='AST-CUL-005',coordinate_system='world XYZ metres; Blender adapter maps (X,-Z,Y)',status='PURE_SOURCE_GEOMETRY_NO_ENGINE_ACCEPTANCE',objects=objects)
write(ROOT/'source/geometry.json',geometry); write(ROOT/'contracts/surface_manifest.json',dict(schema=2,partition_policy='Parent approved source revision: return union subtracts actual fan rake and owns 1:12 rear ramp in its original bounds; eight IDs retained; shared compiler pending',surfaces=surfaces,D11='Compiler owns flat base; preview excluded; asset owns rake/stage/ramp, compiler must partition base against those footprints'))
write(ROOT/'contracts/place_instances.json',dict(source_family='AST-CUL-003',source_sha256=chair_hash,instance_only=True,seat_use_controller=False,places=placements))
write(ROOT/'contracts/fixture_markers.json',dict(fixtures=fixtures,not_runtime_lights=True))
write(ROOT/'qa/source_geometry_receipt.json',dict(object_count=len(objects),surface_count=len(surfaces),place_count=2200,capacity=proposal['capacity'],chair_source_unchanged=sha(chair)==chair_hash,chair_source_sha256=chair_hash,geometry_sha256=sha(ROOT/'source/geometry.json'),surface_manifest_sha256=sha(ROOT/'contracts/surface_manifest.json'),not_run=['Blender','Godot','export','import','render','capsule','species','loaded_cart','runtime_routes']))
print('Generated',len(objects),'source objects; eight owned upper surfaces; 2200 preserved placement IDs')
