from pathlib import Path
import json,struct
R=Path('/workspace/astraea-recovered-532087b9-20261010T083844Z');W=R/'BlenderCatalogue/assets/d04_starboard_forward_remaining_courts_20261011';P=json.load(open(W/'PLAN.json'));raw={};file=P['moves'][0]['source_model'];b=(R/'Game/assets/models'/file).read_bytes();n=struct.unpack_from('<I',b,12)[0];doc=json.loads(b[20:20+n]);off=20+n;length=struct.unpack_from('<I',b,off)[0];data=b[off+8:off+8+length]
for row in P['moves']:
 node=next(q for q in doc['nodes']if q['name']==row['name']);assert not any(k in node for k in ['matrix','translation','rotation','scale']);vs=[]
 for prim in doc['meshes'][node['mesh']]['primitives']:
  a=doc['accessors'][prim['attributes']['POSITION']];v=doc['bufferViews'][a['bufferView']];assert a['componentType']==5126 and a['type']=='VEC3';begin=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',12);vs += [list(struct.unpack_from('<3f',data,begin+i*stride))for i in range(a['count'])]
 raw[row['name']]=vs
(W/'RAW_SOURCE_VERTICES.json').write_text(json.dumps(raw,indent=2)+'\n')
s=(R/'BlenderCatalogue/assets/d04_starboard_forward_work_branches_20261011/probe_fresh_import001.gd').read_text().replace('d04_starboard_forward_work_branches_20261011','d04_starboard_forward_remaining_courts_20261011');(W/'probe_fresh_import001.gd').write_text(s)
s=(R/'BlenderCatalogue/assets/d04_starboard_forward_work_branches_20261011/author_native003.py').read_text();a=s.index("patch=json.load(open(W/'PARTIAL_NATIVE_PATCH_RECEIPT001.json'))");b=s.index(';bpy.ops.wm.read_factory_settings',a);s=s[:a]+"patch=export_native(bpy,W,R,'D04StarboardForwardRemainingPatch_r001.blend',P['patch_file'])"+s[b:];s=s.replace('D04StarboardForwardWorkBranches_r002','D04StarboardForwardRemainingCourts_r001').replace('D04_STARBOARD_FORWARD_WORK_BRANCHES','D04_STARBOARD_FORWARD_REMAINING_COURTS').replace("'SFW_'","'SFR_'").replace("'SFW_G'","'SFR_G'").replace("'SFW_ClosedDock_'","'SFR_ClosedDock_'").replace('and i>=4','and i>=5').replace('4351','4357');(W/'author_native001.py').write_text(s);(W/'prepare_native001.py').write_bytes(Path(__file__).read_bytes())
