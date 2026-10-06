from pathlib import Path
import json,math,hashlib
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
R=Path(__file__).resolve().parent;P=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section');D=json.loads((R/'FIRST_PASS_ADDITIONS_PLAN.json').read_text());S=json.loads((P/'contracts/surface_manifest.json').read_text());floors={69.5:unary_union([Polygon(p['boundary'],p['holes'])for p in json.loads((P/'contracts/D11_FLAT_FLOOR_CANDIDATE.json').read_text())['polygons']])}
for y,deck in [(78,'D12'),(84,'D13')]:floors[y]=unary_union([Polygon(p['boundary_xz'])for s in S['surfaces']if s['deck']==deck for p in s['parts']if p.get('top_y')==y])
contents=[]
for t in D['ground_modules']:
 if t['asset']!='AST-FUR-003'or not t['id'].endswith(('_0','_2')):continue
 x,y,z=t['position_world'];contents.append({'id':t['id']+'_potted_rosette','support_asset':'AST-FUR-003','support_instance':t['id'],'support_part':'inset_stone_worktop','retained_tabletop_y':y+.665,'pot_asset':'AST-BOT-012','pot_origin_world':[x+.23,y+.665,z],'plant_asset':'AST-BOT-003','plant_origin_world':[x+.23,y+.665+.198,z],'support_basis':'Original table worktop.665; centred180mm-wide supported root/foot region fits actual oval; original pot root plane0 and soil top.200, soil marker.198; original rosette root envelope radius.035 within.114soil radius','root_embed_m':.002,'unobstructed_table_use':'The remaining six low tables stay completely free; these pots are offset to one end, not placed in a route','geometry_scaled':False})
assert len(contents)==6
rugs=[]
for deck,y,defs in [('D11',69.5,[(-100.5,-132,4,4.5),(-88.5,-133,4,5)]),('D12',78,[(-99,-131,6,5),(-79,-132,4,4)]),('D13',84,[(-100,-134,5,6),(-83,-132,7,6)])]:
 for i,(x,z,rx,rz)in enumerate(defs):
  poly=Polygon([(x+rx*math.cos(k*math.tau/32),z+rz*math.sin(k*math.tau/32))for k in range(32)]);missing=poly.difference(floors[y]).area;assert missing<1e-8
  rugs.append({'id':f'{deck}_textile_waiting_island_{i}','deck':deck,'boundary_xz':[list(p)for p in list(poly.exterior.coords)[:-1]],'top_y':y+.004,'inner_material':'oatmeal_weave','edge_material':'clay_weave','border_width_m':.15,'collision_role':'visual_finish_nonwalking','missing_supported_floor_m2':missing,'ownership':'Existing compiler/source floor remains sole walkable collider; later runtime adopter must explicitly omit finish collision, not rely on generic model helper','source_import_gate':'4mm cloth separation must remain positive after actual new-asset import; no relaxed face tolerance or existing import changes'})
out={'status':'Additive supported finish/surface-content proposal, not authored or rendered','surface_contents':contents,'additional_retained_instances':12,'floor_finish_islands':rugs,'whole_object_scaling':False,'actual_root_measurement':'Raw retained AST-BOT-003 GLB vertices below5mm give max root radius0.0350000015m; original nursery soil radius0.114m. Foot contact to actual table mesh still checked after assembly.','not_claimed':['Botanical simulation','Movable props','Runtime finish collision exclusion already implemented','Completed visual first pass']};(R/'SURFACE_CONTENTS_AND_FINISH_PLAN.json').write_text(json.dumps(out,indent=2)+'\n');print('Six supported table pot/rosette pairs and six fully supported textile islands planned; no new walking floor.')
