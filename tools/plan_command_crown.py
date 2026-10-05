"""Reversible D18 spatial proposal; never edits allocation sources or runtime floors."""
from pathlib import Path
import json,hashlib
from shapely.geometry import Polygon,box,LineString
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'data/reference/directory_allocations.json'
records={r['programme_key']:r for r in json.loads(source.read_text())['records']if r['deck']==18}
# The bridge and public observation room are shaped terminal volumes.
shapes={
 '01':[[-30,-172],[30,-172],[36,-160],[36,-118],[-36,-118],[-36,-160]],
 '02':[[10,-70],[16,-70],[16,-78],[36,-78],[36,-28],[10,-28]],
 '03':[[-36,-78],[-16,-78],[-16,-70],[-10,-70],[-10,-28],[-36,-28]],
 '04':[[10,-24],[36,-24],[36,28],[10,28]],
 '05':[[-36,-24],[-10,-24],[-10,14],[-36,14]],
 '06':[[-36,18],[-10,18],[-10,60],[-36,60]],
 '07':[[10,32],[36,32],[36,60],[10,60]],
 '08':[[-36,64],[-10,64],[-10,102],[-36,102]],
 '09':[[-36,142],[36,142],[36,182],[26,194],[-26,194],[-36,182]],
 '10':[[10,64],[36,64],[36,102],[10,102]],
}
result=[]
core=box(-7.8,-113,7.8,-80)
for suffix,points in shapes.items():
 key='D18_directory_'+suffix;p=Polygon(points);r=records[key]
 assert p.is_valid and p.intersection(core).area==0
 result.append({'programme_key':key,'name':r['name'],'source_allocation':{'x':r['x'],'z':r['z']},'proposed_floor_boundary':points,'proposed_area_m2':p.area,'status':'Reversible spatial proposal; no existing geometry moved, no final capacity or art acceptance','entrance_intent':'Controlled fore bridge vestibule'if suffix=='01'else'Public observation arrival from central gallery'if suffix=='09'else'Screened side service/controlled corridor','floor_y':106.5})
assert set(records)=={r['programme_key']for r in result}
for i,a in enumerate(result):
 for b in result[i+1:]:assert Polygon(a['proposed_floor_boundary']).intersection(Polygon(b['proposed_floor_boundary'])).area<1e-6
proposal={'schema':1,'scope':'D18 crown massing proposal for full-ship section coordination. Source envelopes preserved; not runtime construction or a recovered historical layout. Public/service access and working functions require detailed fitting.','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'references_visually_reopened':['REF-546a6287cb','REF-f685af904b','REF-e66ade3d9f'],'reference_authority':'Use stepped/curved hull and integrated circulation composition; canonical master deck heights and counts supersede contradictory labels and arithmetic in concept sheets.','reason':'The inherited D18 allocations span932m of a1082m vessel and reach196m across at the centre. Keeping every rectangle fixed would drive a nearly full-length/full-width top storey and undermine the stepped upper silhouette.','source_programmes':10,'programmes':result,'preserved_central_core':{'boundary':list(core.exterior.coords)[:-1],'moving_cabin_top_y':109.44,'authored_shaft_cap_top_y':109.85},'controlled_bridge_vestibule':{'x':[-4,4],'z':[-118,-113],'intent':'Explicit controlled bridge entry across the existing fore-route slab; not a diagnosed missing runtime floor'},'service_link_reservations':[{'id':'screened_fore_crosslink','width_m':3.6,'path_xz':[[-21,-88],[-13,-88],[-13,-115],[13,-115],[13,-86],[21,-86]],'intent':'Join both staff-riser lobbies through a shared controlled bridge junction, outside the public viewing gallery; intersects the controlled bridge vestibule deliberately'},{'id':'port_side_entry','width_m':3.6,'path_xz':[[-13,-88],[-13,-74],[-8,-74]]},{'id':'starboard_side_entry','width_m':3.6,'path_xz':[[13,-86],[13,-74],[8,-74]]}],'existing_cover_reconciliation':{'region':'D18_starboard_house_cover','retain_geometry':True,'current_role':'Opaque D17house cover and future Bridge briefing substrate','proposed_role':'Retained D17house roof/cover; remove the future Bridge briefing ownership only if the new crown placement is adopted','status':'No runtime floor or ownership changed by this proposal'},'aft_arrival_and_alternative_descent':{'status':'Spatial reservation only; no new lift/stair geometry','foyer_area_scope':'Gross receiving envelope; public walkable floor excludes screened service strips and core obstacles','foyer_boundary':[[-36,102],[36,102],[36,142],[-36,142]],'two_level_core_boundary':[[-7.8,106],[7.8,106],[7.8,139],[-7.8,139]],'floor_heights':[102,106.5],'lift_gate_xz':[-1.8,113],'stair_origin':[3,102,123],'stair_file':'AST-CIR-001_H450.glb','purpose':'A second descent to the existing D17 aft spine; breaks the single-ended D18 public journey and gives Upper Horizon a receiving space','public_bypass_x':[[3.5,7.8],[-7.8,-3.5]],'minimum_join_to_observation_m':3,'remaining_gate':'Fit shaft roof, actual entrances and walk/cart turns; proposed foundation/support remains unbuilt'},'public_gallery_reservation':{'x':[-4,4],'z':[-80,102],'intent':'Direct central-core to upper-horizon route, without passing through the command rooms'},'observation_service_links':[{'id':'port_observation_service','width_m':3.6,'path_xz':[[-8,100],[-8,104],[-32,104],[-32,142]]},{'id':'starboard_observation_service','width_m':3.6,'path_xz':[[8,100],[8,104],[32,104],[32,142]]}],'screened_side_corridor_reservations':[{'x':[-10,-6],'z':[-78,102]},{'x':[6,10],'z':[-78,102]}],'dimensions':{'source_longitudinal_span_m':932,'proposed_longitudinal_span_m':366,'source_max_transverse_span_m':196,'proposed_transverse_span_m':72,'proposed_programme_floor_area_m2':sum(r['proposed_area_m2']for r in result)},'proposed_vertical_stop_strategy':{'central_public_core':'Keep all18 installed stops unchanged','four_unbuilt_outlying_public_cores':'Terminate atD17 under the lower roof, with D18 reached through the installed central core or proposed aft D17/D18 connection','central_staff_risers':'Retain proposed D18 access inside the raised crown','other_staff_risers':'Coordinate terminal levels with their local roof section; do not extend every shaft through the stepped roof','status':'Proposal only; not yet applied to the five-core reservation register'},'atrium_support_and_cover_gate':{'retain_opaque_cover':{'x':[-48,48],'z':[-64,64],'floor_y':106.5},'crown_wall_x':[-36,36],'lower_roof_shoulders_m':12,'support_rule':'No new downward posts inside the protected central void. Reserve and resolve a transfer/support system bearing at existing protected perimeter zones; no engineering load acceptance claimed','status':'Beam depth, bearings and headroom require explicit section before construction'},'roof_gate':'Reserve clear occupied height above106.5 and the actual shaft cap above109.85 within118m overall. Roof profile, structural depth, pressure enclosure and high-level glazing are not yet authored.','unchanged':['All18deck datums','All161programme identities','1000guest unit count','100retail address count','400crew target','Existing constructed central core and other districts'],'remaining_gates':['Reconcile D17 guest houses and81luxury replacements with the stepped roof; no upper guest allocations changed here','Fit public/controlled entry vestibules and actual separate staff-riser connections','Verify command workstations, emergency egress and all-species operating space','Design curved observation glazing and views with the hull','Resolve roof/atrium cover ownership, structure and support','Test normal-play access before adopting this proposal as constructed layout']}
for link in proposal['service_link_reservations']:
 corridor=LineString(link['path_xz']).buffer(link['width_m']/2,cap_style=2,join_style=2)
 assert corridor.intersection(core).area<1e-6,link['id']
 assert all(corridor.intersection(Polygon(r['proposed_floor_boundary'])).area<1e-6 for r in result),link['id']
 assert corridor.intersection(box(-4,-80,4,102)).area<1e-6,link['id']
terminal=Polygon(proposal['aft_arrival_and_alternative_descent']['two_level_core_boundary'])
assert all(terminal.intersection(Polygon(r['proposed_floor_boundary'])).area<1e-6 for r in result)
for link in proposal['observation_service_links']:
 corridor=LineString(link['path_xz']).buffer(link['width_m']/2,cap_style=2,join_style=2)
 assert corridor.intersection(terminal).area<1e-6
 assert all(corridor.intersection(Polygon(r['proposed_floor_boundary'])).area<1e-6 for r in result)
 assert corridor.intersection(box(-4,-80,4,102)).area<1e-6
if (ROOT/'data/architecture/AFT_CROWN_LINK.json').exists():
 proposal['aft_arrival_and_alternative_descent']['status']='Two-level core authored in AFT_CROWN_LINK.json; verify current tests. Broader foyer remains an unbuilt proposal'
 proposal['aft_arrival_and_alternative_descent']['remaining_gate']='Complete broader foyer, service entrances and normal-play review; wider crown programme remains unadopted'
(ROOT/'data/architecture/D18_COMMAND_CROWN_PROPOSAL.json').write_text(json.dumps(proposal,indent=2)+'\n')
print(json.dumps(proposal['dimensions']))
