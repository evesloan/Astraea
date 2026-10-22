from pathlib import Path
import hashlib,json
G=Path(__file__).resolve().parents[2]
paths=set(G.glob("assets/**/*.png"))|set(G.glob("**/*.glb.import"))|set(G.glob("scenes/**/*.tscn"))
paths |= set(G.glob("d04_detail_batches_20261022/runtime_r004/**/*.res")) | set(G.glob("d04_detail_batches_20261022/runtime_r004/*.scn"))
paths |= set(G.glob("assets/models/SunsetSpecialty_*_r002.scn")) | set(G.glob("sunset_specialty_bank_20261022/runtime/*_r002.*.scn"))
paths.add(G/"sunset_specialty_bank_20261022/runtime/Sunset47Receiving_r003.scn")
paths.add(G/"sunset_court_finish_20261022/runtime/SunsetCourtFinish_r003.scn")
paths.add(G/"docs/group5/STAFF_RISER_INTERFACE_CONTRACT.json")
for row in json.loads((G/"data/architecture/startup_residency_20261020/runtime_required_receipts.json").read_text()):
 p=G/row["path"].removeprefix("res://");assert hashlib.sha256(p.read_bytes()).hexdigest()==row["sha256"];paths.add(p)
rows=[dict(path="res://"+str(p.relative_to(G)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size) for p in sorted(paths)]
(G/"scripts/runtime_contracts_20261022/SOURCE_CONTRACTS.json").write_text(json.dumps(rows,indent=2)+"\n")
print(json.dumps(dict(files=len(rows),bytes=sum(r["bytes"] for r in rows))))
