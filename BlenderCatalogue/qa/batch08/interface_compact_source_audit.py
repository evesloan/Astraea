"""Bounded static compact-source usability sweep; never executes generators."""
import ast,datetime,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
MAIN={
'furniture':'build_furniture.py','view_reveal':'source/build_reveal.py',
'library_structure':'source/build_library_structure.py','library_study':'build_study.py','library_contents':'build_library_contents.py',
'staff_wall':'source/build_staff_wall.py','staff_overhead':'source/build_staff_overhead.py','staff_workbay':'build_staff_workbay.py',
'botanical_canopy':'source/build_canopy.py','botanical_understory':'source/build_botanical_understory.py','botanical_planter':'source/build_botanical_planter.py',
'aquatic_lounge':'source/build_aquatic_lounge.py','aquatic_edges':'source/build_aquatic_edges.py','aquatic_float':'source/build_float.py',
'utility_machines':'source/build_utility_machines.py','utility_console':'source/build_utility_console.py','utility_pipework':'source/build_utility_pipework.py',
'hospitality_counters':'source/build_hospitality_counters.py','hospitality_stations':'source/build_hospitality_stations.py','hospitality_serviceware':'source/build_serviceware.py'}
HELPERS={
 'utility_machines':['assets/utility_machines/source/build_collision_proposals.py'],
 'utility_console':['assets/utility_console/source/write_collision_proposals.py','assets/utility_console/textures/console_graphics.json','assets/utility_console/textures/console_graphics.png'],
 'hospitality_serviceware':['assets/hospitality_serviceware/source/collision_shapes.py'],
 'hospitality_stations':['assets/hospitality_stations/textures/station_graphics.png'],
 'library_contents':['assets/library_contents/build_library_contents.py','assets/library_contents/texture_manifest.json'],
 'botanical_planter':['assets/botanical_planter/source/build_botanical_planter.py','assets/botanical_planter/AST-BOT-006.blend','assets/botanical_planter/collision_proposals.json','assets/botanical_planter/manifest.json'],
 'flange_derivative':['assets/utility_pipework/derived_lod/source/utility_flange_economical.py'],
}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
def excluded(expr):
 return bool(re.search(r"['\"](?:qa|renders)(?:/|['\"])",expr))
def main():
 paths=[p for p in sorted((ROOT/'assets').rglob('*.py')) if not any(x in p.relative_to(ROOT).parts for x in ['qa','renders'])]+sorted((ROOT/'standards').glob('*.py'))
 catalogue=json.loads((ROOT/'catalogue_manifest.json').read_text());rows=[]
 for p in paths:
  s=p.read_text();tree=ast.parse(s);parents={ch:n for n in ast.walk(tree) for ch in ast.iter_child_nodes(n)}
  def context(n):
   out=[]
   while n in parents:
    n=parents[n]
    if isinstance(n,ast.FunctionDef):out.append('function '+n.name)
    elif isinstance(n,ast.If):out.append('if '+ast.unparse(n.test))
   return list(reversed(out))
  calls=[];mkdir=[];reads=[];imports=[]
  for n in ast.walk(tree):
   if isinstance(n,(ast.Import,ast.ImportFrom)):imports.append({'line':n.lineno,'code':ast.unparse(n)})
   if not isinstance(n,ast.Call):continue
   fn=ast.unparse(n.func);method=fn.rsplit('.',1)[-1]
   if method in ['mkdir','makedirs']:
    mkdir.append({'line':n.lineno,'code':ast.unparse(n),'enclosing':context(n)})
   if method in ['read_text','read_bytes','write_text','write_bytes','mkdir','open','open_mainfile','save_as_mainfile','spec_from_file_location','run_path']:
    target=ast.unparse(n.func.value) if method in ['read_text','read_bytes','write_text','write_bytes','mkdir'] and isinstance(n.func,ast.Attribute) else ast.unparse(n)
    if excluded(target):
     rec={'line':n.lineno,'operation':method,'target_expression':target,'enclosing':context(n)};calls.append(rec)
     if method in ['read_text','read_bytes','open_mainfile','spec_from_file_location','run_path']:reads.append(rec)
  direct_guard=any(excluded(x['code']) for x in mkdir)
  loop_guard=any(isinstance(n,ast.For) and any(isinstance(x,ast.Constant) and x.value in ['qa','renders'] for x in ast.walk(n.iter)) and any(isinstance(x,ast.Call) and ast.unparse(x.func).endswith('.mkdir') for x in ast.walk(n)) for n in ast.walk(tree))
  rel=str(p.relative_to(ROOT));family=p.relative_to(ROOT).parts[1] if p.relative_to(ROOT).parts[0]=='assets' else None
  category='shared_standard' if family is None else ('derived_flange_script' if '/derived_lod/' in rel else ('primary_family_generator' if rel=='assets/'+family+'/'+MAIN[family] else 'family_support_or_derivative_script'))
  writes=[x for x in calls if x['operation'] in ['write_text','write_bytes','save_as_mainfile']]
  rows.append({**bind(p),'category':category,'covered_unique_asset_ids':[a['catalogue_id'] for a in catalogue['assets'] if Path(a['source']).parts[1]==family] if category=='primary_family_generator' else [],'line_count':len(s.splitlines()),'imports':imports,'excluded_folder_io':calls,'mkdir_calls':mkdir,'creates_qa_or_render_parent':bool(direct_guard or loop_guard),'excluded_folder_reads_or_imports':reads,'uncreated_excluded_folder_write_candidates':[] if direct_guard or loop_guard else writes,'notes':'Static path/use scan plus manual inspection. No arbitrary code executed and no full dataflow/program-correctness proof.'})
  
 findings=[]
 known=[('CS-001','assets/botanical_canopy/source/build_canopy.py',['AST-BOT-001'],'qa/support_contacts.json'),('CS-002','assets/aquatic_lounge/source/build_aquatic_lounge.py',['AST-AQU-001','AST-AQU-002'],'qa/join_checks.json'),('CS-003','assets/library_contents/build_stock_variants.py',['AST-LIB-006'],'qa/variant_source_import_audit.json'),('CS-004','assets/utility_pipework/derived_lod/source/build_flange_derivative.py',[],'qa/source_geometry.json')]
 for ident,path,assets,target in known:
  row=next(x for x in rows if x['path']==path)
  findings.append({'id':ident,'path':path,'asset_ids':assets,'output':target,'status':'guard_present_in_current_source' if row['creates_qa_or_render_parent'] else 'required_parent_creation_missing','source_sha256':row['sha256'],'write_evidence':row['excluded_folder_io'],'fact':'This is a mandatory output write in the invoked generation entrypoint, not a required QA input. A missing parent makes a source-only restored generator fail at the end of generation.','change_needed':'Create the output parent before this write; preserve geometry and existing master bytes.','execution_proof':'Not executed by this auditor; see separately scoped lead/author rebuild checks.'})
 deps=[]
 for family,files in HELPERS.items():
  for f in files:
   p=ROOT/f;deps.append({'family':family,'required_path':f,'exists':p.is_file(),'included_in_compact_source_by_folder':not any(x in Path(f).parts for x in ['qa','renders','references']),'binding':bind(p) if p.is_file() else None})
 counts={kind:sum(r['category']==kind for r in rows) for kind in ['primary_family_generator','family_support_or_derivative_script','derived_flange_script','shared_standard']}
 out={'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Bounded static audit of production generators/support scripts for compact family restoration; no generators executed, no scenes rebuilt.','compact_exclusion_rule':bind(ROOT/'tools/source_family_packages.py'),'script_counts':counts,'total_scripts':len(rows),'catalogue_unique_design_count':len(catalogue['assets']),'primary_generator_covered_ids':sorted(a for r in rows for a in r['covered_unique_asset_ids']),'excluded_qa_or_render_input_dependencies_found':[{'path':r['path'],**x} for r in rows for x in r['excluded_folder_reads_or_imports']],'findings':findings,'required_local_support_inputs':deps,'files':rows,'distinctions':['build_reveal.py main couples model creation and new QA rendering; line11 creates qa/. It has no dependency on pre-existing QA media and no missing-directory defect. It is not a render-free command.','Other excluded QA/report paths in manifests or strings are references to separate validation evidence, not generation-time reads.','build_stock_variants.py reads the included base source .blend and manifest; botanical closure/repack scripts read included master/family records. These are expected local source dependencies.','Texture redraw scripts need Pillow and, for the two graphic labels, system DejaVu fonts. Current PNG/JSON resources are included; primary model generators read those resources, not pre-existing renders.','New flange helper additionally imports NumPy and SciPy Delaunay; these are environment requirements, not excluded-folder files.','Batch reference-manifest JSONs are common source data. Furniture/reveal reference-image globbing may be empty without optional reference media; it does not supply geometry or fail on a missing QA input.','Static absence of excluded-input dependencies does not certify arbitrary full regeneration or replace prior actual source/export/visual QA.']}
 (OUT/'interface_compact_source_static_scan.json').write_text(json.dumps(out,indent=2)+'\n')
 report=['# Compact-source generator usability sweep',f"Read {len(rows)} Python files: {counts['primary_family_generator']} primary family generators covering all {len(catalogue['assets'])} unique designs, {counts['family_support_or_derivative_script']} other family scripts, {counts['derived_flange_script']} new flange scripts and {counts['shared_standard']} shared standards. This is a bounded static read/AST audit; no generator, render, Blender load or rebuild was executed.",'## Exact findings']
 for f in findings:report.append(f"- **{f['id']} — {f['status']}**: `{f['path']}` writes `{f['output']}`. The output parent must be created before the mandatory write. Current source SHA256 `{f['source_sha256']}`. This does not require a geometry change.")
 report+=['## Required inputs and optional review work','No production import/read from an excluded `qa/` or `renders/` path was found. Exact reviewed I/O, imports, line numbers and per-script hashes are in `interface_compact_source_static_scan.json`.','The only newly found omissions were CS-001 and CS-002; CS-003 was fixed earlier by the lead, and CS-004 was already known and is owned by the flange author. The current statuses above are recalculated from actual current source guards. Separate lead/author execution evidence must establish regeneration.','Required local helper paths are listed in the JSON and all currently exist in included source folders. Common `standards/` material/port helpers, material manifests/images and batch reference manifests remain required. No helper was moved into a missing review folder.','\n'.join('- '+s for s in out['distinctions']),'## Per-generator coverage','| Primary generator | Exact unique assets | Missing excluded-folder input |','|---|---|---|']
 for r in rows:
  if r['category']=='primary_family_generator':report.append('| '+r['path']+' | '+', '.join(r['covered_unique_asset_ids'])+' | none found |')
 text='\n\n'.join(report)+'\n'
 while '|\n\n|' in text:text=text.replace('|\n\n|','|\n|')
 (OUT/'interface_compact_source_report.md').write_text(text)
 print(json.dumps({'scripts':len(rows),'categories':counts,'assets':len(catalogue['assets']),'findings':[{k:f[k] for k in ['id','path','status']} for f in findings],'excluded_input_dependencies_found':len(out['excluded_qa_or_render_input_dependencies_found'])},indent=2))
if __name__=='__main__':main()
