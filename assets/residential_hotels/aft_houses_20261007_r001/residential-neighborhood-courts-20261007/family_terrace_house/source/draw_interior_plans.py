"""Inspect actual evaluated source plans, including exact curved shell profiles."""
from pathlib import Path
import json,sys,os
os.environ['MPLCONFIGDIR']='/tmp/family-terrace-mpl';R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parents[1]/'geometry-deps'))
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Patch
from shapely.geometry import MultiPoint
p=json.loads((R/'FAMILY_TERRACE_82_PLACEMENT_MAP.json').read_text());fig,axs=plt.subplots(2,4,figsize=(14,12),layout='constrained')
for cfg,ax in zip(sorted(p['prototypes'],key=lambda r:r['address']),axs.flat):
 d=R/'outputs/interiors_r003'/cfg['address'];obs=json.loads((d/'EVALUATED_GEOMETRY.json').read_text());rec=json.loads((d/'SOURCE_RECEIPT.json').read_text());profile=rec['actual_shell_profile'];ax.set_facecolor('#f4f0e7');ax.add_patch(Patch(profile['left']+list(reversed(profile['right'])),facecolor='#e7dbc6',edgecolor='#635847',lw=1.3))
 for ob in obs:
  name=ob['name'];lo,hi=ob['bounds']
  if hi[2]<.03 or lo[2]>1.65 or name.startswith(('SUI_Floor','SUI_FittedCarpet','SUI_CarpetBinding')):continue
  q=MultiPoint([v[:2]for v in ob['vertices']]).convex_hull
  if q.geom_type!='Polygon':continue
  col='#80989a'if ob['assembly_member'].startswith('HistoricalBed')else'#a9865c'if name.startswith('FT_')else'#c8beab'
  ax.add_patch(Patch(q.exterior.coords,facecolor=col,edgecolor='#534e45',lw=.20,alpha=.85))
 for i,a in enumerate(cfg['bed_anchors']):
  x,y,_=a['source_xyz'];ax.text(x,y,str(i+1),ha='center',va='center',weight='bold',fontsize=9,color='white')
 ax.set_xlim(-3.7,3.7);ax.set_ylim(-.1,13.0);ax.invert_yaxis();ax.set_aspect('equal');ax.set_title(cfg['historical_class'].title()+' / '+cfg['family_terrace_design'].replace('_',' ')+' / '+('L'if cfg['family_terrace_handing']==1 else'R')+'\n'+cfg['layout'],fontsize=10);ax.set_xticks([-3,0,3]);ax.set_yticks([0,4,8,12]);ax.grid(alpha=.10)
fig.suptitle('Family Terrace: eight actual evaluated source recipes / 82 exact unit bindings\nShared group table, open belongings storage and independent real rest approaches',fontsize=15,weight='bold');fig.savefig(R/'outputs/FAMILY_TERRACE_INTERIOR_SOURCE_PLANS.png',dpi=130,bbox_inches='tight');fig.savefig(R/'outputs/FAMILY_TERRACE_INTERIOR_SOURCE_PLANS.svg',bbox_inches='tight');print('INTERIOR_SOURCE_PLANS_READY')
