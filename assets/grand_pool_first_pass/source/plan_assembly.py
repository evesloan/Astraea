"""Read-only retained inputs; writes only this NEW package. No engine/import/render."""
import json, math, struct, hashlib
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parents[1]; ROOT=HERE.parents[1]
GAME=Path('/workspace/shared/astraea-godot-production-20261003')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def glb_vertices(p):
 b=p.read_bytes(); _,_,length=struct.unpack_from('<III',b); assert length==len(b)
 off=12; doc=None; buf=None
 while off<len(b):
  n,t=struct.unpack_from('<II',b,off);chunk=b[off+8:off+8+n];off+=8+n
  if t==0x4e4f534a:doc=json.loads(chunk)
  if t==0x004e4942:buf=chunk
 out=[]
 def visit(i,parent):
  node=doc['nodes'][i]
  if 'matrix' in node: m=np.array(node['matrix']).reshape(4,4).T
  else:
   x,y,z,w=node.get('rotation',[0,0,0,1]);m=np.eye(4);m[:3,:3]=[[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]];m[:3,:3]=m[:3,:3]@np.diag(node.get('scale',[1,1,1]));m[:3,3]=node.get('translation',[0,0,0])
  world=parent@m
  if 'mesh' in node:
   for prim in doc['meshes'][node['mesh']]['primitives']:
    a=doc['accessors'][prim['attributes']['POSITION']];assert a['componentType']==5126 and a['type']=='VEC3' and 'sparse' not in a
    v=doc['bufferViews'][a['bufferView']];assert v.get('buffer',0)==0
    arr=np.ndarray((a['count'],3),dtype='<f4',buffer=buf,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',12),4)).astype(float)
    out.append((np.c_[arr,np.ones(len(arr))]@world.T)[:,:3])
  for j in node.get('children',[]):visit(j,world)
 for i in doc['scenes'][doc.get('scene',0)]['nodes']:visit(i,np.eye(4))
 return np.concatenate(out)
contract_path=ROOT/'assets/grand_pool_orchard_section/source/connected_contract.json'; c=json.loads(contract_path.read_text())
files={
 'lounger':'assets/aquatic_lounge/exports/AST-AQU-001.glb',
 'side_table':'assets/aquatic_lounge/exports/AST-AQU-002.glb',
 'towels':'assets/aquatic_towel_use/exports/AST-AQU-007.glb',
 'return':'assets/aquatic_towel_use/exports/AST-AQU-008.glb',
 'understory':'assets/botanical_understory/exports/AST-BOT-002.glb',
 'rosette':'assets/botanical_understory/exports/AST-BOT-003.glb',
 'pot':'assets/nursery_pottery/exports/AST-BOT-012.glb',
 'retail_bay':'assets/retail_display/exports/AST-RTL-001.glb',
 'retail_island':'assets/retail_display/exports/AST-RTL-002.glb',
 'goods_case':'assets/retail_work/exports/AST-RTL-004.glb',
 'bench':'assets/furniture/AST-FUR-001_day_window_bench.glb'}
verts={k:glb_vertices(ROOT/v) for k,v in files.items()}
items=[]
def add(name,key,xyz,yaw=0,purpose='',support=None):
 p=verts[key];a=math.cos(yaw);b=math.sin(yaw);m=np.array([[a,0,b],[0,1,0],[-b,0,a]]);p=p@m.T+xyz
 items.append(dict(name=name,retained_export=files[key],position_xyz=xyz,yaw_radians=yaw,scale_xyz=[1,1,1],purpose=purpose,support=support or ('D09_orchard_market_gallery' if xyz[1]==52.5 else 'D08_grand_pool_wet'),envelope_min_xyz=p.min(0).tolist(),envelope_max_xyz=p.max(0).tolist(),asset=key))
for z in [-448,-444,-440,-436,-429,-425,-421]:
 add(f'wet_rest_{abs(z)}','lounger',[-47.5,46.2,z],math.pi/2,'View-facing rest outside continuous pool apron')
for z in [-446,-438,-427,-423]:add(f'wet_table_{abs(z)}','side_table',[-47,46.2,z],0,'Personal-item support between paired rest positions')
add('clean_towel_retrieval','towels',[-47,46.2,-454],math.pi/2,'Dry guest retrieval; front restock reserve required')
add('used_towel_return','return',[-47,46.2,-451],math.pi/2,'Separated used return; rear extraction reserve required')
for i,soil in enumerate(p for p in c['source_parts'] if p['name'].startswith('GP_PlantSoil')):
 v=np.array(soil['world_vertices']);lo=v.min(0);hi=v.max(0);x=(lo[0]+hi[0])/2;z=(lo[2]+hi[2])/2
 add(f'market_understory_{i}','understory',[x,hi[1],z],0,'Contained rooted understory',soil['name'])
 for j,dx in enumerate([-.9,.9]):add(f'market_rosette_{i}_{j}','rosette',[x+dx,hi[1],z],0,'Low contained flowering edge',soil['name'])
for i,z in enumerate([-448.9,-438,-420.5]):
 add(f'market_display_{i}','retail_bay',[-52.7,52.5,z],math.pi/2,'Existing programme display, no new business identity')
 add(f'market_goods_{i}','goods_case',[-52.635,53.45,z+.4],math.pi/2,'Static retained case on main_display_left_patch','market_display_'+str(i))
for i,z in enumerate([-455,-443,-432,-416,-409]):
 add(f'wet_planter_{i}','pot',[-47,46.2,z],0,'Contained botanical pause')
 add(f'wet_pot_rosette_{i}','rosette',[-47,46.4,z],0,'Plant root at retained pot physical soil top .200m','wet_planter_'+str(i))
for i,z in enumerate([-448.9,-436.5,-419.5]):add(f'market_rest_{i}','bench',[-50.4,52.5,z],0,'Social pause seat with front approach outside 3.4m market circuit')
add('wet_end_rest','bench',[-47,46.2,-402.5],math.pi/2,'Level non-reclining rest at pool end')
def overlap(a,b):return all(min(a[1][k],b[1][k])-max(a[0][k],b[0][k])>1e-5 for k in range(3))
obstacles=[]
for p in c['source_parts']:
 if p.get('export_excluded'):continue
 v=np.array(p['world_vertices']);obstacles.append((p['name'],(v.min(0),v.max(0))))
issues=[]
for it in items:
 box=(it['envelope_min_xyz'],it['envelope_max_xyz'])
 hits=[name for name,ob in obstacles if name!=it['support'] and overlap(box,ob)]
 if hits:issues.append(dict(item=it['name'],source_envelope_intersections=hits))
for i,it in enumerate(items):
 for other in items[i+1:]:
  if it['name']!=other['support'] and other['name']!=it['support'] and overlap((it['envelope_min_xyz'],it['envelope_max_xyz']),(other['envelope_min_xyz'],other['envelope_max_xyz'])):issues.append(dict(item=it['name'],other_item=other['name']))
# Test the entire translated visual envelope against protected circulation rectangles.
protected_rects=[('wet_retained_walk_capsule',46.2,[-46.22,-45.58,-458.32,-404.68]),('market_west_ring',52.5,[-47.6,-44.2,-464.8,-399.2]),('market_fore_ring',52.5,[-47.6,-14.4,-464.8,-461.4]),('market_aft_ring',52.5,[-47.6,-8.45,-402.6,-399.2]),('market_east_ring',52.5,[-17.8,-14.4,-464.8,-429.5]),('market_dry_bypass',52.5,[-10.85,-8.45,-427.9,-410.2]),('wet_west_apron',46.2,[-44,-40.4,-457.4,-406.6]),('wet_aft_apron',46.2,[-44,-18,-406.6,-404.2])]
for it in items:
 for name,y,r in protected_rects:
  if overlap((it['envelope_min_xyz'],it['envelope_max_xyz']),([r[0],y+.001,r[2]],[r[1],y+3.2,r[3]])):issues.append(dict(item=it['name'],protected_route=name))
# Entire contact envelope must lie on its declared compiler floor; sample every footprint corner/edge at <= .05m.
def inside_tri(pt,t):
 a,b,c=np.array(t);v0=c-a;v1=b-a;v2=np.array(pt)-a;den=v0[0]*v1[1]-v1[0]*v0[1]
 if abs(den)<1e-10:return False
 u=(v2[0]*v1[1]-v1[0]*v2[1])/den;v=(v0[0]*v2[1]-v2[0]*v0[1])/den
 return u>=-1e-8 and v>=-1e-8 and u+v<=1+1e-8
floor_checks=[]
for it in items:
 if not it['support'].startswith('D0'):continue
 f=next(x for x in c['floor_regions'] if x['id']==it['support']);lo=it['envelope_min_xyz'];hi=it['envelope_max_xyz'];samples=[]
 for x in np.linspace(lo[0],hi[0],max(2,int((hi[0]-lo[0])/.05)+2)):
  for z in np.linspace(lo[2],hi[2],max(2,int((hi[2]-lo[2])/.05)+2)):samples.append([x,z])
 unsupported=[p for p in samples if not any(inside_tri(p,t) for t in f['triangles'])]
 floor_checks.append(dict(item=it['name'],support=it['support'],samples=len(samples),unsupported_count=len(unsupported)))
 if unsupported:issues.append(dict(item=it['name'],unsupported_floor_envelope=unsupported[:4]))
# This conservative AABB test cannot establish absence of actual triangle intersections where boxes overlap.
inv={}
for k,p in files.items():
 ep=ROOT/p;sp=ep.parent.parent/'source'/(ep.stem+'.blend') if ep.parent.name=='exports' else ep.with_suffix('.blend')
 assert sp.exists(),sp
 inv[k]=dict(path=p,sha256=sha(ep),editable_source=str(sp.relative_to(ROOT)),editable_source_sha256=sha(sp),actual_gltf_bounds=[verts[k].min(0).tolist(),verts[k].max(0).tolist()])
result=dict(schema=1,status='planning_candidate_not_adopted',programme_ids=c['programme_ids'],source_contract_sha256=sha(contract_path),input_inventory=inv,placements=items,existing_supported_fixtures=c['fixtures'],protected=dict(market=c['market'],ramp=c['accessible_ramp'],wet_market_link=c['wet_market_link'],doors=c['door_fittings'],staff=c['staff']),issues=issues,floor_checks=floor_checks,protected_route_rects=protected_rects,limitations=['AABB plan only, not source triangle or runtime acceptance','Display stock uses source main_display_left_patch; actual triangle clearance remains untested','No new collisions, floors, controllers, catalogue IDs or business identities'])
(HERE/'source/placement_contract.json').write_text(json.dumps(result,indent=2)+'\n')
(HERE/'qa/plan_envelope_report.json').write_text(json.dumps(dict(placement_count=len(items),issues=issues,floor_checks=floor_checks,protected_route_rects=protected_rects,status='plan_checks_pass' if not issues else 'fail_closed_if_issues'),indent=2)+'\n')
print(json.dumps(dict(count=len(items),issues=issues),indent=2))
