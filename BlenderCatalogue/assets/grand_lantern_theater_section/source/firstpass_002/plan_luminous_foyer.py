"""Pure proposed full-room foyer light coverage. No engine or source mutation."""
from pathlib import Path
import json,math,hashlib
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
R=Path(__file__).resolve().parent;P=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section');S=json.loads((P/'contracts/surface_manifest.json').read_text());old=json.loads((P/'source/geometry.json').read_text())['objects'];plans=[];skipped=[]
for deck,floor,upper in [('D11',69.5,'D12'),('D12',78,'D13'),('D13',84,None)]:
 if upper:
  row=next(s for s in S['surfaces']if s['region_id']==upper+'_theater_foyer_landings');support=unary_union([Polygon(p['boundary_xz'])for p in row['parts']]);y=row['absolute_floor_y']-.45;owner=row['region_id']
 else:support=box(-108.3,-153,-34.75,-116);y=91.4;owner='FP_rear_foyer_acoustic_ceiling'
 for x in [-108,-96,-84,-72,-60,-40]:
  for z in [-147,-138,-129,-120]:
   plate=box(x-1.5,z-.38,x+1.5,z+.38);missing=plate.difference(support).area
   if missing>1e-7:skipped.append({'deck':deck,'centre':[x,y,z],'missing_support_m2':missing});continue
   collisions=[]
   for o in old:
    if o['role']=='preview_only':continue
    vs=o['vertices_world'];lo=[min(v[k]for v in vs)for k in range(3)];hi=[max(v[k]for v in vs)for k in range(3)]
    if min(y,hi[1])-max(y-.18,lo[1])>3e-5 and plate.intersection(Polygon([(v[0],v[2])for v in vs]).convex_hull).area>1e-7:collisions.append(o['name'])
   if collisions:skipped.append({'deck':deck,'centre':[x,y,z],'old_structure_contacts':collisions});continue
   plans.append({'id':f'{deck}_foyer_opal_coffer_{x}_{z}','deck':deck,'mount_centre_world':[x,y,z],'backplate_size_xz':[3,.76],'housing_bottom_y':y-.18,'visible_opal_lens_size_xz':[2.76,.50],'visible_opal_lens_y':y-.155,'area_emitter_world':[x,y-.16,z],'area_emitter_size_xz':[2.70,.44],'aim_world':[0,-1,0],'source_support':owner,'backplate_missing_support_m2':missing,'minimum_body_height_above_floor_m':y-.18-floor,'material_reuse':['retained ivory enamel housing','champagne perimeter and short scalloped side profile','warm retained hospitality opal lens, copied visible luminous state'],'preview_trial_watts':500,'preview_color_linear':[1,.91,.80],'no_global_fill':True,'source_only':True})
result={'status':'Proposed visible architecture-sized coffer fixtures; actual source geometry/contacts and same-camera render required','base_source_sha256':'a3f1d01b0927ddd873986b2d1f2dbb44f234bced2b034c2cff42c2c0bfd8d0ce','diagnostic':'Prior6ceiling lanterns per foyer left500m² per fixture and the east arrival stair void with no overhead coverage. Visible coffer banks improve distribution; decorative existing lanterns stay.', 'new_coffers':plans,'rejected_grid_points':skipped,'counts_by_deck':{d:sum(p['deck']==d for p in plans)for d in ['D11','D12','D13']},'stair_void_remaining_gate':'Grid rejects unsupported holes; actual stair/landing mounted linear practicals remain needed. No pendant may be hung through a stair or protected route by implication.','optical_contract':'Analytic area emitters lie5mm below actual visible opal lenses, inset30mm per side; no hidden fill panels. Housing mounts to actual retained underside. Lens radiance/power are preview trials, not electrical/illumination certification.'}
(R/'PROPOSED_FOYER_COFFER_COVERAGE.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'counts':result['counts_by_deck'],'rejected':len(skipped)},indent=2))
