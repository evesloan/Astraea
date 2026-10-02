"""Read-only byte and old-index preservation audit against accepted Batch09."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch10';BASE='ea303a53c42de3d8b9fb3f05ae513c5d83cbab59'
sha=lambda b:hashlib.sha256(b).hexdigest()
def raw_records(text):
 decoder=json.JSONDecoder();pos=text.index('[',text.index('"assets"'))+1;rows=[]
 while True:
  while text[pos].isspace() or text[pos]==',':pos+=1
  if text[pos]==']':return rows
  start=pos;_,pos=decoder.raw_decode(text,pos);rows.append(text[start:pos].encode())
rows=[]
for line in subprocess.check_output(['git','ls-tree','-r','-z',BASE],cwd=ROOT).split(b'\0'):
 if not line:continue
 meta,path=line.split(b'\t',1);name=path.decode();mode,kind,oid=meta.decode().split()
 if kind!='blob' or not name.startswith(('assets/','standards/','textures/','materials/')):continue
 if name in ['standards/catalogue_interfaces.json','standards/source_package_groups.json']:continue
 actual=subprocess.check_output(['git','hash-object','--',name],cwd=ROOT,text=True).strip() if (ROOT/name).is_file() else None
 rows.append({'path':name,'baseline_git_blob':oid,'current_git_blob':actual,'unchanged':actual==oid})
oldtext=subprocess.check_output(['git','show',BASE+':standards/catalogue_interfaces.json'],cwd=ROOT,text=True)
nowtext=(ROOT/'standards/catalogue_interfaces.json').read_text();old=raw_records(oldtext);now=raw_records(nowtext)
protected=all(r['unchanged']for r in rows);identical=len(old)==51 and old==now[:51]
res={'passed':protected and identical,'baseline_commit':BASE,'protected_file_count':len(rows),'protected_files':rows,'source_and_common_bytes_unchanged':protected,'old_interface_record_count':len(old),'old_51_raw_json_record_bytes_identical':identical,'index_whole_sha256':sha(nowtext.encode()),'scope':'Every prior asset and shared standard/material file except lead-owned index/package group metadata. The first 51 canonical interface row slices are compared byte-for-byte.'}
(OUT/'independent_preservation_report.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps({k:v for k,v in res.items()if k!='protected_files'},indent=2))
