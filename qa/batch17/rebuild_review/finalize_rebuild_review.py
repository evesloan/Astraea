"""Bind final reproducibility evidence after both author production freezes."""
from pathlib import Path
import sys,json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bind(p):
    p=Path(p);return {'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
def verify(row):
    p=ROOT/row['path'];assert p.is_file()and sha(p)==row['sha256'],f'Changed bound file: {row["path"]}'
family_revs=dict(x.split(':',1)for x in sys.argv[1:]);assert set(family_revs)=={'housekeeping_equipment','housekeeping_handling'}
dest=OUT/'FINAL_REBUILD_RECEIPT.json';assert not dest.exists(),'Do not overwrite final receipt'
families=[];witnesses=[];current_bound={};all_assets=[]
for family,rev in sorted(family_revs.items()):
    rp=OUT/f'rebuild_{family}_{rev}.json';sp=OUT/f'stage2_{family}_{rev}.json';r=json.loads(rp.read_text());s=json.loads(sp.read_text());assert r['passed']and s['passed']
    original=ROOT/'assets'/family;rows=r['production_original_inputs']+[r['declared_dependency_manifest']]
    rows+=[x['current']for x in r['actual_exports']]+[x['current_source']for x in r['editable_sources']]+[x['current']for x in r['generated_interface_and_manifest_json']]+[x['current']for x in r['regenerated_original_artwork']]
    for row in rows:verify(row);current_bound[row['path']]=row
    for row in [x['rebuilt']for x in r['actual_exports']]+[x['rebuilt_source']for x in r['editable_sources']]+[x['rebuilt']for x in r['generated_interface_and_manifest_json']]+[x['rebuilt']for x in r['regenerated_original_artwork']]:verify(row);witnesses.append(row)
    full_images=[]
    for asset in r['editable_sources']:
        for b in asset['audit_bindings']:verify(b);witnesses.append(b)
        a,b=[json.loads((ROOT/x['path']).read_text())for x in asset['audit_bindings']]
        witnesses.extend([bind(ROOT/x['geometry_cache'])for x in [a,b]])
        assert a['used_images']==b['used_images'],'Actual image reference paths/identities/packed bytes differ'
        full_images.append({'catalogue_id':asset['catalogue_id'],'used_image_records_including_filepath_exact':True})
        all_assets.append(asset)
    for b in r.get('exact_reviewer_code_snapshots',[]):verify(b);witnesses.append(b)
    witnesses.extend([bind(rp),bind(sp),r['file_read_trace'],r['instrumentation_script'],r['source_audit_script']]+r.get('child_python_read_traces',[]))
    for command in r['commands']:verify(command['log']);witnesses.append(command['log'])
    for b in s['stage2_exact_inputs']+[x['output']for x in s['outputs']]:verify(b);witnesses.append(b)
    fp=original/'FROZEN_PRODUCTION_INDEX.json';frozen=None
    if fp.exists():
        f=json.loads(fp.read_text())
        for row in f['files']:assert sha(original/row['path'])==row['sha256'],f'Frozen author file changed: {row["path"]}'
        frozen=bind(fp);witnesses.append(frozen)
    families.append({'family':family,'revision':rev,'source_only_rebuild_receipt':bind(rp),'stage2_receipt':bind(sp),'author_freeze_index':frozen,'original_input_count':len(r['production_original_inputs']),'source_count':len(r['editable_sources']),'byte_identical_export_count':len(r['actual_exports']),'byte_identical_artwork_count':len(r['regenerated_original_artwork']),'equal_generated_json_count':len(r['generated_interface_and_manifest_json']),'complete_image_path_checks':full_images,'outside_stage_catalogue_reads':r['outside_stage_catalogue_reads'],'stage2_assets':s['selection_provenance']})
for b in witnesses:verify(b)
report=OUT/'REBUILD_REVIEW.md'
lines=['# Batch17 independent source reconstruction','', 'PASS for the frozen four-design sources and all actual exports. This review performs no rendering or production writes.','', '| Family | Original inputs | Editable sources | Identical GLBs | Identical art PNGs | Equal generated JSON |','|---|---:|---:|---:|---:|---:|']
for f in families:lines.append(f"| {f['family']} | {f['original_input_count']} | {f['source_count']} | {f['byte_identical_export_count']} | {f['byte_identical_artwork_count']} | {f['equal_generated_json_count']} |")
lines+=['','Each fresh stage initially contains exactly the declared original generator/artwork/helper/material inputs. No existing new blend, GLB, generated artwork, body proxy, author QA file or reviewer report is seeded. Original graphics regenerate from encoded original glyphs. Python catalogue-open attempts and actual native Blender image bytes at each source save are recorded; external Python artwork children are instrumented when present. No out-of-stage catalogue read was observed. This is not a complete OS syscall trace; Blender, Python, Pillow and their system resources are execution-environment dependencies.','', 'All actual GLBs are byte-identical, including states, native node transforms, mesh data, UVs, normals, materials, extras and embedded images. Editable sources agree for evaluated triangles/material assignment, mesh topology/UV/normals, modifiers, drivers, shape keys, hierarchy/transforms, properties, complete used material node graphs and packed image records including their reference paths. Source-container binary hashes may differ; generated JSON normalizes only each source_sha256 value already bound to the independently read source pair. No geometry, interface, hash of an export, artwork value, timing field or source semantic property is normalized.','', 'Body selection is explicitly documented as a separate reviewer second stage. Its generated inputs are the already rebuilt detailed collision JSON and selection names recovered from author keep flags in the rebuilt editable sources. The selector is run twice; exact shape dictionaries, ownership, voids and motion records are preserved. The generated selection config and generated detailed geometry are never labelled original production inputs. Literal subset preservation adds no hull or intrusion at any owner pose; omitted detail stays omitted. Physical adequacy and omitted-distance measurements belong to the separate geometry review.','']
for f in families:
    lines.append(f"- {f['family']}: "+'; '.join(f"{a['catalogue_id']} {a['detailed_shape_count']} detailed → {a['retained_shape_count']} retained ({a['omitted_shape_count']} omitted)"for a in f['stage2_assets']))
lines+=['','Earlier attempts are retained. Handling r01 stopped because of a reviewer audit helper naming collision, after successful generation; corrected subsequent independent runs passed. Any later superseded attempts remain in their own stage and receipt. No engine adoption, host room or species fit, mechanical/operational acceptance, runtime performance or render acceptance is claimed here.','', 'See FINAL_REBUILD_RECEIPT.json for exact input/source/export/JSON/artwork/stage2 bindings and per-family receipts for all individual source and output pairs.']
report.write_text('\n'.join(lines)+'\n')
receipt={'passed':True,'issued_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Independent final frozen Batch17 source-only reconstruction, exact actual outputs and editable semantics, original artwork, interface JSON, and separately labelled generated-input stage2 literal body selection','families':families,'assets':all_assets,'all_current_production_bindings':[current_bound[k]for k in sorted(current_bound)],'evidence_bindings':list({b['path']:b for b in witnesses}.values()),'report':bind(report),'finalizer':bind(Path(__file__)),'no_production_mutation':True,'rendering_performed':False,'limits':'Reconstruction proves declared deterministic source/output closure and semantic identity. It does not prove physical usefulness, engine implementation, fit, host paths, dynamics, performance or final visual review.'}
dest.write_text(json.dumps(receipt,indent=2)+'\n');print('FINAL_REBUILD_PASS',sha(dest),'production bindings',len(current_bound),'evidence',len(receipt['evidence_bindings']))
