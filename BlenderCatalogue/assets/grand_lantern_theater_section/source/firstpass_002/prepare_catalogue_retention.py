"""Create scratch manifest for a parent-reviewed new-only catalogue package copy."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent;D=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section/source/firstpass_002');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();assert not D.exists()
files=[p for p in R.iterdir()if p.is_file()and p.suffix in['.py','.json','.md']and p.name not in['CATALOGUE_RETENTION_MANIFEST.json','retain_catalogue_package.py']]
files += [R/'source/AST-CUL-005_firstpass_002.blend']+list((R/'composed_run001').glob('*.json'))+list((R/'composed_run001').glob('*.log'))+list((R/'composed_run001/images').glob('*'))
assert sha(R/'source/AST-CUL-005_firstpass_002.blend')=='dbf534bb1a9743bcf608072440680758bde94e7f58e707ca03a2934b41619a2a';rows=[]
for p in sorted(files):
 assert p.is_file()and not p.is_symlink();rel=p.relative_to(R);rows.append({'source':str(p),'destination':str(D/rel),'sha256':sha(p),'bytes':p.stat().st_size,'operation':'new_only'})
manifest={'scope':'New-only editable theater source revision002 and its scripts/evidence; no runtime/catalogue-registry installation','destination_root':str(D),'files':rows,'protected_sources':{'/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section/source/AST-CUL-005.blend':'c91193af1e4a14aac3a4e75c743e7c86b6a57a669981e9a7e7cfb0412e1cb5f5','/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section/source/AST-CUL-005_firstpass_001.blend':'a3f1d01b0927ddd873986b2d1f2dbb44f234bced2b034c2cff42c2c0bfd8d0ce'},'source_sha256':'dbf534bb1a9743bcf608072440680758bde94e7f58e707ca03a2934b41619a2a','visual_acceptance':False}
(R/'CATALOGUE_RETENTION_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Files',len(rows),'bytes',sum(r['bytes']for r in rows),'manifest',sha(R/'CATALOGUE_RETENTION_MANIFEST.json'))
