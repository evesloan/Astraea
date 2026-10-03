"""Export current authored guard paths for the Blender construction family."""
from pathlib import Path
import argparse,json
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
root=Path(__file__).resolve().parents[1];layout=json.loads((root/'data/spatial_layout.json').read_text());contours=json.loads((root/'data/reference/atrium_contours.json').read_text());levels={x['deck_id']:x['floor_elevation_m'] for x in json.loads((root/'data/design_contract.json').read_text())['deck_datums']};paths=[]
for c in contours['decks']:
 hole=Polygon(c['inner'])
 if c['deck']=='D06':hole=hole.union(Polygon(next(v['boundary'] for v in layout['voids'] if v['id']=='D06_swept_edge_cut')))
 assert hole.geom_type=='Polygon'
 hole=orient(hole.simplify(.005,preserve_topology=True),sign=1)
 paths.append({'deck':c['deck'],'floor_y':levels[c['deck']],'major':c['deck'] in ['D06','D09','D12','D16'],'boundary':[list(x) for x in hole.exterior.coords[:-1]]})
args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps({'source':'Historical authored contours plus current fitted edge adjustments; one construction family, not sixteen independent new designs','decks':paths},indent=2)+'\n')
print(args.output)
