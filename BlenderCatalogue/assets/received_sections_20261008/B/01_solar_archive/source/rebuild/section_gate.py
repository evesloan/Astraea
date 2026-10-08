import json,pathlib,sys,datetime,hashlib
B=pathlib.Path(__file__).resolve().parent;I=B/'inputs';S=sys.argv[1];C=json.loads((B/'section_profiles.json').read_text())[S];P=B/S
ledger=json.loads((I/'Game/data/programme_ledger.json').read_text());rec=next(x for x in ledger['destinations']if x['programme_key']==C['key']);assert rec['current_geometry_owner']is None,rec
env=rec['historical_envelope'];assert env['x']==([-C['x']-46,-C['x']]if C['sign']<0 else[C['x'],C['x']+46]);assert env['z']==[C['z'],C['z']+68]
claims=[];root=B.parents[2]
for p in (root/'external_packages').rglob('placements.json'):
 if B in p.parents:continue
 if C['key']in p.read_text(errors='replace'):claims.append(str(p))
assert not claims,claims
protected=json.loads((I/'PROTECTED_VOLUMES.json').read_text());deck=C['key'][:3];hits=[]
for v in protected['voids']:
 if deck not in v['decks']:continue
 pp=v['boundary'];bb=[min(a[0]for a in pp),max(a[0]for a in pp),min(a[1]for a in pp),max(a[1]for a in pp)]
 if bb[0]<env['x'][1]and bb[1]>env['x'][0]and bb[2]<env['z'][1]and bb[3]>env['z'][0]:hits.append(v['id'])
assert not hits,hits
crew=json.loads((I/'BlenderCatalogue/assets/crew_service_platform/source/geometry_parts.json').read_text());actual=[]
for g in crew:
 a=g['world_aabb']
 if a[0]<env['x'][1]and a[1]>env['x'][0]and a[2]<C['roof']and a[3]>C['floor']and a[4]<env['z'][1]and a[5]>env['z'][0]:actual.append(g)
out={'root_checkpoint':'7955f22b2e1301bcfc8b5972f65073668377b803','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'programme_record':rec,'profile':C,'other_source_claims':claims,'intersecting_voids':hits,'protected_crew_aabbs_in_envelope':actual,'reservation':'Explicit root exclusive isolated-source reservation; receiving slabs/portals/runtime remain root-owned','holds':['Root receiving slab/support','Shared entry connections and doors','Installed Godot player/cart/species/CRT acceptance','Operational behaviour and finish refinement'],'capacity_policy':'No registry/capacity changes. Unknown values stay unknown; no new berths or people.'}
(P/'docs').mkdir(parents=True,exist_ok=True);(P/'docs/source_gate.json').write_text(json.dumps(out,indent=2));print(C['key'],'gate: exclusive, source owner absent; protected crew parts',len(actual))
