import json,pathlib,re,hashlib,collections,subprocess
ROOT=pathlib.Path('/workspace/Astraea'); OUT=ROOT/'Game/docs/validation/ship_scope_20261019'; OUT.mkdir(parents=True,exist_ok=True)
def read(p):return json.loads((ROOT/p).read_text())
def digest(p):return hashlib.file_digest(open(p,'rb'),'sha256').hexdigest()
base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
survey=json.load(open('/workspace/ship-scope-reconciliation-20261019/RUNTIME_SURVEY.json'))
rows=survey['rows']; bykey=collections.defaultdict(list)
for row in rows:
 for field in ['programme_key','programme_keys','program_key','commons_programme_key']:
  values=row['metadata'].get(field,[])
  if isinstance(values,str):values=[values]
  if isinstance(values,list):
   for value in values:
    if re.fullmatch(r'D\d\d_directory_\d\d',str(value)):bykey[value].append(row)
plan=read('Game/data/delivery_20261019/INCLUSION_PLAN.json')
paths={r['path'].lstrip('/'):r for r in rows}
for r in plan['received_sections']:
 node=paths.get(r['root'])
 if node and node not in bykey[r['key']]:bykey[r['key']].append(node)
manual={'D03_directory_01':'ShipSpace/Districts/SharedCrewHome_WIP','D06_directory_05':'ShipSpace/Districts/D06_CanopyTerrace_Arrival_WIP','D09_directory_06':'ShipSpace/Districts/D09_StarboardTerrace_AuthoredFootprint_WIP'}
for number,name in [(2,'D04StarboardFullCommons'),(3,'D04PortCentralHabitatNeighborhood'),(4,'D04StarboardCentralHabitatNeighborhood'),(5,'D04PortAftHabitatNeighborhood'),(6,'D04StarboardAftHabitatNeighborhood')]:manual[f'D04_directory_{number:02}']='ShipSpace/Districts/'+name
for deck in range(13,18):
 for number,name in [(3 if deck==13 else 2,'QuietGroveReceivingCandidate'),(6 if deck==13 else 5,'SunsetReceivingCandidate'),(7 if deck==13 else 6,'FamilyTerraceReceivingCandidate')]:manual[f'D{deck}_directory_{number:02}']='ShipSpace/Districts/'+name
for key,path in manual.items():
 if bykey[key]:continue
 node=paths.get(path)
 if not node:
  child=next((r for p,r in paths.items()if p.startswith(path+'/')),None)
  if child:node={'path':path,'attached':child['attached'],'scene_source':'','metadata':{'existence_evidence_child':child['path']}}
 if node:bykey[key].append(node)
evidence=collections.defaultdict(list); requirement_evidence=collections.defaultdict(list)
for folder in ['Game/scripts','Game/data']:
 for p in (ROOT/folder).rglob('*'):
  if p.suffix not in ['.gd','.json'] or '/packages/' in str(p) or '/reference/' in str(p) or p.stat().st_size>3_000_000:continue
  text=p.read_text(errors='replace'); rel=str(p.relative_to(ROOT))
  if p.name in ['programme_ledger.json','AMENITY_SCOPE_AUDIT.json','ENGINEERING_SERVICE_SCOPE_AUDIT.json']:continue
  for key in set(re.findall(r'D\d\d_directory_\d\d',text)):evidence[key].append(rel)
  for key in set(re.findall(r'(?:AME|ENGS)-\d{3}',text)):requirement_evidence[key].append(rel)
sources=collections.defaultdict(list)
for r in read('Game/data/architecture/received_sections.json')['sections']:sources[r['programme_key']].append(r)
for r in read('Game/docs/REMAINING_SECTION_INSTALLATIONS.json')['installed_remaining_sections']:sources[r['programme_key']].append(r)
for r in read('SOURCE_ARCHIVE_INDEX.json')['original_section_restore_mapping']['sections']:sources[r['programme_key']].append(r)
matrix=[]
for p in read('Game/data/programme_ledger.json')['destinations']:
 k=p['programme_key']; observed=bykey[k]
 matrix.append({'key':k,'name':p['name'],'deck':p['historical_deck'],'required_scope':'v0.3 chapters4–7,21,27,30,32; later explicit overlays; associated child requirements retained separately','retained_source_receipts':sources[k],'runtime_named_roots':[{'path':r['path'],'attached':r['attached'],'scene_source':r['scene_source'],'metadata':r['metadata']}for r in observed],'current_source_references':evidence[k],'status':'NAMED_RUNTIME_PRESENCE_VERIFIED' if observed else 'NEEDS_EXPLICIT_CURRENT_OWNER_JOIN','historical_ledger_status_not_current_evidence':p['current_status'],'full_programme_and_visual_acceptance':False})
requirements=[]
for file in ['AMENITY_SCOPE_AUDIT.json','ENGINEERING_SERVICE_SCOPE_AUDIT.json']:
 for r in read('Game/data/architecture/'+file)['items']:
  keys=r.get('parent_programme_keys',r.get('programme_keys',[]))
  requirements.append({'id':r['id'],'name':r['name'],'authoritative_requirement':r,'current_explicit_requirement_references':requirement_evidence[r['id']],'parent_runtime_presence':{k:bool(bykey[k])for k in keys},'status':'REQUIREMENT_SPECIFIC_RECONCILIATION_REQUIRED','warning':'Parent presence and a source reference do not establish child construction or acceptance.'})
docs=['Game/docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx','Game/docs/master_source/MASTER_FULL_CONTENT_INDEX.json','Game/docs/master_source/MASTER_CURRENT_APPLICATION.json','Game/docs/master_source/README.md','Game/docs/WHOLE_SHIP_SECTION_COORDINATION.md','Game/docs/FULL_SHIP_SCOPE_INDEX.md','Game/docs/reference_register/REFERENCE_IMAGE_INDEX.json','Game/data/architecture/SHIP_SCOPE_INDEX.json','Game/data/architecture/AMENITY_SCOPE_AUDIT.json','Game/data/architecture/ENGINEERING_SERVICE_SCOPE_AUDIT.json','SOURCE_ARCHIVE_INDEX.json','Game/docs/coordination/sol_fifty_sections_20261008/DELIVERY_MANIFEST.json','external_packages/remaining_sections_20261009/E/deliveries/DELIVERY_INDEX.json']
docs += [str(p.relative_to(ROOT))for p in (ROOT/'RetainedConstruction').glob('*/SOURCE_MAP.json')]
documents=[{'path':p,'bytes':(ROOT/p).stat().st_size,'sha256':digest(ROOT/p)}for p in docs]
def save(name,data):(OUT/name).write_text(json.dumps(data,indent=2)+'\n')
save('DOCUMENTS.json',{'base_commit':base,'authoritative_local_documents':documents,'library_remaining_work_review':{'id':'libfile_f98507bdc71c819196e4820144c8d553','name':'Astraea_remaining_work_for_confirmation.docx','date':'2026-10-09','pages':62,'status':'Read via Library; dated construction labels require current-scene reconciliation'},'version_warning':'Library Master(2) is older v0.1; current retained v0.3 remains governing.'})
save('PROGRAMME_MATRIX.json',{'base_commit':base,'scope':'161 canonical headings, not exhaustive interiors or acceptance','programmes':matrix})
save('REQUIREMENT_MATRIX.json',{'base_commit':base,'non_additive':True,'requirements':requirements})
summary={'programmes':len(matrix),'named_runtime_presence':sum(bool(r['runtime_named_roots'])for r in matrix),'unjoined':[{'key':r['key'],'name':r['name'],'references':r['current_source_references']}for r in matrix if not r['runtime_named_roots']],'requirements':len(requirements),'confirmed_completed_source_omissions':[],'omission_search_complete':False,'final_acceptance':False}
save('SUMMARY.json',summary)
print(json.dumps(summary,indent=2))
