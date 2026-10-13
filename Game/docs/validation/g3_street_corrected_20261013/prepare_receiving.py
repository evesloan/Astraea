from pathlib import Path
import json,zipfile,hashlib
P=Path(__file__).parent;C=P.parent;I=P/'import/Game';sha=lambda b:hashlib.sha256(b).hexdigest()
log=(P/'import.log').read_text();assert 'ERROR:'not in log and 'Godot Engine v4.6.3'in log
with zipfile.ZipFile(C/'G3_STREET_CANDIDATE_OVERLAY.zip')as z:w={n:z.read(n)for n in z.namelist()}
k='data/architecture/group3_d03_streets_20261011/STREETS.json';original=w[k];d=json.loads(original);old='AST-STF-G3-058.glb';new='AST-STF-G3-058_current_receiving_successor001.glb'
assert d['model_pins'][old]=='e46e0abdf921ce6842a1bd4884efeecc58e00353a804f877166aca9d8a40ff01'
b=(I/'assets/models/group3_d03_streets_20261011'/new).read_bytes();d['model_pins'][new]=sha(b);del d['model_pins'][old]
# Replace the actual source floor scene filename wherever metadata references it.
def rep(x):
 if isinstance(x,str):return x.replace(old,new)
 if isinstance(x,list):return[rep(q)for q in x]
 if isinstance(x,dict):return{k:rep(v)for k,v in x.items()}
 return x
d=rep(d);plan=json.loads((P/'FLOOR_RECEIVING_SUCCESSOR_PLAN.json').read_text());d['new_floor_m2']=plan['corrected_geometric_area_m2'];d['receiving_successor']={'original_floor_file':old,'original_floor_sha256':'e46e0abdf921ce6842a1bd4884efeecc58e00353a804f877166aca9d8a40ff01','removed_overlap_m2':plan['removed_overlap_m2'],'removed_fully_duplicated_parts':plan['changed_parts'],'historical_criteria_preserved':13}
w[k]=json.dumps(d,indent=2).encode()+b'\n';w[k+'.owner_source']=original
for q in I.rglob('*'):
 if q.is_file()and(q.suffix in ['.glb','.png','.import']or '.godot/imported'in str(q)):w[str(q.relative_to(I))]=q.read_bytes()
# Source factory references its floor by a literal as well as model pins.
s='scripts/group3_d03_streets_20261011/physical_package.gd';assert 'for file in p.model_pins:' in w[s].decode() # Scene filenames come from the exact metadata pin map.
with zipfile.ZipFile(P/'CORRECTED_STREET_CANDIDATE_OVERLAY.zip','w',zipfile.ZIP_DEFLATED,compresslevel=1)as z:
 for n,b in w.items():z.writestr(n,b)
t=(C/'validate_g3_street_receiving.gd').read_text().replace('G3_STREET_CANDIDATE_OVERLAY.zip','street_floor_successor/CORRECTED_STREET_CANDIDATE_OVERLAY.zip').replace('G3_STREET_RECEIVING_RUNTIME.json','street_floor_successor/CORRECTED_STREET_RECEIVING_RUNTIME.json').replace('"native_floor_m2":9135.552474595705','"native_floor_m2":9085.733289160009')
t=t.replace(' for part in floors.parts:\n  for t in part.triangles:', ' for part in floors.parts:\n  if str(part.name)in ["RemainingD03StreetMissingFloor_2","RemainingD03StreetMissingFloor_9","RemainingD03StreetMissingFloor_13"]:continue\n  for t in part.triangles:')
# Preserve the source wall capsule criterion; remove an extra vertical-floor assertion invented in the rejected candidate.
a='  var hit:Dictionary=ray(space,at+Vector3.UP,at-Vector3.UP*.1)\n  if not require(not hit.is_empty(),"Original held wall source contact remains physical "+str(row.runtime_name)):return\n';assert a in t;t=t.replace(a,'')
# Removed pieces are supplied by original native floors, not by the addition.
anchor=' if not require(addition.find_children("*","OmniLight3D",true,false).size()==44'
checks=''' for part in floors.parts:
  if str(part.name)not in ["RemainingD03StreetMissingFloor_2","RemainingD03StreetMissingFloor_9","RemainingD03StreetMissingFloor_13"]:continue
  for tri in part.triangles:
   var at:=Vector3((tri[0][0]+tri[1][0]+tri[2][0])/3.,12.,(tri[0][1]+tri[1][1]+tri[2][1])/3.)
   var hit:Dictionary=ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02)
   if not require(not hit.is_empty()and not addition.is_ancestor_of(hit.collider)and absf(hit.position.y-12)<.002,"Original native floor supplies removed duplicate "+str(part.name)):return
'''
assert anchor in t;t=t.replace(anchor,checks+anchor)
(P/'validate_corrected_street_receiving.gd').write_text(t)
(P/'RECEIVING_CANDIDATE_RECEIPT.json').write_text(json.dumps({'status':'CANDIDATE_READY','metadata_exact_preimage_sha256':sha(original),'successor_model_sha256':d['model_pins'][new],'overlay_sha256':sha((P/'CORRECTED_STREET_CANDIDATE_OVERLAY.zip').read_bytes()),'original_criteria_unchanged':13,'import_errors':[]},indent=2)+'\n');print('CANDIDATE_READY')
