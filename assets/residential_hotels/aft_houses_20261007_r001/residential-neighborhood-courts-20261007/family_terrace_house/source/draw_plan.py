"""Source plan diagram from exact authored polygon data; never a game capture."""
from pathlib import Path
import json,os,sys
os.environ['MPLCONFIGDIR']='/tmp/family-terrace-mpl-cache'
sys.path.insert(0,'/workspace/scratch/375c2e438292/geometry-deps')
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Patch
from shapely.geometry import Polygon,shape
R=Path(__file__).resolve().parents[1];p=json.loads((R/'outputs/house_r001/PLAN.json').read_text());cross=json.loads((R.parents[1]/'residential-neighborhood-audit-20261007/ALL_1000_NEIGHBORHOOD_CROSSWALK.json').read_text())['records'];house=[r for r in cross if r['house']==p['house_id']];vip={r['source_envelope_index']:r for r in p['D17_replacement_reservations']};built={r['census_source_index']for r in p['rooms']}
fig,axs=plt.subplots(1,5,figsize=(17,10),layout='constrained');fig.patch.set_facecolor('#f4f1e8')
for level,(ax,y)in enumerate(zip(axs,p['upper_datums'])):
 ax.set_facecolor('#f4f1e8');ax.set_aspect('equal');ax.set_xlim(0,120);ax.set_ylim(245,495);ax.invert_yaxis();ax.set_xticks([8,44,63,100]);ax.tick_params(labelsize=7)
 for row in p['floor_regions']:
  if row['floor_y']!=y:continue
  geo=shape(row['geometry']);polys=[geo]if geo.geom_type=='Polygon'else list(geo.geoms)
  for q in polys:
   ax.add_patch(Patch(q.exterior.coords,facecolor='#ddd0b8',edgecolor='#8f826d',linewidth=.5))
   for hole in q.interiors:ax.add_patch(Patch(hole.coords,facecolor='#f4f1e8',edgecolor='#8f826d',linewidth=.4))
 for part in p['parts']:
  if part['kind']!='mesh'or part['category']not in['water','planter']or not(y<=min(v[1]for v in part['verts'])<y+1.4):continue
  q=Polygon([(v[0],v[2])for v in part['verts']]).convex_hull;ax.add_patch(Patch(q.exterior.coords,facecolor='#79b7b6'if part['category']=='water'else'#729777',edgecolor='none',alpha=.8))
 units=[r for r in house if r['deck']=='D'+str(13+level)]
 for r in units:
  i=r['source_envelope_index'];q=vip[i]['proposed_floor_boundary']if i in vip else[(r['allocation_x'][0],r['allocation_z'][0]),(r['allocation_x'][1],r['allocation_z'][0]),(r['allocation_x'][1],r['allocation_z'][1]),(r['allocation_x'][0],r['allocation_z'][1])]
  ax.add_patch(Patch(q,facecolor='#577c87'if i in built else'#e6d9c9',edgecolor='#3c5c62'if i in built else'#a38b71',linewidth=.55,hatch=None if i in built else'///'))
  if i in built:
   rr=next(v for v in p['rooms']if v['census_source_index']==i);x,z=rr['historical_door_marker_xz'];ax.plot([x],[z],'.',color='#1d3438',ms=1.8)
 n=sum(r['source_envelope_index']in built for r in units);ax.set_title(f'D{13+level} · Y{y:g}m\n{len(units)} allocations / {n} authored interiors',fontsize=9,fontweight='bold')
 ax.grid(alpha=.10);ax.set_xlabel('World X (m)',fontsize=8)
axs[0].set_ylabel('World Z (m), forward upward',fontsize=9)
fig.suptitle('FAMILY TERRACE HOUSE · 145 preserved allocations · 82 source interiors / 63 unbuilt reservations\nExact starboard-aft court, sociable terraces, group pockets and actual D17 replacement polygons',fontsize=15,fontweight='bold')
fig.text(.5,.006,'Blue: 82 authored interior placements  |  Hatching: 47 specialty + 16 VIP unbuilt  |  Tan: owned public floor  |  Green: rooted planting\nSource diagram only. D12 Celestial lounge / Reading nooks protected; base receiving support, operating lift, full-house privacy and runtime acceptance remain open.',ha='center',fontsize=8)
fig.savefig(R/'outputs/FAMILY_TERRACE_FIVE_LEVEL_SOURCE_PLAN.png',dpi=150,bbox_inches='tight');fig.savefig(R/'outputs/FAMILY_TERRACE_FIVE_LEVEL_SOURCE_PLAN.svg',bbox_inches='tight');print('FAMILY_TERRACE_SOURCE_PLAN_DIAGRAM_READY')
