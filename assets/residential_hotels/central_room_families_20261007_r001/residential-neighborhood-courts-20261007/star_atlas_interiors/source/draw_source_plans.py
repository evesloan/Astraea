from pathlib import Path
import json,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Patch
R=Path(__file__).resolve().parents[1];W=R.parents[1];sys.path.insert(0,str(W/'geometry-deps'))
from shapely.geometry import MultiPoint
from shapely.ops import unary_union
P=json.loads((R/'STAR_ATLAS_85_PLACEMENT_MAP.json').read_text());fig,axs=plt.subplots(2,4,figsize=(15,14),layout='constrained');colors={'rest':'#4f7c85','seat':'#af7467','bath':'#8d999a','wood':'#7a5944','door':'#c4995c'}
for cfg,ax in zip(P['prototypes'],axs.ravel()):
 obs=json.loads((R/'outputs/source_r002'/cfg['address']/'EVALUATED_GEOMETRY.json').read_text());groups={}
 for o in obs:
  lo,hi=o['bounds'];name=o['name'];member=o['assembly_member']
  if hi[2]<=.04 or lo[2]>=2 or name.startswith(('SUI_Fitted','SUI_Carpet','SA_LibraryWoven','SA_OutlookWoven')):continue
  p=MultiPoint(np.array(o['vertices'])[:,:2]).convex_hull
  if p.area<1e-8:continue
  key=member or 'shell';groups.setdefault(key,[]).append(p)
 for key,geoms in groups.items():
  p=unary_union(geoms);parts=list(p.geoms)if hasattr(p,'geoms')else[p]
  c=colors['rest'if 'BedAnchor'in key else'seat'if'Chair'in key or'Bench'in key else'bath'if'bath_'in key else'door'if'Door'in key else'wood']
  for part in parts:
   if hasattr(part,'exterior'):ax.add_patch(Patch(part.exterior.coords,facecolor=c,edgecolor='#332d2a',lw=.25))
 for o in obs:
  if o['name']=='SA_FanningLibraryCanopy':
   p=MultiPoint(np.array(o['vertices'])[:,:2]).convex_hull;ax.plot(*p.exterior.xy,color='#c09341',ls='--',lw=1.4)
 for a in cfg['bed_anchors']:
  x,y,_=a['source_xyz'];ax.text(x,y,str(a['historical_anchor_index']+1),ha='center',va='center',color='white',weight='bold',fontsize=10)
 ax.plot([-3.4,3.4],[12.78,12.78],color='#67a7b3',lw=3);ax.text(0,13.18,'SEALED WINDOW / retained view class',ha='center',fontsize=7)
 ax.text(0,-.75,'ENTRY',ha='center',fontsize=7);ax.set_title(cfg['historical_class'].title()+' · '+cfg['star_atlas_design'].replace('_',' ').title()+' · '+('L'if cfg['star_atlas_handing']==1 else'R'),fontsize=10)
 ax.set(xlim=(-3.9,3.9),ylim=(-1.1,13.7),aspect='equal');ax.set_xticks([-3,0,3]);ax.set_yticks([0,4,8,12]);ax.grid(alpha=.12);ax.set_xlabel('metres');ax.set_ylabel('metres')
fig.suptitle('Star Atlas · eight actual evaluated source plans (r002)\n85 mapped units / 221 retained slot IDs · dashed line: lowered library canopy\nSource-only: receiving architecture, moving doors, cart/species clearance and runtime privacy remain open',fontsize=13)
fig.savefig(R/'outputs/STAR_ATLAS_EIGHT_SOURCE_PLANS.png',dpi=140);fig.savefig(R/'outputs/STAR_ATLAS_EIGHT_SOURCE_PLANS.svg');print('ACTUAL_SOURCE_PLANS_SAVED')
