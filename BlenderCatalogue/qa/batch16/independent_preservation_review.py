"""Independent protected-file, old-row and canonical-index audit; read-only."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch16';BASE='b8e259f451d1bcdf67d049089caf04caf7a33da7'
sha=lambda b:hashlib.sha256(b).hexdigest()
def raw_records(text):
 decoder=json.JSONDecoder();pos=text.index('[',text.index('"assets"'))+1;rows=[]
 while True:
  while text[pos].isspace() or text[pos]==',':pos+=1
  if text[pos]==']':return rows
  start=pos;_,pos=decoder.raw_decode(text,pos);rows.append(text[start:pos].encode())
protected_document=json.loads((OUT/'prior_protected_source_hashes.json').read_text());protected={x['path']:x['sha256'] for x in protected_document['files']};rows=[]
for name,expected in protected.items():
 p=ROOT/name;actual=sha(p.read_bytes()) if p.exists() else None
 rows.append({'path':name,'baseline_sha256':expected,'current_sha256':actual,'unchanged':actual==expected})
indices=[]
for name in ['standards/catalogue_interfaces.json','catalogue_manifest.json']:
 oldtext=subprocess.check_output(['git','show',BASE+':'+name],cwd=ROOT,text=True);nowtext=(ROOT/name).read_text();old=raw_records(oldtext);now=raw_records(nowtext)
 indices.append({'path':name,'old_record_count':len(old),'current_record_count':len(now),'old_77_raw_json_record_bytes_identical':len(old)==77 and old==now[:77],'old_77_decoded_objects_identical':json.loads(oldtext)['assets']==json.loads(nowtext)['assets'][:77],'current_whole_sha256':sha(nowtext.encode()),'canonical_whole_bytes_unchanged_since_freeze':oldtext==nowtext})
res={'passed':len(rows)==2626 and all(r['unchanged']for r in rows) and all(x['old_77_raw_json_record_bytes_identical'] and x['old_77_decoded_objects_identical']for x in indices),'executed_script_sha256':sha(Path(__file__).read_bytes()),'baseline_commit':BASE,'protected_file_count':len(rows),'protected_files':rows,'indices':indices,'scope':'Exact supplied2626 protected files and every old77 interface/catalogue object and raw record byte. A lead-promoted append may alter canonical container metadata but no historical row.'}
(OUT/'independent_preservation_report.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps({k:v for k,v in res.items() if k!='protected_files'},indent=2))
