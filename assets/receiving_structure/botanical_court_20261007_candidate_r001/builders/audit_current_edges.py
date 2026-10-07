from pathlib import Path
import json,hashlib,sys
import numpy as np
from shapely.geometry import Polygon,box,LineString
from shapely.ops import unary_union
R=Path(__file__).resolve().parent;G=Path('/workspace/shared/Astraea_recovery_20261007_AXWr5x/Game');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text())
helper=Path('/workspace/scratch/375c2e438292/botanical_court_proposal_20261007/screen_proposal.py');ns={'__file__':str(helper)};exec(helper.read_text().split('compiled=json.loads')[0],ns)
comp=load(G/'data/generated/structural_meshes.json');level=unary_union([Polygon(t) for r in comp['regions'] if r['floor_y']==27 for t in r['triangles']]);records=[]
for side,x in [('port',-8),('starboard',8)]:
 out=box(x-1 if x<0 else x,-238,x if x<0 else x+1,-208)
 assert level.intersection(out).area==0
 records.append({'side':side,'edge_x':x,'z_interval':[-238,-208],'length_m':30,'installed_room_side_support_area_in_1m_strip_m2':0,'installed_room_side_enclosure_intervals':[],'open_intervals':[[-238,-208]],'future_portal_z':[-218.1,-213.9] if x<0 else [-219,-213]})
ship=(G/'scripts/ship.gd').read_text();assert all(x not in ship for x in ['WP04','WP10','moss_sanctuary','botanical_nursery'])
# Every relevant installed D06 local family and the nearest multi-deck core, at exact runtime transforms.
models=[('AST-GAR-003.glb',[-39,27,-27]),('AST-GAR-004.glb',[-52,27,0]),('AST-GAR-005.glb',[-52,27,0]),('AST-ATR-001.glb',[0,0,0]),('AST-CIR-005_spine_core.glb',[0,0,-272])]
model_bounds=[]
for file,at in models:
 p=G/'assets/models'/file;bounds=ns['glb_bounds'](p.read_bytes(),np.array(at));hits=[]
 for o in bounds:
  a,b=o['min'],o['max']
  if min(30.6,b[1])-max(27,a[1])<=1e-6:continue
  for r in records:
   if box(r['edge_x']-.45,-238,r['edge_x']+.45,-208).intersection(box(a[0],a[2],b[0],b[2])).area>1e-6:hits.append([r['side'],o['name']])
 assert not hits,hits
 model_bounds.append({'file':file,'sha256':sha(p),'placement_xyz':at,'objects':len(bounds),'edge_collision_candidates':hits,'overall_min':[min(o['min'][i] for o in bounds) for i in range(3)],'overall_max':[max(o['max'][i] for o in bounds) for i in range(3)]})
files=['scenes/main.tscn','scenes/ship.tscn','scripts/presentation.gd','scripts/ship.gd','scripts/structural_floor_builder.gd','scripts/garden_overlook.gd','scripts/canopy_terrace.gd','scripts/primary_atrium_core.gd','scripts/medical_welcome.gd','data/architecture/FORE_MIDSHIP_PUBLIC_CORE.json','data/generated/structural_meshes.json','data/spatial_layout.json']
report={'status':'READ-ONLY CURRENT GAME SOURCE/COLLISION-OWNER AUDIT; no engine execution','edges':records,'runtime_entry_chain':'presentation.gd -> scenes/ship.tscn -> ship.gd::_ready. No authored room loader interprets D06 directory reservations as runtime geometry.','source_meshes_are_not_adoption':'WP04/WP10 retained intake meshes are absent from the main-scene builder chain and receive no installed collision credit.','actual_collision_mechanisms':'structural_floor_builder builds compiled slab trimeshes. ship.model calls _static_contacts on visible meshes. build_structural_datums emits hull-outline datum beams, no directory room floors/enclosures.','nearby_runtime_models':model_bounds,'other_nearby_vertical_programs':'Thread/Shell and Orchard exchange at Y52.5; foodhall Y61; D05 installed medical welcome/triage is at forward core, not these Clinical Research/Pharmacy reservations. They provide no Y27 edge closure.','hashes':{f:sha(G/f) for f in files},'decision':'Close the entire 60m outer edge with supported fitted interim guards, including independently removable closure sections over future portal spans. Do not authorize room entry.','limits':'This authenticates source-defined installed ownership/placement, not an in-engine physics sweep or fresh import.'}
(R/'CURRENT_GAME_EDGE_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
