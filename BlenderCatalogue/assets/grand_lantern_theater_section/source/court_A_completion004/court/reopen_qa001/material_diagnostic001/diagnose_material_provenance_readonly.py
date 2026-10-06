"""Read-only retained-material provenance diagnostic. Never saves any blend.
Run once in parent's Blender slot: blender -b --python this.py -- --run
Imports the exact current QA graph implementation without running its check.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, sys
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent; QA=D.parent/'reopen_court_A_winding_readonly.py'; R=D.parents[1]
OUT=R/'reopen_qa001/winding_repair001/authored_source001'
CONTRACT=R/'reopen_qa001/winding_repair001/COURT_A_GEOMETRY_CONTRACT_WINDING_SUCCESSOR.json'
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def label(x):
 return {'python_type':type(x).__name__,'is_string':isinstance(x,str),'name_or_value':x if isinstance(x,str)else getattr(x,'name',str(x))}

def diff(actual,expected,path='$'):
 out=[]
 if isinstance(actual,dict)and isinstance(expected,dict):
  for k in sorted(set(actual)|set(expected)):
   if k not in actual:out.append({'path':path+'.'+k,'actual':'<missing>','expected':expected[k]})
   elif k not in expected:out.append({'path':path+'.'+k,'actual':actual[k],'expected':'<missing>'})
   else:out.extend(diff(actual[k],expected[k],path+'.'+k))
 elif isinstance(actual,(list,tuple))and isinstance(expected,(list,tuple)):
  if len(actual)!=len(expected):out.append({'path':path+'.length','actual':len(actual),'expected':len(expected)})
  for i,(a,b)in enumerate(zip(actual,expected)):out.extend(diff(a,b,path+'['+str(i)+']'))
 elif actual!=expected:out.append({'path':path,'actual':actual,'expected':expected})
 return out

def run():
 report_path=D/'MATERIAL_PROVENANCE_DIAGNOSTIC.json';assert not report_path.exists()
 spec=importlib.util.spec_from_file_location('court_winding_qa_readonly',QA);q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
 import bpy
 sys.path.insert(0,str(q.HELPER.parent))
 from firstpass_common import material_record,digest
 c=read(CONTRACT);build=read(OUT/'BUILD_REPORT.json');source=Path(build['source']);source_hash=sha(source)
 assert source_hash==build['sha256'] and sha(c['base_source'])==q.EXPECTED_BASE
 bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
 original_objects=list(bpy.data.objects);court=bpy.data.collections['A4_COMPLETED_COURT'];new_mats={m for o in court.objects if o.type=='MESH'for m in o.data.materials if m}
 used={m for o in original_objects if o.type=='MESH'for m in o.data.materials if m}
 actual={};errors=[]
 def graph(mat):
  try:return q.graph_record(mat,material_record)
  except Exception as e:errors.append({'material':mat.name,'error':str(e)});return None
 for mat in sorted(used,key=lambda m:m.name):actual[mat]=graph(mat)
 libs={r['source']:r['source_sha256']for r in c['retained_instances']}
 for path in q.MAT_SOURCES:libs.setdefault(str(path),sha(path))
 requested={(v['source'],v['requested_datablock'])for v in build['material_provenance'].values()if'source'in v}
 native={};bindings=[];objects_append_sources={r['source']for r in c['retained_instances']}
 # Combined load duplicates the failing check, while immutable name tuples
 # retain the true requested labels regardless of Blender's list mutation.
 for path,pin in sorted(libs.items()):
  assert sha(path)==pin
  with bpy.data.libraries.load(path,link=False)as(src,dst):
   true_mat_names=tuple(src.materials);true_obj_names=tuple(src.objects)if path in objects_append_sources else ()
   alias_mats=list(true_mat_names);alias_objects=list(true_obj_names)
   dst.materials=alias_mats;dst.objects=alias_objects
   before={'materials':list(alias_mats),'objects':list(alias_objects),'dst_materials_same_list_inside':dst.materials is alias_mats,'dst_objects_same_list_inside':dst.objects is alias_objects}
  bindings.append({'source':path,'source_sha256':pin,'requested_before':before,
                   'after_alias_materials':[label(x)for x in alias_mats],'after_alias_objects':[label(x)for x in alias_objects],
                   'returned_materials':[label(x)for x in dst.materials],'returned_objects':[label(x)for x in dst.objects],
                   'alias_material_list_mutated':not all(isinstance(x,str)for x in alias_mats),'alias_object_list_mutated':not all(isinstance(x,str)for x in alias_objects),
                   'dst_materials_same_list_after':dst.materials is alias_mats,'dst_objects_same_list_after':dst.objects is alias_objects})
  assert len(true_mat_names)==len(dst.materials)
  for source_name,old_label,mat in zip(true_mat_names,alias_mats,dst.materials):
   native[('combined',path,source_name)]={'graph':graph(mat),'generated_name':mat.name,'original_qa_match_label':label(old_label),'original_qa_label_equals_requested':old_label==source_name}
  # Material-only full append distinguishes list-binding from object dependency behavior.
  with bpy.data.libraries.load(path,link=False)as(src,dst):
   only_names=tuple(src.materials);dst.materials=list(only_names)
  for source_name,mat in zip(only_names,dst.materials):native[('materials_only',path,source_name)]={'graph':graph(mat),'generated_name':mat.name}
 # Reproduce each exact one-material builder request too, with names preserved.
 for path,name in sorted(requested):
  with bpy.data.libraries.load(path,link=False)as(src,dst):
   assert name in src.materials;dst.materials=[name]
  mat=dst.materials[0];native[('builder_single_material',path,name)]={'graph':graph(mat),'generated_name':mat.name}
 rows=[];all_missing=[];strict_declared_fail=[];label_only=[]
 for mat,g in actual.items():
  role=q.role_of(mat)
  if role.startswith('court_A_'):continue
  matches=[{'mode':mode,'source':path,'requested_datablock':name,'generated_name':entry['generated_name']}for(mode,path,name),entry in native.items()if g is not None and entry['graph']==g]
  targets=[];declared=build['material_provenance'].get(role)
  if declared and'source'in declared:
   for mode in ['combined','materials_only','builder_single_material']:
    entry=native.get((mode,declared['source'],declared['requested_datablock']))
    targets.append({'mode':mode,'found':entry is not None,'graph_exact':entry is not None and g is not None and entry['graph']==g,
                    'exact_normalized_field_differences':diff(g,entry['graph'])if entry else[{'path':'$','actual':g,'expected':'<native entry absent>'}],
                    'native_graph_sha256':digest(entry['graph'])if entry and entry['graph']is not None else None,
                    'original_qa_match_label':entry.get('original_qa_match_label')if entry else None,
                    'original_qa_label_equals_requested':entry.get('original_qa_label_equals_requested')if entry else None})
  used_by=[{'object':o.name,'prototype_source_name':o.get('firstpass_retained_source_object'),'new_court_mesh':o in court.objects[:],'slots':[i for i,m in enumerate(o.data.materials)if m==mat]}for o in original_objects if o.type=='MESH'and any(m==mat for m in o.data.materials)]
  needed=mat in new_mats and declared and'source'in declared
  combined=next((t for t in targets if t['mode']=='combined'),None)
  if not matches:all_missing.append(mat.name)
  if needed and not (combined and combined['graph_exact']):strict_declared_fail.append({'material':mat.name,'role':role})
  if needed and combined and combined['graph_exact'] and combined['original_qa_label_equals_requested']is False:label_only.append({'material':mat.name,'role':role})
  rows.append({'material':mat.name,'role':role,'used_on_new_court_geometry':mat in new_mats,'used_by':used_by,'actual_graph_sha256':digest(g)if g is not None else None,'exact_native_matches_all_modes':matches,'declared_provenance':declared,'declared_provenance_diagnostics':targets})
 mode_differences=[]
 for mode,path,name in native:
  if mode!='combined':continue
  a=native[(mode,path,name)]['graph'];b=native.get(('materials_only',path,name),{}).get('graph')
  differences=diff(a,b)
  if differences:mode_differences.append({'source':path,'material':name,'combined_vs_material_only_exact_differences':differences})
 assert sha(source)==source_hash and sha(c['base_source'])==q.EXPECTED_BASE
 for p,h in libs.items():assert sha(p)==h
 summary={'status':'READ_ONLY_DIAGNOSTIC_COMPLETE_NO_ACCEPTANCE','source_sha256':source_hash,'retained_material_count':len(rows),
          'materials_without_any_exact_native_graph_match':all_missing,'strict_declared_provenance_graph_failures':strict_declared_fail,
          'label_only_provenance_gate_failures':label_only,'combined_vs_material_only_graph_differences':len(mode_differences),
          'any_mutated_material_label_list':any(b['alias_material_list_mutated']for b in bindings),'any_mutated_object_label_list':any(b['alias_object_list_mutated']for b in bindings),'graph_record_errors':errors}
 report={'summary':summary,'source':str(source),'source_resaved':False,'qa_script_sha256':sha(QA),'diagnostic_script_sha256':sha(__file__),
         'protected_base_sha256':q.EXPECTED_BASE,'library_binding_observations':bindings,'all_retained_materials':rows,'library_load_mode_graph_differences':mode_differences,
         'limits':['No source acceptance or repairs are performed','All node values, links, sampling settings and packed image hashes are retained in exact comparisons','Datablock names are reported as labels; source-name tuples preserve immutable lookup provenance']}
 with report_path.open('x')as h:json.dump(report,h,indent=2,allow_nan=False);h.write('\n')
 print(json.dumps(summary));print(str(report_path))

def main():
 p=argparse.ArgumentParser();p.add_argument('--run',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else sys.argv[1:])
 if a.run:run()
 else:print(json.dumps({'status':'PREPARED_NOT_RUN','qa':str(QA),'output':str(D/'MATERIAL_PROVENANCE_DIAGNOSTIC.json'),'only_bpy_operator':'open_mainfile'}))
if __name__=='__main__':main()
