"""Port2 D03 branch and current-live-composite interface contract."""
from pathlib import Path
import json,copy,math,hashlib
import shapely
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[4];EXT=HERE.parent;OLD=EXT/'d03_port2_branch_batch007'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();write=lambda f,q:f.write_text(json.dumps(q,indent=2)+'\n')
for folder in ['d03_port2_branch_batch007','port2_clinical_physical_batch016','d03_service_receivers_physical_batch021']:
 for line in(EXT/folder/'SHA256SUMS.txt').read_text().splitlines():h,f=line.split('  ',1);assert sha(EXT/folder/f)==h,f
paths=[OLD/'source/D03_PORT2_BRANCH.json',OLD/'source/D03_SPINE_RECEIVER_PATCH.json',OLD/'SHA256SUMS.txt',HERE/'source/CURRENT_SPINE_PREIMAGES.json',ROOT/'Game/assets/models/AST-STF-009_pool_market_home_equipment.glb',ROOT/'Game/scripts/lower_staff_network.gd',ROOT/'Game/scripts/crew_home_approach.gd',ROOT/'Game/scripts/service_door.gd',ROOT/'Game/assets/models/AST-STF-008.glb',ROOT/'Game/data/generated/structural_meshes.json',ROOT/'Game/data/generated/received_structural_meshes.json',ROOT/'Game/data/architecture/REMAINING_BATCH_FLOORS.json',EXT/'port2_clinical_physical_batch016/source/PHYSICAL_CONTRACT.json',EXT/'port2_clinical_physical_batch016/source/PORT2_MISSING_ONLY_FLOORS.json']
pins={str(f.relative_to(ROOT)):sha(f)for f in paths};base=dict(schema=1,family='group3_crew_service_20261009',material_contract='retained_lower_staff_network',source_pins=pins,automatic_runtime_adoption=False,authoritative_identity_map=None,registered_berths_added=0)
for i in range(52,56):assert not any(q['catalogue_id']==f'AST-STF-G3-{i:03d}'for q in json.load(open(ROOT/'BlenderCatalogue/catalogue_manifest.json'))['assets'])
branch=json.load(open(paths[0]));pre=json.load(open(paths[3]));doors=[dict(name='port2_D03_arrival',position=[-21,12,-289.5],yaw=math.pi,persistent_id=None),dict(name='port2_D03_spine',position=[-54.7,12,-293],yaw=math.pi/2,persistent_id=None)]
def shape(q):
 if'boundary'in q:return Polygon(q['boundary'],q['holes'])
 a=q['aabb'];return box(a[0],a[4],a[1],a[5])
def yr(q):return q['y']if'y'in q else q['aabb'][2:4]
def prism(out,name,g,lo,hi,role,category,cell):
 lo=round(lo,6);hi=round(hi,6)
 if hi-lo<.000001:return
 g=shapely.set_precision(g,grid_size=.000001)
 for i,p in enumerate(shapely.get_parts(g)):
  if p.geom_type!='Polygon'or p.area<1e-10:continue
  out.append(dict(name=name+'_'+str(i),boundary=list(p.exterior.coords)[:-1],holes=[list(r.coords)[:-1]for r in p.interiors],triangles=[list(t.exterior.coords)[:3]for t in shapely.constrained_delaunay_triangles(p).geoms],y=[lo,hi],role=role,category=category,batch_cell=cell))
def gate_rect(q,x0,x1,z0,z1):
 x,y,z=q['position'];c=math.cos(q['yaw']);s=math.sin(q['yaw']);return Polygon([(x+c*a+s*b,z-s*a+c*b)for a,b in[(x0,z0),(x1,z0),(x1,z1),(x0,z1)]])
cut=unary_union([gate_rect(q,-1.382,1.382,-.182,.182)for q in doors]);parts=[]
for q in branch['parts']:
 lo,hi=yr(q);levels=sorted({round(v,6)for v in[lo,hi,*[v for v in[14.822]if lo<v<hi]]})
 for a,b in zip(levels,levels[1:]):prism(parts,q['name']+'_FrameFit'+str(a),shape(q).difference(cut)if a<14.822 else shape(q),a,b,q['role'],q['category'],q.get('batch_cell','branch'))
# Existing current spine remains intact until the owner applies the exact
# triangle derivative. These infills affect only new branch gate planes.
for q in doors:
 for suffix,x0,x1,lo in [('Left',-1.8,-1.38,12),('Right',1.38,1.8,12),('Head',-1.38,1.38,14.82)]:
  g=gate_rect(q,x0,x1,-.18,.18);hi=15.2;fixed=list(parts);levels=sorted({round(v,6)for v in[lo,hi,*[v for p in fixed for v in yr(p)if lo<v<hi]]})
  for a,b in zip(levels,levels[1:]):prism(parts,q['name']+suffix+str(a),g.difference(unary_union([shape(p)for p in fixed if yr(p)[0]<b and yr(p)[1]>a])),a,b,'staff_white_paint','door_receiver',q['name'])
fixtures=copy.deepcopy(branch['fixtures'])
for q in fixtures:q.update(color=[.78,.88,1],energy=.9,range_m=8,runtime_calibration='Verified first-pass supported staff-task profile; final photometry held')
write(HERE/'source/D03_PORT2_FITTED_BRANCH.json',dict(base,catalogue_id='AST-STF-G3-053',parts=parts,fixtures=fixtures,originals_or_current_spine_modified=False))
existing=[]
for f in paths[9:12]:existing.extend(json.load(open(f))['regions'])
previous=unary_union([Polygon(t)for q in existing if q['deck']=='D03'for t in q['triangles']]);prior=[]
for folder,file in [('d03_remaining_receivers_batch013','MISSING_ONLY_FLOOR_PATCH.json'),('port2_clinical_physical_batch016','PORT2_MISSING_ONLY_FLOORS.json'),('d03_service_receivers_physical_batch021','D03_SERVICE_MISSING_FLOOR.json')]:
 f=EXT/folder/'source'/file;p=json.load(open(f));pins[str(f.relative_to(ROOT))]=sha(f)
 for q in p['parts']:
  if yr(q)[1]==12:prior.append(shape(q))
request=unary_union([Polygon(q['boundary'],q['holes'])for q in branch['floor_proposal']['polygons']]);missing=request.difference(previous).difference(unary_union(prior));floors=[]
prism(floors,'D03Port2BranchMissingFloor',missing,11.76,12,'staff_floor','floor','D03')
write(HERE/'source/D03_PORT2_MISSING_FLOOR.json',dict(base,catalogue_id='AST-STF-G3-054',parts=floors,fixtures=[],new_floor_m2=missing.area,existing_or_prior_floors_overlaid=False))
contract=dict(base,parent_handoff_commit='d3f8825202e0b7dbd0e85020dc1d65415954433b',door_bindings=doors,fixtures=fixtures,new_floor_m2=missing.area,current_spine_source=pre['current_source'],current_spine_sha256=pre['current_source_sha256'],exact_current_meshes_to_replace=[q['name']for q in pre['preimage_meshes']],other_current_composite_meshes_retained=pre['unrelated_current_meshes_to_preserve'],cut_min=pre['proposed_cut_min'],cut_max=pre['proposed_cut_max'],current_spine_patch_requires_owner_adoption=True,required_existing_port2_package='Group3Port2ClinicalPhysical',unchanged_forward_port_stop_keys=[1,2,3,8,9,13,14,15,16,17],D01_D04_or_registered_berths_or_room_headers_modified=False,source_floor_contacts_not_primary_engineering_acceptance=True,full_400_berth_identity_species_loaded_cart_stock_graphical_or_group_acceptance=False)
write(HERE/'source/D03_PORT2_CONNECTION_CONTRACT.json',contract);print(json.dumps(dict(new_floor_m2=missing.area,new_parts=len(parts),doors=2,fixture_profiles=len(fixtures),current_cells_to_replace=len(pre["preimage_meshes"]),other_current_cells_preserved=pre["unrelated_current_meshes_to_preserve"])))
