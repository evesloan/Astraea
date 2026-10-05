from pathlib import Path
import bpy,json,hashlib,math
R=Path(__file__).resolve().parents[1];C=R.parents[1];B=C/'assets/bridge_platform';EPS=2e-5
code=(B/'qa/independent_review_contacts.py').read_text();exec(code[code.index('def cross'):code.index('for i,p in enumerate(P):')])
old=json.loads((B/'qa/independent_review_geometry.json').read_text())['parts']
bpy.ops.wm.open_mainfile(filepath=str(R/'source/AST-CMD-004.blend'));new=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 v=[o.matrix_world@p.co for p in o.data.vertices];v=[(p.x,p.z,-p.y)for p in v];b=[f(p[k]for p in v)for k in range(3)for f in(min,max)];new.append({'name':o.name,'assembly':o.get('assembly'),'vertices':v,'aabb':b,'poly':hull(v)})
for p in old:p['poly']=hull(p['vertices'])
reports=[]
for side,n,assembly,sign in[('Port',0,'BRE_Fore_HangerCollar',-1),('Starboard',2,'BRE_Aft_HangerCollar',1)]:
 caps=[f'BRP_{side}_GuardCap_{i:02d}'for i in[n,n+1]];collars=[p for p in new if p['assembly']==assembly and (p['aabb'][0]+p['aabb'][1])*sign>0];assert len(collars)==1
 collar=collars[0];joins=[]
 for cap in caps:
  ps=[p for p in old if p['assembly']==cap];hits=[{'cap_part':p['name'],'contact':c}for p in ps if(c:=contact(p,collar))and c['kind']=='volume'and c['volume']>1e-8];assert hits,(side,cap)
  back=cap.replace('GuardCap','GuardBack');supports=[{'cap_part':p['name'],'back_part':q['name'],'contact':c}for p in ps for q in old if q['assembly']==back and(c:=contact(p,q))and c['kind']=='volume'and c['volume']>1e-8];assert supports
  joins.append({'old_cap_assembly':cap,'positive_collar_contacts':hits,'retained_direct_back_supports':supports})
 # Collar is continuous over the full former height transition, not a top-only decorative ring.
 assert collar['aabb'][2]<=107.10002 and collar['aabb'][3]>=111.17998
 adjacent=[]
 for p in new:
  if p['assembly']==assembly:continue
  c=contact(p,collar)
  if c and c['kind']=='volume'and c['volume']>1e-8:adjacent.append({'assembly':p['assembly'],'part':p['name'],'contact':c})
 assert any('Mullion'in p['assembly']or'UpperOpaque'in p['assembly']for p in adjacent)
 reports.append({'side':side,'old_corner':n,'old_cap_to_cap_assertion_pass':False,'reason':'Approved differing cap heights no longer share a cap-to-cap volume','replacement_collar':{'name':collar['name'],'assembly':assembly,'actual_world_aabb':collar['aabb']},'old_caps_to_actual004_collar':joins,'actual004_adjacent_positive_contacts':adjacent,'full_height_transition_closure':[107.10,111.18],'perimeter_escape_slit_check':'Independent004 audit checks all145 critical perimeter height slices, excluding only approved door apertures'})
report={'pass':True,'003_source_sha256':hashlib.sha256((B/'source/AST-CMD-003.blend').read_bytes()).hexdigest(),'004_source_sha256':hashlib.sha256((R/'source/AST-CMD-004.blend').read_bytes()).hexdigest(),'method':'Actual reopened004 Blender world vertices and freshly reopened003 measured mesh extract. Convex polygon clipping and actual vertical overlap. Strict positive-volume collar-to-cap and cap-to-back support; original false cap-to-cap assertions remain false.','interfaces':reports}
(R/'qa/changed_guard_interfaces.json').write_text(json.dumps(report,indent=2)+'\n');print('ACTUAL_CHANGED_GUARD_INTERFACES_PASS',len(reports))
