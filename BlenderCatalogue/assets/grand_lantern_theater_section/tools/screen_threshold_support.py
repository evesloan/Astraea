import json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
import build_geometry as g
surfaces=json.load(open(R/'contracts/surface_manifest.json'))['surfaces']
w=[]
for deck,y in [('D12',78),('D13',84)]:
 for name,r in [('main_vestibule_floor',[-38.4,-128.6,-34,-123.4]),('secondary_exit_floor',[-38.4,-172.7,-34,-169.3]),('lift_boarding_5x5',[-44.5,-129,-39.5,-124]),('lift_fixed_sill',[-43.2,-124,-39.8,-123.5])]:
  uncovered=[g.rect(r)]
  for f in surfaces:
   if f['deck']!=deck:continue
   for p in f['parts']:
    if p['top_y'] is None or abs(p['top_y']-y)>1e-6:continue
    uncovered=[q for u in uncovered for q in g.subtract_convex(u,p['boundary_xz'])]
    if not uncovered:break
   if not uncovered:break
  w.append(dict(deck=deck,interface=name,rectangle=r,top_y=y,unsupported_area=sum(g.area(q) for q in uncovered)))
(R/'qa/threshold_support_screen.json').write_text(json.dumps(dict(witnesses=w,failures=[x for x in w if x['unsupported_area']>1e-7],D11='Compiler-owned flat support and threshold deltas remain conditional; no source floor fabricated.',external='X>-34 unbuilt parent interface'),indent=2)+'\n');print('Threshold/boarding whole-area support failures',sum(x['unsupported_area']>1e-7 for x in w))
