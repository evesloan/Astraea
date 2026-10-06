"""Generated geometric review diagram, not an engine or image-editing operation."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent;C=json.loads((R/'COURT_A_GEOMETRY_CONTRACT.json').read_text());S=json.loads((R/'COURT_A_PURE_SCREEN.json').read_text())
im=Image.new('RGB',(1180,1060),'#f6f1e9');d=ImageDraw.Draw(im);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15);small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12);title=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',23)
def p(q):return (70+(q[0]+79)*63,95+(q[1]+148)*43)
def poly(points,fill,outline=None):d.polygon([p(q)for q in points],fill=fill,outline=outline)
d.text((35,24),'Court A: exact additive placement draft',fill='#26312c',font=title)
d.text((35,55),'Plan only. No Blender/Godot build or visual acceptance. All existing source objects remain fixed.',fill='#505951',font=font)
for x in range(-78,-63,2):
 a,b=p((x,-148)),p((x,-128));d.line([a,b],fill='#ded9d0');d.text((a[0]-15,966),str(x),font=small,fill='#686d68')
for z in range(-146,-129,2):
 a,b=p((-79,z)),p((-63,z));d.line([a,b],fill='#ded9d0');d.text((9,a[1]-7),str(z),font=small,fill='#686d68')
for o in C['objects']:
 if o['name'].endswith('_canopy_shell'):
  n=len(o['vertices_world'])//2;poly([[v[0],v[2]]for v in o['vertices_world'][:n]],'#e9dfcc','#cfbda0')
for points in S['route']['cart_operator_sweep_polygon_xz']:poly(points,'#d0e1ee','#6993ac')
for r in C['reservations']:
 if r['id']=='central_clear_spine':poly(r['polygon_xz'],'#e1ecd8','#8ca775')
for row in C['grounded_supports']:poly(row['polygon_xz'],'#c5ac85','#66563d')
for soil in C['soil_receivers']:poly(soil['polygon_xz'],'#62543e','#3b382e')
for o in C['objects']:
 if o['name'].endswith('_crowned_cushion'):
  n=len(o['vertices_world'])//4;poly([[v[0],v[2]]for v in o['vertices_world'][3*n:]],'#b9765d'if'_W_'in o['name']else'#467f7e','#3c5751')
for i in C['retained_instances']:
 if i['asset']not in['AST-FUR-003','AST-CUL-002']:continue
 lo,hi=i['bounds_world'];poly([[lo[0],lo[2]],[hi[0],lo[2]],[hi[0],hi[2]],[lo[0],hi[2]]],'#936b43','#5d4229')
for root in S['all_preserved_and_new_root_collars']['circles']:
 x,y=p(root['xz']);rr=max(4,root['radius']*63);d.ellipse((x-rr,y-rr,x+rr,y+rr),fill='#5b854c',outline='#315c38')
for x in[-73.88,-65.12]:
 for z in[-146.2,-138.3,-130.4]:poly([[x-.25,z-.32],[x+.25,z-.32],[x+.25,z+.32],[x-.25,z+.32]],'#d4cabe','#736b61')
for x in[-73,-69]:
 poly([[x-.755,-133.375],[x+.755,-133.375],[x+.755,-132.595],[x-.755,-132.595]],'#8c8378','#393a35')
 poly([[x-.9,-134.35],[x+.9,-134.35],[x+.9,-133.55],[x-.9,-133.55]],None,'#9c7060')
 d.text(p((x-.8,-132.35)),'Retained usher',fill='#433f39',font=small)
for s in C['seats']:
 a=p([s['seat_contact_world'][0],s['seat_contact_world'][2]]);b=p([s['focus_world'][0],s['focus_world'][2]]);end=(a[0]+(b[0]-a[0])*.23,a[1]+(b[1]-a[1])*.23);d.line([a,end],fill='#253b38',width=2);d.ellipse((a[0]-3,a[1]-3,a[0]+3,a[1]+3),fill='#fff7e3')
for text,point in [('Curved acoustic backing + original programme',(-73.5,-147.2)),('Preserved rear basin; fuller middle crowns pending',(-73.5,-144.7)),('New reception',(-70.35,-140.85)),('3.1 m inner clear spine',(-71.0,-137.0)),('1.5 m reserved cross-aisle',(-72.0,-135.05)),('Cart / operator sweep',(-78.75,-140.0))]:d.text(p(point),text,fill='#27372f',font=small)
d.text((35,1004),'Blue: continuous guarded cart/operator sweep. Green: inner clear spine. Grey: unchanged usher stations.',font=font,fill='#455047')
d.text((35,1030),'The six upholstered places are informal foyer seating; the 2,200 audience chairs are not rebuilt or changed.',font=font,fill='#455047')
im.save(R/'COURT_A_PLAN_PREVIEW.png')
