"""Verify existing protected source/common resources without writing any of them."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch09'
BASE='620908833951216425172c95dfdb337ec33afc4c'
sha=lambda b:hashlib.sha256(b).hexdigest()
raw=subprocess.check_output(['git','ls-tree','-r','-z',BASE],cwd=ROOT)
rows=[]
for line in raw.split(b'\0'):
 if not line:continue
 meta,path=line.split(b'\t',1);name=path.decode();mode,kind,oid=meta.decode().split()
 if kind!='blob':continue
 # All historical assets and shared resources; lead may legitimately change global catalogues.
 if not name.startswith(('assets/','standards/','textures/','materials/')):continue
 p=ROOT/name
 actual=subprocess.check_output(['git','hash-object','--',name],cwd=ROOT,text=True).strip() if p.is_file() else None
 rows.append({'path':name,'baseline_git_blob':oid,'current_git_blob':actual,'unchanged':actual==oid})
base_index=json.loads(subprocess.check_output(['git','show',BASE+':standards/catalogue_interfaces.json'],cwd=ROOT))
current_index=json.loads((ROOT/'standards/catalogue_interfaces.json').read_text())
old={a['catalogue_id']:a for a in base_index['assets']};new={a['catalogue_id']:a for a in current_index['assets']}
canonical=lambda a:json.dumps(a,ensure_ascii=False,indent=2).encode()
index_rows=[{'catalogue_id':k,'baseline_canonical_record_sha256':sha(canonical(v)),'current_canonical_record_sha256':sha(canonical(new[k])) if k in new else None,'unchanged_record':k in new and canonical(v)==canonical(new[k])} for k,v in old.items()]
# A promoted index can have six added records while preserving all original records.
source_rows=[r for r in rows if r['path'] not in ['standards/catalogue_interfaces.json','standards/source_package_groups.json']]
group_base=json.loads(subprocess.check_output(['git','show',BASE+':standards/source_package_groups.json'],cwd=ROOT))
group_now=json.loads((ROOT/'standards/source_package_groups.json').read_text())
group_expected=json.loads(json.dumps(group_base))
group_expected['revision']='source-family-delivery-02'
for g in group_expected['groups']:
 if g['name']=='Guest_Day_Use':g['asset_directories'].append('guest_use')
 if g['name']=='Library':g['asset_directories'].append('library_use')
group_only_authorized_additions=group_expected==group_now
result={'baseline_commit':BASE,'protected_file_count':len(source_rows),'protected_files':source_rows,'source_and_common_bytes_unchanged':all(r['unchanged'] for r in source_rows),'original_interface_record_count':len(index_rows),'original_interface_records':index_rows,'old_45_records_identical':len(index_rows)==45 and all(r['unchanged_record'] for r in index_rows),'index_file_whole_sha256':sha((ROOT/'standards/catalogue_interfaces.json').read_bytes()),'limits':'Global catalogue and batch records are lead-owned and outside the protected byte check. Old asset files, texture files and all other common standards are checked against actual Git object bytes.'}
result['source_package_groups_only_six_asset_family_additions']=group_only_authorized_additions
result['pass']=result['source_and_common_bytes_unchanged'] and result['old_45_records_identical'] and group_only_authorized_additions
(OUT/'independent_preservation_report.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['protected_files','original_interface_records']},indent=2))
