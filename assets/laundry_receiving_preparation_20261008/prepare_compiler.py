from pathlib import Path
import json,hashlib,shutil,math,sys,subprocess,re
import shapely
from shapely.geometry import box,Polygon
from shapely.geometry.polygon import orient
R=Path(__file__).resolve().parent;G=Path('/workspace/shared/Astraea_recovery_20261007_AXWr5x/Game');C=R/'compiler_candidate';assert not C.exists();shutil.copytree(G/'data',C/'data');shutil.copytree(G/'tools',C/'tools');(C/'docs').mkdir();(C/'assets/models').mkdir(parents=True);shutil.copy2(G/'assets/models/AST-CUL-005_static_003.glb',C/'assets/models/AST-CUL-005_static_003.glb')
sha=lambda b:hashlib.sha256(b).hexdigest()
def put(rel,b):
 p=C/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b if isinstance(b,bytes)else b.encode())
def dump(rel,d):put(rel,json.dumps(d,indent=2)+'\n')
pre={};prefix='data/architecture/packages/laundry/retained_284/'
for rel in ['data/spatial_layout.json','data/generated/structural_meshes.json','docs/LAYOUT_COMPILE_CHECKS.json','tools/compile_layout.py','scripts/ship.gd','tests/medical_triage_successor_guard.gd']:
 b=(G/rel).read_bytes();put(prefix+rel,b);pre[rel]={'sha256':sha(b),'retained_path':prefix+rel}
added=[]
for ident,boundary in [('D01_laundry_floor',[[-54,-250],[-8,-250],[-8,-182],[-54,-182]]),('D01_laundry_entry',[[-8,-218],[-4,-218],[-4,-214],[-8,-214]])]:
 added.append({'id':ident,'deck':'D01','kind':'amenity_receiving_floor','boundary':boundary,'thickness':.24,'render_cell_m':8,'priority':0,'material_role':'staff_floor','status':'Laundry source-preserved receiving floor/link; final art and operation pending'})
layout=json.loads((G/'data/spatial_layout.json').read_text());layout['regions']+=added;dump('data/spatial_layout.json',layout)
sys.path.insert(0,str(C/'tools'))
from theater_incremental_preservation import effective_shapes
contract=json.loads((G/'data/design_contract.json').read_text());elevations={x['deck_id']:x['floor_elevation_m']for x in contract['deck_datums']}
owned=effective_shapes(layout,elevations)
expected=[]
for item in added:
 shape=owned[item['id']];chunks=[];x0,z0,x1,z1=shape.bounds
 for x in range(math.floor(x0/8),math.ceil(x1/8)):
  for z in range(math.floor(z0/8),math.ceil(z1/8)):
   part=shape.intersection(box(x*8,z*8,(x+1)*8,(z+1)*8))
   if part.area<1e-8:continue
   chunks.append({'id':f'cell_{x}_{z}','triangles':[[list(c)for c in t.exterior.coords[:3]]for t in shapely.constrained_delaunay_triangles(part).geoms]})
 expected.append({'id':item['id'],'deck':'D01','floor_y':0,'thickness':.24,'triangles':[[list(c)for c in t.exterior.coords[:3]]for t in shapely.constrained_delaunay_triangles(shape).geoms],'rings':[[list(c)for c in orient(shape,sign=1).exterior.coords[:-1]]],'structural_area_m2':shape.area,'render_chunks':chunks,'status':item['status'],'material_role':'staff_floor'})
p='data/architecture/packages/laundry/LAUNDRY_COMPILER_PROOF.json';dump(p,{'schema':1,'programme_key':'D01_directory_03','predecessors':{k:pre[k]for k in list(pre)[:3]},'new_layout_records':added,'new_expected_compiled_records':expected,'contract_sha256':sha((G/'data/design_contract.json').read_bytes())})

s=(G/'tools/night_table_incremental_preservation.py').read_text().replace('night_table','laundry').replace('NIGHT_TABLE','LAUNDRY').replace('Night Table','Laundry').replace('All282','All284').replace('all282','all284').replace("{'D10_laundry_floor','D10_laundry_entry'}","{'D01_laundry_floor','D01_laundry_entry'}").replace("row['deck']=='D10' and row['floor_y']==61","row['deck']=='D01' and row['floor_y']==0").replace('min(61,','min(0,').replace('max(60.76,','max(-.24,')
s=re.sub("PROOF_SHA='[a-f0-9]+'","PROOF_SHA='"+sha((C/p).read_bytes())+"'",s)
s=s.replace('outputs,preserve_sports,','outputs,preserve_night,preserve_sports,',1)
s=s.replace('preserved,welcome,triage,botanical,lounge,movement,moss,sports=preserve_sports(root,projected,elevations,prior_owned,old_outputs,preserve_moss,preserve_movement,preserve_lounge,preserve_botanical,preserve_triage,preserve_welcome)','preserved,welcome,triage,botanical,lounge,movement,moss,sports,night=preserve_night(root,projected,elevations,prior_owned,old_outputs,preserve_sports,preserve_moss,preserve_movement,preserve_lounge,preserve_botanical,preserve_triage,preserve_welcome)')
s=s.replace('return preserved+new_outputs,welcome,triage,botanical,lounge,movement,moss,sports,receipt','return preserved+new_outputs,welcome,triage,botanical,lounge,movement,moss,sports,night,receipt');put('tools/laundry_incremental_preservation.py',s)
s=(G/'tools/compile_layout.py').read_text();edits=[]
def edit(before,after):
 global s
 assert s.count(before)==1,(before,s.count(before));edits.insert(0,{'before':before,'after':after,'count':1});s=s.replace(before,after)
a='from night_table_incremental_preservation import preserve_night_table_successor, canonicalize_night_table_predecessor_chunks';edit(a,a+'\nfrom laundry_incremental_preservation import preserve_laundry_successor, canonicalize_laundry_predecessor_chunks')
a='outputs=canonicalize_night_table_predecessor_chunks(root,layout,elevations,owned,outputs)';edit(a,a.replace('canonicalize_night_table','canonicalize_laundry'))
a=next(line for line in s.splitlines()if '=preserve_night_table_successor(root,layout' in line);edit(a,a.replace('night_table_preservation=preserve_night_table_successor','night_table_preservation,laundry_preservation=preserve_laundry_successor').replace('outputs,preserve_sports','outputs,preserve_night_table_successor,preserve_sports'))
a="checks['night_table_additive_preservation']=night_table_preservation";edit(a,a+"\nchecks['laundry_additive_preservation']=laundry_preservation");put('tools/compile_layout.py',s)
dump('data/architecture/packages/laundry/BUILD_CONTEXT.json',{'predecessors':pre,'added':added,'expected':expected,'compiler_inverse_edits':edits})
r=subprocess.run([sys.executable,str(C/'tools/compile_layout.py')],capture_output=True,text=True);(R/'compiler001.log').write_text(r.stdout+r.stderr);print(r.returncode,r.stdout[-1000:],r.stderr[-1000:]);assert r.returncode==0
old=json.loads((G/'data/generated/structural_meshes.json').read_text());new=json.loads((C/'data/generated/structural_meshes.json').read_text());assert new['regions'][:284]==old['regions'] and len(new['regions'])==286;print('Exact 284 old floor records preserved; Laundry 3128m2 and 16m2 connector compiled')
