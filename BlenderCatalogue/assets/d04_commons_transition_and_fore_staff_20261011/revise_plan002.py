from pathlib import Path
import json,hashlib
R=Path('/workspace/astraea-recovered-532087b9-20261010T083844Z');W=R/'BlenderCatalogue/assets/d04_commons_transition_and_fore_staff_20261011';P=json.load(open(W/'PLAN.json'));hold=W/'geometry_attempt001_fixed_controls_and_bearing_contacts';hold.mkdir()
for f in ['PLAN.json','RUNTIME_PLAN.json','EXACT_NATIVE_SOURCE_AUDIT.json','geometry001.log','SOURCE_VIEW_RUN001.json']:(hold/f).write_bytes((W/f).read_bytes())
(hold/'geometry.json').write_bytes((R/'Game/artifacts/d04_commons_transition_fore_staff_geometry.json').read_bytes());P['retained_own_r001_files']={str(f.relative_to(R)):hashlib.sha256(f.read_bytes()).hexdigest()for rec in P['native_export_records']for f in [W/rec['native'],W/rec['export'],R/'Game/assets/models'/rec['export']]};P['source_protected_native_exports'].update(P['retained_own_r001_files']);assert len(P['source_protected_native_exports'])==4339
P['fore_rigid_fixed_control_moves']={'D04PC_StaffUsed_Control':[0,0,.08],'D04PC_StaffClean_Control':[0,0,.08]}
for g in P['fore_new_gates'][:2]:g['control_at'][2]+=.08
for g in P['commons_gates']:
 g['control_at'][0]=g['pivot'][0]+(-.12 if g['name']!='PCCShortStockR'else .12)
 for q in P['commons_parts']:
  if q['name']==g['name']+'_JambPivot':q['verts']=[[x,y,z-.13]for x,y,z in q['verts']]
  if q['name']==g['name']+'_Control':
   center=sum(v[0]for v in q['verts'])/len(q['verts']);delta=g['control_at'][0]-center;q['verts']=[[x+delta,y,z]for x,y,z in q['verts']]
# Remove overlapping centre stock headers; one fixed full header preserves the2.28m profile.
P['commons_parts']=[q for q in P['commons_parts']if q['name']not in ['PCCShortStockL_Head','PCCShortStockR_Head']]
for g in P['commons_gates'][1:]:g['control_members']=[n for n in g['control_members']if not n.endswith('_Head')]
faces=[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
P['commons_parts'].append({'name':'PCCShortStockPair_Head','verts':[[x,y,z]for y in[18.75,18.78]for x,z in[(-73.49,-3.305),(-70.11,-3.305),(-70.11,-3.195),(-73.49,-3.195)]],'faces':faces,'category':'fixed_frame','role':'champagne_metal','runtime_collision':True});P['commons_gates'][1]['control_members'].append('PCCShortStockPair_Head');P['commons_file']='D04_PORT_CENTRAL_SHORT_SERVICE_TRANSITIONS_r002.glb';(W/'PLAN.json').write_text(json.dumps(P,indent=2)+'\n');(W/'revise_plan002.py').write_bytes(Path(__file__).read_bytes())
s=(W/'author_native001.py').read_text().replace('D04CommonsShortServiceTransitions_r001.blend','D04CommonsShortServiceTransitions_r002.blend').replace('D04PortForwardStaffCourtConnection_r001.blend','D04PortForwardStaffCourtConnection_r002.blend').replace('D04_PORT_FORWARD_STAFF_COURT_CONNECTION_r001.glb','D04_PORT_FORWARD_STAFF_COURT_CONNECTION_r002.glb')
a=s.index("fore=export_native");s=s[:a]+'''for name,d in P['fore_rigid_fixed_control_moves'].items():bpy.data.objects[name].location+=Vector((d[0],-d[2],d[1]))
'''+s[a:];s=s.replace("for q in mapping:assert payload(bpy.data.objects[q['name']])==q['payload'],q['name']",'''for q in mapping:
 now=payload(bpy.data.objects[q['name']]);old=q['payload'];assert all(now[k]==old[k]for k in ['verts','faces','uvs','materials']),q['name']
 if q['name']not in P['fore_rigid_fixed_control_moves']:assert now['world_matrix']==old['world_matrix'],q['name']
 else:
  d=P['fore_rigid_fixed_control_moves'][q['name']];delta=Vector((d[0],-d[2],d[1]));assert (bpy.data.objects[q['name']].matrix_world.translation-Vector([old['world_matrix'][i][3]for i in range(3)])-delta).length<.00001
''');s=s.replace("'old4333_native_export_files_unchanged':True","'old4333_native_export_files_unchanged':True,'own_r001_native_exports_preserved':6,'rigid_fixed_staff_control_translations':P['fore_rigid_fixed_control_moves'],'private_gate_leaf_geometry_and_controllers_unchanged':True");(W/'author_native003.py').write_text(s)
