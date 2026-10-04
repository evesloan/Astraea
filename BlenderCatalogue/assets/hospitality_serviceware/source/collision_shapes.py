"""Conservative split geometry proposals, never runtime collisions or dynamics."""
import json,math
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
def C(p):return [p[0],p[2],-p[1]]
def box(name,lo,hi,node=None):
 corners=[[x,y,z]for x in[lo[0],hi[0]]for y in[lo[1],hi[1]]for z in[lo[2],hi[2]]];g=list(map(C,corners))
 return {'name':name,'type':'box','source_node':node or name,'blender_z_up':{'min_m':lo,'max_m':hi},'gltf_y_up':{'min_m':[min(v[k]for v in g)for k in range(3)],'max_m':[max(v[k]for v in g)for k in range(3)]}}
def capsule(name,a,b,r,node=None,kind='capsule'):
 return {'name':name,'type':kind,'source_node':node or name,'blender_z_up':{'a_m':a,'b_m':b,'radius_m':r},'gltf_y_up':{'a_m':C(a),'b_m':C(b),'radius_m':r}}
def build():
 s=[]
 s.append(box('005_top',[-.55,-.39,.852],[.55,.39,.9],'005_rounded_warm_stone_worktop'))
 s.append(box('005_plinth',[-.5275,-.355,.128],[.5275,.355,.181],'005_lower_ivory_continuous_plinth'))
 s.append(box('005_guest_fascia',[-.489,-.375,.180],[.489,-.310,.838],'005_bowed_walnut_guest_fascia'))
 for name,x in[('left',-.527),('right',.483)]:s.append(box('005_'+name+'_cheek',[x,-.358,.177],[x+.044,.353,.852],'005_'+name+'_shaped_ivory_end_cheek'))
 s.append(box('005_divider',[.040,-.309,.180],[.064,.345,.840],'005_central_structural_divider'))
 for kind,zs,xs in[('tray',[.245,.473,.701],[-.4725,.0285]),('plate',[.245,.535],[.073,.475])]:
  for i,z in enumerate(zs):
   s.append(box('005_'+kind+'_shelf_'+str(i),[xs[0],-.294,z-.020],[xs[1],.326,z]))
   pairs=[(-.490,-.456),(.020,.048)]if kind=='tray'else[(.056,.086),(.460,.491)]
   for k,(a,b)in enumerate(pairs):s.append(box('005_'+kind+'_shelf_'+str(i)+'_folded_cleat_'+str(k),[a,-.285,z-.048],[b,.306,z-.020]))
 for x,side in[(-.441,'left'),(.441,'right')]:
  for y,end in[(-.257,'front'),(.257,'rear')]:s.append(capsule('005_'+side+'_'+end+'_foot',[x,y,0],[x,y,.128],.047,'005_'+side+'_'+end+'_leveling_foot','cylinder'))
 t=[]
 for tier,z in[('lower',.225),('upper',.785)]:
  t.append(box('006_'+tier+'_tier',[-.34,-.27,z-.041],[.34,.27,z+.006],'006_'+tier+'_ivory_formed_tier'))
  pts=[[-.297,.150,z+.032],[-.302,-.140,z+.032],[-.280,-.192,z+.032],[-.235,-.215,z+.032],[.235,-.215,z+.032],[.280,-.192,z+.032],[.302,-.140,z+.032],[.297,.150,z+.032]]
  for i,(a,b)in enumerate(zip(pts,pts[1:])):t.append(capsule('006_'+tier+'_retention_'+str(i),a,b,.008,'006_'+tier+'_three_sided_retention_rail'))
 for x,side in[(-.272,'left'),(.272,'right')]:
  for y,end in[(-.184,'front'),(.184,'rear')]:
   pts=[[x,y,.128],[x,y,.220],[x,y,.745],[x*.96,y*.94,.780]]
   for i,(a,b)in enumerate(zip(pts,pts[1:])):t.append(capsule('006_'+side+'_'+end+'_support_'+str(i),a,b,.016,'006_'+side+'_'+end+'_continuous_support'))
  pts=[[x,.184,.737],[x,.190,.824],[x*.97,.240,.889],[x*.92,.302,.923],[x*.90,.355,.925]]
  for i,(a,b)in enumerate(zip(pts,pts[1:])):t.append(capsule('006_'+side+'_push_'+str(i),a,b,.016,'006_'+side+'_swept_push_stanchion'))
 t.append(capsule('006_push_grip',[-.2448,.355,.925],[.2448,.355,.925],.019,'006_rear_dark_push_grip'))
 for x,side in[(-.267,'left'),(.267,'right')]:
  for y,end in[(-.179,'front'),(.179,'rear')]:
   tag=side+'_'+end
   t.append(capsule('006_'+tag+'_wheel',[x-.019,y-.020,.055],[x+.019,y-.020,.055],.055,'006_'+tag+'_rubber_wheel','cylinder'))
   t.append(capsule('006_'+tag+'_bearing',[x,y,.120],[x,y,.136],.029,'006_'+tag+'_swivel_bearing','cylinder'))
   for sign in[-1,1]:t.append(box('006_'+tag+'_fork_'+str(sign),[x+sign*.030-.005,y-.061,.052],[x+sign*.030+.005,y+.025,.127]))
   for q in t[-4:]:q['moving_parent']='006_'+tag+'_swivel'
 # Numeric volume proposals are world-in-asset coordinates, translated/rotated by the consumer with the imported hierarchy.
 data={'status':'Conservative component collision proposals only; no engine solver or player cart/controller behavior','coordinate_contract':'Each shape is duplicated in Blender asset Z-up and native GLB Y-up, source(x,y,z)→exchange(x,z,−y). Shapes are asset-datum coordinates, not node-local coordinates.','assets':{'AST-HSP-005':{'shapes':s,'exclude_context_stock':True,'open_probe_volumes_blender':[{'name':'tray_rear_extraction_'+str(i),'min_m':[-.447,.064,z+.003],'max_m':[.003,.944,z+.044]}for i,z in enumerate([.245,.473,.701])],'purpose':'Individual planes/supports preserve accessible rear compartments'},'AST-HSP-006':{'shapes':t,'exclude_context_stock':True,'open_probe_volumes_blender':[{'name':'lower_tier_rear_access','min_m':[-.225,-.16,.270],'max_m':[.225,.420,.715]},{'name':'push_grip_underhand_void','min_m':[-.180,.325,.835],'max_m':[.180,.385,.898]}],'swivel_sweep_radius_m':.091,'purpose':'Shallow tier shells, narrow frame/grip capsules, separated castors; no global box filling access'}}}
 (BASE/'collision_proposals.json').write_text(json.dumps(data,indent=2)+'\n');return data
if __name__=='__main__':build()
