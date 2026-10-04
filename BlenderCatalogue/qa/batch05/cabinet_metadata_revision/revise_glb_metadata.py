"""Change only JSON hinge extras; retain every non-JSON chunk byte-for-byte."""
from pathlib import Path
import copy,hashlib,json,struct
BASE=Path(__file__).resolve().parents[3]
QA=BASE/'qa/batch05/cabinet_metadata_revision'
ASSET=BASE/'assets/staff_workbay'
NAME='AST-STF-007_supply_work_cabinet.glb'
def sha(b):return hashlib.sha256(b).hexdigest()
def read(path):
    b=path.read_bytes();magic,version,total=struct.unpack_from('<4sII',b)
    assert magic==b'glTF' and version==2 and total==len(b)
    chunks=[];off=12
    while off<len(b):
        length,kind=struct.unpack_from('<II',b,off);chunks.append((kind,b[off+8:off+8+length]));off+=8+length
    assert off==len(b) and chunks[0][0]==0x4e4f534a
    return b,chunks,json.loads(chunks[0][1])
def without_hinge_extras(data):
    result=copy.deepcopy(data)
    for node in result['nodes']:
        if node.get('name')=='AST-STF-007_door_hinge_pivot':node.pop('extras',None)
    return result

def main():
    before,chunks,old=read(QA/'original_inputs'/NAME)
    assert (ASSET/NAME).read_bytes()==before,'Refuse to patch an unexpected export'
    new=copy.deepcopy(old);pivot=next(n for n in new['nodes'] if n.get('name')=='AST-STF-007_door_hinge_pivot')
    props=json.loads((QA/'source_preservation_report.json').read_text())['current_hinge_custom_properties']
    pivot['extras'].pop('axis')
    for k,v in props.items():
        if k.startswith('hinge_') or k=='coordinate_metadata_revision':pivot['extras'][k]=v
    raw=json.dumps(new,separators=(',',':'),ensure_ascii=False).encode();raw+=b' '*((-len(raw))%4)
    new_chunks=[(chunks[0][0],raw)]+chunks[1:]
    payload=b''.join(struct.pack('<II',len(v),k)+v for k,v in new_chunks)
    output=struct.pack('<4sII',b'glTF',2,len(payload)+12)+payload
    (ASSET/NAME).write_bytes(output)
    final,final_chunks,actual=read(ASSET/NAME)
    report={'revision':'hinge-frame-metadata-02','method':'Surgical replacement of GLB JSON hinge extras; all other JSON values and all non-JSON chunks preserved.','old_glb_sha256':sha(before),'current_glb_sha256':sha(final),'old_json_chunk_sha256':sha(chunks[0][1]),'current_json_chunk_sha256':sha(final_chunks[0][1]),'old_bin_chunk_sha256':sha(chunks[1][1]),'current_bin_chunk_sha256':sha(final_chunks[1][1]),'bin_bytes':len(chunks[1][1]),'non_json_chunks_byte_identical':chunks[1:]==final_chunks[1:],'all_json_outside_hinge_extras_identical':without_hinge_extras(old)==without_hinge_extras(actual),'source_and_glb_hinge_properties_match':pivot['extras']==props,'current_hinge_node':pivot,'unqualified_axis_absent':'axis' not in pivot['extras']}
    assert all(report[k] for k in ['non_json_chunks_byte_identical','all_json_outside_hinge_extras_identical','source_and_glb_hinge_properties_match','unqualified_axis_absent'])
    (QA/'glb_preservation_report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
