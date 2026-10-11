from pathlib import Path
import json,struct,numpy as np
R=Path('/workspace/astraea-recovered-532087b9-20261010T083844Z');W=R/'BlenderCatalogue/assets/d04_port_central_west_staff_circuit_20261011';P=json.load(open(W/'CANDIDATE_PLAN_r002.json'));site=json.load(open(W/'SITE_PREFLIGHT_r002.json'));assert all(not q['blockers']for q in site['supports']+site['roof_rows']);assert len(site['meshes'])==20
P['runtime_preimages']=site['meshes'];P['support_preimages']=site['supports'];faces=[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
def box(name,lo,hi,role='champagne_metal',cat='frame'):
 x,y,z=lo;X,Y,Z=hi;P['parts'].append({'name':name,'verts':[[a,b,c]for b in[y,Y]for a,c in[(x,z),(X,z),(X,Z),(x,Z)]],'faces':faces,'role':role,'category':cat,'runtime_collision':True})
for i,q in enumerate(site['supports']):
 x=q['x'];z=q['z'];h=q['half'];co={(round(c['point'][0],6),round(c['point'][2],6)):c['point'][1]for c in q['corners']};base=[]
 for X,Z in [(x-h,z-h),(x+h,z-h),(x+h,z+h),(x-h,z+h)]:base.append([X,min(q['corners'],key=lambda c:(c['point'][0]-X)**2+(c['point'][2]-Z)**2)['point'][1],Z])
 P['parts'].append({'name':'PCW_Foot'+str(i),'verts':base+[[X,q['column_bottom'],Z]for X,Y,Z in base],'faces':faces,'role':'champagne_metal','category':'frame','runtime_collision':True})
 box('PCW_Column'+str(i),(x-h+.04,q['column_bottom'],z-h+.04),(x+h-.04,16.14,z+h-.04))
 box('PCW_BearingCap'+str(i),(x-h-.06,16.14,z-h-.06),(x+h+.06,16.26,z+h+.06))
# Original uncompressed raw GLB mesh vertices, without transfer modification.
b=(R/'Game/assets/models/D04_PORT_CENTRAL_COMBINEDSTRUCTURE_r002.glb').read_bytes();n=struct.unpack_from('<I',b,12)[0];doc=json.loads(b[20:20+n]);off=20+n;length=struct.unpack_from('<I',b,off)[0];data=b[off+8:off+8+length];raw={}
for row in P['moves']:
 node=next(q for q in doc['nodes']if q['name']==row['name']);assert not any(k in node for k in ['matrix','translation','rotation','scale']),node;mesh=doc['meshes'][node['mesh']];vs=[]
 for prim in mesh['primitives']:
  a=doc['accessors'][prim['attributes']['POSITION']];v=doc['bufferViews'][a['bufferView']];assert a['componentType']==5126 and a['type']=='VEC3';begin=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',12);vs += [list(struct.unpack_from('<3f',data,begin+i*stride))for i in range(a['count'])]
 raw[row['name']]=vs
(W/'RAW_SOURCE_VERTICES.json').write_text(json.dumps(raw,indent=2)+'\n')
for f in ['PLAN.json','NATIVE_AUTHORING_INPUT_PLAN.json']:(W/f).write_text(json.dumps(P,indent=2)+'\n')
old=R/'BlenderCatalogue/assets/d04_port_central_staff_work_links_20261011';s=(old/'author_work_links004.py').read_text().replace("compression_diagnostic/fresh_import_faces.json","FRESH_IMPORT_FACES_r002.json").replace("compression_diagnostic/RAW_GLB_TARGET_VERTICES.json","RAW_SOURCE_VERTICES.json").replace('D04PortCentralCourtWorkPatch_r001','D04PortCentralWestStaffPatch_r002').replace('D04PortCentralCourtWorkLinks_r001','D04PortCentralWestStaffCircuit_r002').replace('D04_PORT_CENTRAL_COURT_WORK_LINKS','D04_PORT_CENTRAL_WEST_STAFF_CIRCUIT').replace('4315','4327');(W/'author_circuit002.py').write_text(s);(W/'finalize_plan002.py').write_bytes(Path(__file__).read_bytes());print('Final plan prepared',len(P['parts']),'parts',len(P['support_preimages']),'supports')
