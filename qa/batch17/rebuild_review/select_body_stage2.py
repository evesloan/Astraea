"""Stage two only: select exact whole shape dictionaries from generated detailed collision."""
from pathlib import Path
import json,hashlib,argparse
p=argparse.ArgumentParser();p.add_argument('--detailed',required=True);p.add_argument('--selection',required=True);p.add_argument('--output',required=True);a=p.parse_args()
dp=Path(a.detailed);sp=Path(a.selection);base=json.loads(dp.read_text());spec=json.loads(sp.read_text())
assert hashlib.sha256(dp.read_bytes()).hexdigest()==spec['detailed_sha256']
result={}
for ident,row in base.items():
    shapes=row.get('shapes',row.get('precise_reference'));names=spec['assets'][ident]['retained_shape_names'];by={s['name']:s for s in shapes}
    assert len(by)==len(shapes)and len(set(names))==len(names)and set(names)<=set(by)
    result[ident]={'source_frame':row['source_frame'],'native_frame':row.get('native_frame',row.get('exchange_frame')),'shapes':[s for s in shapes if s['name']in names],'omitted_shape_names':[s['name']for s in shapes if s['name']not in names],'voids':row.get('preserve_voids',row.get('preserved_voids')),'motion_records':row.get('motion_records',[]),'derivation':'Reviewer stage2 literal selection from independently rebuilt generated detailed collision; no new hull, changed shape dictionary or inflation','original_source_input':False}
Path(a.output).write_text(json.dumps(result,indent=2)+'\n')
