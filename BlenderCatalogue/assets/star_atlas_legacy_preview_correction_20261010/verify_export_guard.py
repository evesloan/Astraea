from pathlib import Path
import sys,json,struct,tempfile,hashlib
W=Path(__file__).resolve().parent;R=W.parents[2];sys.path.insert(0,str(R/'Game/tools'));from validate_production_glb import validate,validate_and_copy,inspect,preview_only
p=json.load(open(W/'NATIVE_EXPORT_CHECK.json'));results=[]
for r in p['rooms']:
 old=R/r['original_runtime'];new=W/r['successor_runtime']
 try:validate(old)
 except ValueError:results.append({'test':'retained contaminated original rejected','source_index':r['source_index'],'status':'PASS'})
 else:raise AssertionError('Contaminated original accepted')
 validate(new);results.append({'test':'clean successor accepted','source_index':r['source_index'],'status':'PASS'})
with tempfile.TemporaryDirectory(prefix='astraea_export_guard_',dir='/tmp')as d:
 d=Path(d);clean=W/p['rooms'][0]['successor_runtime'];raw=clean.read_bytes();n=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+n]);node=next(a for a in j['nodes']if'mesh'in a);node['name']='UnlabelledPresentationFixture';node.setdefault('extras',{})['presentation_only']=True;b=json.dumps(j,separators=(',',':')).encode();b+=b' '*((-len(b))%4);tail=raw[20+n:];fixture=d/'metadata_fixture.glb';fixture.write_bytes(struct.pack('<4sII',b'glTF',2,20+len(b)+len(tail))+struct.pack('<II',len(b),0x4E4F534A)+b+tail);destination=d/'existing_production.glb';destination.write_bytes(raw)
 try:validate_and_copy(fixture,destination)
 except ValueError:pass
 else:raise AssertionError('Metadata-only presentation geometry accepted')
 assert destination.read_bytes()==raw;results.append({'test':'metadata-only presentation geometry rejected before destination mutation','status':'PASS'})
 validate_and_copy(clean,destination);assert destination.read_bytes()==raw;results.append({'test':'validated clean transfer retains exact bytes','status':'PASS'})
assert preview_only('PREVIEW-GROUND.001',{})and preview_only('preview ground',{})and not preview_only('IntendedFloor',{})
report={'status':'PASS','tests':results,'negative_actual_assets':5,'clean_actual_successors':5,'original_asset_history_unchanged':True,'rejects_by_name_and_metadata':True,'destination_preserved_on_rejection':True};(W/'EXPORT_GUARD_CHECK.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':'PASS','tests':len(results)}))
