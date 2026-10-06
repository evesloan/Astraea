from pathlib import Path
import json,hashlib
import numpy as np
R=Path(__file__).resolve().parent;P=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section');objects=[o for o in json.loads((P/'source/geometry.json').read_text())['objects']if o['role']!='preview_only'];rows=[]
for deck,y,z,kind in [('D11',69.5,-171,'guest'),('D12',78,-171,'guest'),('D13',84,-171,'guest'),('D11',69.5,-257,'staff')]:
 lo=np.array([-34.970,y,z-2.67]);hi=np.array([-34.770,y+3.60,z+2.67]);hits=[];bearings=[]
 for o in objects:
  v=np.array(o['vertices_world']);a=v.min(0);b=v.max(0)
  if (np.minimum(hi,b)-np.maximum(lo,a)>1e-8).all():hits.append(o['name'])
 for dz in [-2.40,2.40]:
  for h in [.35,1.4,2.7]:
   point=[-34.75,y+h,z+dz];matches=[]
   for o in objects:
    if not o['name'].startswith('east_acoustic_wall_'):continue
    v=np.array(o['vertices_world']);a=v.min(0);b=v.max(0)
    if a[1]+.05<=point[1]<=b[1]-.05 and a[2]+.10<=point[2]<=b[2]-.10 and abs(a[0]-point[0])<1e-8:matches.append(o['name'])
   assert matches,(deck,z,h,dz)
   bearings.append({'point_world':point,'actual_unchanged_wall_part':matches[0],'fixed_bracket_range_x':[-34.79,-34.735],'attachment':'35mm bridge from header/pocket back toward wall, including15mm bearing/fastener engagement. Only these fixed wall attachments have permitted source bearing; no moving-leaf penetration.'})
 assert not hits,hits
 rows.append({'id':f'{deck}_{kind}_secondary_{abs(z)}','clear_opening_world_z':[z-1.7,z+1.7],'clear_height':3.4,'frame_and_continuous_leaf_sweep_bounds':{'min':lo.tolist(),'max':hi.tolist()},'proposed_family':'AST-DOR-003 genuine four-leaf/two-rank3.4m derivative; guest acoustic/opaque SunCorp staff finishes as appropriate','new_source_representation':'Four new self-contained wall-hung assemblies; no cut in original wall or floor and no claim that a bare opening is operational','complete_leaf_parameters':{'inner_body_width_m':.845,'outer_body_width_m':.865,'inner_stroke_m':1.740,'outer_stroke_m':.890,'including_seal_max_open_halfwidth_m':2.5975,'fixed_header_halfwidth_m':2.67,'leaf_top_relative_y':3.38,'header_bottom_relative_y':3.4,'header_top_relative_y':3.6},'existing_inner_wall_clearance_m':.020,'existing3_4m_route_clearance_m':.030,'retained_geometry_contacts_excluding_explicit_wall_bearings':hits,'fixed_wall_bearings':bearings,'floor_support':'Existing narrow3.4m threshold supports passage. Pockets are genuinely wall-hung from the listed side-wall contacts, not assumed to stand on the unbuilt floor outside the threshold. No new floor strip.','remaining':['Actual derivative-owned channel/roller geometry and sweeps','Fixed attachment strength not certified','External guest/staff receiving route remains parent-owned/unbuilt','Shared input/controller binding and physical cart/door tests after integration']})
out={'status':'Additional source proposal accounting for all three secondary guest apertures and backstage staff portal; not authored','source_geometry_sha256':hashlib.sha256((P/'source/geometry.json').read_bytes()).hexdigest(),'doors':rows,'no_cut_or_new_walking_floor':True,'frame_static_moving_bounds_contacts':0,'explicit_fixed_wall_bearings':24,'not_claimed':['Working doors','Completed external exits','Cabin/lift or other gate approval applied to these by implication']};(R/'SECONDARY_INTERFACE_DOOR_PLAN.json').write_text(json.dumps(out,indent=2)+'\n');print('Four secondary/staff frames: no source-envelope contacts;24actual fixed wall bearing locations identified. Proposal only.')
