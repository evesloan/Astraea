from pathlib import Path
import json,hashlib,math
R=Path(__file__).resolve().parents[3];W=R/'BlenderCatalogue/assets/quiet_court_finish_20261022';P=R/'Game/quiet_court_finish_20261022';W.mkdir();P.mkdir();(P/'runtime').mkdir();(P/'evidence').mkdir();S=R/'BlenderCatalogue/assets/quiet_lift_receiving_20261009';d=json.loads((S/'LIFT_GEOMETRY_PLAN.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();cat=json.loads((R/'BlenderCatalogue/catalogue_manifest.json').read_text());assets=next(v for v in cat.values() if isinstance(v,list) and v and isinstance(v[0],dict) and 'catalogue_id'in v[0]);sources=[a for a in assets if a['catalogue_id'] in ['AST-BOT-008','AST-BOT-009']]
for a in sources:assert sha(R/'BlenderCatalogue'/a['source'])==a['source_sha256'];assert sha(R/'Game/assets/models'/(a['catalogue_id']+'.glb'))==a['export_sha256']
placements=[];beds=[]
for part in d['parts']:
 if part['category']!='soil' and not part['name'].startswith('GalleryPlant_'):continue
 vs=part['verts'];lo=[min(v[k] for v in vs) for k in range(3)];hi=[max(v[k] for v in vs) for k in range(3)];x=(lo[0]+hi[0])/2;z=(lo[2]+hi[2])/2;upper=part['name'].startswith('GalleryPlant_');count=3 if upper else 8;scale=.55 if upper else .85
 for i in range(count):
  if upper:px=x;pz=z+(i-1)*.65
  else:ang=2*math.pi*i/count;px=x+(hi[0]-lo[0])*.3*math.cos(ang);pz=z+(hi[2]-lo[2])*.3*math.sin(ang)
  placements.append(dict(name='CourtPlant_'+part['name']+'_'+str(i),catalogue_id='AST-BOT-009' if i%3 else 'AST-BOT-008',position=[px,hi[1],pz],yaw=0 if upper else 2*math.pi*i/count,scale=scale,receiving_bed=part['name'],bed_min=lo,bed_max=hi))
 beds.append(part['name'])
plan=dict(parent='0ae12c0ad5afd92062286ac4117d6306d1e1bea0',native_source=str((S/'source/architecture_lift_fit.blend').relative_to(R)),native_sha256=sha(S/'source/architecture_lift_fit.blend'),installed_glb='QUIET_GROVE_ARCHITECTURE_lift_r003.glb',installed_sha256=sha(S/'exports/architecture_lift_fit.glb'),source_plan_sha256=sha(S/'LIFT_GEOMETRY_PLAN.json'),sources=sources,placements=placements,beds=beds,materials={'warm_stone':[.82,.73,.58,1],'ivory_enamel':[.91,.84,.69,1],'warm_walnut':[.53,.29,.13,1],'champagne_metal':[.62,.47,.26,1],'oatmeal_weave':[.75,.65,.48,1]},fixtures=79,fixture_energy=2.8,fixture_range=16,light_budget=8,structural_geometry_unchanged=True,capacity_added=0,visual_accepted=False)
(P/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print('plantings',len(placements),'beds',len(beds))
