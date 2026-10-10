from pathlib import Path
import json,hashlib,numpy as np
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
W=Path(__file__).resolve().parent;R=W.parents[2];first=R/'BlenderCatalogue/assets/star_atlas_specialty_first_20261010';P=json.loads((first/'PLAN.json').read_text());U=json.loads((R/'Game/data/architecture/STAR_ATLAS_UNITS.json').read_text());streets=json.loads((R/'Game/data/architecture/CENTRAL_RESIDENTIAL_STREETS.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();parts=[];supports=[];lower=[]
def cube(name,lo,hi,category):
 v=[[lo[0],lo[1],lo[2]],[hi[0],lo[1],lo[2]],[hi[0],hi[1],lo[2]],[lo[0],hi[1],lo[2]],[lo[0],lo[1],hi[2]],[hi[0],lo[1],hi[2]],[hi[0],hi[1],hi[2]],[lo[0],hi[1],hi[2]]];parts.append({'name':name,'verts':v,'faces':[[0,3,2,1],[4,5,6,7],[0,1,5,4],[3,7,6,2],[0,4,7,3],[1,2,6,5]],'category':category,'runtime_collision':True})
def beam(name,a,b,width,category):
 a=np.array(a,dtype=float);b=np.array(b,dtype=float);d=(b-a)/np.linalg.norm(b-a);u=np.array([1.,0,0]);v=np.cross(d,u);v/=np.linalg.norm(v);u=np.cross(v,d);verts=[(p+du*u*width/2+dv*v*width/2).tolist()for p in [a,b]for du,dv in [(-1,-1),(1,-1),(1,1),(-1,1)]]
 parts.append({'name':name,'verts':verts,'faces':[[0,3,2,1],[4,5,6,7],[0,1,5,4],[3,7,6,2],[0,4,7,3],[1,2,6,5]],'category':category,'runtime_collision':True})
def owner(y,toe):
 regions=streets['regions']+json.loads((R/'Game/data/generated/structural_meshes.json').read_text())['regions']+json.loads((R/'Game/data/generated/received_structural_meshes.json').read_text())['regions']
 matches=[r for r in regions if float(r['floor_y'])==y and unary_union([Polygon(t)for t in r['triangles']]).buffer(1e-7).covers(toe)];assert len(matches)==1,(y,toe.bounds,[r['id']for r in matches]);return matches[0]['id']
for side,sign in [('North',-1),('South',1)]:
 for i,d in enumerate([13.5,38,45.7,52.8]):
  z=d*sign;x=-85.8;toe=box(x-.1,z-.1,x+.1,z+.1);o=owner(88.5,toe)
  cube(f'SA_D15_{side}_BridgePier_{i}',[x-.1,88.5,z-.1],[x+.1,92.6,z+.1],'D14_street_to_D15_bridge_pier');supports.append({'name':parts[-1]['name'],'position':[x,88.5,z],'full_toe_area_m2':.04,'owner':o,'deck':'D14'})
  cube(f'SA_D15_{side}_BridgeCrossmember_{i}',[-85.9,92.6,z-.1],[-81.95,92.76,z+.1],'D15_bridge_transverse_frame')
 # A physical triangulated side frame spans the existing lower-floor gap.
 # Its chord/member dimensions are architectural proposals, not load ratings.
 for x in [-85.8,-82.2]:
  for y in [91.25,92.6]:cube(f'SA_D15_{side}_BridgeChord_{x}_{y}',[x-.08,y, min(13.5*sign,38*sign)],[x+.08,y+.12,max(13.5*sign,38*sign)],'D15_bridge_truss_chord')
  for j,d in enumerate([13.5,19.625,25.75,31.875,38]):
   z=d*sign;cube(f'SA_D15_{side}_BridgeVertical_{x}_{j}',[x-.06,91.25,z-.06],[x+.06,92.72,z+.06],'D15_bridge_truss_vertical')
  for j,(a,b)in enumerate(zip([13.5,19.625,25.75,31.875],[19.625,25.75,31.875,38])):
   beam(f'SA_D15_{side}_BridgeDiagonal_{x}_{j}',[x,91.31,(a if j%2==0 else b)*sign],[x,92.66,(b if j%2==0 else a)*sign],.12,'D15_bridge_truss_diagonal')
 # Deck crossmembers transfer floor load into both side frames.
 for j,d in enumerate([19.625,25.75,31.875]):
  z=d*sign;cube(f'SA_D15_{side}_BridgeCrossTie_{j}',[-85.9,92.6,z-.08],[-82.1,92.76,z+.08],'D15_bridge_transverse_frame')
for room in P['rooms']:
 idx=room['allocation']['source_envelope_index'];z=sum(room['allocation']['allocation_z'])/2;u=room['below_unit'];proto=next(p for p in U['prototypes']if p['key']==u['source_recipe_key']);assert sha(R/proto['editable_source'])==proto['editable_source_sha256'];lower.append({'source_index':idx,'owner':u['rebuild_identity'],'allocation_sha256':u['allocation_sha256'],'native_source':proto['editable_source'],'native_sha256':proto['editable_source_sha256'],'runtime_source':proto['model_file'],'runtime_sha256':proto['sha256'],'origin':u['source_origin_world_xyz'],'yaw':u['source_yaw_godot'],'persistent_structure_only':True,'rendering_policy':'Persistent contacts hidden to avoid coincident source skins; original visual remains residency managed','selected_prefixes':['SUI_Floor','SUI_Ceiling_','SUI_Wall_'],'contacts':room['receiving_contacts']})
 # Retained lower walls start0.24m above their source floor. Real base rails
 # will be extruded from those exact source footprints in build_native.py.
 for v in [-3.35,-1.7,0,1.7,3.35]:
  cube(f'SA{idx}_D15FloorJoist_{v}',[-81.95,92.6,z+v-.08],[-69.05,92.76,z+v+.08],'D15_room_floor_joist')
 for x in [-81.85,-75.3,-69.9]:cube(f'SA{idx}_D15CrossTie_{x}',[x-.1,92.6,z-3.5],[x+.1,92.76,z+3.5],'D15_room_transverse_tie')
 for v in [-3.3,0,3.3]:
  x=-85.8;zz=z+v;toe=box(x-.1,zz-.1,x+.1,zz+.1);o=owner(84,toe)
  cube(f'SA{idx}_D14FloorPier_{v}',[x-.1,84,zz-.1],[x+.1,88.10,zz+.1],'D13_street_to_D14_floor_pier');supports.append({'name':parts[-1]['name'],'position':[x,84,zz],'full_toe_area_m2':.04,'owner':o,'deck':'D13'})
  cube(f'SA{idx}_D14FloorCrossbeam_{v}',[-85.9,88.10,zz-.1],[-69.05,88.28,zz+.1],'D14_retained_floor_bridge')
 for x in [-81.85,-75.3,-69.9]:cube(f'SA{idx}_D14FloorTie_{x}',[x-.1,88.10,z-3.5],[x+.1,88.28,z+3.5],'D14_retained_floor_transverse_tie')
T={'schema':'astraea.star_atlas_specialty_structural_receiving.v1','base_commit':'8858b37fe732020d16072c01bc6f95a530343fce','model_file':'StarAtlasSpecialtyStructuralReceiving.glb','parts':parts,'support_toes':supports,'lower_structural_owners':lower,'source_pins':{p:sha(R/p)for p in ['Game/data/architecture/STAR_ATLAS_UNITS.json','Game/data/architecture/CENTRAL_RESIDENTIAL_STREETS.json','Game/data/generated/structural_meshes.json','Game/data/generated/received_structural_meshes.json','Game/docs/master_source/MASTER_CURRENT_APPLICATION.json','Game/docs/master_source/MASTER_FULL_CONTENT_INDEX.json','BlenderCatalogue/assets/residential_production_batch/inputs/PROPOSED_FULL_1000_PRODUCTION_ROWS.json']},'culling_preserved':True,'new_units':0,'new_source_ids':0,'structural_capacity_accepted':False,'geometric_load_path':'D13 retained street owner -> floor piers/crossbeams -> retained D14 floor/base rails/walls/roof -> fitted roof posts -> D15 floor frame; D14 street owners -> bridge piers/crossmembers -> D15 longitudinal floor bridge. Source/structural geometry only, no load capacity certificate.'}
(W/'PLAN.json').write_text(json.dumps(T,indent=2)+'\n');print('Prepared',len(parts),'frame members and',len(supports),'exact owner-supported toes')
