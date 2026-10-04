"""Freeze hashes of final review media and imported sources after pixel review."""
import json,hashlib
from pathlib import Path
BASE=Path(__file__).resolve().parent
rows=[]
for p in sorted(BASE.glob('*_*.png')):
 if p.name.endswith(('_raw.png','_labelled.png')):rows.append({'file':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
e=json.loads((BASE/'render_evidence.json').read_text())
record={'scope':'Final labelled Blender imported-component evidence; labels are outside untouched raw pixels. No ship, route, game or electrical acceptance.','qa_exposure_stops':e['qa_exposure_stops'],'imported_overhead_glb_hashes':e['source_hashes'],'context_glb_hashes':e['context_glb_hashes'],'files':rows,'all_under_8MB':all(r['bytes']<8_000_000 for r in rows)}
(BASE/'review_media_manifest.json').write_text(json.dumps(record,indent=2)+'\n');print('FINAL_REVIEW_FILES',len(rows))
