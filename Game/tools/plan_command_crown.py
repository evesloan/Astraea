"""Reversible D18 spatial proposal; never edits allocation sources or runtime floors."""
from pathlib import Path
import json,hashlib
from shapely.geometry import Polygon,box
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'data/reference/directory_allocations.json'
records={r['programme_key']:r for r in json.loads(source.read_text())['records']if r['deck']==18}
# The bridge and public observation room are shaped terminal volumes.
shapes={
 '01':[[-30,-172],[30,-172],[36,-160],[36,-118],[-36,-118],[-36,-160]],
 '02':[[10,-78],[36,-78],[36,-28],[10,-28]],
 '03':[[-36,-78],[-10,-78],[-10,-28],[-36,-28]],
 '04':[[10,-24],[36,-24],[36,28],[10,28]],
 '05':[[-36,-24],[-10,-24],[-10,14],[-36,14]],
 '06':[[-36,18],[-10,18],[-10,60],[-36,60]],
 '07':[[10,32],[36,32],[36,78],[10,78]],
 '08':[[-36,64],[-10,64],[-10,102],[-36,102]],
 '09':[[-36,126],[36,126],[36,166],[26,178],[-26,178],[-36,166]],
 '10':[[10,82],[36,82],[36,120],[10,120]],
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
proposal={'schema':1,'scope':'D18 crown massing proposal for full-ship section coordination. Source envelopes preserved; not runtime construction or a recovered historical layout. Public/service access and working functions require detailed fitting.','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'references_visually_reopened':['REF-546a6287cb','REF-f685af904b','REF-e66ade3d9f'],'reference_authority':'Use stepped/curved hull and integrated circulation composition; canonical master deck heights and counts supersede contradictory labels and arithmetic in concept sheets.','reason':'The inherited D18 allocations span932m of a1082m vessel and reach196m across at the centre. Keeping every rectangle fixed would drive a nearly full-length/full-width top storey and undermine the stepped upper silhouette.','source_programmes':10,'programmes':result,'preserved_central_core':{'boundary':list(core.exterior.coords)[:-1],'physical_top_clearance_y':109.44},'public_gallery_reservation':{'x':[-4,4],'z':[-80,126],'intent':'Direct central-core to upper-horizon route, without passing through the command rooms'},'screened_side_corridor_reservations':[{'x':[-10,-6],'z':[-78,124]},{'x':[6,10],'z':[-78,124]}],'dimensions':{'source_longitudinal_span_m':932,'proposed_longitudinal_span_m':350,'source_max_transverse_span_m':196,'proposed_transverse_span_m':72,'proposed_programme_floor_area_m2':sum(r['proposed_area_m2']for r in result)},'proposed_vertical_stop_strategy':{'central_public_core':'Keep all18 installed stops unchanged','four_unbuilt_outlying_public_cores':'Terminate atD17 under the lower roof, with D18 reached through the central core','central_staff_risers':'Retain proposed D18 access inside the raised crown','other_staff_risers':'Coordinate terminal levels with their local roof section; do not extend every shaft through the stepped roof','status':'Proposal only; not yet applied to the five-core reservation register'},'roof_gate':'Reserve clear occupied height above106.5 and cabin clearance above109.44 within118m overall. Roof profile, structural depth, pressure enclosure and high-level glazing are not yet authored.','unchanged':['All18deck datums','All161programme identities','1000guest unit count','100retail address count','400crew target','Existing constructed central core and other districts'],'remaining_gates':['Reconcile D17 guest houses and81luxury replacements with the stepped roof; no upper guest allocations changed here','Fit public/controlled entry vestibules and actual separate staff-riser connections','Verify command workstations, emergency egress and all-species operating space','Design curved observation glazing and views with the hull','Resolve roof/atrium cover ownership, structure and support','Test normal-play access before adopting this proposal as constructed layout']}
(ROOT/'data/architecture/D18_COMMAND_CROWN_PROPOSAL.json').write_text(json.dumps(proposal,indent=2)+'\n')
print(json.dumps(proposal['dimensions']))
