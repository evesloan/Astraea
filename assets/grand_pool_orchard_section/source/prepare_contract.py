"""Bounded source-only contract and triangulated compiler-floor previews. Never writes Godot."""
from pathlib import Path
import json,hashlib,sys,copy
sys.path.insert(0,'/workspace/scratch/375c2e438292/geometry-deps')
import shapely
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];C=R.parents[1];G=C.parent/'astraea-godot-production-20261003'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
P=json.loads((G/'data/architecture/GRAND_POOL_SECTION_PLAN.json').read_text())
for p,h in P['source_sha256'].items(): assert sha(G/p)==h,p
for p,h in P['catalogue_source_sha256'].items(): assert sha(C/p)==h,p
assert all(a['catalogue_id']!='AST-AQU-016' or a['family']=='grand_pool_orchard_section' for a in json.loads((C/'catalogue_manifest.json').read_text())['assets'])
(R/'source/planning_proposal_retained.json').write_text(json.dumps(P,indent=2)+'\n')
rect=lambda r:box(r[0],r[2],r[1],r[3])
outer=rect([-54,-8,-466,-398]);main=Polygon(P['shared_volume']['candidate_boundary_xz'])
void=unary_union([main,rect([-18,-11.1,-425.5,-415.7]),rect([-18,-13.5,-415.7,-410.2])])
upper_landing=rect([-14.0,-11.1,-425.5,-423.5])
market=outer.difference(void).union(upper_landing)
pool_shell=rect([-40.4,-21.6,-457.4,-406.6])
wet=outer.difference(unary_union([pool_shell,rect(P['public_interfaces']['D08_dry_arrival_bay_rect']),rect(P['public_interfaces']['D08_dry_approach_raised_deck_exclusion_rect']),rect(P['accessible_ramp']['gross_envelope']),rect(P['wet_market_link']['lift']['shaft_floor_exclusion_rect'])]))
# Supported top ramp landing joins the raised terrace; compiler, not exported asset, owns it.
wet=wet.union(rect(P['accessible_ramp']['top_landing_and_bridge']['rect'])).union(rect([-18,-16.2,-434,-430]))
# Staff streets meet the pre-existing frame sill at X-23.0 without entering cabin sweep.
staff=unary_union([rect(r) for r in P['staff']['upper_route_floor_rects']])
floors=[]
def add(id,deck,y,shape,role='guest_floor',thickness=.24):
 assert shape.is_valid and not shape.is_empty,id
 for i,p in enumerate(shapely.get_parts(shape)):
  if p.geom_type!='Polygon':continue
  name=id if len(shapely.get_parts(shape))==1 else id+'_'+str(i)
  floors.append({'id':name,'deck':deck,'floor_y':y,'offset_y':y-{'D08':44,'D09':52.5,'D10':61}[deck],'thickness':thickness,'priority':-1,'owner':'floor_compiler','boundary':[list(v)for v in p.exterior.coords[:-1]],'holes':[[list(v)for v in ring.coords[:-1]]for ring in p.interiors],'area_m2':p.area,'material_role':role,'triangles':[[list(v)for v in t.exterior.coords[:3]]for t in shapely.constrained_delaunay_triangles(p).geoms]})
add('D08_grand_pool_base','D08',44,outer)
add('D08_grand_pool_wet','D08',46.2,wet)
add('D08_grand_pool_core_tongue','D08',44,rect(P['public_interfaces']['new_floor_tongue_rect']))
add('D09_orchard_market_gallery','D09',52.5,market)
add('D09_orchard_market_core_tongue','D09',52.5,rect(P['public_interfaces']['new_floor_tongue_rect']))
add('D08_grand_pool_upper_staff','D08',46.2,staff)
add('D09_orchard_market_upper_staff','D09',52.5,staff)
add('D10_shared_table_reserved_cap','D10',61,outer)
# Five narrow, connected structural seats only, wholly outside protected court/homes and current circulation.
bearings=[{'name':'west_fore','x':[-61.4,-59.8],'z':[-454.2,-451.8]},{'name':'west_middle','x':[-61.4,-59.8],'z':[-433.2,-430.8]},{'name':'west_aft','x':[-61.4,-59.8],'z':[-406.2,-403.8]},{'name':'east_fore','x':[-6.8,-5.2],'z':[-466.6,-464.2]},{'name':'east_aft','x':[-6.8,-5.2],'z':[-405.2,-402.8]}]
keel=json.loads((C/'assets/lower_hull_body/source/body_contract.json').read_text());kp=Polygon(keel['rings'][0]['inner'])
compiled=json.loads((G/'data/generated/structural_meshes.json').read_text());homes=json.loads((G/'data/reference/historical_guest_census.json').read_text())['guest_envelopes'];alloc=json.loads((G/'data/reference/directory_allocations.json').read_text())['records']
for b in bearings:
 s=rect(b['x']+b['z']);assert kp.covers(s),b
 for a in homes+alloc:
  d=a.get('deck');d=int(d[1:])if isinstance(d,str)else d
  if d is not None and d<=7:assert s.intersection(rect(a['x']+a['z'])).area<1e-8,(b,a)
 for f in compiled['regions']:
  if f['floor_y']<=43.76:assert sum(s.intersection(Polygon(t)).area for t in f['triangles'])<1e-8,(b,f['id'])
 b.update(footing_y=[-3.2,-2.8],pier_y=[-2.8,43.76],retained_contact='AST-HUL-001 / HUL_KeelPan upper surface Y-3.2',plan_contact_area_m2=s.area)
# Verify low-profile common under-basin transfer can touch pan, without datum override.
D={'schema':1,'catalogue_id':'AST-AQU-016','family':'grand_pool_orchard_section','status':'Source-authored construction; not runtime acceptance','origin_gltf_xyz':[0,0,0],'coordinate_system':'Godot world XYZ metres; Blender=(x,-z,y), GLB=(x,y,z)','planning_provenance':{'file':'source/planning_proposal_retained.json','sha256':sha(R/'source/planning_proposal_retained.json'),'source':'data/architecture/GRAND_POOL_SECTION_PLAN.json','source_sha256':sha(G/'data/architecture/GRAND_POOL_SECTION_PLAN.json')},'programme_ids':['D08_directory_01','D09_directory_01'],'historical_aliases':{'D08_directory_01':{'historical':'D08_pool0','status':'Sourced historical alias only; ledger reconciliation owned by parent'},'D09_directory_01':'D09_market0'},'floor_regions':floors,'section':P['section'],'architectural_fit':{'under_basin_transfer_y':[43.76,44.4],'basin_shell_y':[44.4,44.8],'terrace_transfer_y':[43.76,45.96],'market_edge_beam_y':[50.95,52.26],'minimum_wet_clear_below_deep_edge_beams':4.75,'roof_transfer_y':[59.16,60.76],'central_wet_to_lowest_roof_beam_clear':12.96,'market_to_lowest_roof_beam_clear':6.66,'scope':'Finite geometric bearing/transfer connections for game architecture, not load certification. Local edge beams replace trial unobstructed soffit assumption; all canonical/wet datums preserved.'},'bearings':bearings,'plan_adjustments':[{'reason':'Actual unchanged commons_lift.gd PI placement gives fixed sill X-13.59..-13.50. Trial void east edge-13.18 leaves unsupported0.32m seam.','original_lift_extension_rect':[-18,-13.18,-415.7,-410.2],'adopted_lift_extension_rect':[-18,-13.5,-415.7,-410.2],'world_cabin_front_x':-13.6,'world_landing_gate_centre_x':-13.48,'world_sill_x':[-13.59,-13.5]},{'reason':'Top stair landing must be real horizontal compiler floor reaching the return flight, not an implied platform inside a void','upper_stair_landing_rect':[-14,-11.1,-425.5,-423.5],'floor_y':52.5,'area_m2':5.8}], 'opening':{'main_boundary':P['shared_volume']['candidate_boundary_xz'],'combined_before_stair_landing_boundary':[list(p)for p in void.exterior.coords[:-1]],'combined_before_stair_landing_area_m2':void.area,'upper_stair_landing_m2':5.8,'market_floor_area_m2':market.area,'rule':'No convex-hull replacement; use exact floor rings/holes and concave static collision'},'public_interfaces':P['public_interfaces'],'accessible_ramp':P['accessible_ramp'],'wet_market_link':copy.deepcopy(P['wet_market_link']),'market':P['market'],'staff':P['staff'],'protected':{'programmes':P['programmes'],'original_compiled_regions':250,'original_compiled_sha256':sha(G/'data/generated/structural_meshes.json'),'original_spatial_sha256':sha(G/'data/spatial_layout.json'),'guest_envelopes_sha256':sha(G/'data/reference/historical_guest_census.json'),'retail_allocations_sha256':sha(G/'data/reference/historical_atlas_allocations.json'),'D07_new_geometry_lower_limit_y':43.76,'D10_occupied_volume_above_y':61},'preserved_catalogue_inputs':{},'fixtures':[],'interfaces':[],'source_parts':[],'derivatives':{'forward_core':{'parent':'AST-CIR-005','source':'source/AST-CIR-005_forward_pool_market.blend','export':'exports/AST-CIR-005_forward_pool_market.glb','changed_original_objects':['CORE_OuterWall_07_-1','CORE_WallDado_07_-1','CORE_OuterWall_08_-1','CORE_WallDado_08_-1'],'all_other_objects':'Must compare unchanged against retained original'},'staff':{'parent':'AST-STF-009','source':'source/AST-STF-009_pool_market.blend','export':'exports/AST-STF-009_pool_market.glb','removed_original_objects':['STF_ShaftTopCap'],'all_other_objects':'Must compare unchanged against retained original'},'local_stair':{'parent':'AST-CIR-001','representation':'AST-CIR-001_H630_GPM','ownership':'Named derivative pieces embedded in AST-AQU-016 source/export; not a new unique design','rise_m':6.3,'risers':36,'clear_width':2.6,'going_m':.32}},'unfinished':['Runtime import, floor compiler adoption and exact250-record preservation','Door/gate/controller integration and full lift cabin sweep','Actual player/capsule and loaded four-product cart routes','Normal/effects-off in-ship source-matched visuals','Water simulation, water entry assistance, furnishing/stock, species fitting, acoustic systems and final art']}
D['wet_market_link']['D09_opening_extensions_rects'][1]=[-18,-13.5,-415.7,-410.2]
for f in ['assets/primary_atrium_core/source/AST-CIR-005_forward_core.blend','assets/primary_atrium_core/exports/AST-CIR-005_forward_core.glb','assets/lower_staff_network/source/AST-STF-009.blend','assets/lower_staff_network/exports/AST-STF-009.glb','assets/lower_hull_body/source/AST-HUL-001.blend','assets/lower_hull_body/exports/AST-HUL-001.glb','assets/circulation_architecture/source/build_switchback.py','assets/commons_lift_cabin/source/AST-CIR-003.blend','assets/guest_entry_door/source/AST-DOR-002.blend']:
 D['preserved_catalogue_inputs'][f]=sha(C/f)
(R/'source/connected_contract.json').write_text(json.dumps(D,indent=2)+'\n')
print(json.dumps({'floor_areas':{f['id']:f['area_m2']for f in floors},'bearings_clear':len(bearings),'market_void':void.area,'market_floor':market.area},indent=2))
