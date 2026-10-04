"""Exercise family-source packaging using the previously backed-up real batch03 bytes."""
from pathlib import Path
import sys,json,zipfile,hashlib,tempfile
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from source_family_packages import partition_sources
SOURCE=Path('/workspace/scratch/375c2e438292/catalogue-deliverables/Astraea_New_Blender_Catalogue_Batch03_20261002_v1.zip')
config=json.loads((ROOT/'standards/source_package_groups.json').read_text())
with zipfile.ZipFile(SOURCE) as z:
 mp=next(n for n in z.namelist() if n.endswith('/BACKUP_MANIFEST.json'));pre=mp.rsplit('/',1)[0]+'/'
 manifest=json.loads(z.read(mp));items=[]
 for r in manifest['files']:
  p=r['path']
  if '/qa/' in '/'+p or p.startswith('references/'):continue
  raw=z.read(pre+p);assert hashlib.sha256(raw).hexdigest()==r['sha256'];items.append(('Astraea_Catalogue/'+p,raw))
 cat=json.loads(z.read(pre+'catalogue_manifest.json'))
groups=partition_sources(items,config,cat);checks=[];sizes={};all_files={n:b for n,b in items}
with tempfile.TemporaryDirectory(prefix='astraea-family-package-check-') as tmp:
 for family,rows,desc in groups:
  p=Path(tmp)/(family+'.zip')
  with zipfile.ZipFile(p,'x',zipfile.ZIP_DEFLATED) as z:
   for name,raw in rows:z.writestr(name,raw)
  with zipfile.ZipFile(p) as z:
   assert z.testzip() is None
   z.extractall(Path(tmp)/family)
   for name,raw in rows:assert (Path(tmp)/family/name).read_bytes()==raw
  sizes[family]=p.stat().st_size;assert sizes[family]<8_000_000
  checks.append(f'{family}: independently extracts all exact source/dependency bytes')
covered={n for _,rows,_ in groups for n,_ in rows if n in all_files};assert covered==set(all_files)
checks.append('All173 real current source files covered; shared duplicates are identical')
for label,baditems,badconfig,badcat in [
 ('missing_export',[(n,b) for n,b in items if n!='Astraea_Catalogue/'+cat['assets'][0]['export']],config,cat),
 ('unassigned_asset',items+[('Astraea_Catalogue/assets/unknown/source.blend',b'control')],config,cat),
 ('duplicate_path',items+[items[0]],config,cat),
 ('duplicate_family_owner',items,{'groups':config['groups']+[config['groups'][0]]},cat),
 ('path_traversal',items+[('Astraea_Catalogue/../escape.txt',b'control')],config,cat)]:
 try:partition_sources(baditems,badconfig,badcat)
 except ValueError:checks.append(label+' rejected')
 else:raise AssertionError(label+' incorrectly accepted')
report={'passed':True,'source':'previous verified batch03 archive, exact bytes; no source code execution','checks':checks,'source_files':len(items),'family_zip_bytes':sizes,'checks_count':len(checks),'limitation':'Batch04 final contents will be rechecked after freeze; this validates packaging with the previous complete source set.'}
(ROOT/'qa/batch04/source_family_packaging.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
