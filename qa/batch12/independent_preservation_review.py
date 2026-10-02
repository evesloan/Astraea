"""Read-only historical file and raw catalogue/interface row preservation audit."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch12';BASE='d1bd76caf5ef2a10992514b312f9e3464de47fb4'
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
indices=[]
for name in ['standards/catalogue_interfaces.json','catalogue_manifest.json']:
 oldtext=subprocess.check_output(['git','show',BASE+':'+name],cwd=ROOT,text=True);nowtext=(ROOT/name).read_text();old=raw_records(oldtext);now=raw_records(nowtext)
 indices.append({'path':name,'old_record_count':len(old),'current_record_count':len(now),'old_61_raw_json_record_bytes_identical':len(old)==61 and old==now[:61],'current_whole_sha256':sha(nowtext.encode())})
protected=all(r['unchanged']for r in rows)
res={'passed':protected and all(x['old_61_raw_json_record_bytes_identical']for x in indices),'executed_script_sha256':sha(Path(__file__).read_bytes()),'baseline_commit':BASE,'protected_file_count':len(rows),'protected_files':rows,'source_and_common_bytes_unchanged':protected,'indices':indices,'scope':'All prior assets and shared standards/materials/textures except lead-owned interface index and source package group metadata. First61 canonical interface and catalogue row slices compared byte-for-byte.'}
(OUT/'independent_preservation_report.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps({k:v for k,v in res.items()if k!='protected_files'},indent=2))
