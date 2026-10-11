from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
W=Path(__file__).resolve().parent;R=W.parents[2];p=json.load(open(W/'PLAN.json'))
fig,ax=plt.subplots(figsize=(9,8));ax.fill([-97,-63,-63,-97],[-384,-384,-356,-356],color='#eeeeee',label='952m² reservation; remainder unreconciled')
for layer in json.load(open(W/'FLOOR_COVERAGE_LAYERS.json')):
 for j,ring in enumerate(layer['rings']):
  x,z=zip(*ring);ax.fill(x,z,color=layer['color'],label=layer['name']if j==0 else None);ax.plot(x,z,color='#333333',linewidth=.8)
ax.fill([-64.8,-63,-63,-64.8],[-381.3,-381.3,-370.8,-370.8],facecolor='white',hatch='///',edgecolor='#666666',label='Retained stair void18.9m²')
route=p['route'];ax.plot([a[0]for a in route],[a[2]for a in route],'k--',linewidth=1.5,label='Dayroom public route')
ax.set_xlim(-98,-62);ax.set_ylim(-385,-355);ax.set_aspect('equal');ax.set_xlabel('Ship X (m)');ax.set_ylabel('Ship Z (m)');ax.set_title('D04 commons: actual floor union421.28m² / reservation952m²\n530.72m² remainder: functions / negative volume not reconciled');ax.legend(loc='lower left',fontsize=8);fig.tight_layout();assert not(W/'FLOOR_COVERAGE.png').exists();fig.savefig(W/'FLOOR_COVERAGE.png',dpi=150)
