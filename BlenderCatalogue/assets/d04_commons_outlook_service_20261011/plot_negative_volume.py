from pathlib import Path
import json,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as PlotPath
from matplotlib.patches import PathPatch
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));fig,ax=plt.subplots(figsize=(9,8));ax.fill([-97,-63,-63,-97],[-384,-384,-356,-356],color='#eeeeee')
for layer in json.load(open(R/'BlenderCatalogue/assets/d04_commons_social_dayroom_20261011/FLOOR_COVERAGE_LAYERS.json')):
 for j,ring in enumerate(layer['rings']):x,z=zip(*ring);ax.fill(x,z,color=layer['color'],label=layer['name']if j==0 else None)
colors=['#d7cb9d','#d4c4d9','#bac9d7','#e5d0b4'];labels=['Stair void18.90m²','Outside keel projection357.02m²','South support/service reserve149.48m²','Boundary clearances5.32m²']
for zone,color,label in zip(P['negative_volume_zones'],colors,labels):
 g=zone['geometry'];polys=[g['coordinates']]if g['type']=='Polygon'else g['coordinates']
 for j,rings in enumerate(polys):
  verts=[];codes=[]
  for ring in rings:verts+=ring;codes +=[PlotPath.MOVETO]+[PlotPath.LINETO]*(len(ring)-2)+[PlotPath.CLOSEPOLY]
  ax.add_patch(PathPatch(PlotPath(verts,codes),facecolor=color,edgecolor='#666666',hatch='//'if j==0 else'//',linewidth=.6,label=label if j==0 else None))
ax.set_xlim(-98,-62);ax.set_ylim(-385,-355);ax.set_aspect('equal');ax.set_xlabel('Ship X (m)');ax.set_ylabel('Ship Z (m)');ax.set_title('D04952m² reservation:421.28m² floor +530.72m² negative volume\nFloor-free clearance purposes; perimeter/service engineering remains held');ax.legend(loc='lower left',fontsize=8);fig.tight_layout();assert not(W/'RESERVATION_RECONCILIATION.png').exists();fig.savefig(W/'RESERVATION_RECONCILIATION.png',dpi=150)
