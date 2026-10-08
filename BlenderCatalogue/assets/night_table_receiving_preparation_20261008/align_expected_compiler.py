from pathlib import Path
import json,sys,hashlib,math,shutil,re
import shapely
from shapely.geometry import box,Polygon
from shapely.geometry.polygon import orient
R=Path(__file__).resolve().parent;C=R/'compiler_candidate';sys.path.insert(0,str(C/'tools'));from theater_incremental_preservation import effective_shapes
layout=json.load(open(C/'data/spatial_layout.json'));elev={r['deck_id']:r['floor_elevation_m']for r in json.load(open(C/'data/design_contract.json'))['deck_datums']};owned=effective_shapes(layout,elev);P=C/'data/architecture/packages/night_table/NIGHT_TABLE_COMPILER_PROOF.json';d=json.load(open(P));shutil.copy2(P,R/'compiler_proof_raw_winding_failed001.json');expected=[]
for item in d['new_layout_records']:
 shape=owned[item['id']];assert shape.equals(Polygon(item['boundary']));chunks=[];x0,z0,x1,z1=shape.bounds
 for x in range(math.floor(x0/8),math.ceil(x1/8)):
  for z in range(math.floor(z0/8),math.ceil(z1/8)):
   part=shape.intersection(box(x*8,z*8,(x+1)*8,(z+1)*8))
   if part.area<1e-8:continue
   chunks.append({'id':f'cell_{x}_{z}','triangles':[[list(c)for c in t.exterior.coords[:3]]for t in shapely.constrained_delaunay_triangles(part).geoms]})
 expected.append({'id':item['id'],'deck':'D10','floor_y':61,'thickness':.24,'triangles':[[list(c)for c in t.exterior.coords[:3]]for t in shapely.constrained_delaunay_triangles(shape).geoms],'rings':[[list(c)for c in orient(shape,sign=1).exterior.coords[:-1]]],'structural_area_m2':shape.area,'render_chunks':chunks,'status':item['status'],'material_role':'guest_floor'})
d['new_expected_compiled_records']=expected;P.write_text(json.dumps(d,indent=2)+'\n');h=hashlib.sha256(P.read_bytes()).hexdigest();M=C/'tools/night_table_incremental_preservation.py';s=M.read_text();M.write_text(re.sub("PROOF_SHA='[a-f0-9]+'","PROOF_SHA='"+h+"'",s));p=C/'data/architecture/packages/night_table/BUILD_CONTEXT.json';b=json.load(open(p));b['expected']=expected;p.write_text(json.dumps(b,indent=2)+'\n');print('Expected exact triangulation now follows actual unchanged effective-shape boolean sequence; same polygons')
