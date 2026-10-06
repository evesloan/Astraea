"""Pure triangle SAT joining preflight, no Blender or application launch."""
from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'source'))
from prepare_contract import g
import media_geometry as mg
C=json.loads((ROOT/'source_contract.json').read_text());out=[]
for c in C['candidates']:
 parts={p['name']:p for p in c['parts']};tris={k:mg.triangles(p)for k,p in parts.items()};boxes={k:[g.bounds(t)for t in v]for k,v in tris.items()};contacts=[]
 for name,p in parts.items():
  if p['kind']=='art':continue
  for other in p['joins']:
   hit=None
   for i,a in enumerate(tris[name]):
    for j,b in enumerate(tris[other]):
     if g.overlap(boxes[name][i],boxes[other][j],-1e-6)and g.triangle_intersects(a,b):hit=[i,j];break
    if hit:break
   assert hit,(c['name'],name,other,'no triangle bearing contact')
   contacts.append({'part':name,'bearing':other,'actual_recipe_triangle_pair':hit})
 out.append({'candidate':c['name'],'joins':contacts})
(ROOT/'qa/PURE_CONTACT_QA.json').write_text(json.dumps({'status':'PASS_RECIPE_TRIANGLE_CONTACTS','candidates':out,'evaluated_blender_modifiers_checked':False,'visual_acceptance':False},indent=2)+'\n');print('PURE_CONTACT_PASS',sum(len(x['joins'])for x in out))
