"""Reviewed future job: JSON-only marker precision repair in NEW GLB copies.
No Blender, source rebuild/save, tolerance changes, native work or original edits.
The unchanged strict verifier runs in a separate pure-Python process afterward.
"""
import sys
sys.dont_write_bytecode = True
import argparse, copy, hashlib, json, os, shutil, struct, subprocess, time, traceback
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
P = Path('/workspace/scratch/375c2e438292/pool-feature-export-preparation001')
sys.path.insert(0, str(P)); sys.path.insert(0, str(P/'vendor'))
from gate import gate, sha, read, require, run_path, write_new, INPUTS
from check_glb import decode
CONFIG = HERE / 'CORRECTION_INPUTS.json'
EXPECTED_CONFIG_SHA = '6055120423becd86e5626aabecaa5d53ea564402efc2d600338d126593f7e2fd'

def check_inputs():
    require(sha(CONFIG) == EXPECTED_CONFIG_SHA, 'Correction input manifest changed')
    c = read(CONFIG)
    for name, h in c['files'].items(): require(sha(name) == h, 'Original input changed: '+name)
    g = gate()
    require(c['expected_affected_markers'] == 30 and c['expected_affected_plant_files'] == 6, 'Correction scope changed')
    return c,g

def chunks(path):
    data = Path(path).read_bytes(); require(len(data)>=20, 'Invalid GLB')
    magic,version,length = struct.unpack_from('<III',data)
    require(magic==0x46546c67 and version==2 and length==len(data), 'Invalid GLB header')
    out=[]; offset=12
    while offset < len(data):
        length,kind=struct.unpack_from('<II',data,offset);offset+=8
        require(length%4==0 and offset+length<=len(data),'Invalid padded GLB chunk')
        out.append((kind,data[offset:offset+length]));offset+=length
    require([k for k,b in out]==[0x4e4f534a,0x004e4942], 'Exact JSON/BIN chunk inventory required')
    return out

def make_copy(asset, source_snapshot, old_path, new_path, config):
    old_chunks=chunks(old_path); doc=json.loads(old_chunks[0][1]); original=copy.deepcopy(doc)
    d=decode(old_path); objects={o['name']:o for o in source_snapshot['objects']}; edits=[]
    require(sha(source_snapshot['source'])==source_snapshot['source_sha256']==asset['source_sha256'], 'Actual retained source pin mismatch')
    if asset['family']=='lighting':
        shutil.copyfile(old_path,new_path)
        require(sha(old_path)==sha(new_path),'Lighting copy must be byte-identical')
    else:
        require(asset['family']=='plant','Unexpected asset family')
        root=d['nodes'][asset['name']]
        require(root['parent'] is None and root['mesh'] is None and np.array_equal(root['matrix'],np.eye(4)), 'Plant root must remain exact identity')
        source_root=objects[asset['name']]
        require(source_root['type']=='EMPTY' and source_root['parent'] is None and np.array_equal(source_root['world_matrix_godot'],np.eye(4)), 'Source root is not identity')
        for name,o in sorted(objects.items()):
            if o['type']!='EMPTY' or name==asset['name']: continue
            require(name.endswith('_SOIL_CONTACT'),'Unapproved marker kind')
            node=d['nodes'][name]; raw=doc['nodes'][node['index']]; expected=np.asarray(o['world_matrix_godot'])
            require(node['parent']==o['parent']==asset['name'] and node['mesh'] is None,'Marker hierarchy/type changed')
            require(node['extras']==o['extras'] and o['extras']['physical_part'] in asset['mesh_parts'],'Marker physical provenance changed')
            require(np.array_equal(expected[:3,:3],np.eye(3)) and np.array_equal(node['matrix'][:3,:3],np.eye(3)), 'Marker basis changed')
            require(not any(k in raw for k in ['matrix','rotation','scale','mesh','skin','camera']), 'Only plain marker translation is allowed')
            t=expected[:3,3].tolist(); old=raw.get('translation')
            require(t[1]==config['source_marker_y_m'] and 0 < t[1] <= config['exporter_near_zero_threshold_m'], 'Wrong near-zero source value')
            predicted=[v if abs(v)>config['exporter_near_zero_threshold_m'] else 0.0 for v in t]
            require(old==predicted and old[1]==0 and old[0]==t[0] and old[2]==t[2], 'Current translation is not exact documented canonicalization')
            require(np.array_equal(node['matrix'][:3,3],old), 'Unexpected parent effect')
            raw['translation']=t
            edits.append(dict(node_index=node['index'],name=name,parent=node['parent'],old_translation=old,new_translation=t,
                source_snapshot_sha256=sha(Path(config['original_run'])/'snapshots'/(asset['name']+'.json')),
                source_world_matrix=o['world_matrix_godot'],source_parent_world_matrix=source_root['world_matrix_godot'],
                source_properties=o['extras'],basis_unchanged=True,exact_installed_exporter_canonicalization=True))
        require(len(edits)==5,'Exactly five existing markers per plant required')
        reverted=copy.deepcopy(doc)
        for edit in edits: reverted['nodes'][edit['node_index']]['translation']=edit['old_translation']
        require(reverted==original,'Any non-marker-translation JSON change is forbidden')
        encoded=json.dumps(doc,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode('utf-8'); encoded+=b' '*((-len(encoded))%4)
        binary=old_chunks[1][1]
        data=struct.pack('<III',0x46546c67,2,12+8+len(encoded)+8+len(binary))+struct.pack('<II',len(encoded),0x4e4f534a)+encoded+struct.pack('<II',len(binary),0x004e4942)+binary
        with new_path.open('xb') as f:f.write(data)
    new_chunks=chunks(new_path); new_doc=json.loads(new_chunks[0][1]); require(new_chunks[1][1]==old_chunks[1][1],'Binary chunk bytes changed')
    require(new_doc==doc,'Serialized JSON differs from the scoped correction')
    corrected=decode(new_path)
    for name,o in objects.items():
        if o['type']=='EMPTY':
            n=corrected['nodes'][name]
            require(np.array_equal(n['matrix'],np.asarray(o['world_matrix_godot'])), 'Corrected marker/root matrix is not exact source')
            require(n['extras']==o['extras'] and n['parent']==o['parent'], 'Corrected marker/root provenance changed')
    return dict(asset=asset['name'],original_glb=str(old_path),original_glb_sha256=sha(old_path),corrected_glb=str(new_path),corrected_glb_sha256=sha(new_path),
        original_binary_sha256=hashlib.sha256(old_chunks[1][1]).hexdigest(),corrected_binary_sha256=hashlib.sha256(new_chunks[1][1]).hexdigest(),binary_byte_count=len(old_chunks[1][1]),binary_byte_identical=True,
        original_json_chunk_sha256=hashlib.sha256(old_chunks[0][1]).hexdigest(),corrected_json_chunk_sha256=hashlib.sha256(new_chunks[0][1]).hexdigest(),
        only_permitted_semantic_json_changes=True,marker_translations=edits,source_sha256=asset['source_sha256'],lighting_byte_identical=(sha(old_path)==sha(new_path)) if asset['family']=='lighting' else None)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',required=True);args=ap.parse_args();config,g=check_inputs()
    out=run_path(args.run); require(not out.exists(),'Preserve surviving run; choose a new label')
    old=Path(config['original_run']); original_export=read(old/'EXPORT_RECEIPT.json'); original_snapshot=read(old/'SNAPSHOT_RECEIPT.json')
    require(original_export['status']=='EXPORTED_PENDING_INDEPENDENT_EQUIVALENCE','Unexpected original stage')
    require(original_export['inputs_sha256']==original_snapshot['inputs_sha256']==sha(INPUTS),'Original input receipt mismatch')
    require(original_export['snapshot_receipt_sha256']==sha(old/'SNAPSHOT_RECEIPT.json'),'Original snapshot receipt mismatch')
    out.mkdir(); (out/'snapshots').mkdir(); (out/'exports').mkdir(); (out/'correction_logs').mkdir(); lineage=[]
    try:
        sr=copy.deepcopy(original_snapshot); er=copy.deepcopy(original_export)
        for asset in g['assets']:
            r=next(x for x in sr['assets'] if x['asset']==asset['name']); old_snapshot=Path(r['snapshot']); new_snapshot=out/'snapshots'/old_snapshot.name
            require(old_snapshot==old/'snapshots'/(asset['name']+'.json') and sha(old_snapshot)==r['snapshot_sha256'],'Unexpected original snapshot')
            shutil.copyfile(old_snapshot,new_snapshot);require(sha(new_snapshot)==r['snapshot_sha256'],'Snapshot must be byte-identical');r['snapshot']=str(new_snapshot)
            e=next(x for x in er['assets'] if x['asset']==asset['name']); old_glb=Path(e['export']); new_glb=out/'exports'/old_glb.name
            require(old_glb==old/'exports'/(asset['name']+'.glb') and sha(old_glb)==e['export_sha256'],'Unexpected original GLB')
            require(e['snapshot_sha256']==r['snapshot_sha256'],'Original export snapshot pin changed')
            row=make_copy(asset,read(new_snapshot),old_glb,new_glb,config);lineage.append(row)
            e['export']=str(new_glb);e['export_sha256']=sha(new_glb);e['precision_correction']='Only copied-GLB marker JSON translations restored from exact saved-source snapshot; original binary preserved'
            write_new(out/(asset['name']+'_EXPORT.json'),e)
        require(sum(len(r['marker_translations']) for r in lineage)==30,'Exactly 30 total marker corrections required')
        write_new(out/'SNAPSHOT_RECEIPT.json',sr)
        correction=dict(status='PASS_EXACT_JSON_TRANSLATION_COPY_PENDING_UNCHANGED_STRICT_KEEPER',script_sha256=sha(__file__),config_sha256=sha(CONFIG),
            original_export_receipt_sha256=sha(old/'EXPORT_RECEIPT.json'),original_snapshot_receipt_sha256=sha(old/'SNAPSHOT_RECEIPT.json'),assets=lineage,
            exact_marker_translations_restored=30,binary_chunks_changed=False,source_files_changed=False,blender_launched=False,native_operations=False,originals_preserved=True)
        write_new(out/'PRECISION_CORRECTION_LINEAGE.json',correction)
        er['snapshot_receipt_sha256']=sha(out/'SNAPSHOT_RECEIPT.json');er['precision_correction_lineage_sha256']=sha(out/'PRECISION_CORRECTION_LINEAGE.json');er['original_export_receipt_sha256']=sha(old/'EXPORT_RECEIPT.json')
        write_new(out/'EXPORT_RECEIPT.json',er);check_inputs()
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',BLIS_NUM_THREADS='2',MKL_NUM_THREADS='2',NUMEXPR_NUM_THREADS='2');env.pop('PYTHONPATH',None);env.pop('PYTHONHOME',None)
        command=['/usr/bin/python3',str(P/'verify_features.py'),'--run',args.run];log=out/'correction_logs/unchanged_strict_equivalence.log';started=time.monotonic()
        with log.open('x')as f:result=subprocess.run(command,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=300)
        record=dict(command=command,timeout_s=300,elapsed_s=time.monotonic()-started,exit_code=result.returncode,log_sha256=sha(log),unchanged_checker_sha256=sha(P/'verify_features.py'))
        write_new(out/'correction_logs/VERIFIER_RECEIPT.json',record);require(result.returncode==0,'Unchanged strict checker failed; preserve all output')
        q=out/'equivalence/GLB_EQUIVALENCE.json';require(read(q)['status']=='PASS_SEVEN_ACTUAL_SOURCE_GLB_EQUIVALENCE','Missing aggregate strict pass');check_inputs()
        write_new(out/'CORRECTION_RUN_RECEIPT.json',dict(status='PASS_EXACT_TRANSLATION_COPY_AND_UNCHANGED_STRICT_EQUIVALENCE',lineage_sha256=sha(out/'PRECISION_CORRECTION_LINEAGE.json'),equivalence_sha256=sha(q),verifier=record,originals_unchanged=True,native_acceptance='NOT_RUN'))
        print('PASS_EXACT_TRANSLATION_COPY_AND_UNCHANGED_STRICT_EQUIVALENCE',str(out),flush=True)
    except BaseException:
        write_new(out/'CORRECTION_FAILURE.json',dict(status='FAILED_PRESERVE_ALL_OUTPUTS',completed_assets=lineage,traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
