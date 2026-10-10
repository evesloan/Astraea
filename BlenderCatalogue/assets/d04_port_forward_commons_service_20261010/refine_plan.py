from pathlib import Path
import json,hashlib,shutil
R=Path('/workspace/astraea-recovered-532087b9-20261010T083844Z');W=R/'BlenderCatalogue/assets/d04_port_forward_commons_service_20261010';d=W/'attempt01_inherited_corner_contacts';d.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for f in ['PLAN.json','prepare.py','PREIMAGE_SUPPORT.json','PREIMAGE_SUPPORT.log']:shutil.copy2(W/f,d/f)
shutil.copy2(R/'Game/tests/validate_d04_commons_preimage.gd',d/'validate_d04_commons_preimage.gd')
p=json.load(open(W/'PLAN.json'));original=json.load(open(R/'BlenderCatalogue/assets/d04_port_forward_receiving_20261010/PLAN.json'))['parts'];first=json.load(open(R/'BlenderCatalogue/assets/d04_port_forward_homes_first_20261010/PLAN.json'))['commons_parts']
def bounds(q):return[[min(v[k]for v in q['verts'])for k in range(3)],[max(v[k]for v in q['verts'])for k in range(3)]]
p['successor_inherited_joint_contacts']={};p['successor_exact_containment_proof']=[]
for q in p['successor_parts']:
 lo,hi=bounds(q);name=q['name'].removeprefix('D04CS_').split('_Remaining')[0];src=next(a for a in p['preimages']if a['name']==name);a,b=bounds(src);assert all(a[k]<=lo[k]<=hi[k]<=b[k]for k in range(3))
 p['successor_exact_containment_proof'].append({'successor':q['name'],'predecessor':name,'predecessor_part_sha256':hashlib.sha256(json.dumps(src,sort_keys=True).encode()).hexdigest(),'contained_all_xyz':True})
 p['successor_inherited_joint_contacts'][q['name']]=[a['name']for a in original+first if a['name'] not in [t['name']for t in p['preimages']] and all(bounds(a)[0][k]<hi[k]-.002 and bounds(a)[1][k]>lo[k]+.002 for k in range(3))]
# Add explicit floor-bearing linen-rack uprights; place both shelves on those uprights.
ns={};s=(R/'BlenderCatalogue/assets/d04_port_forward_homes_second_20261010/prepare.py').read_text();exec(s[:s.index('from shapely import affinity')].replace('R=Path(__file__).resolve().parents[3];W=Path(__file__).resolve().parent',''),ns)
for j,(x,z)in enumerate([(x,z)for x in [-79.3,-78.7]for z in [-358.48,-357.42]]):ns['cube']('D04CS_LinenRackLeg_'+str(j),[x-.04,16.5,z-.04],[x+.04,17.65,z+.04],role='warm_walnut',category='storage')
p['parts']+=ns['parts']
for q in p['parts']:
 if q['name'].startswith('D04CS_CleanLinenShelf_'):
  for v in q['verts']:v[2]=max(-358.52,min(-357.38,v[2]+(-.27 if q['name'].endswith('_0') else .27)))
(W/'PLAN.json').write_text(json.dumps(p,indent=2)+'\n')
(d/'REJECTION.json').write_text(json.dumps({'status':'RETAINED_FAILED_PREIMAGE','reason':'Unqualified original corner joints of exact contained predecessor subsets; source-derived named joint proofs added, no collision exclusions or blanket allowances','files':{f.name:sha(f)for f in d.iterdir()}},indent=2)+'\n')
# Current reproducible successor script retains the initial generator and applies this reviewed refinement.
(W/'refine_plan.py').write_bytes(Path(__file__).read_bytes())
t=R/'Game/tests/validate_d04_commons_preimage.gd';s=t.read_text();s=s.replace('if str(h.collider.get_parent().name) not in p.preimages.map(func(q):return str(q.name)):', 'if str(h.collider.get_parent().name) not in p.preimages.map(func(q):return str(q.name)) and str(h.collider.get_parent().name) not in p.successor_inherited_joint_contacts.get(str(part.name),[]):');t.write_text(s)
print(json.dumps({'owned_parts':len(p['parts'])+len(p['successor_parts']),'exact_contained_successors':len(p['successor_parts']),'qualified_joint_lists':len(p['successor_inherited_joint_contacts'])}))
