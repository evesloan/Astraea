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
pre={};prefix='data/architecture/packages/crew_batch/retained_286/'
for rel in ['data/spatial_layout.json','data/generated/structural_meshes.json','docs/LAYOUT_COMPILE_CHECKS.json','tools/compile_layout.py','scripts/ship.gd','tests/medical_triage_successor_guard.gd']:
 b=(G/rel).read_bytes();put(prefix+rel,b);pre[rel]={'sha256':sha(b),'retained_path':prefix+rel}
added=[];links={'05':[-52,-51,-2,2],'06':[51,52,-2,2],'07':[-8,-4,214,218],'08':[4,8,214,218],'10':[7.8,8,430,434]}
for item in json.loads((R/'INTAKE.json').read_text()):
 key=item['programme'];i=key[-2:]
 for suffix,bounds in [('floor',item['placement']['boundary']),('entry',links[i])]:
  x0,x1,z0,z1=bounds; added.append({'id':f'D03_crew_{i}_{suffix}','deck':'D03','kind':'amenity_receiving_floor','boundary':[[x0,z0],[x1,z0],[x1,z1],[x0,z1]],'thickness':.24,'render_cell_m':8,'priority':0,'material_role':'staff_floor','status':'Crew source receiving preparation; existing support reused; Uniforms aperture and all installed acceptance pending'})
layout=json.loads((G/'data/spatial_layout.json').read_text());layout['regions']+=added;dump('data/spatial_layout.json',layout)
sys.path.insert(0,str(C/'tools'))
from theater_incremental_preservation import effective_shapes
contract=json.loads((G/'data/design_contract.json').read_text());elevations={x['deck_id']:x['floor_elevation_m']for x in contract['deck_datums']};owned=effective_shapes(layout,elevations);expected=[]
for item in added:
 shape=owned[item['id']];assert shape.equals(Polygon(item['boundary']));chunks=[];x0,z0,x1,z1=shape.bounds
 for x in range(math.floor(x0/8),math.ceil(x1/8)):
  for z in range(math.floor(z0/8),math.ceil(z1/8)):
   part=shape.intersection(box(x*8,z*8,(x+1)*8,(z+1)*8))
   if part.area<1e-8:continue
   chunks.append({'id':f'cell_{x}_{z}','triangles':[[list(c)for c in t.exterior.coords[:3]]for t in shapely.constrained_delaunay_triangles(part).geoms]})
 expected.append({'id':item['id'],'deck':'D03','floor_y':12,'thickness':.24,'triangles':[[list(c)for c in t.exterior.coords[:3]]for t in shapely.constrained_delaunay_triangles(shape).geoms],'rings':[[list(c)for c in orient(shape,sign=1).exterior.coords[:-1]]],'structural_area_m2':shape.area,'render_chunks':chunks,'status':item['status'],'material_role':'staff_floor'})
p='data/architecture/packages/crew_batch/CREW_BATCH_COMPILER_PROOF.json';dump(p,{'schema':1,'programme_keys':[x['programme']for x in json.loads((R/'INTAKE.json').read_text())],'predecessors':{k:pre[k]for k in list(pre)[:3]},'new_layout_records':added,'new_expected_compiled_records':expected,'contract_sha256':sha((G/'data/design_contract.json').read_bytes())})
s=(G/'tools/laundry_incremental_preservation.py').read_text().replace('laundry','crew_batch').replace('LAUNDRY','CREW_BATCH').replace('Laundry','Crew batch').replace('All284','All286').replace('all284','all286').replace('exactly two','exactly ten').replace('exactly two','exactly ten')
s=s.replace("{'D01_crew_batch_floor','D01_crew_batch_entry'}",repr({x['id']for x in added})).replace("row['deck']=='D01' and row['floor_y']==0","row['deck']=='D03' and row['floor_y']==12").replace('min(0,','min(12,').replace('max(-.24,','max(11.76,').replace('len(new_outputs)==2 and len(outputs)==len(preserved)+2','len(new_outputs)==10 and len(outputs)==len(preserved)+10')
s=re.sub("PROOF_SHA='[a-f0-9]+'","PROOF_SHA='"+sha((C/p).read_bytes())+"'",s)
s=s.replace('outputs,preserve_night,','outputs,preserve_laundry,preserve_night,',1)
a='preserved,welcome,triage,botanical,lounge,movement,moss,sports,night=preserve_night(root,projected,elevations,prior_owned,old_outputs,preserve_sports,preserve_moss,preserve_movement,preserve_lounge,preserve_botanical,preserve_triage,preserve_welcome)'
b='preserved,welcome,triage,botanical,lounge,movement,moss,sports,night,laundry=preserve_laundry(root,projected,elevations,prior_owned,old_outputs,preserve_night,preserve_sports,preserve_moss,preserve_movement,preserve_lounge,preserve_botanical,preserve_triage,preserve_welcome)';assert a in s;s=s.replace(a,b).replace('return preserved+new_outputs,welcome,triage,botanical,lounge,movement,moss,sports,night,receipt','return preserved+new_outputs,welcome,triage,botanical,lounge,movement,moss,sports,night,laundry,receipt');put('tools/crew_batch_incremental_preservation.py',s)
s=(G/'tools/compile_layout.py').read_text();edits=[]
def edit(before,after):
 global s
 assert s.count(before)==1,(before,s.count(before));edits.insert(0,{'before':before,'after':after,'count':1});s=s.replace(before,after)
a='from laundry_incremental_preservation import preserve_laundry_successor, canonicalize_laundry_predecessor_chunks';edit(a,a+'\nfrom crew_batch_incremental_preservation import preserve_crew_batch_successor, canonicalize_crew_batch_predecessor_chunks')
a='outputs=canonicalize_laundry_predecessor_chunks(root,layout,elevations,owned,outputs)';edit(a,a.replace('canonicalize_laundry','canonicalize_crew_batch'))
a=next(line for line in s.splitlines()if '=preserve_laundry_successor(root,layout' in line);edit(a,a.replace('laundry_preservation=preserve_laundry_successor','laundry_preservation,crew_batch_preservation=preserve_crew_batch_successor').replace('outputs,preserve_night','outputs,preserve_laundry_successor,preserve_night'))
a="checks['laundry_additive_preservation']=laundry_preservation";edit(a,a+"\nchecks['crew_batch_additive_preservation']=crew_batch_preservation");put('tools/compile_layout.py',s)
dump('data/architecture/packages/crew_batch/BUILD_CONTEXT.json',{'predecessors':pre,'added':added,'expected':expected,'compiler_inverse_edits':edits,'uniforms_connector_hold':'Dedicated D03 aft-core aperture required before live adoption'})
r=subprocess.run([sys.executable,str(C/'tools/compile_layout.py')],capture_output=True,text=True);(R/'compiler001.log').write_text(r.stdout+r.stderr);print(r.returncode,r.stdout[-800:],r.stderr[-1400:]);assert r.returncode==0
old=json.loads((G/'data/generated/structural_meshes.json').read_text());new=json.loads((C/'data/generated/structural_meshes.json').read_text());assert new['regions'][:286]==old['regions'] and len(new['regions'])==296;print('Exact 286 old floor records preserved; ten new clipped room/link records compiled in isolated preparation only')
