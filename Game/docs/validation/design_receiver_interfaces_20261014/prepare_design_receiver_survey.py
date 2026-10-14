from pathlib import Path
import json,struct,hashlib
C=Path(__file__).parent;R=Path('/workspace/astraea-protected-integration-20261012');P=C/'design_connections_20261014';P.mkdir(exist_ok=True);plan=json.loads((C/'consolidated_all_eight_20261013/CONSOLIDATED_PLAN.json').read_text());source=json.loads((R/'RetainedConstruction/group2/SOURCE_MAP.json').read_text());wet=[]
for export in plan['G2_wet']['exports']:
 row=next(x for x in source['files']if x['source_path']==export['path']);b=(R/row['storage_path']).read_bytes();assert hashlib.sha256(b).hexdigest()==row['sha256']==export['sha256'];n=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+n]);parts=[]
 for node in d['nodes']:
  if 'mesh'not in node:continue
  assert not any(k in node for k in ['matrix','translation','rotation','scale'])
  for p in d['meshes'][node['mesh']]['primitives']:
   a=d['accessors'][p['attributes']['POSITION']]
   if any(k in node['name']for k in ['BearingPad','Column','RoofPanel','AftRoof']):parts.append({'name':node['name'],'min':a['min'],'max':a['max']})
 wet.append({'kit':export['kit'],'model_sha256':export['sha256'],'candidate':next(x for x in plan['G2_wet']['candidate_transforms']if x['kit']==export['kit']),'parts':parts})
out={'base':'3244fe82ef483995ca83ab78ced98abea198501a','floor_rows':plan['G2_floor_rows'],'wet':wet,'wet_terrace_y':plan['G2_wet']['terrace_y'],'wet_roof_max_y':plan['G2_wet']['roof_max_y'],'new_design_selected':False};(P/'DESIGN_RECEIVER_PLAN.json').write_text(json.dumps(out,indent=2)+'\n');print('DESIGN_RECEIVER_SURVEY_PLAN91FLOORS_2EXACTWETKITS')
