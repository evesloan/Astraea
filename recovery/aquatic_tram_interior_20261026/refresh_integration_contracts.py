from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2];G=R/'Game';P=G/'aquatic_tram_interior_20261026';owned={}
for folder in ['integration','r002','r003']:
 for p in sorted((P/folder).glob('*')):
  if p.is_file() and p.suffix in ['.gd','.tscn','.json','.glb'] and p.name!='CONTRACTS.json':owned['res://'+p.relative_to(G).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
out=P/'integration/CONTRACTS.json';out.write_bytes((json.dumps({'scope':'Unselected aquatic integration; original Orchard contract verification retained','owned':owned},indent=2)+'\n').encode());print(len(owned))
