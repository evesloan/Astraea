"""Update presence counts in an explicitly selected catalogue. Not room/quality acceptance."""
from pathlib import Path
import json,argparse
parser=argparse.ArgumentParser();parser.add_argument('--catalogue',required=True,type=Path);args=parser.parse_args()
root=Path(__file__).resolve().parents[1];path=args.catalogue/'catalogue_manifest.json';catalogue=json.loads(path.read_text());report=json.loads((root/'artifacts/asset_adoption.json').read_text())
identifiers=sorted((a['catalogue_id'] for a in catalogue['assets']),key=len,reverse=True);counts={}
for name,count in report['by_file'].items():
 matches=[aid for aid in identifiers if name==aid+'.glb' or name.startswith(aid+'_') or name.startswith(aid+'-H')]
 assert matches,('Unregistered imported design',name)
 aid=matches[0];counts[aid]=counts.get(aid,0)+count
for asset in catalogue['assets']:asset['adopted_game_instances']=counts.get(asset['catalogue_id'],0)
catalogue['game_static_stock_groups']=report.get('static_stock_groups',0);catalogue['game_adoption_count']=len(counts);catalogue['game_instance_count']=report['instances'];catalogue['game_adoption_scope']='Instantiated Godot main-scene presence only; not completed rooms, visible quality or gameplay acceptance'
temporary=path.with_suffix('.json.tmp');temporary.write_text(json.dumps(catalogue,indent=2)+'\n');temporary.replace(path)
print(json.dumps({'designs_present':len(counts),'instances':report['instances'],'scope':catalogue['game_adoption_scope']}))
