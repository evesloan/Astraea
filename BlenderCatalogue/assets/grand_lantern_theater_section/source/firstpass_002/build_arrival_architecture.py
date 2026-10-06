"""Open vaulted arrival courts: real supported forms, framed planting and thresholds.
Additive bounded source-only geometry. No cuts to retained stairs, floors or walls.
"""
from pathlib import Path
import json,math,numpy as np,ast,copy
R=Path(__file__).resolve().parent;objects=[]
t=ast.parse((R/'build_luminous_fixture_geometry.py').read_text());defs=[n for n in t.body if isinstance(n,ast.FunctionDef)and n.name in ['emit','rect','prism']];exec(compile(ast.Module(body=defs,type_ignores=[]),'<reviewed_geometry_helpers>','exec'))
lighting=json.loads((R/'LUMINOUS_FIXTURE_GEOMETRY_002.json').read_text());newcoffers=[];courts=[]
def cube(name,lo,hi,mat,role,**extra):
 cx=(lo[0]+hi[0])/2;cz=(lo[2]+hi[2])/2;prism(name,rect(hi[0]-lo[0],hi[2]-lo[2],min(.035,(hi[2]-lo[2])/4,(hi[0]-lo[0])/4)),lo[1],hi[1],mat,role,origin=(cx,cz),**extra)
def coffer(pre,x,y,z):
 top=rect(3,.76);bottom=rect(2.88,.64);inner=rect(2.76,.50,.05);n=8
 prism(pre+'_backplate',top,y-.035,y,'ivory_enamel','fixed_luminaire',origin=(x,z),contact=pre.rsplit('_LIGHT',1)[0]+'_ribbon_actual_flat_crown')
 vv=[[x+a,h,z+b]for poly,h in[(top,y-.035),(inner,y-.035),(bottom,y-.18),(inner,y-.18)]for a,b in poly];ff=[]
 for i in range(n):
  j=(i+1)%n;ff.extend([[i,j,n+j,n+i],[2*n+i,3*n+i,3*n+j,2*n+j],[i,2*n+i,2*n+j,j],[n+i,n+j,3*n+j,3*n+i]])
 emit(pre+'_hollow_frame',vv,ff,'champagne_metal','fixed_luminaire');prism(pre+'_opal_lens',rect(2.8,.54,.055),y-.155,y-.143,'hospitality_opal','physical_luminous_lens',origin=(x,z))
 return {'fixture_name':pre+'_opal_lens','position_world':[x,y-.160,z]}
for deck,floor in [('D11',69.5),('D12',78),('D13',84)]:
 for code,cx,width,front,back in [('A',-69.5,9.0,-130.4,-146.2),('B',-89.5,11.4,-133.0,-146.2),('C',-106.5,10.0,-133.8,-121.5)]:
  pre=f'FP2_{deck}_COURT_{code}';zs=[front,(front+back)/2,back];half=width/2
  # Three open transverse vault ribbons leave the multi-level space visible between them.
  xx=sorted(set([-half,-half+.3,-half*.72,-half*.48,-1.7,0,1.7,half*.48,half*.72,half-.3,half]))
  def top(x):
   t=max(0.,(abs(x)-1.7)/(half-1.7));return floor+4.65-.60*(.5-.5*math.cos(math.pi*t))
  centre_lens=None
  for j,z in enumerate(zs):
   vv=[[cx+x,h,z+dz]for dz in[-.525,.525]for hfn in[lambda x:top(x)-.24,top]for x in xx for h in[hfn(x)]];n=len(xx);ff=[]
   for i in range(n-1):ff.extend([[i,i+1,n+i+1,n+i],[2*n+i,3*n+i,3*n+i+1,2*n+i+1],[i,2*n+i,2*n+i+1,i+1],[n+i,n+i+1,3*n+i+1,3*n+i]])
   ff.extend([[0,n,3*n,2*n],[n-1,2*n-1,4*n-1,3*n-1]])
   emit(f'{pre}_VAULT_{j}',vv,ff,'ivory_enamel','architectural_open_vault',contact='Six full-height piers on exact foyer floors; stepped flat crown supports real coffer plate')
   lens=coffer(f'{pre}_LIGHT_{j}',cx,floor+4.41,z)
   if j==1:centre_lens=lens
   for side in[-1,1]:
    x=cx+side*(half-.12);cube(f'{pre}_PIER_{j}_{side}',[x-.22,floor,z-.28],[x+.22,floor+3.83,z+.28],'ivory_enamel','architectural_pier',contact='Exact owned foyer walking-floor surface; no load certification')
    cube(f'{pre}_FOOT_{j}_{side}',[x-.25,floor,z-.32],[x+.25,floor+.055,z+.32],'champagne_metal','architectural_pier_foot')
    cube(f'{pre}_CAP_{j}_{side}',[x-.27,floor+3.78,z-.34],[x+.27,floor+3.84,z+.34],'warm_walnut','architectural_pier_head',contact='Bounded shaped-ribbon bearing')
  # A low transparent framed backdrop establishes a room edge without blank walls.
  rear=back if code!='C'else-121.9;innerwidth=width-.80;panelwidth=(innerwidth-.12)/3
  for j in range(3):
   x0=cx-innerwidth/2+j*(panelwidth+.06);x1=x0+panelwidth
   cube(f'{pre}_SCREEN_{j}',[x0,floor+.22,rear-.004],[x1,floor+2.40,rear+.004],'gallery_glass','fixed_transparent_screen',contact='Supported toe/head rails and end mullions; not an operational glazing/impact certificate')
   cube(f'{pre}_SCREEN_TOE_{j}',[x0-.025,floor+.15,rear-.035],[x1+.025,floor+.24,rear+.035],'champagne_metal','fixed_screen_frame')
   cube(f'{pre}_SCREEN_HEAD_{j}',[x0-.025,floor+2.38,rear-.035],[x1+.025,floor+2.43,rear+.035],'champagne_metal','fixed_screen_frame')
   for side,x in [('L',x0-.018),('R',x1+.018)]:cube(f'{pre}_SCREEN_POST_{j}_{side}',[x-.018,floor,rear-.04],[x+.018,floor+2.43,rear+.04],'champagne_metal','fixed_screen_frame')
  courts.append({'id':pre,'deck':deck,'floor_y':floor,'purpose':{'A':'Framed programme/usher threshold with layered garden backdrop','B':'Open intermission salon with seating facing planted focal court','C':'Quiet rear conversation court framing foliage and the passing gallery'}[code],'centre_light':centre_lens,'maximum_y':floor+4.65,'open_vault_bands':3,'screen_kind':'Transparent interior decorative screens only; original walls and all circulation voids remain'})
# Six bank candidates per foyer: three court crowns, two real east-entry coffers,
# and a rear spine coffer. Eight-source arrival adds the two actual stair-face banks.
old_lights=lighting['physical_bank_light_candidates'];newlights=[]
for deck in ['D11','D12','D13']:
 for i,code in enumerate(['A','B','C']):
  court=next(c for c in courts if c['deck']==deck and c['id'].endswith('_'+code));lens=court['centre_light'];cx,y,z=lens['position_world']
  newlights.append({'id':f'FP2_{deck}_BANK_{i}','type':'SPOT','fixture_name':lens['fixture_name'],'position_world':lens['position_world'],'aim_world':[0,-1,0],'full_cone_degrees':160,'range_m':90,'initial_source_watts':700,'color_linear':[1,.91,.80],'shadow_candidate':True,'represented_fixtures':[lens['fixture_name']],'illumination_anchor':[cx,court['floor_y']+.05,z+1.7],'budget_basis':'Actual luminous court crown; authored receiver permits existing source/receiver visibility policy. Native selection still to test.'})
 for i,(x,z)in enumerate([(-40,-138),(-40,-129),(-84,-120)],3):
  c=next(c for c in lighting['coffers']if c['deck']==deck and c['mount_centre_world'][0]==x and c['mount_centre_world'][2]==z)
  newlights.append({'id':f'FP2_{deck}_BANK_{i}','type':'OMNI','fixture_name':c['native_fixture_name'],'position_world':c['emitter_world'],'range_m':90,'initial_source_watts':1800,'color_linear':[1,.91,.80],'shadow_candidate':True,'represented_fixtures':[c['native_fixture_name']]})
newlights += [x for x in old_lights if '_ST_'in x['id']]
lighting['objects']+=objects;lighting['composed_arrival_courts']=courts;lighting['physical_bank_light_candidates']=newlights
lighting['first_arrival_eight_source_preview']=[l['id']for l in newlights if l['id'].startswith('FP2_D11_BANK_')or l['id'].startswith('FP2_ST_D11_D12_')];assert len(lighting['first_arrival_eight_source_preview'])==8
(R/'COMPOSED_ARRIVAL_LIGHT_ARCHITECTURE_002.json').write_text(json.dumps(lighting,indent=2)+'\n');print('Authored9open vaulted courts;',len(objects),'new architectural/fixture mesh parts; arrival uses8physical source anchors')
