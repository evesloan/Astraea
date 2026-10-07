from pathlib import Path
import bpy,json,gzip,importlib.util
B=Path(__file__).parent;spec=importlib.util.spec_from_file_location('finish_source_methods',B/'build_source.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);O=B/'source_build001';receipt=json.loads((O/'qa/BUILD_RECEIPT.json').read_text());source=Path(receipt['source']);assert m.sha(source)==receipt['sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));plan=json.loads((B/'CORE_PLAN.json').read_text());actual=dict(plan,parts=m.core.snapshot(bpy.context.scene,plan));assert actual==json.loads((O/'qa/BUILD_EVALUATED_CORE.json').read_text()),'Saved core source changed on independent reopen';fp={o.name:m.m.retained.fingerprint(o)for o in bpy.context.scene.objects};assert fp==json.loads((O/'qa/OBJECT_PRESERVATION.json').read_text())['after']
with gzip.open(O/'qa/BUILD_EVALUATED_STOCK.json.gz','rt')as f:stock=json.load(f)
assert m.stock_snapshot(bpy.data.collections['FIN_RETAINED_RECEIVING_CONTENTS'])==stock,'Retained stock changed after independent save/reopen'
planned={p['name']:p for p in plan['parts']};tri=json.loads((B/'SOURCE_TRIANGLES.json').read_text());evaluated={p['name']:p for p in actual['parts']}
for n in tri['parts']:
 assert evaluated[n]['vertices_xyz']==planned[n]['vertices_xyz'],n
 assert sorted(tuple(sorted(t))for t in evaluated[n]['evaluated_triangles'])==sorted(tuple(sorted(t))for t in tri['parts'][n]),n
m.m.newjson(O/'qa/INDEPENDENT_REOPEN.json',{'status':'PASS_EXACT_COMPLETE_FINISH_SOURCE_REOPEN','source_sha256':m.sha(source),'objects':len(fp),'core_parts':len(actual['parts']),'retained_stock_meshes':len(stock),'source_only':True,'native_lighting_and_visual_acceptance':False,'Game_or_Catalogue_writes':False});print('CONNECTED_FINISH_REOPEN_PASS',flush=True)
