from pathlib import Path
import json,hashlib,sys,re,zipfile
import numpy as np
from shapely.geometry import Polygon,box,LineString
from shapely.ops import unary_union
R=Path(__file__).resolve().parent;G=Path('/workspace/shared/Astraea_recovery_20261007_AXWr5x/Game');C=R/'candidate/Game'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
old=load(G/'data/spatial_layout.json');before=load(G/'data/generated/structural_meshes.json');after=load(C/'data/generated/structural_meshes.json');layout=load(C/'data/spatial_layout.json')
assert after['regions'][:-2]==before['regions'];assert layout['regions'][:-2]==old['regions']
assert {k:v for k,v in old.items() if k!='regions'}=={k:v for k,v in layout.items() if k!='regions'}
mesh=lambda r:unary_union([Polygon(t) for t in r['triangles']])
shapes={r['id']:mesh(r) for r in after['regions']};added=after['regions'][-2:];axial=shapes['D06_fore_route']
slab_hits=[]
for a in added:
 for b in before['regions']:
  area=shapes[a['id']].intersection(shapes[b['id']]).area
  height=min(a['floor_y'],b['floor_y'])-max(a['floor_y']-a['thickness'],b['floor_y']-b['thickness'])
  if area>1e-8 and height>1e-8:slab_hits.append([a['id'],b['id'],area,height])
assert not slab_hits
sys.path.insert(0,str(C/'tools'));from theater_incremental_preservation import effective_shapes
el={x['deck_id']:x['floor_elevation_m'] for x in load(G/'data/design_contract.json')['deck_datums']}
owners=effective_shapes(old,el);all_owner_hits=[]
for a in added:
 for b in old['regions']:
  y=el[b['deck']]+b.get('offset_y',0);area=shapes[a['id']].intersection(owners[b['id']]).area
  if area>1e-8 and min(27,y)-max(26.76,y-b.get('thickness',.24))>1e-8:all_owner_hits.append([a['id'],b['id']])
assert not all_owner_hits
# Use only the read-only GLB decoder, never execute the old proposal screen.
helper=Path('/workspace/scratch/375c2e438292/botanical_court_proposal_20261007/screen_proposal.py').read_text();ns={'__file__':'/workspace/scratch/375c2e438292/botanical_court_proposal_20261007/screen_proposal.py'};exec(helper[:helper.index('compiled=json.loads')],ns)
b10=zipfile.ZipFile(ns['WP10']).read('WP10_D06_directory_03/exports/WP10_moss_sanctuary.glb');b04=(ns['WP04']/'exports/WP04_botanical_nursery.glb').read_bytes()
objects={'WP10':ns['glb_bounds'](b10),'WP04':ns['glb_bounds'](b04,np.array([8,27,-216]))}
(R/'SOURCE_OBJECT_BOUNDS.json').write_text(json.dumps(objects,indent=2)+'\n')
source_hits=[];portal_hits=[]
receivers=[('WP10',box(-8,-218.1,-4,-213.9),30.6),('WP04',box(4,-219,8,-213),31.2)]
for package,obs in objects.items():
 for o in obs:
  a,b=o['min'],o['max'];foot=box(a[0],a[2],b[0],b[2])
  for band in added:
   if min(27,b[1])-max(26.76,a[1])>1e-6 and foot.intersection(shapes[band['id']]).area>1e-6:source_hits.append([package,o['name'],band['id']])
  for label,receiver,top in receivers:
   if min(top,b[1])-max(27,a[1])>1e-5 and foot.intersection(receiver).area>1e-5:portal_hits.append([package,o['name'],label])
assert not source_hits,source_hits;assert not portal_hits,portal_hits
walk=unary_union([shapes[r['id']] for r in after['regions'] if r['floor_y']==27])
assert walk.covers(box(-8,-238,8,-208))
seams=[]
for r in added:
 contact=axial.boundary.intersection(shapes[r['id']].boundary).length;assert abs(contact-30)<1e-8
 seams.append({'owner':r['id'],'axial_shared_edge_m':contact,'level_delta_m':r['floor_y']-27,'duplicate_area_m2':axial.intersection(shapes[r['id']]).area})
for label,receiver,top in receivers:assert walk.covers(receiver)
# Continuous swept rectangular footprints, not only center points. Stop at receiver edge: interiors remain unadopted.
routes=[]
for label,x in [('port',-6.8),('starboard',6.8)]:
 sweep=LineString([(0,-240),(0,-216),(x,-216)]).buffer(1.2,cap_style='square',join_style='mitre')
 assert walk.buffer(1e-8).covers(sweep)
 routes.append({'name':label,'clear_width_m':2.4,'footprint':'continuous square-cap/mitre 1.2m buffered route; conservative floor-support envelope only','centerline':[[0,-240],[0,-216],[x,-216]],'supported':True})
# Existing uninterrupted axial reservation and upper slab are exact, including its actual underside.
assert axial.covers(box(-4,-238,4,-208))
upper=next(r for r in before['regions'] if r['id']=='D07_fore_route')
assert next(r for r in after['regions'] if r['id']=='D07_fore_route')==upper
# Inventory potential acceptance consumers and exact current hash dependencies; do not modify them.
changed=['data/spatial_layout.json','data/generated/structural_meshes.json','docs/LAYOUT_COMPILE_CHECKS.json','tools/compile_layout.py']
hashes={p:sha(G/p) for p in changed};consumers=[]
for folder in ['tools','tests','docs','data/architecture']:
 for p in (G/folder).rglob('*'):
  if not p.is_file() or p.suffix not in ['.py','.gd','.json','.md'] or p.stat().st_size>20_000_000:continue
  s=p.read_text(errors='replace');tokens=[k for k,v in hashes.items() if v in s]
  lines=[]
  if p.suffix in ['.gd','.py']:
   for n,line in enumerate(s.splitlines(),1):
    if any(t in line for t in ['structural_meshes.json','spatial_layout.json','LAYOUT_COMPILE_CHECKS.json','medical_triage_successor_guard','compile_layout.py']):lines.append({'line':n,'text':line[:320]})
  if tokens or lines:consumers.append({'path':str(p.relative_to(G)),'sha256':sha(p),'exact_old_hashes':tokens,'references':lines})
(R/'AFFECTED_CONSUMERS.json').write_text(json.dumps(consumers,indent=2)+'\n')
input_before=load(R/'SOURCE_INPUT_HASHES_BEFORE.json');input_after={p:sha(G/p) for p in input_before};assert input_before==input_after
(R/'SOURCE_INPUT_HASHES_AFTER.json').write_text(json.dumps(input_after,indent=2)+'\n')
proof={'status':'PASS: bounded source/compiler geometry; runtime adoption HOLD','counts':{'layout_before':len(old['regions']),'layout_after':len(layout['regions']),'compiled_before':len(before['regions']),'compiled_after':len(after['regions']),'new_floor_area_m2':240},'preserved_complete_layout_records':len(old['regions']),'preserved_complete_compiled_records':len(before['regions']),'source_inputs_hash_unchanged':len(input_before),'all_current_effective_owner_volume_hits':all_owner_hits,'compiled_volume_hits':slab_hits,'source_slab_aabb_hits':source_hits,'source_receiver_clear_volume_aabb_hits':portal_hits,'source_object_counts':{k:len(v) for k,v in objects.items()},'source_glb_sha256':{'WP10':hashlib.sha256(b10).hexdigest(),'WP04':hashlib.sha256(b04).hexdigest()},'contact_seams':seams,'swept_floor_routes':routes,'upper_axial_slab_underside_y':upper['floor_y']-upper['thickness'],'upper_axial_floor_clearance_m':upper['floor_y']-upper['thickness']-27,'new_upper_structures':0,'changed_or_removed_upper_structures':0,'limits':['No Godot/Blender run; no runtime physics or visual acceptance.','Whole room base floors are not present; this reaches package boundary, not supported interior journeys.','Open side-band end edges at Z-238 and Z-208 need receiving edge protection before public runtime use; no guard added outside scope.','Geometric floor contact is not structural load certification.','WP04 native/export identity discrepancy remains held; decoded retained export only.','Current laptop-owned source successors have not been inspected; rebase requires their issued bounds.','Existing medical_triage_successor_guard directly pins all four changed input files; proposed floor apply is held until exact predecessor recovery is integrated and engine regressions run.']}
(R/'VALIDATION.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps(proof,indent=2))
