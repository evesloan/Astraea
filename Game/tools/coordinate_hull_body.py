"""Resolve a bounded lower-body envelope against source allocations and built floors.
A section proposal, not an installed pressure shell or final structural acceptance.
"""
from pathlib import Path
import json,hashlib
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text())
paths=['data/hull_envelope.json','data/design_contract.json','data/reference/directory_allocations.json','data/reference/historical_guest_census.json','data/reference/D03_crew_envelopes.json','data/generated/structural_meshes.json','data/architecture/UPPER_SECTION_COORDINATION.json']
hull=Polygon(read(paths[0])['plan_xz_m']);datums=read(paths[1])['deck_datums'];programmes=read(paths[2])['records'];guests=read(paths[3])['guest_envelopes'];crew=read(paths[4])['records'];floors=read(paths[5])['regions'];upper=read(paths[6]);reserve=1.0
# Chined lower body opens into the full beam at D04; preserve all actual source envelopes.
# A12m D01inset clipped33.975m2 of existing end-spine floor.9m retains those interfaces.
insets={1:9.0,2:6.0,3:3.0}
def ring(p):return [list(q)for q in p.exterior.coords[:-1]]
def envelope(r):return box(r['x'][0],r['z'][0],r['x'][1],r['z'][1])
def deckof(r):return int(str(r['deck']).replace('D',''))
levels=[]
for i,d in enumerate(datums,1):
 inset=insets.get(i,0);outer=hull.buffer(-inset,join_style=2);inner=hull.buffer(-inset-reserve,join_style=2)
 groups={'directory':[(j,r)for j,r in enumerate(programmes)if deckof(r)==i], 'guest':[(j,r)for j,r in enumerate(guests)if deckof(r)==i], 'crew_bank':list(enumerate(crew))if i==3 else[]}
 conflicts=[]
 for kind,rows in groups.items():
  for j,r in rows:
   area=envelope(r).difference(inner).area
   if area>1e-6:conflicts.append({'kind':kind,'source_index':j,'outside_inner_area_m2':round(area,6)})
 floor_conflicts=[]
 for f in floors:
  if f['deck']!=d['deck_id']:continue
  shape=unary_union([Polygon(t)for t in f['triangles']]);area=shape.difference(inner).area
  if area>1e-6:floor_conflicts.append({'region':f['id'],'outside_inner_area_m2':round(area,6)})
 levels.append({'deck':d['deck_id'],'floor_y':d['floor_elevation_m'],'plan_inset_m':inset,'outer_boundary':ring(outer),'inner_reservation_boundary':ring(inner),'source_counts':{k:len(v)for k,v in groups.items()},'allocation_conflicts':conflicts,'compiled_floor_conflicts':floor_conflicts,'section_role':'Proposed lower body'if i<=3 else'Body datum through D17'if i<=17 else'Reference fit only: use compact crown/private upper pavilions, not a full D18 outer wall'})
assert all(not d['allocation_conflicts'] and not d['compiled_floor_conflicts']for d in levels)
keel=-3.5
result={'schema':1,'scope':'Architectural lower-body/upper-body coordination proposal. No installed hull, shell collision, pressure enclosure, engine pod or final structural acceptance. Allocation clearance is plan-based, not a finished room check.','source_sha256':{p:hashlib.sha256((R/p).read_bytes()).hexdigest()for p in paths},'reference_outline_authority':'Historical calibrated1082x240m outline; concept deck labels do not override canonical18datums.','lower_body_knots':[{'y':keel,'inset_m':32,'purpose':'Provisional narrower flat keel boundary; validate thickness and equipment beneath D01'},{'y':-.5,'inset_m':9,'purpose':'Vertical D01seat preserves the existing0.24m floor slabs and lift pit pans before the chine slopes inward'},{'y':0,'inset_m':9},{'y':6,'inset_m':6},{'y':12,'inset_m':3},{'y':16.5,'inset_m':0}], 'body_top_y':106.5,'roof_rule':'Stop the general body roof at106.5. Continue only the compact crown and six same-unit private upper pavilions under UPPER_SECTION_COORDINATION. Preserve atrium and house opaque covers.','maximum_external_roof_y':114.5,'provisional_keel_y':keel,'total_height_m':114.5-keel,'wall_frame_glazing_reservation_m':reserve,'levels':levels,'summary':{'canonical_decks':18,'directory_source_allocations':len(programmes),'guest_source_allocations':len(guests),'crew_bank_source_allocations':len(crew),'allocation_conflicts':sum(len(d['allocation_conflicts'])for d in levels),'compiled_floor_conflicts':sum(len(d['compiled_floor_conflicts'])for d in levels),'source_or_runtime_geometry_changed':False},'rejected_trial':{'D01_inset_m':12,'source_programme_conflicts':0,'compiled_end_spine_outside_inner_area_m2':33.975,'decision':'Reduced to9m to preserve existing fore/aft structural route ends rather than cutting them silently'},'remaining_gates':['Generate and check actual shell bands, slopes, frames and soffits at full3D height','Check asset-owned floors and mesh bounds beyond compiled structural floors','Resolve engine/shuttle apertures, plant/service clearances and underfloor structure','Compose genuine hull-facing windows and deliberate space views with each occupied frontage','Adopt and fit compact D18command crown/private upper pavilions before removing old datum guides','Fit supports and wall thickness without intruding into protected grand volumes','Normal-player, cart, species and target-performance acceptance after geometry installation']}
(R/'data/architecture/HULL_BODY_SECTION_PROPOSAL.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result['summary']))
