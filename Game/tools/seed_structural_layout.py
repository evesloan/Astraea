"""One-time seed of reviewed structural reservations, not a room generator."""
import json, math, shutil
from pathlib import Path
root = Path(__file__).resolve().parents[1]
assert not (root/'data/spatial_layout.json').exists(), 'Preserve authored layout; edit its records deliberately'
regions = []
def rect(x0,z0,x1,z1):
    return [[x0,z0],[x1,z0],[x1,z1],[x0,z1]]
def add(identifier,deck,boundary,**extra):
    regions.append(dict(id=identifier,deck=deck,boundary=boundary,status='R1 structural circulation only; final architecture unfinished',**extra))
for index in range(18):
    deck = f'D{index+1:02}'
    width = 6 if index in [5,8,11,15] else 3
    add(deck+'_fore_route',deck,rect(-4,-530,4,-80))
    add(deck+'_aft_route',deck,rect(-4,80,4,530))
    limit = 64+width if 1 <= index <= 16 else 64
    add(deck+'_fore_apron',deck,rect(-48,-80,48,-limit))
    add(deck+'_aft_apron',deck,rect(-48,limit,48,80))
    if 1 <= index <= 16:
        add(deck+'_atrium_circulation',deck,rect(-48-width,-64-width,48+width,64+width),holes=[rect(-48,-64,48,64)],thickness=.55 if index in [5,8,11,15] else .24)
    else:
        add(deck+'_service_side',deck,rect(42,-64,48,64))
add('D09_salon5_initial_terrace','D09',[[48,-34],[66,-34],[72,-30],[76,-22],[76,-10],[70,-3],[60,4],[48,4]],priority=10,thickness=.45,room_id='D09_salon5')
angle = math.pi/6
outer = []
inner = []
for index in range(13):
    theta = angle*index/12
    outer.append([-48-(10-10*math.cos(theta)),-10*math.sin(theta)])
    inner.append([-48-(10-5.8*math.cos(theta)),-5.8*math.sin(theta)])
add('D06_arc001_component','D06',outer+list(reversed(inner)),priority=20,provided_by_asset='AST-ARC-001',placement={'position':[-48,27,0],'rotation_y_degrees':90})
voids = [
    {'id':'central_atrium','decks':[f'D{i:02}' for i in range(2,18)],'boundary':rect(-48,-64,48,64),'source':'Master96x128m opening; D02basin authored separately'},
    {'id':'theater_upper_volume','decks':['D12','D13','D14'],'boundary':rect(-118,-265,-34,-115),'source':'Master and auditorium footprint; no generic floor through theater'},
    {'id':'D06_swept_edge_cut','decks':['D06'],'boundary':outer+[[-48,outer[-1][1]]],'source':'Reversible authored edge study; retains central void; port-side away from tram'}
]
layout = {'schema_version':1,'status':'Permanent ship structural foundation, not final deck/room design','source_policy':'Latest owner decisions and reconciled master; no floor inferred from a room label','regions':regions,'voids':voids}
(root/'data/spatial_layout.json').write_text(json.dumps(layout,indent=2)+'\n')
