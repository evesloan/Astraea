"""Read-only source reconciliation. Does not turn allocation rectangles into rooms."""
from pathlib import Path
import json,re,hashlib
root=Path(__file__).resolve().parents[1]
source=root/'data/reference/historical_atlas_text.txt'
allocations=json.loads((root/'data/reference/historical_atlas_allocations.json').read_text())
entries=[]
for page in source.read_text().split('\f'):
    match=re.match(r'D(\d\d) (.+?)\s{3}',page)
    if not match: continue
    deck=int(match[1])
    for line in page.splitlines():
        if not re.match(r'^\d\d\s{3,}[A-Za-z]',line):continue
        for index,name in re.findall(r'(\d\d)\s{3,}(.+?)(?=\s{3,}\d\d\s{3,}|$)',line):
            name=re.split(r'\s{3,}',name.strip())[0]
            number=int(index)
            if number>20:continue
            match_alloc=next((x for x in allocations if x['deck']==deck and x.get('atlas_directory_number')==number),None)
            entries.append({'programme_key':f'D{deck:02}_directory_{number:02}', 'historical_deck':f'D{deck:02}', 'name':name,'source':'Historical atlas October1; directory entry, not proof of current construction','historical_room_id':match_alloc.get('stable_id') if match_alloc else None,'historical_envelope':{'x':match_alloc['x'],'z':match_alloc['z']} if match_alloc else None,'current_status':'partial architecture' if match_alloc and match_alloc.get('stable_id')=='D09_salon5' else 'required programme; architecture pending','current_geometry_owner':'D09_salon5_initial_terrace' if match_alloc and match_alloc.get('stable_id')=='D09_salon5' else None})
assert len({x['programme_key'] for x in entries})==len(entries)
assert len({x['historical_deck'] for x in entries})==18
result={'schema':1,'authority':'Programme continuity ledger, not a second room registry. Historical envelopes are allocations, not mandatory walls. Latest owner decisions override old species, bed and tier assumptions.','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'destinations':entries,'accommodation':{'guest_unit_target':1000,'passenger_admission_cap':2000,'crew_including_player':400,'historical_upper_guest_envelopes':sum(x['kind']=='unlabelled_guest_allocation' for x in allocations),'historical_D04_units_without_extracted_envelopes':120,'luxury_replacements':{'deluxe':50,'premium':25,'royalty':5,'supreme':1},'current_finished_units':0,'identity_policy':'Anonymous atlas footprints cannot establish original persistent IDs. Reconcile IDs explicitly before occupancy/save creation.','physical_beds':'To be reconciled separately from passenger admission cap'},'retail':{'small_shop_target':100,'historical_shop_envelopes':sum(x['kind']=='unlabelled_shop_allocation' for x in allocations),'large_destination_target':10},'later_required_features':[{'name':'Lazy river, tube ride and slide park','status':'Required; final connected allocation and section pending'},{'name':'Restaurant watercourse and waterpark cascade','status':'Required; reconcile Vesper and connected lower allocation before slab removal'},{'name':'Royalty and Supreme multi-storey suites','status':'Required within existing1000units; final boundary/bed/clearance review pending'},{'name':'Named multi-deck residential courts','status':'Required; local lobbies/lifts and inward views must be coordinated with retained destinations'}]}
(root/'data/programme_ledger.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'destinations':len(entries),'decks':18,'anonymous_guest_envelopes':880,'anonymous_shop_envelopes':100,'finished_units':0}))
