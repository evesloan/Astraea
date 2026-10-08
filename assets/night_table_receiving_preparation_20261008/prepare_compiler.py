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
pre={};prefix='data/architecture/packages/night_table/retained_282/'
for rel in ['data/spatial_layout.json','data/generated/structural_meshes.json','docs/LAYOUT_COMPILE_CHECKS.json','tools/compile_layout.py','scripts/ship.gd','tests/medical_triage_successor_guard.gd']:
 b=(G/rel).read_bytes();put(prefix+rel,b);pre[rel]={'sha256':sha(b),'retained_path':prefix+rel}
added=[]
for ident,boundary in [('D10_night_table_floor',[[-54,182],[-8,182],[-8,250],[-54,250]]),('D10_night_table_entry',[[-8,214],[-4,214],[-4,218],[-8,218]])]:
 added.append({'id':ident,'deck':'D10','kind':'amenity_receiving_floor','boundary':boundary,'thickness':.24,'render_cell_m':8,'priority':0,'material_role':'guest_floor','status':'Night Table source-preserved receiving floor/link; final art and operation pending'})
layout=json.loads((G/'data/spatial_layout.json').read_text());layout['regions']+=added;dump('data/spatial_layout.json',layout)
expected=[]
for item in added:
 shape=Polygon(item['boundary']);chunks=[];x0,z0,x1,z1=shape.bounds
 for x in range(math.floor(x0/8),math.ceil(x1/8)):
  for z in range(math.floor(z0/8),math.ceil(z1/8)):
   part=shape.intersection(box(x*8,z*8,(x+1)*8,(z+1)*8))
   if part.area<1e-8:continue
   chunks.append({'id':f'cell_{x}_{z}','triangles':[[list(c)for c in t.exterior.coords[:3]]for t in shapely.constrained_delaunay_triangles(part).geoms]})
 expected.append({'id':item['id'],'deck':'D10','floor_y':61,'thickness':.24,'triangles':[[list(c)for c in t.exterior.coords[:3]]for t in shapely.constrained_delaunay_triangles(shape).geoms],'rings':[[list(c)for c in orient(shape,sign=1).exterior.coords[:-1]]],'structural_area_m2':shape.area,'render_chunks':chunks,'status':item['status'],'material_role':'guest_floor'})
p='data/architecture/packages/night_table/NIGHT_TABLE_COMPILER_PROOF.json';dump(p,{'schema':1,'programme_key':'D10_directory_07','predecessors':{k:pre[k]for k in list(pre)[:3]},'new_layout_records':added,'new_expected_compiled_records':expected,'contract_sha256':sha((G/'data/design_contract.json').read_bytes())})
s=(G/'tools/sports_care_incremental_preservation.py').read_text().replace('preserve_sports_care_successor','preserve_night_table_successor').replace('packages/sports_care/SPORTS_CARE_COMPILER_PROOF','packages/night_table/NIGHT_TABLE_COMPILER_PROOF').replace("{'D07_sports_care_floor','D07_sports_care_entry'}","{'D10_night_table_floor','D10_night_table_entry'}").replace("row['deck']=='D07' and row['floor_y']==35.5","row['deck']=='D10' and row['floor_y']==61").replace('min(35.5,','min(61,').replace('max(35.26,','max(60.76,').replace('Sports Care','Night Table').replace('All280','All282').replace('all280','all282').replace('two Moss owner','two Night Table owners')
s=re.sub("PROOF_SHA='[a-f0-9]+'","PROOF_SHA='"+sha((C/p).read_bytes())+"'",s)
s=s.replace('outputs,preserve_moss,','outputs,preserve_sports,preserve_moss,',1)
s=s.replace('preserved,welcome,triage,botanical,lounge,movement,moss=preserve_moss(root,projected,elevations,prior_owned,old_outputs,preserve_movement,preserve_lounge,preserve_botanical,preserve_triage,preserve_welcome)','preserved,welcome,triage,botanical,lounge,movement,moss,sports=preserve_sports(root,projected,elevations,prior_owned,old_outputs,preserve_moss,preserve_movement,preserve_lounge,preserve_botanical,preserve_triage,preserve_welcome)')
s=s.replace('return preserved+new_outputs,welcome,triage,botanical,lounge,movement,moss,receipt','return preserved+new_outputs,welcome,triage,botanical,lounge,movement,moss,sports,receipt');put('tools/night_table_incremental_preservation.py',s)
s=(G/'tools/compile_layout.py').read_text();edits=[]
def edit(before,after):
 global s
 assert s.count(before)==1;edits.insert(0,{'before':before,'after':after,'count':1});s=s.replace(before,after)
a='from sports_care_incremental_preservation import preserve_sports_care_successor';edit(a,a+'\nfrom night_table_incremental_preservation import preserve_night_table_successor')
a='outputs,medical_preservation,triage_preservation,botanical_preservation,team_lounge_preservation,movement_preservation,moss_preservation,sports_care_preservation=preserve_sports_care_successor(root,layout,elevations,owned,outputs,preserve_moss_sanctuary_successor,preserve_movement_studio_successor,preserve_team_lounge_successor,preserve_botanical_court_successor,preserve_medical_triage_successor,preserve_medical_predecessor)';edit(a,a.replace('sports_care_preservation=preserve_sports_care_successor','sports_care_preservation,night_table_preservation=preserve_night_table_successor').replace('outputs,preserve_moss','outputs,preserve_sports_care_successor,preserve_moss'))
a="checks['sports_care_additive_preservation']=sports_care_preservation";edit(a,a+"\nchecks['night_table_additive_preservation']=night_table_preservation");put('tools/compile_layout.py',s)
dump('data/architecture/packages/night_table/BUILD_CONTEXT.json',{'predecessors':pre,'added':added,'expected':expected,'compiler_inverse_edits':edits})
r=subprocess.run([sys.executable,str(C/'tools/compile_layout.py')],capture_output=True,text=True);(R/'compiler001.log').write_text(r.stdout+r.stderr);print(r.returncode,r.stdout[-1000:],r.stderr[-1000:]);assert r.returncode==0
old=json.loads((G/'data/generated/structural_meshes.json').read_text());new=json.loads((C/'data/generated/structural_meshes.json').read_text());assert new['regions'][:282]==old['regions'] and len(new['regions'])==284;print('Exact282old floor records preserved; Night Table3128m2 and16m2 connector compiled')
