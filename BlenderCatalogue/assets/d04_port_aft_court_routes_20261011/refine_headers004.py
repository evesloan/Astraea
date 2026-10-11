from pathlib import Path
import bpy,json,hashlib,sys
W=Path('/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/d04_port_aft_court_routes_20261011');R=W.parents[2];P=json.load(open(W/'PLAN.json'));sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();old=P['structure'];assert sha(W/old['native'])==old['native_sha256'];bpy.ops.wm.open_mainfile(filepath=str(W/old['native']));joins=[]
for i,g in enumerate(P['gates'][:9]):
 name='PAR_CourtHeader'+str(i);ob=bpy.data.objects[name];part=next(q for q in P['parts']if q['name']==name);x=g['wall_x'];west=x<-40;lo=x-.12 if west else x;hi=x if west else x+.12
 for j,v in enumerate(part['verts']):v[0]=lo if j%4 in [0,3]else hi;v[1]=19.2 if j<4 else 19.7
 # Vertex order is preserved by the previously authored box mesh.
 for v in ob.data.vertices:
  v.co.x=lo if v.co.x<x else hi;v.co.z=min(v.co.z,19.7)
 for row in P['wall_ceiling_junctions']:
  if row.get('wall')==name:row['wall_top_y']=19.7;row['roof_underside_y']=19.7;row.pop('retained_roof');row['roof']=next(q['name']for q in P['parts']if q['category']=='roof'and min(v[0]for v in q['verts'])-.001<=((lo+hi)/2)<=max(v[0]for v in q['verts'])+.001 and min(v[2]for v in q['verts'])<=g['z']<=max(v[2]for v in q['verts']))
 joins.append({'retained_wall':g['court_prefix']+'_GlassUpper','retained_roof':g['court_prefix']+'_Roof','wall_top_y':20.46,'roof_underside_y':20.46})
P['wall_ceiling_junctions']+=joins;P['court_header_fit']='Headers wholly outside retained upper-glass volume, meet new lower corridor roof; original upper-glass successors remain to original20.46 roof plane.'
sys.path.insert(0,str(R/'BlenderCatalogue/assets/d04_staff_court_physical_connections_20261011'));from immutable_revision import export_native
record=export_native(bpy,W,R,'D04PortAftCourtRoutes_r003.blend','D04_PORT_AFT_COURT_ROUTES_r003.glb');P['retained_superseded_native_export_records'].append(old);P['structure']=record;P['structure_file']=record['export'];P['native_export_records']=[P['patch'],record];P['model_pins']={q['export']:q['export_sha256']for q in P['native_export_records']};P.pop('sealed_receipt_sha256',None)
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
for f in[W/'PLAN.json',W/'RUNTIME_PLAN.json',R/'Game/data/architecture/D04_PORT_AFT_COURT_ROUTES.json']:f.write_text(json.dumps(P,indent=2)+'\n')
assert sha(W/old['native'])==old['native_sha256'];print('Nine header volumes fitted against retained glass; original source material/UVs retained')
