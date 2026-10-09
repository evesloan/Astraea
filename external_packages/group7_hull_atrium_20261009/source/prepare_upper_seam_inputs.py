"""Bounded upper source-owner census request, not a scene or room rewrite."""
import json
from pathlib import Path
P=Path(__file__).resolve().parents[1];D=P/'dependencies/canonical_77a745'
old=json.loads((P/'qa/canonical_tree_9d6f85.json').read_text())['files'];paths={r['path'] for r in old};placements=[]
for r in json.loads((D/'Game/data/architecture/received_sections.json').read_text())['sections']:
 if r['translation_xyz'][1]>=69.5:
  placements.append({'key':r['programme_key'],'path':'Game/assets/models/'+r['model_file'],'origin':r['translation_xyz'],'yaw':r.get('rotation_y',0),'expected_sha256':r['source_sha256']})
for r in json.loads((D/'Game/data/architecture/REMAINING_BATCH_SECTIONS.json').read_text())['sections']:
 if r['position'][1]>=69.5:
  placements.append({'key':r['key'],'path':'Game/assets/models/'+r['glb'],'origin':r['position'],'yaw':r.get('rotation_y',0),'expected_sha256':r.get('sha256')})
catalogue=json.loads((D/'BlenderCatalogue/catalogue_manifest.json').read_text())['assets']
for prefix in ['AST-RES-','AST-CMD-']:
 for r in catalogue:
  if r['catalogue_id'].startswith(prefix) and r['catalogue_id'][-3:].isdigit():
   path='BlenderCatalogue/'+r['export']
   if path in paths:placements.append({'key':r['catalogue_id'],'path':path,'origin':[0,0,0],'yaw':0,'expected_sha256':None,'placement_authority':'World-coordinate house/crown export; verify against retained bootstrap/source before design use'})
request=sorted({r['path'] for r in placements});assert all(q in paths for q in request)
(P/'qa/input_request_upper_sources.json').write_text(json.dumps(request,indent=2)+'\n');(P/'qa/upper_source_placements_unconfirmed.json').write_text(json.dumps(placements,indent=2)+'\n');print('UPPER_INPUT_REQUEST',len(request))
