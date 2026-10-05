"""Prepare reviewed bridge-platform adoption; the public bypass precedes bridge enclosure."""
from pathlib import Path
import argparse,copy,hashlib,json,shutil
from shapely.geometry import Polygon
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1]
C=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
OWNER='bridge_platform'

def write(path,value):path.write_text(json.dumps(value,indent=2)+'\n')

def plan_floors(layout,brief):
    result=copy.deepcopy(layout)
    result['regions']=[r for r in result['regions'] if r.get('authoring_owner')!=OWNER]
    existing=unary_union([Polygon(r['boundary'],r.get('holes',[])) for r in result['regions'] if r['deck']=='D18' and abs(r.get('offset_y',0))<1e-6])
    added=[]
    for kind,target,expected in [('bridge',Polygon(brief['bridge_floor']['boundary']),3384),('bypass',Polygon(brief['public_bypass']['boundary']),1096)]:
        missing=target.difference(existing)
        assert abs(missing.area-expected)<1e-6, 'Current substrate changed: '+kind
        pieces=sorted(list(missing.geoms) if missing.geom_type=='MultiPolygon' else [missing],key=lambda p:p.centroid.x)
        assert len(pieces)==(2 if kind=='bridge' else 1)
        for i,p in enumerate(pieces):
            assert p.is_valid and len(p.interiors)==0
            assert p.intersection(existing).area<1e-6
            assert all(p.intersection(Polygon(v['boundary'])).area<1e-6 for v in result['voids'] if 'D18' in v.get('decks',[]))
            suffix=('port_wing' if i==0 else 'starboard_wing') if kind=='bridge' else 'public_bypass'
            row={'id':'D18_bridge_platform_'+suffix,'authoring_owner':OWNER,'deck':'D18','boundary':[list(q) for q in p.exterior.coords[:-1]],'holes':[],'priority':80,'thickness':.24,'material_role':'guest_floor','status':'Supported platform stage; bridge enclosure and route revision are separate acceptance gates'}
            result['regions'].append(row);added.append(p)
    assert abs(sum(p.area for p in added)-4480)<1e-6
    assert abs(unary_union(added).area-4480)<1e-6
    return result

def author(expected_sha):
    brief=json.loads((R/'data/architecture/BRIDGE_PLATFORM_CONSTRUCTION.json').read_text())
    asset=C/'assets/bridge_platform/exports/AST-CMD-003.glb'
    assert hashlib.sha256(asset.read_bytes()).hexdigest()==expected_sha,'Export differs from reviewed final bytes'
    data=json.loads((asset.parent.parent/'source/section_contract.json').read_text())
    assert data['catalogue_id']=='AST-CMD-003'
    manifest=json.loads((C/'catalogue_manifest.json').read_text())
    rows=[r for r in manifest['assets'] if r['catalogue_id']=='AST-CMD-003']
    assert len(rows)==1 and rows[0]['family']=='bridge_platform' and rows[0]['export_sha256']==expected_sha
    assert not data.get('doors',[]),'Stage1 must leave original centreline open; bridge enclosure belongs later'
    layout=plan_floors(json.loads((R/'data/spatial_layout.json').read_text()),brief)
    data['export_sha256']=expected_sha
    data['runtime_status']='Supported platform/bypass integration; no private bridge enclosure or final route acceptance yet'
    write(R/'data/spatial_layout.json',layout)
    write(R/'data/architecture/BRIDGE_PLATFORM_RUNTIME.json',data)
    shutil.copyfile(asset,R/'assets/models/AST-CMD-003.glb')
    # Keep the programme ledger unchanged until its partial geometry scope is explicitly reviewed.
    print(json.dumps({'added_floor_m2':4480,'new_private_bridge_enclosure':False,'existing_fore_route_preserved':True,'runtime_and_visual_acceptance_pending':True}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--expected-sha',required=True);a=p.parse_args();author(a.expected_sha)
