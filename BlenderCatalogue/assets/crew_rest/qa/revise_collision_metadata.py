from pathlib import Path
import json,hashlib,shutil
B=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
oldhash={str(p.relative_to(B)):sha(p)for p in list((B/'source').glob('*.blend'))+list((B/'exports').glob('*.glb'))+[B/'collision_proposals.json',B/'source/build_crew_rest.py']}
archive=B/'qa/before_collision_profile_revision';archive.mkdir(exist_ok=True)
for n in('collision_proposals.json','dependency_manifest.json','manifest.json','AST-CRW-001.manifest.json','AST-CRW-002.manifest.json'):shutil.copy2(B/n,archive/n)
shutil.copy2(B/'source/build_crew_rest.py',archive/'build_crew_rest.py')
p=B/'source/build_crew_rest.py';s=p.read_text();s=s.replace("[lo[1],2.155,.425],'Folded side rail and bearing lip',.003)","[lo[1],2.155,.414],'Vertical folded side rail; separate thin bearing-lip profile',.003)")
s=s.replace("'metal',.001))\nfor i,y in enumerate([.16", "'metal',.001));C.append(cb(f'bearing_lip_{sx}',[min(sx*.445,sx*.53),.065,.414],[max(sx*.445,sx*.53),2.135,.425],'Thin inward bearing lip, separate from vertical rail so the inner under-frame bay stays open',.001))\nfor i,y in enumerate([.16")
s=s.replace("lateral drape/turned fold up to .028m outside mattress", "lateral drape/turned fold conservatively up to .080m outside mattress hull").replace("'maximum_declared_visual_detail_omission_m':.028", "'maximum_declared_visual_detail_omission_m':.080")
p.write_text(s)
c=json.loads((B/'collision_proposals.json').read_text());shapes=c['assets']['AST-CRW-001']['shapes']
for row in shapes:
 if row['name'].startswith('side_rail_'):row['max_source_m'][2]=.414;row['reason']='Vertical folded side rail; separate thin bearing-lip profile'
 if row['name']=='blanket':row['maximum_declared_visual_detail_omission_m']=.080;row['reason']=row['reason'].replace('lateral drape/turned fold up to .028m outside mattress','lateral drape/turned fold conservatively up to .080m outside mattress hull')
# Insert in generator's order, adjacent to each structural rail.
for sx in(-1,1):
 idx=next(i for i,r in enumerate(shapes)if r['name']==f'side_rail_{sx}')
 shapes.insert(idx+1,{'name':f'bearing_lip_{sx}','type':'box','min_source_m':[min(sx*.445,sx*.53),.065,.414],'max_source_m':[max(sx*.445,sx*.53),2.135,.425],'reason':'Thin inward bearing lip, separate from vertical rail so the inner under-frame bay stays open','conservative_empty_corner_limit_m':.001})
(B/'collision_proposals.json').write_text(json.dumps(c,indent=2))
d=json.loads((B/'dependency_manifest.json').read_text())
for r in d['source_only_inputs']:
 if r['path'].endswith('/source/build_crew_rest.py'):r['sha256']=sha(p)
(B/'dependency_manifest.json').write_text(json.dumps(d,indent=2))
for name in('AST-CRW-001.manifest.json','AST-CRW-002.manifest.json'):
 row=json.loads((B/name).read_text());row['generator_sha256']=sha(p);(B/name).write_text(json.dumps(row,indent=2))
m=json.loads((B/'manifest.json').read_text())
for r in m['assets']:r['generator_sha256']=sha(p)
(B/'manifest.json').write_text(json.dumps(m,indent=2))
newhash={str(p.relative_to(B)):sha(p)for p in list((B/'source').glob('*.blend'))+list((B/'exports').glob('*.glb'))+[B/'collision_proposals.json',B/'source/build_crew_rest.py']}
r={'revision':'crew-rest-collision-profile-02','scope':'Collision proposal and corresponding generator metadata only; preserved actual source/GLB bytes and earlier exact render binding.','before':oldhash,'after':newhash,'source_and_glb_unchanged':all(oldhash[n]==v for n,v in newhash.items()if n.endswith(('.blend','.glb'))),'changes':['Separate thin inward rail bearing-lip boxes now cover actual lip while preserving open inner bay','Blanket omission bound corrected to80mm, a conservative full triangle bound from convex mattress distance; explicit flexible visual-only omission remains'],'render_evidence':'Existing qa/render_evidence.json retains exact earlier collision hash and unchanged visual hashes; no recapture implied'};(B/'qa/collision_metadata_revision.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
